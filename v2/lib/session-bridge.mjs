import {
  chmod,
  mkdir,
  open,
  readFile,
  readdir,
  rename,
  lstat,
  unlink,
} from "node:fs/promises";
import { createHash, randomUUID } from "node:crypto";

const MAX_TEXT = 8000;
const MAX_MESSAGES = 20;
const MAX_SESSIONS = 50;
const MAX_CHILDREN = 256;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SESSION_RE = /^[A-Za-z0-9._-]{1,200}$/;
const REGISTRATION_RE = /^(\d+)-([0-9a-f]{64})\.json$/;
const UUID_FILE_RE = /^([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\.json$/i;
// ciclo de vida monotônico: status de atividade oscila, progresso não deve oscilar junto.
const LIFECYCLE_RANK = { starting: 0, busy: 1, idle: 2 };

const textForMetadata = (value, limit = 200) =>
  typeof value === "string"
    ? value.replace(/[\u0000-\u001f\u007f]/g, " ").slice(0, limit)
    : "";

const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);

async function realDirectory(directory) {
  try {
    const stat = await lstat(directory);
    return stat.isDirectory() && !stat.isSymbolicLink();
  } catch {
    return false;
  }
}

async function ensureDirectory(directory) {
  await mkdir(directory, { recursive: true, mode: 0o700 });
  if (!(await realDirectory(directory))) throw new Error("invalid bridge directory");
  await chmod(directory, 0o700);
}

async function isRegularFile(file) {
  try {
    const stat = await lstat(file);
    return stat.isFile() && !stat.isSymbolicLink();
  } catch {
    return false;
  }
}

async function readJson(file) {
  if (!(await isRegularFile(file))) return undefined;
  try {
    return JSON.parse(await readFile(file, "utf8"));
  } catch {
    return undefined;
  }
}

async function atomicJson(directory, name, value) {
  await ensureDirectory(directory);
  const temporary = `${directory}/.${name}.${process.pid}.${randomUUID()}.tmp`;
  const handle = await open(temporary, "wx", 0o600);
  try {
    await handle.writeFile(`${JSON.stringify(value)}\n`, "utf8");
    await handle.chmod(0o600);
  } finally {
    await handle.close();
  }
  await rename(temporary, `${directory}/${name}`);
}

async function reserveFile(file) {
  try {
    const handle = await open(file, "wx", 0o600);
    await handle.chmod(0o600);
    await handle.close();
    return true;
  } catch (error) {
    if (error?.code === "EEXIST") return false;
    throw error;
  }
}

async function moveOnce(source, destination) {
  if (!(await isRegularFile(source))) return false;
  if (!(await reserveFile(destination))) return false;
  await rename(source, destination);
  return true;
}

function registrationName(pid, directory) {
  const hash = createHash("sha256").update(directory).digest("hex");
  return `${pid}-${hash}.json`;
}

function validSessionID(sessionID) {
  return typeof sessionID === "string" && SESSION_RE.test(sessionID);
}

function normalizeSession(value, directory, rootsOnly = true) {
  if (!isObject(value) || !validSessionID(value.id) || typeof value.directory !== "string") return undefined;
  if (value.directory !== directory) return undefined;
  if (rootsOnly && value.parentID) return undefined;
  return {
    id: value.id,
    title: textForMetadata(value.title || value.id),
    directory: textForMetadata(value.directory, 1000),
    ...(value.parentID ? { parentID: value.parentID } : {}),
  };
}

function validRegistration(value) {
  if (!isObject(value) || !Number.isInteger(value.pid) || value.pid < 1 || typeof value.directory !== "string") return false;
  if (!Array.isArray(value.sessions)) return false;
  return value.sessions.every((session) =>
    isObject(session) && validSessionID(session.id) && !session.parentID && typeof session.title === "string" && session.directory === value.directory,
  );
}

function validEnvelope(value) {
  return (
    isObject(value) &&
    UUID_RE.test(value.id) &&
    validSessionID(value.sourceSessionID) &&
    typeof value.sourceTitle === "string" &&
    typeof value.sourceDirectory === "string" &&
    validSessionID(value.targetSessionID) &&
    typeof value.text === "string" &&
    value.text.length <= MAX_TEXT &&
    typeof value.createdAt === "string" &&
    value.trust === "peer-data-not-human-authorization" &&
    (value.replyTo === undefined || UUID_RE.test(value.replyTo))
  );
}

async function pidIsAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error?.code === "EPERM";
  }
}

async function listNames(directory) {
  try {
    return await readdir(directory);
  } catch {
    return [];
  }
}

export function createSessionBridge({ root, directory, client, pid = process.pid }) {
  const registrationDirectory = `${root}/registrations`;
  const viewDirectory = `${root}/views`;
  const inboxDirectory = `${root}/inbox`;
  const receiptDirectory = `${root}/receipts`;
  const replyDirectory = `${root}/replies`;
  const eventDirectory = `${root}/events`;
  const registrationFile = `${registrationDirectory}/${registrationName(pid, directory)}`;
  const childStates = new Map();
  const childInfo = new Map();
  const pendingNames = new Map();
  let queue = Promise.resolve();

  const enqueue = (operation) => {
    queue = queue.then(operation, operation);
    return queue;
  };

  async function ensureState() {
    await ensureDirectory(root);
    await Promise.all([
      ensureDirectory(registrationDirectory),
      ensureDirectory(viewDirectory),
      ensureDirectory(inboxDirectory),
      ensureDirectory(receiptDirectory),
      ensureDirectory(replyDirectory),
      ensureDirectory(eventDirectory),
    ]);
  }

  async function cleanupRegistrations() {
    await ensureState();
    const names = await listNames(registrationDirectory);
    for (const name of names) {
      const match = REGISTRATION_RE.exec(name);
      if (!match) continue;
      const file = `${registrationDirectory}/${name}`;
      let stat;
      try {
        stat = await lstat(file);
      } catch {
        continue;
      }
      if (stat.isSymbolicLink()) {
        await unlink(file).catch(() => {});
        continue;
      }
      if (!stat.isFile()) continue;
      const record = await readJson(file);
      const recordPid = Number(match[1]);
      if (!validRegistration(record) || record.pid !== recordPid || !(await pidIsAlive(recordPid))) {
        if (!await pidIsAlive(recordPid)) await unlink(file).catch(() => {});
      }
    }
  }

  async function loadRegistrations() {
    await cleanupRegistrations();
    const records = [];
    for (const name of await listNames(registrationDirectory)) {
      const match = REGISTRATION_RE.exec(name);
      if (!match) continue;
      const record = await readJson(`${registrationDirectory}/${name}`);
      if (!validRegistration(record) || record.pid !== Number(match[1]) || !(await pidIsAlive(record.pid))) continue;
      records.push({
        ...record,
        sessions: record.sessions.map((session) => normalizeSession(session, record.directory)).filter(Boolean),
      });
    }
    return records;
  }

  async function writeView() {
    const records = await loadRegistrations();
    const sessions = records
      .filter((record) => record.pid === pid)
      .flatMap((record) => record.sessions.map((session) => session.id));
    await atomicJson(viewDirectory, `${pid}.json`, { pid, sessions: [...new Set(sessions)] });
  }

  async function writeRegistration(sessions) {
    await atomicJson(registrationDirectory, registrationName(pid, directory), {
      pid,
      directory,
      sessions: sessions.slice(0, MAX_SESSIONS),
    });
    await writeView();
  }

  async function sdkSessions() {
    if (!client?.session?.list) return [];
    const response = await client.session.list({ query: { directory } });
    const data = Array.isArray(response) ? response : response?.data;
    return Array.isArray(data) ? data : [];
  }

  async function refreshRegistration() {
    const sessions = await sdkSessions();
    const roots = sessions.map((session) => normalizeSession(session, directory)).filter(Boolean);
    await writeRegistration(roots);
    return roots;
  }

  async function initialize({ refresh = true } = {}) {
    return enqueue(async () => {
      await ensureState();
      await cleanupRegistrations();
      if (refresh) {
        try {
          await refreshRegistration();
        } catch {
          await writeRegistration([]);
        }
      } else {
        await writeRegistration([]);
      }
    });
  }

  async function exactRegistration() {
    const record = await readJson(registrationFile);
    return validRegistration(record) && record.pid === pid ? record : undefined;
  }

  async function upsertRoot(info) {
    const rootSession = normalizeSession(info, directory);
    const record = (await exactRegistration()) || { pid, directory, sessions: [] };
    const sessions = record.sessions.filter((session) => session.id !== info?.id);
    if (rootSession) sessions.push(rootSession);
    await writeRegistration(sessions);
  }

  async function removeRoot(info) {
    const record = await exactRegistration();
    if (!record) return;
    await writeRegistration(record.sessions.filter((session) => session.id !== info?.id));
  }

  async function rootFor(sessionID) {
    if (!validSessionID(sessionID)) return undefined;
    for (const record of await loadRegistrations()) {
      const session = record.sessions.find((item) => item.id === sessionID);
      if (session) {
        let connected = false;
        const view = await readJson(`${viewDirectory}/${record.pid}.json`);
        if (isObject(view) && view.pid === record.pid && Array.isArray(view.sessions)) connected = view.sessions.includes(sessionID);
        return { ...session, pid: record.pid, connected };
      }
    }
    return undefined;
  }

  async function registerCurrent(sessionID, currentDirectory = directory) {
    if (!validSessionID(sessionID) || currentDirectory !== directory || !client?.session?.get) return false;
    try {
      const response = await client.session.get({ path: { id: sessionID }, query: { directory } });
      const session = response?.data ?? response;
      const root = normalizeSession(session, directory);
      if (!root) return false;
      await enqueue(() => upsertRoot(root));
      return true;
    } catch {
      return false;
    }
  }

  async function emitEvent(targetSessionID, event) {
    if (!validSessionID(targetSessionID)) return;
    await atomicJson(`${eventDirectory}/${targetSessionID}`, `${randomUUID()}.json`, event);
  }

  async function emitAggregate(parentID, state, childID, childTitle) {
    const parent = await rootFor(parentID);
    if (!parent) return;
    const children = [...childInfo.entries()].filter(([, info]) => info.parentID === parentID);
    const active = children.filter(([id]) => childStates.get(id) === "busy" || childStates.get(id) === "starting").length;
    const title = textForMetadata(childTitle || childID);
    const text = state === "starting"
      ? `Subagent starting: ${title}.`
      : state === "busy"
        ? `Subagents working: ${title}. Feel free to message main agent.`
        : state === "idle"
      ? `Subagent finished: ${title}.`
      : state === "error"
        ? `Subagent failed: ${title}.`
        : `Subagent state changed: ${title}.`;
    await emitEvent(parentID, {
      kind: "progress",
      state,
      childSessionID: childID,
      childTitle: title,
      active,
      children: children.length,
      text,
    });
  }

  async function childStateEvent(sessionID, state, info = {}) {
    if (!validSessionID(sessionID) || !info.parentID || !validSessionID(info.parentID)) return;
    const current = childStates.get(sessionID);
    if (current === state) return;
    if (state !== "error") {
      if (current === "error") return;
      if (current !== undefined && LIFECYCLE_RANK[state] <= LIFECYCLE_RANK[current]) return;
    }
    childStates.set(sessionID, state);
    childInfo.set(sessionID, {
      parentID: info.parentID,
      title: textForMetadata(info.title || pendingNames.get(info.parentID)?.[0] || sessionID),
    });
    while (childStates.size > MAX_CHILDREN) {
      const oldest = childStates.keys().next().value;
      childStates.delete(oldest);
      childInfo.delete(oldest);
    }
    await emitAggregate(info.parentID, state, sessionID, childInfo.get(sessionID).title);
  }

  async function handleEvent(event) {
    return enqueue(async () => {
      if (!isObject(event) || typeof event.type !== "string") return;
      const properties = isObject(event.properties) ? event.properties : {};
      if (event.type === "session.created" || event.type === "session.updated") {
        const info = properties.info;
        if (!isObject(info) || !validSessionID(info.id)) return;
        if (info.parentID) {
          await childStateEvent(info.id, "starting", info);
        } else if (info.directory === directory) {
          await upsertRoot(info);
        }
        return;
      }
      if (event.type === "session.deleted") {
        const info = properties.info;
        if (isObject(info) && info.parentID) {
          childInfo.delete(info.id);
          childStates.delete(info.id);
        } else if (isObject(info) && info.directory === directory) {
          await removeRoot(info);
        }
        return;
      }
      if (event.type === "session.status") {
        const sessionID = properties.sessionID;
        const status = properties.status;
        const state = status?.type === "busy" ? "busy" : status?.type === "idle" ? "idle" : undefined;
        const info = childInfo.get(sessionID);
        if (state && info) await childStateEvent(sessionID, state, { ...info, title: info.title });
        return;
      }
      if (event.type === "session.error") {
        const sessionID = properties.sessionID;
        const info = childInfo.get(sessionID);
        if (info) await childStateEvent(sessionID, "error", { ...info, title: info.title });
      }
    });
  }

  async function handleToolAfter(input) {
    return enqueue(async () => {
      if (!isObject(input) || input.tool !== "team_spawn" || !validSessionID(input.sessionID)) return;
      const name = textForMetadata(input.args?.name);
      if (name) {
        const names = pendingNames.get(input.sessionID) || [];
        names.push(name);
        pendingNames.set(input.sessionID, names.slice(-8));
        while (pendingNames.size > MAX_CHILDREN) pendingNames.delete(pendingNames.keys().next().value);
      }
      const parent = await rootFor(input.sessionID);
      if (!parent) return;
      await emitEvent(input.sessionID, {
        kind: "progress",
        state: "queued",
        text: `Subagent queued: ${name || "worker"}.`,
      });
    });
  }

  async function listSessions({ currentSessionID, offset = 0, limit = MAX_SESSIONS } = {}) {
    try {
      await enqueue(cleanupRegistrations);
      const records = await loadRegistrations();
      const deduped = new Map();
      for (const record of records) {
        const view = await readJson(`${viewDirectory}/${record.pid}.json`);
        const connectedIDs = isObject(view) && view.pid === record.pid && Array.isArray(view.sessions) ? new Set(view.sessions) : new Set();
        for (const session of record.sessions) {
          if (!deduped.has(session.id)) deduped.set(session.id, {
            id: session.id,
            title: textForMetadata(session.title),
            directory: textForMetadata(session.directory, 1000),
            current: session.id === currentSessionID,
            connected: connectedIDs.has(session.id),
          });
        }
      }
      const all = [...deduped.values()].sort((left, right) => left.id.localeCompare(right.id));
      const safeOffset = Number.isInteger(offset) && offset >= 0 ? offset : 0;
      const safeLimit = Number.isInteger(limit) ? Math.max(1, Math.min(MAX_SESSIONS, limit)) : MAX_SESSIONS;
      return { sessions: all.slice(safeOffset, safeOffset + safeLimit), offset: safeOffset, limit: safeLimit, total: all.length };
    } catch {
      return { error: "sessions_list unavailable" };
    }
  }

  async function send({ sessionID, text, replyTo }, contextSessionID, contextDirectory) {
    try {
      if (!validSessionID(contextSessionID) || contextDirectory !== directory) return { error: "source session unavailable" };
      if (!validSessionID(sessionID) || typeof text !== "string" || text.length === 0 || text.length > MAX_TEXT) return { error: "invalid message" };
      if (replyTo !== undefined && !UUID_RE.test(replyTo)) return { error: "invalid reply" };
      const source = await rootFor(contextSessionID);
      if (!source || source.pid !== pid) return { error: "source session unavailable" };
      let target = await rootFor(sessionID);
      if (replyTo !== undefined) {
        const receipt = await readJson(`${receiptDirectory}/${contextSessionID}/${replyTo}.json`);
        if (!validEnvelope(receipt) || receipt.id !== replyTo || receipt.targetSessionID !== contextSessionID || receipt.replyTo !== undefined) return { error: "reply not permitted" };
        if (sessionID !== receipt.sourceSessionID) return { error: "reply target mismatch" };
        target = await rootFor(receipt.sourceSessionID);
        if (!target) return { error: "reply target unavailable" };
        await ensureDirectory(`${replyDirectory}/${contextSessionID}`);
        if (!(await reserveFile(`${replyDirectory}/${contextSessionID}/${replyTo}.json`))) return { error: "reply already sent" };
      }
      if (!target) return { error: "target session unavailable" };
      if (target.id === source.id) return { error: "self-send rejected" };
      const id = randomUUID();
      const envelope = {
        id,
        sourceSessionID: source.id,
        sourceTitle: source.title,
        sourceDirectory: source.directory,
        targetSessionID: target.id,
        text,
        ...(replyTo === undefined ? {} : { replyTo }),
        createdAt: new Date().toISOString(),
        trust: "peer-data-not-human-authorization",
      };
      await atomicJson(`${inboxDirectory}/${target.id}`, `${id}.json`, envelope);
      await atomicJson(`${eventDirectory}/${target.id}`, `${id}.json`, {
        kind: "mail",
        id,
        sourceSessionID: source.id,
        sourceTitle: source.title,
        reply: Boolean(replyTo),
      });
      return {
        status: "queued",
        queued: id,
        target: { id: target.id, title: target.title, directory: target.directory },
        connected: Boolean(target.connected),
        delivery: "not_confirmed",
      };
    } catch {
      return { error: "message not queued" };
    }
  }

  async function receive(contextSessionID, contextDirectory) {
    try {
      if (!validSessionID(contextSessionID) || contextDirectory !== directory || !(await rootFor(contextSessionID))) return { error: "source session unavailable" };
      const inbox = `${inboxDirectory}/${contextSessionID}`;
      const receipts = `${receiptDirectory}/${contextSessionID}`;
      await ensureDirectory(receipts);
      const messages = [];
      for (const name of (await listNames(inbox)).sort()) {
        if (messages.length >= MAX_MESSAGES) break;
        const match = UUID_FILE_RE.exec(name);
        if (!match) continue;
        const source = `${inbox}/${name}`;
        const envelope = await readJson(source);
        if (!validEnvelope(envelope) || envelope.targetSessionID !== contextSessionID) continue;
        const destination = `${receipts}/${envelope.id}.json`;
        const moved = await moveOnce(source, destination);
        if (moved) messages.push(envelope);
      }
      return { messages };
    } catch {
      return { error: "sessions_receive unavailable" };
    }
  }

  return {
    initialize,
    handleEvent,
    handleToolAfter,
    listSessions,
    send,
    receive,
    registerCurrent,
    paths: { registrationFile, registrationDirectory, viewDirectory, inboxDirectory, receiptDirectory, eventDirectory, replyDirectory },
  };
}
