import assert from "node:assert/strict";
import { test } from "node:test";
import { statusText, playerName, musicTerminal } from "../../herdr-app/.config/herdr-app/mods/music-dock/model.js";

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

test("launch name is stable, scoped by app home, and accepted by hc", () => {
  assert.equal(playerName("/home/user/.config/herdr-app"), playerName("/home/user/.config/herdr-app"));
  assert.notEqual(playerName("/one"), playerName("/two"));
  assert.match(playerName("/path with spaces/音楽"), /^[a-z0-9_-]{1,32}$/);
});
