import fs from "node:fs/promises";
import path from "node:path";

// Um agente por papel: o nome lógico é o próprio agente configurado.
export const AGENT_TARGETS = Object.freeze({
  "coder-basic": ["coder-basic"],
  "coder-plus": ["coder-plus"],
  "coder-pro": ["coder-pro"],
  explorer: ["explorer"],
  summarizer: ["summarizer"],
  reviewer: ["reviewer"],
});

const EFFORT_ALIASES = Object.freeze({
  l: "low",
  low: "low",
  m: "medium",
  medium: "medium",
  h: "high",
  high: "high",
  xh: "xhigh",
  xhigh: "xhigh",
  max: "max",
});

const safeFile = (value) => typeof value === "string" && value.length > 0 && !value.includes("\0");

export const configPath = (configDir) => path.join(configDir, "subagent-models.json");

export const indexPath = (stateDir) => path.join(stateDir, "subconfig-index.json");

export const readIndex = async (file) => {
  if (!safeFile(file)) return { version: 1, agents: {}, models: [] };
  try {
    return JSON.parse(await fs.readFile(file, "utf8"));
  } catch {
    return { version: 1, agents: {}, models: [] };
  }
};

export const targetAgents = (name, config) => {
  const configured = config?.agent && typeof config.agent === "object" ? config.agent : {};
  if (AGENT_TARGETS[name]) return AGENT_TARGETS[name].filter((id) => configured[id]);
  return configured[name] ? [name] : [];
};

export const canonicalEffort = (value) => {
  if (typeof value !== "string") return undefined;
  return EFFORT_ALIASES[value.trim().toLowerCase()];
};

const normalizeModel = (value) => String(value).toLowerCase().replace(/[._]/g, "-");

const extractModel = (entry) => {
  if (!entry || typeof entry !== "object") return undefined;
  const variants = entry.variants && typeof entry.variants === "object" ? Object.keys(entry.variants) : [];
  return {
    id: entry.id,
    name: entry.name ?? entry.id,
    providerID: entry.providerID,
    variants,
  };
};

export const flattenProviders = (payload) => {
  const providers = payload?.data?.providers ?? payload?.providers ?? [];
  if (!Array.isArray(providers)) return [];
  return providers.flatMap((provider) => {
    const models = provider?.models && typeof provider.models === "object" ? provider.models : {};
    return Object.values(models).map((model) => extractModel(model)).filter((model) => model?.id && model?.providerID);
  });
};

export const findModel = (models, requested) => {
  if (!Array.isArray(models) || typeof requested !== "string") return undefined;
  const exact = models.find((model) => model.id === requested);
  if (exact) return exact;
  const normalized = normalizeModel(requested);
  const matches = models.filter((model) => normalizeModel(`${model.providerID}/${model.id}`) === normalized);
  return matches.length === 1 ? matches[0] : undefined;
};

export const readOverrides = async (file) => {
  if (!safeFile(file)) return {};
  try {
    const parsed = JSON.parse(await fs.readFile(file, "utf8"));
    return parsed?.overrides && typeof parsed.overrides === "object" ? parsed.overrides : {};
  } catch {
    return {};
  }
};

const atomicWrite = async (file, value) => {
  await fs.mkdir(path.dirname(file), { recursive: true, mode: 0o700 });
  const temp = `${file}.${process.pid}.tmp`;
  await fs.writeFile(temp, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  await fs.rename(temp, file);
};

export const writeIndex = (file, value) => atomicWrite(file, value);

export const writeOverride = async (file, agent, model, variant) => {
  const overrides = await readOverrides(file);
  overrides[agent] = { model, variant };
  await atomicWrite(file, { version: 1, overrides });
};

export const applyOverrides = (config, overrides) => {
  if (!config?.agent || !overrides || typeof overrides !== "object") return config;
  for (const [logicalName, override] of Object.entries(overrides)) {
    if (!override || typeof override.model !== "string" || typeof override.variant !== "string") continue;
    for (const target of targetAgents(logicalName, config)) {
      config.agent[target].model = override.model;
      config.agent[target].variant = override.variant;
    }
  }
  return config;
};

export const buildIndex = (models, config) => ({
  version: 1,
  generatedAt: new Date().toISOString(),
  agents: Object.fromEntries(Object.keys(AGENT_TARGETS).map((name) => [name, targetAgents(name, config)])),
  models: models.sort((a, b) => `${a.providerID}/${a.id}`.localeCompare(`${b.providerID}/${b.id}`)),
});

export const resolveSelection = ({ agent, model, effort, index, config }) => {
  const targets = targetAgents(agent, config);
  if (!targets.length) throw new Error(`agente desconhecido ou não carregado: ${agent}`);
  const selectedModel = findModel(index?.models, model);
  if (!selectedModel) throw new Error(`modelo não encontrado no catálogo: ${model}`);
  const variant = canonicalEffort(effort);
  if (!variant) throw new Error(`effort inválido: ${effort}; use low, medium, high, xhigh ou max`);
  if (!selectedModel.variants.includes(variant)) {
    const available = selectedModel.variants.length ? selectedModel.variants.join(", ") : "nenhum";
    throw new Error(`${selectedModel.providerID}/${selectedModel.id} não oferece ${variant}; disponíveis: ${available}`);
  }
  return { agent, targets, model: `${selectedModel.providerID}/${selectedModel.id}`, variant };
};
