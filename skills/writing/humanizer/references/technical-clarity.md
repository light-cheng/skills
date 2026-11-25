# Technical / Clarity Mode

Apply this reference **only** when Register routing in [../SKILL.md](../SKILL.md) selects **Technical / Clarity Mode**: technical documentation, specifications, ADRs, API or CLI references, SOPs, runbooks, and engineering explanations.

Leave essays, blog posts, narratives, correspondence, and creative prose in General Mode. Applying technical sentence-length caps or banning figurative language outside technical registers flattens human voice.

Combine these rules with the AI-pattern checks in [patterns.md](patterns.md) (and [zh-adaptation.md](zh-adaptation.md) for Chinese) plus the core invariants in [../SKILL.md](../SKILL.md): preserve every factual claim, condition, threshold, unit, error code, and ordering constraint, and never invent parameters, defaults, or guarantees.

---

## 1. English Technical Register (ASD-STE100 Principles)

Use Simplified Technical English (ASD-STE100) principles so operators and engineers can parse every sentence on the first read without ambiguity.

### 1.1 One approved meaning per word (consistent terminology, no synonym cycling)

Choose one canonical noun for each component, artifact, or role and reuse that exact term everywhere in the document. Assign one distinct meaning to each technical verb (for example, use `select` for choosing an option and `verify` for checking a condition rather than using `check` for both). Repeat the exact term across adjacent sentences instead of cycling through synonyms.

**Before:**
> When a worker fails three consecutive probes, the control plane cordons the host, drains active pods from the machine, and marks the instance unschedulable.

**After:**
> After three consecutive health checks fail on a worker node, the control plane marks that worker node unschedulable and drains its active pods.

### 1.2 Active voice with explicit actors

State who or what performs every action: `you` (the operator in procedural steps), the client, the CLI, the scheduler, or the gateway. Replace agentless passives (`validation is performed`, `tokens are rotated`, `requests are dropped`) with explicit subject-verb clauses. Use passive voice only when the receiver of the action is the true topic and the external actor does not matter (`if the TCP socket is closed by an intermediate firewall`).

**Before:**
> Validation of the webhook signature must be performed before the payload is enqueued, and invalid requests are rejected with HTTP 401.

**After:**
> The ingress handler validates the webhook signature before enqueueing the payload and rejects invalid requests with HTTP 401.

### 1.3 Procedural sentences: <= 20 words, one instruction per sentence

Write operator steps in the imperative mood starting with a direct command verb (`Run`, `Set`, `Verify`, `Restart`). Keep every procedural sentence at **20 words or fewer**, carrying **one instruction** per sentence. Combine two actions in one sentence only when the operator must perform them simultaneously (`Hold Option and click Reload`). When a step depends on a precondition or safety gate, state the condition *before* the command so the operator reads the guard before acting, and place expected system output in its own descriptive sentence.

**Before:**
> Stop the ingestion worker and flush any buffered batches after verifying that no active compaction job is running so you do not corrupt shard metadata.

**After:**
> 1. Verify that no compaction job is running.
> 2. Flush all buffered batches to disk.
> 3. Stop the ingestion worker.

### 1.4 Descriptive sentences: <= 25 words, one topic per sentence

Keep architectural, behavioral, and conceptual sentences at **25 words or fewer**, with one main point per sentence and at most six sentences per paragraph. Unpack stacked prepositional phrases, nested parentheticals, and noun clusters longer than three consecutive nouns (`container runtime health check timeout configuration override` becomes `timeout override for the container runtime health check`). Present three or more parallel conditions, flags, or states as a vertical list or table rather than a run-on clause.

**Before:**
> The client-side exponential backoff retry jitter calculation configuration parameter prevents synchronized reconnection storms across distributed edge gateways during regional upstream outages.

**After:**
> The jitter parameter randomizes client retry delays during exponential backoff. Randomizing delays prevents edge gateways from reconnecting simultaneously after a regional outage.

### 1.5 Concrete verbs over nominalizations

Convert abstract `-tion`, `-ment`, `-ance`, `-ence`, and `-ing` noun wrappers back into direct finite verbs:

- `perform validation of` / `conduct an inspection of` -> `validate` / `inspect`
- `make a modification to` -> `modify` or `change`
- `causes the termination of` -> `terminates` or `stops`
- `provides enforcement of` -> `enforces`
- `achieve convergence` -> `converge`

**Before:**
> This module performs the initialization of the connection pool and provides enforcement of per-tenant rate limits prior to query execution.

**After:**
> This module initializes the connection pool and enforces per-tenant rate limits before executing queries.

### 1.6 Zero metaphors or idioms

State operational mechanics literally. Replace idioms, figurative clichés, and engineering slang (`under the hood`, `spin up`, `footgun`, `kick the tires`, `magic`, `choke on`, `single pane of glass`, `battle-tested`) with observable behavior (`internally`, `start`, `misconfiguration risk`, `run health checks`, `reject`, `tested under production load`). Preserve established domain terms that have standard technical definitions (`deadlock`, `TLS handshake`, `backpressure`, `cold start`, `garbage collection`), using them strictly in their literal technical sense.

**Before:**
> Under the hood, the scheduler spins up a shadow worker and kicks the tires on the new binary before flipping traffic over; misconfiguring the drain window is a classic footgun.

**After:**
> Internally, the scheduler starts a standby worker and runs health checks on the new binary before routing traffic to it. Setting the drain window below active request latency drops in-flight requests.

---

## 2. Chinese Technical Register (简明技术中文)

Note: In Technical / Clarity Mode, the actor and passive-voice rule in §2.4 below supersedes the general formal-prose exemption in [zh-adaptation.md](zh-adaptation.md) §5 whenever omitting the subject obscures operational responsibility.

### 2.1 Verb-first clauses (动词先行)

Lead procedural instructions directly with a concrete action verb (`运行`, `配置`, `校验`, `导出`, `重启`). When a precondition governs the step (`当……时`, `若……`, `确认……后`), place the condition cleanly before the action verb instead of burying the verb behind nominalized subject clauses.

**Before:**
> 在确认上游数据分片副本同步延迟已经降为零的前提下，主库连接切换操作才允许执行。

**After:**
> 确认上游分片的副本同步延迟降为 0 后，再切换主库连接。

### 2.2 Strip empty wrapper verbs (剔除空壳动词与虚词套话)

Remove dummy wrapper verbs (`虚化动词`) and corporate buzzwords so the real technical verb carries the clause directly:

- **`进行`:** `对配置文件进行修改` -> `修改配置文件`; `进行日志排查` -> `排查日志`
- **`实现`:** `实现吞吐量的提升` -> `提高吞吐量`; `实现自动故障转移` -> `自动切换故障节点` (keep `实现` only when meaning "implement an interface or specification", such as `实现 Storage 接口`)
- **`赋能`:** `为持续集成流水线赋能` -> state the concrete mechanism (`缓存构建产物，缩短流水线耗时`)
- **`抓手`:** `以核心延迟指标为抓手优化调度` -> `依据核心延迟指标调整调度策略`
- **`打造`:** `打造高可用网关体系` -> `构建高可用网关` (or state the fault-tolerance guarantee directly)
- **`予以` / `加以`:** `对过期令牌予以拒绝` -> `拒绝过期令牌`; `对异常状态加以记录` -> `记录异常状态`

**Before:**
> 本组件以结构化追踪日志为抓手，通过对慢查询请求进行实时采样与加以聚合，为线上故障定位赋能，打造全链路可观测能力并实现排障耗时的降低。

**After:**
> 本组件实时采样并聚合慢查询的结构化追踪日志，辅助定位线上故障，缩短排障耗时。

### 2.3 Split long `的`-chained pre-modifiers (拆分多层“的”字长定语)

When a noun phrase stacks two or more nested `的` modifiers (translationese left-branching chains), unpack the chain into short sequential clauses ordered by time or cause. Drop redundant `的` inside standard two-noun technical compounds (`内存分配`, `权限校验`, `超时阈值`).

**Before:**
> 网关会丢弃所有未携带由认证服务在当前会话周期内签发的且通过公钥验签校验的访问令牌的写入请求。

**After:**
> 写入请求必须携带认证服务在当前会话内签发的访问令牌。网关用公钥校验令牌签名；若缺失令牌或验签失败，则丢弃该请求。

### 2.4 Explicit actor + action (明确执行主体与动作)

Chinese prose frequently omits grammatical subjects, which in specifications, SOPs, and runbooks creates ambiguity about whether the operator, client SDK, gateway, or background worker performs an action. Name the actor explicitly whenever responsibility starts or shifts (`客户端重试该请求`, `运维人员执行回滚脚本`, `服务端返回 429 状态码`). Omit the subject only in uniform imperative checklists where every step belongs to the human operator, or in a follow-up clause that shares the opening clause's stated subject. Replace vague obligations (`需要处理超时`, `应当保证幂等`) with actor + concrete action (`调用方捕获超时异常并按指数退避重试`, `服务端通过幂等键去重`).

**Before:**
> 当遇到 429 响应时，需要等待 `Retry-After` 指定的时间后再重试，同时应该把限流事件记录下来以便排查。

**After:**
> 收到 429 响应时，客户端按响应头 `Retry-After` 指定的秒数等待后重试，并将限流事件写入本地审计日志。

---

## 3. Normative Precision & Completion Check

Before returning a Technical / Clarity Mode rewrite, verify every item below:

- **Normative keywords preserved:** Formal RFC/specification modals (`MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `MAY` / `必须`, `不得`, `应当`, `可以`) keep their exact obligation level; never soften a hard requirement or harden an optional behavior.
- **Technical literals untouched:** Code spans, CLI flags, API routes, environment variables, error codes, versions, units, and numeric bounds match the source verbatim.
- **English ASD-STE100 bounds met:** One canonical term per concept; active voice with explicit actors; procedural sentences <= 20 words (one instruction unless simultaneous, preconditions first); descriptive sentences <= 25 words; concrete verbs instead of nominalizations; zero metaphors or idioms.
- **Chinese 简明技术中文 bounds met:** Verb-first clauses; zero empty wrapper verbs (`进行`, filler `实现`, `赋能`, `抓手`, `打造`, `予以`, `加以`); multi-`的` chains unpacked into sequential short clauses; actor + action explicit across every state transition.
