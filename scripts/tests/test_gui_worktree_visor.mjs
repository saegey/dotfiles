import assert from "node:assert/strict";
import { test } from "node:test";
import { rowsFor, safeUrl, targetFor } from "../../herdr-app/.config/herdr-app/mods/worktree-visor/model.js";

test("repo context prefers the focused terminal and preserves the machine", () => {
  const spaces = [{ id: "remote/s1", folder: "/srv/main", machine: "remote" }];
  assert.deepEqual(targetFor({ space: "remote/s1", cwd: "/srv/worktree" }, spaces),
    { cwd: "/srv/worktree", machine: "remote" });
  assert.deepEqual(targetFor({ space: "remote/s1", cwd: null }, spaces),
    { cwd: "/srv/main", machine: "remote" });
  assert.deepEqual(targetFor(null, []), { cwd: null, machine: null });
});

test("only web links become clickable", () => {
  for (const url of ["https://repo.app.localhost", "http://localhost:1338/path", "https://github.com/org/repo/pull/1"])
    assert.equal(safeUrl(url), url);
  for (const url of [null, "file:///tmp/a", "javascript:alert(1)", "https://user:secret@host/a", "https://host/a b", "https://host/\x1b[31m", "https://host\\evil", "https://host:bad", "https://host:99999"])
    assert.equal(safeUrl(url), null);
});

test("renders fallback issues, distinct PR checks, local Actions and partial failures", () => {
  const rows = rowsFor({
    head: "local-head", ticket: "SKY-12", apps: [], linear: { issue: null, error: "Linear unavailable" },
    github_issues: { issues: [{ identifier: "#9", title: "Issue title", state: { name: "OPEN" },
      url: "https://github.com/o/r/issues/9", description: "Issue description" }] },
    github: { pr: { number: 2, title: "PR title", state: "OPEN", reviewDecision: "CHANGES_REQUESTED",
      url: "https://github.com/o/r/pull/2", headRefOid: "remote-head",
      statusCheckRollup: [{ name: "Tests", conclusion: "FAILURE", detailsUrl: "https://github.com/check" }] } },
    actions: { runs: [{ workflowName: "Build", conclusion: "SUCCESS", event: "push", url: "https://github.com/run" }] },
    stacks: { projects: [], error: "Stack monitor unavailable" },
  });
  assert(rows.some(r => r.heading && r.text === "GitHub issues"));
  assert(rows.some(r => r.markdown && r.text === "Issue description"));
  assert(rows.some(r => r.text.includes("PR head differs") && r.tone === "warning"));
  assert(rows.some(r => r.text.includes("FAILURE") && r.tone === "error"));
  assert(rows.some(r => r.text.includes("SUCCESS") && r.tone === "success"));
  assert(rows.some(r => r.text === "Stack monitor unavailable"));
  assert(!rows.some(r => r.text === "Linear unavailable"));
});

test("Linear takes precedence and unsafe remote URLs remain plain text", () => {
  const rows = rowsFor({ head: "abc", linear: { issue: { identifier: "SKY-1", title: "Linear title",
    url: "file:///tmp/a", description: "a".repeat(7000) } },
    github_issues: { issues: [{ identifier: "#2", title: "Fallback title" }] } });
  assert(rows.some(r => r.text === "Linear title"));
  assert(!rows.some(r => r.text === "Fallback title"));
  assert.equal(rows.find(r => r.text.startsWith("SKY-1  ·")).url, null);
  assert.equal(rows.find(r => r.markdown).text.length, 6000);
});
