import assert from "node:assert/strict";
import { test } from "node:test";
import {
  applyOverrides,
  buildIndex,
  canonicalEffort,
  findModel,
  flattenProviders,
  resolveSelection,
  targetAgents,
} from "../v2/lib/subconfig.mjs";

const config = {
  agent: {
    "coder-basic": { model: "anthropic/old", variant: "high" },
    "coder-plus": { model: "anthropic/old", variant: "medium" },
    explorer: { model: "anthropic/old", variant: "medium" },
  },
};

test("catálogo achata providers e aceita alias de effort", () => {
  const models = flattenProviders({ providers: [{ id: "openai", models: {
    luna: { id: "gpt.5-luna", providerID: "openai", name: "Luna", variants: { low: {}, xhigh: {} } },
  } }] });
  assert.equal(models.length, 1);
  assert.equal(canonicalEffort("xh"), "xhigh");
  assert.equal(findModel(models, "openai/gpt-5-luna").id, "gpt.5-luna");
});

test("override lógico se aplica ao agente único do papel", () => {
  const copy = structuredClone(config);
  applyOverrides(copy, { "coder-plus": { model: "openai/gpt-5.6-luna", variant: "xhigh" } });
  assert.deepEqual(targetAgents("coder-plus", copy), ["coder-plus"]);
  assert.equal(copy.agent["coder-plus"].model, "openai/gpt-5.6-luna");
  assert.equal(copy.agent["coder-plus"].variant, "xhigh");
  // papel não carregado não recebe override nem cria agente novo
  assert.deepEqual(targetAgents("coder-pro", copy), []);
  assert.equal(copy.agent["coder-pro"], undefined);
});

test("seleção rejeita effort ausente e resolve modelo pontuado", () => {
  const models = [{ id: "gpt-5.6-luna", providerID: "openai", name: "Luna", variants: ["low", "xhigh"] }];
  const index = buildIndex(models, config);
  const selected = resolveSelection({ agent: "coder-plus", model: "openai/gpt-5-6-luna", effort: "xh", index, config });
  assert.equal(selected.model, "openai/gpt-5.6-luna");
  assert.equal(selected.variant, "xhigh");
  assert.throws(() => resolveSelection({ agent: "coder-plus", model: "openai/gpt-5.6-luna", effort: "high", index, config }), /não oferece high/);
});
