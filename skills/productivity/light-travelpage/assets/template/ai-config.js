/** Public generation switch: does the page show an AI entry? Endpoint, key, model and format live only in server settings. */
export function normalizeAiConfig(raw = { provider: "off" }) {
  if (!raw || typeof raw !== "object" || Array.isArray(raw) ||
      Object.keys(raw).some((key) => key !== "provider") ||
      !["off", "on", "openai"].includes(raw.provider)) {
    throw new Error("ai-config.json must contain only provider: off or on");
  }
  // "openai" is the value older pages were generated with; it means on.
  return { provider: raw.provider === "off" ? "off" : "on" };
}
