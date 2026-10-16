// Server-side transport for OpenAI- and Anthropic-format APIs. No secrets are included in UI status.
// Internally every message keeps the OpenAI chat shape; each format converts at the edge.
export const API_FORMATS = ["openai-chat", "openai-responses", "anthropic-messages"];
const LEGACY_STYLES = { "chat-completions": "openai-chat", responses: "openai-responses" };
const ANTHROPIC_VERSION = "2023-06-01";

export function normalizeApiFormat(value = "openai-chat") {
  const format = LEGACY_STYLES[value] || value;
  if (!API_FORMATS.includes(format)) throw new Error(`AI API 格式必须为 ${API_FORMATS.join("、")} 之一。`);
  return format;
}

export function normalizeBaseUrl(value){
  let url;try{url=new URL(value);}catch{throw new Error('AI 服务地址必须是完整的 HTTP(S) Base URL。');}
  if(!['http:','https:'].includes(url.protocol)||url.username||url.password||url.search||url.hash)throw new Error('AI Base URL 不能包含密钥、账号、查询参数或片段。');
  if(/\/(chat\/completions|responses|messages|models)\/?$/.test(url.pathname))throw new Error('请填写 Base URL（如 /v1），不要填写具体请求端点。');
  const pathname=url.pathname.replace(/\/+$/,'')||'/v1';
  return url.origin+pathname;
}

function responseInput(messages){
  return messages.flatMap(m=>{
    if(m.role==='tool')return [{type:'function_call_output',call_id:m.tool_call_id,output:String(m.content)}];
    if(m.role==='assistant'&&m.responseItems)return m.responseItems;
    const content=typeof m.content==='string'?[{type:m.role==='assistant'?'output_text':'input_text',text:m.content}]:Array.isArray(m.content)?m.content.map(c=>{
      if(c.type==='text')return {type:'input_text',text:c.text};
      if(c.type==='image_url')return {type:'input_image',image_url:c.image_url.url,...(c.image_url.detail?{detail:c.image_url.detail}:{})};
      throw new Error('当前 AI 输入仅支持文字和图片。');
    }):[];
    return [...(content.length?[{role:m.role,content}]:[]),...(m.tool_calls||[]).map(c=>({type:'function_call',call_id:c.id,name:c.function.name,arguments:c.function.arguments}))];
  });
}

function anthropicBlocks(content){
  if(typeof content==='string')return content?[{type:'text',text:content}]:[];
  if(!Array.isArray(content))return [];
  return content.map(c=>{
    if(c.type==='text')return {type:'text',text:c.text};
    if(c.type==='image_url'){
      const url=c.image_url.url, data=/^data:([^;,]+);base64,(.*)$/.exec(url);
      return {type:'image',source:data?{type:'base64',media_type:data[1],data:data[2]}:{type:'url',url}};
    }
    throw new Error('当前 AI 输入仅支持文字和图片。');
  });
}

// Anthropic keeps the system prompt apart and answers tool calls inside the next user turn.
function anthropicRequest(messages){
  const system=messages.filter(m=>m.role==='system').map(m=>String(m.content)).join('\n\n');
  const out=[];
  const push=(role,blocks)=>{
    const last=out.at(-1);
    if(last&&last.role===role)last.content.push(...blocks);else out.push({role,content:[...blocks]});
  };
  for(const m of messages){
    if(m.role==='system')continue;
    if(m.role==='tool'){push('user',[{type:'tool_result',tool_use_id:m.tool_call_id,content:String(m.content)}]);continue;}
    if(m.role==='assistant'){
      out.push({role:'assistant',content:m.anthropicContent||[...anthropicBlocks(m.content),...(m.tool_calls||[]).map(c=>{
        let input;try{input=JSON.parse(c.function.arguments||'{}');}catch{input={};}
        return {type:'tool_use',id:c.id,name:c.function.name,input};
      })]});
      continue;
    }
    push('user',anthropicBlocks(m.content));
  }
  return {system,messages:out};
}

export function createAiClient({baseUrl,apiKey='',apiFormat='openai-chat',fetchImpl=fetch}){
  const base=normalizeBaseUrl(baseUrl), format=normalizeApiFormat(apiFormat);
  async function request(endpoint,body,signal){
    const key=typeof apiKey==='function'?await apiKey():apiKey;
    const auth=format==='anthropic-messages'
      ?{...(key?{'x-api-key':key}:{}),'anthropic-version':ANTHROPIC_VERSION}
      :(key?{Authorization:'Bearer '+key}:{});
    let res;try{res=await fetchImpl(base+'/'+endpoint,{method:body?'POST':'GET',redirect:'manual',headers:{'Content-Type':'application/json',...auth},...(body?{body:JSON.stringify(body)}:{}),signal:signal||AbortSignal.timeout(15000)});}
    catch(e){throw new Error(e.name==='TimeoutError'||e.name==='AbortError'?'AI 请求超时；已执行的动作保留，可在记录中撤销。':'无法连接 AI 服务。手动操作仍可使用。');}
    if(!res.ok)throw new Error(`AI 服务返回 HTTP ${res.status}。请检查格式、模型、密钥与服务权限。`);
    try{return await res.json();}catch{throw new Error('AI 服务未返回有效 JSON。');}
  }
  return {
    format,
    async listModels(signal){const data=await request('models',null,signal);return (data.data||[]).map(m=>m.id).filter(id=>typeof id==='string');},
    async complete({model,messages,tools=[],signal}){
      if(!model)throw new Error('请先配置 AI_MODEL。');
      if(format==='openai-chat'){
        const data=await request('chat/completions',{model,messages,tools,tool_choice:'auto',stream:false,max_tokens:5000},signal);
        const m=data.choices?.[0]?.message;if(!m||m.role!=='assistant')throw new Error('AI 服务未返回有效助手消息。');return m;
      }
      if(format==='anthropic-messages'){
        const {system,messages:converted}=anthropicRequest(messages);
        const data=await request('messages',{model,max_tokens:5000,...(system?{system}:{}),messages:converted,
          tools:tools.map(t=>({name:t.function.name,description:t.function.description,input_schema:t.function.parameters})),
          ...(tools.length?{tool_choice:{type:'auto'}}:{})},signal);
        if(!Array.isArray(data.content)||data.role!=='assistant')throw new Error('AI 服务未返回有效助手消息。');
        if(data.stop_reason==='max_tokens')throw new Error('AI 回复被截断，未保存任何改动。');
        return {role:'assistant',content:data.content.filter(c=>c.type==='text').map(c=>c.text).join('\n'),
          tool_calls:data.content.filter(c=>c.type==='tool_use').map(c=>({id:c.id,type:'function',function:{name:c.name,arguments:JSON.stringify(c.input??{})}})),
          anthropicContent:data.content};
      }
      const data=await request('responses',{model,input:responseInput(messages),tools:tools.map(t=>({type:'function',...t.function,strict:false})),tool_choice:'auto',stream:false,store:false,max_output_tokens:5000,include:['reasoning.encrypted_content']},signal);
      if(!Array.isArray(data.output)||data.status&&data.status!=='completed')throw new Error('AI 服务未返回完整 Responses 输出。');
      return {role:'assistant',content:data.output.filter(o=>o.type==='message').flatMap(o=>o.content||[]).filter(c=>c.type==='output_text').map(c=>c.text).join('\n'),tool_calls:data.output.filter(o=>o.type==='function_call').map(o=>({id:o.call_id,type:'function',function:{name:o.name,arguments:o.arguments}})),responseItems:data.output};
    }
  };
}

/** Server settings: the AI_* set when AI_BASE_URL is set, otherwise the older OPENAI_* set.
 * Fields are never mixed across sets, so a new key never reaches an old endpoint. Travelers never choose any of these. */
export function serverAiSettings(env){
  if(env.AI_BASE_URL)return {baseUrl:env.AI_BASE_URL,apiKey:env.AI_API_KEY||'',model:env.AI_MODEL,
    apiFormat:normalizeApiFormat(env.AI_API_FORMAT||'openai-chat')};
  return {baseUrl:env.OPENAI_BASE_URL,apiKey:env.OPENAI_API_KEY||'',model:env.OPENAI_MODEL,
    apiFormat:normalizeApiFormat(env.OPENAI_API_STYLE||'openai-chat')};
}
