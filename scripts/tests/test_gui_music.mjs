import assert from "node:assert/strict";
import { test } from "node:test";
import { statusText, musicTerminal, freshPlayer, OWNER } from "../../herdr-app/.config/herdr-app/mods/music-dock/model.js";

test("now-playing text cannot replay terminal controls or add extra rows", () => {
  assert.equal(statusText("\x1b[31m曲 Track\x1b[0m\nArtist\x00"), "曲 Track Artist");
  assert.equal(statusText(null), "");
});

test("reuse live local players from label-filtered compact hc JSON, without labels", () => {
  const record = (address, state = "live") => ({ address, state });
  assert.equal(musicTerminal([record("remote/t2"), record("t3", "finished"), record("t1g")]), "t1g");
  assert.equal(musicTerminal([]), null);
  assert.throws(() => musicTerminal([record("t1"), record("t2")]), /Multiple/);
});

test("each opening replaces only the owned UI before starting a fresh client", async () => {
  let current = "t-old";
  const calls = [];
  const core = async args => {
    calls.push(args);
    if (args[0] === "ls") return { code: 0, stdout: JSON.stringify({ terminals: [{ address: current, state: "live" }] }) };
    if (args[0] === "kill") { assert.equal(args[1], current); return { code: 0 }; }
    if (args[0] === "run") { current = "t-new"; return { code: 0 }; }
    throw new Error("Unexpected command");
  };
  assert.equal(await freshPlayer(core, "/app", "/home"), "t-new");
  assert.deepEqual(calls.map(c => c[0]), ["ls", "kill", "run", "ls"]);
  assert.deepEqual(calls[0], ["ls", "--json", "--label", `${OWNER}=/app`]);
  assert.deepEqual(calls[2].slice(-2), ["/home/.local/bin/herdr-music", "--player"]);
  assert.equal(calls[2].includes("--name"), false);
});

test("an ambiguous session or failed close never launches or kills another client", async () => {
  const calls = [];
  const core = async args => {
    calls.push(args[0]);
    return args[0] === "ls"
      ? { code: 0, stdout: JSON.stringify({ terminals: [{ address: "t1", state: "live" }, { address: "t2", state: "live" }] }) }
      : { code: 1 };
  };
  await assert.rejects(freshPlayer(core, "/app", "/home"), /Multiple/);
  assert.deepEqual(calls, ["ls"]);
  const failedClose = async args => args[0] === "ls"
    ? { code: 0, stdout: '{"terminals":[{"address":"t1","state":"live"}]}' }
    : (assert.equal(args[0], "kill"), { code: 1 });
  await assert.rejects(freshPlayer(failedClose, "/app", "/home"), /previous GrooveNet UI/);
});
