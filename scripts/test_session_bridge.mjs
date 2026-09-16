import assert from "node:assert/strict";
import {
  mkdir,
  mkdtemp,
  readFile,
  readdir,
  rm,
  stat,
  symlink,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { test } from "node:test";
import { createSessionBridge } from "../v2/lib/session-bridge.mjs";
import sessionBridgePlugin from "../v2/plugins/session-bridge.mjs";

const makeFixture = async () => {
  const root = await mkdtemp(`${tmpdir()}/session-bridge-`);
  const dirs = { a: `${root}/project-a`, b: `${root}/project-b` };
  await Promise.all([mkdir(dirs.a), mkdir(dirs.b)]);
  const sessions = {
    a: [{ id: "ses_root_a", title: "Main A", directory: dirs.a }, { id: "ses_child_a", title: "Child A", directory: dirs.a, parentID: "ses_root_a" }],
    b: [{ id: "ses_root_b", title: "Main B", directory: dirs.b }],
  };
  const client = { session: {
    list: async ({ query }) => sessions[query.directory === dirs.a ? "a" : "b"],
    get: async ({ path }) => [...sessions.a, ...sessions.b].find((session) => session.id === path.id),
  } };
  return { root, dirs, client, sessions };
};

const context = (sessionID, directory) => ({ sessionID, directory });
const json = (value) => JSON.parse(value);

test("guard ausente retorna {} sem criar estado", async () => {
  const root = await mkdtemp(`${tmpdir()}/session-bridge-guard-`);
  const previous = process.env.OPENCODE_V2_BRIDGE_DIR;
  delete process.env.OPENCODE_V2_BRIDGE_DIR;
  try {
    assert.deepEqual(await sessionBridgePlugin({ client: {}, directory: `${root}/project` }), {});
    assert.deepEqual(await readdir(root), []);
  } finally {
    if (previous === undefined) delete process.env.OPENCODE_V2_BRIDGE_DIR;
    else process.env.OPENCODE_V2_BRIDGE_DIR = previous;
    await rm(root, { recursive: true, force: true });
  }
});

test("lista raízes cross-directory, pagina, filtra mortos e symlink", async () => {
  const fixture = await makeFixture();
  const bridgeA = createSessionBridge({ root: fixture.root, directory: fixture.dirs.a, client: fixture.client });
  const bridgeB = createSessionBridge({ root: fixture.root, directory: fixture.dirs.b, client: fixture.client });
  try {
    await bridgeA.initialize();
    await bridgeB.initialize();
    await writeFile(`${bridgeA.paths.registrationDirectory}/999999999-${"a".repeat(64)}.json`, JSON.stringify({ pid: 999999999, directory: "/dead", sessions: [] }));
    await symlink(bridgeA.paths.registrationFile, `${bridgeA.paths.registrationDirectory}/12345-${"b".repeat(64)}.json`);
    await writeFile(`${bridgeA.paths.registrationDirectory}/control.json`, "not state");
    const result = await bridgeA.listSessions({ currentSessionID: "ses_root_a", limit: 50 });
    assert.deepEqual(result.sessions.map((session) => session.id), ["ses_root_a", "ses_root_b"]);
    assert.equal(result.sessions[0].current, true);
    assert.equal(result.sessions[1].directory, fixture.dirs.b);
    assert.equal(result.sessions[1].connected, true);
    assert.equal((await readdir(bridgeA.paths.registrationDirectory)).includes(`999999999-${"a".repeat(64)}.json`), false);
  } finally {
    await rm(fixture.root, { recursive: true, force: true });
  }
});

test("send autoriza origem registrada, rejeita spoof/destino/self e enfileira receipt", async () => {
  const fixture = await makeFixture();
  const bridgeA = createSessionBridge({ root: fixture.root, directory: fixture.dirs.a, client: fixture.client });
  const bridgeB = createSessionBridge({ root: fixture.root, directory: fixture.dirs.b, client: fixture.client });
  try {
    await bridgeA.initialize();
    await bridgeB.initialize();
    assert.deepEqual(await bridgeA.send({ sessionID: "ses_root_b", text: "hello" }, "ses_child_a", fixture.dirs.a), { error: "source session unavailable" });
    assert.deepEqual(await bridgeA.send({ sessionID: "ses_missing", text: "hello" }, "ses_root_a", fixture.dirs.a), { error: "target session unavailable" });
    assert.deepEqual(await bridgeA.send({ sessionID: "ses_root_a", text: "hello" }, "ses_root_a", fixture.dirs.a), { error: "self-send rejected" });
    const queued = await bridgeA.send({ sessionID: "ses_root_b", text: "hello" }, "ses_root_a", fixture.dirs.a);
    assert.equal(typeof queued.queued, "string");
    assert.equal(queued.connected, true);
    const events = json(await readFile(`${bridgeA.paths.eventDirectory}/ses_root_b/${queued.queued}.json`, "utf8"));
    assert.equal(events.kind, "mail");
    assert.equal("text" in events, false);
    assert.deepEqual((await bridgeB.receive("ses_root_b", fixture.dirs.b)).messages.map((message) => message.text), ["hello"]);
    const mode = (await stat(`${bridgeA.paths.registrationDirectory}/${(await readdir(bridgeA.paths.registrationDirectory))[0]}`)).mode & 0o777;
    assert.equal(mode, 0o600);
    assert.equal((await stat(bridgeA.paths.inboxDirectory)).mode & 0o777, 0o700);
  } finally {
    await rm(fixture.root, { recursive: true, force: true });
  }
});

test("reply só usa receipt original, é exclusiva e não permite pingpong", async () => {
  const fixture = await makeFixture();
  const bridgeA = createSessionBridge({ root: fixture.root, directory: fixture.dirs.a, client: fixture.client });
  const bridgeB = createSessionBridge({ root: fixture.root, directory: fixture.dirs.b, client: fixture.client });
  try {
    await bridgeA.initialize();
    await bridgeB.initialize();
    const original = await bridgeA.send({ sessionID: "ses_root_b", text: "question" }, "ses_root_a", fixture.dirs.a);
    const received = (await bridgeB.receive("ses_root_b", fixture.dirs.b)).messages[0];
    assert.equal(received.id, original.queued);
    const reply = await bridgeB.send({ sessionID: "ses_root_a", text: "answer", replyTo: received.id }, "ses_root_b", fixture.dirs.b);
    assert.equal(typeof reply.queued, "string");
    assert.deepEqual(await bridgeB.send({ sessionID: "ses_root_a", text: "again", replyTo: received.id }, "ses_root_b", fixture.dirs.b), { error: "reply already sent" });
    const answer = (await bridgeA.receive("ses_root_a", fixture.dirs.a)).messages[0];
    assert.equal(answer.replyTo, received.id);
    assert.deepEqual(await bridgeA.send({ sessionID: "ses_root_b", text: "pingpong", replyTo: answer.id }, "ses_root_a", fixture.dirs.a), { error: "reply not permitted" });
  } finally {
    await rm(fixture.root, { recursive: true, force: true });
  }
});

test("receive ignora JSON inválido e symlink; lifecycle emite progresso agregado coalescido", async () => {
  const fixture = await makeFixture();
  const bridgeA = createSessionBridge({ root: fixture.root, directory: fixture.dirs.a, client: fixture.client });
  try {
    await bridgeA.initialize();
    await mkdir(`${bridgeA.paths.inboxDirectory}/ses_root_a`, { recursive: true });
    await writeFile(`${bridgeA.paths.inboxDirectory}/ses_root_a/bad.json`, "{}");
    await symlink(`${bridgeA.paths.inboxDirectory}/ses_root_a/bad.json`, `${bridgeA.paths.inboxDirectory}/ses_root_a/00000000-0000-4000-8000-000000000000.json`);
    assert.deepEqual(await bridgeA.receive("ses_root_a", fixture.dirs.a), { messages: [] });
    await bridgeA.handleToolAfter({ tool: "team_spawn", sessionID: "ses_root_a", args: { name: "worker" } });
    const child = { id: "ses_child_new", title: "Worker title", directory: fixture.dirs.a, parentID: "ses_root_a" };
    await bridgeA.handleEvent({ type: "session.created", properties: { info: child } });
    await bridgeA.handleEvent({ type: "session.status", properties: { sessionID: child.id, status: { type: "busy" } } });
    await bridgeA.handleEvent({ type: "session.status", properties: { sessionID: child.id, status: { type: "busy" } } });
    await bridgeA.handleEvent({ type: "session.status", properties: { sessionID: child.id, status: { type: "idle" } } });
    await bridgeA.handleEvent({ type: "session.error", properties: { sessionID: child.id, error: { message: "secret raw error" } } });
    const files = await readdir(`${bridgeA.paths.eventDirectory}/ses_root_a`);
    const progress = [];
    for (const file of files) {
      const event = json(await readFile(`${bridgeA.paths.eventDirectory}/ses_root_a/${file}`, "utf8"));
      if (event.kind === "progress") progress.push(event);
    }
    assert.equal(progress.some((event) => event.text?.startsWith("Subagent queued: worker.")), true);
    assert.equal(progress.some((event) => event.text?.startsWith("Subagent starting: Worker title.")), true);
    assert.equal(progress.some((event) => event.text?.startsWith("Subagents working: Worker title.")), true);
    assert.equal(progress.some((event) => event.text?.startsWith("Subagent finished: Worker title.")), true);
    assert.deepEqual(new Set(progress.filter((event) => event.childSessionID === child.id).map((event) => event.state)), new Set(["starting", "busy", "idle", "error"]));
    assert.equal(progress.some((event) => JSON.stringify(event).includes("secret raw error")), false);
  } finally {
    await rm(fixture.root, { recursive: true, force: true });
  }
});

test("status oscilante do filho não repete progresso de ciclo de vida", async () => {
  const fixture = await makeFixture();
  const bridgeA = createSessionBridge({ root: fixture.root, directory: fixture.dirs.a, client: fixture.client });
  try {
    await bridgeA.initialize();
    const child = { id: "ses_child_flap", title: "Worker", directory: fixture.dirs.a, parentID: "ses_root_a" };
    await bridgeA.handleEvent({ type: "session.created", properties: { info: child } });
    for (let round = 0; round < 5; round += 1) {
      await bridgeA.handleEvent({ type: "session.updated", properties: { info: child } });
      await bridgeA.handleEvent({ type: "session.status", properties: { sessionID: child.id, status: { type: "busy" } } });
      await bridgeA.handleEvent({ type: "session.status", properties: { sessionID: child.id, status: { type: "idle" } } });
    }
    const states = [];
    for (const file of await readdir(`${bridgeA.paths.eventDirectory}/ses_root_a`)) {
      const event = json(await readFile(`${bridgeA.paths.eventDirectory}/ses_root_a/${file}`, "utf8"));
      if (event.kind === "progress" && event.childSessionID === child.id) states.push(event.state);
    }
    assert.equal(states.filter((state) => state === "idle").length, 1);
    assert.equal(states.filter((state) => state === "starting").length, 1);
    assert.equal(states.filter((state) => state === "busy").length, 1);
  } finally {
    await rm(fixture.root, { recursive: true, force: true });
  }
});

test("plugin registra ferramentas e hooks sem HTTP", async () => {
  const fixture = await makeFixture();
  const previous = process.env.OPENCODE_V2_BRIDGE_DIR;
  process.env.OPENCODE_V2_BRIDGE_DIR = fixture.root;
  try {
    const hooks = await sessionBridgePlugin({ client: fixture.client, directory: fixture.dirs.a });
    const bridgeB = createSessionBridge({ root: fixture.root, directory: fixture.dirs.b, client: fixture.client });
    await bridgeB.initialize();
    await hooks.event({ event: { type: "session.created", properties: { info: fixture.sessions.a[0] } } });
    assert.deepEqual(Object.keys(hooks.tool).sort(), ["sessions_list", "sessions_receive", "sessions_send", "subconfig", "team_spawn"]);
    const listed = json(await hooks.tool.sessions_list.execute({}, context("ses_root_a", fixture.dirs.a)));
    assert.equal(listed.sessions.some((session) => session.id === "ses_root_a"), true);
    const queued = json(await hooks.tool.sessions_send.execute({ sessionID: "ses_root_b", text: "from tool" }, context("ses_root_a", fixture.dirs.a)));
    assert.equal(typeof queued.queued, "string");
    assert.equal(json(await hooks.tool.sessions_receive.execute({}, context("ses_root_a", fixture.dirs.a))).messages.length, 0);

    const calls = [];
    const spawningHooks = await sessionBridgePlugin({
      client: {
        ...fixture.client,
        session: {
          ...fixture.client.session,
          create: async (options) => {
            calls.push(["create", options]);
            return { data: { id: "ses_child_spawn" } };
          },
          promptAsync: async (options) => {
            calls.push(["promptAsync", options]);
            return { data: undefined };
          },
        },
      },
      directory: fixture.dirs.a,
    });
    spawningHooks.config({ agent: { explorer: { model: "anthropic/claude-sonnet-4-6", variant: "medium" } } });
    const spawned = json(await spawningHooks.tool.team_spawn.execute(
      { name: "worker", prompt: "inspect only", agent: "explorer" },
      context("ses_root_a", fixture.dirs.a),
    ));
    assert.equal(spawned.queued, true);
    assert.equal(spawned.childSessionID, "ses_child_spawn");
    assert.equal(calls.length, 2);
    assert.equal(calls[0][1].body.parentID, "ses_root_a");
    assert.equal(calls[1][1].body.agent, "explorer");
    assert.equal("model" in calls[1][1].body, false);
  } finally {
    if (previous === undefined) delete process.env.OPENCODE_V2_BRIDGE_DIR;
    else process.env.OPENCODE_V2_BRIDGE_DIR = previous;
    await rm(fixture.root, { recursive: true, force: true });
  }
});

test("subconfig recarrega catálogo e grava override para restart", async () => {
  const fixture = await makeFixture();
  const previousRoot = process.env.OPENCODE_V2_BRIDGE_DIR;
  const previousConfig = process.env.OPENCODE_CONFIG_DIR;
  const configDir = `${fixture.root}/config`;
  await mkdir(configDir, { recursive: true });
  await writeFile(`${configDir}/subagent-models.json`, '{"version":1,"overrides":{}}\n');
  process.env.OPENCODE_V2_BRIDGE_DIR = fixture.root;
  process.env.OPENCODE_CONFIG_DIR = configDir;
  try {
    const hooks = await sessionBridgePlugin({
      client: {
        ...fixture.client,
        config: {
          providers: async () => ({ providers: [{ id: "openai", models: {
            luna: { id: "gpt.5.6-luna", providerID: "openai", name: "Luna", variants: { low: {}, xhigh: {} } },
          } }] }),
        },
      },
      directory: fixture.dirs.a,
    });
    hooks.config({ agent: {
      "coder-plus": { model: "anthropic/old", variant: "low" },
    } });
    const reloaded = json(await hooks.tool.subconfig.execute({ agent: "reload" }, context("ses_root_a", fixture.dirs.a)));
    assert.equal(reloaded.status, "reloaded");
    const saved = json(await hooks.tool.subconfig.execute({ agent: "coder-plus", model: "openai/gpt-5-6-luna", effort: "xh" }, context("ses_root_a", fixture.dirs.a)));
    assert.equal(saved.status, "saved");
    assert.equal(saved.model, "openai/gpt.5.6-luna");
    assert.equal(saved.variant, "xhigh");
    assert.equal(JSON.parse(await readFile(`${configDir}/subagent-models.json`, "utf8")).overrides["coder-plus"].variant, "xhigh");
  } finally {
    if (previousRoot === undefined) delete process.env.OPENCODE_V2_BRIDGE_DIR;
    else process.env.OPENCODE_V2_BRIDGE_DIR = previousRoot;
    if (previousConfig === undefined) delete process.env.OPENCODE_CONFIG_DIR;
    else process.env.OPENCODE_CONFIG_DIR = previousConfig;
    await rm(fixture.root, { recursive: true, force: true });
  }
});
