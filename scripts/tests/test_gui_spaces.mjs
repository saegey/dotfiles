import { test } from 'node:test';
import assert from 'node:assert/strict';
import { repoPath, iconFor, badgeFor, ticketFor, foldRows, reviewFor } from '../../herdr-app/.config/herdr-app/mods/dotfiles-spaces/model.js';

test('review markers match explicit checkout and branch and exclude remote paths', () => {
  const records = { '/worktree': { repo: 'skysafe/cloud', pr: 12, branch: 'author/SKY-12' } };
  const g = { top: '/worktree', branch: 'author/SKY-12' };
  assert.equal(reviewFor(records, g, null).pr, 12);
  assert.equal(reviewFor(records, { ...g, branch: 'main' }, null), null);
  assert.equal(reviewFor(records, g, 'vps'), null);
  assert.equal(reviewFor(records, { ...g, top: '/other' }, null), null);
});

test('folding hides only grouped worktrees and keeps active children and counts on the parent', () => {
  const rows = [
    { w: { id: 'main' }, g: { repo: 'local/repo' } },
    { w: { id: 'child', active: true }, g: { repo: 'local/repo' }, tree: '└─' },
    { w: { id: 'remote' }, g: { repo: 'remote/repo' } },
    { w: { id: 'remote-child' }, g: { repo: 'remote/repo' }, tree: '└─' },
    { w: { id: 'orphan' }, g: { repo: 'orphan' } },
  ];
  const original = JSON.stringify(rows);
  const folded = foldRows(rows, new Set(['local/repo']));
  assert.deepEqual(folded.map(r => r.w.id), ['main', 'remote', 'remote-child', 'orphan']);
  assert.equal(folded[0].children.length, 1);
  assert.equal(folded[0].children[0].w.active, true);
  assert.equal(folded[0].closed, true);
  assert.deepEqual(foldRows(rows, new Set()).map(r => r.w.id), rows.map(r => r.w.id));
  assert.equal(JSON.stringify(rows), original);
});

test('repo icons survive space renames and inherit through a worktree common dir', () => {
  const config = { repos: [{ path: '~/Projects/cloud', icon: { emoji: '☁️' } }] };
  const g = { repo: JSON.stringify([null, '/home/adam/Projects/cloud/.git']), linked: true };
  const path = repoPath(g, '/worktrees/new-name');
  assert.deepEqual(iconFor(config, null, path, '/home/adam'), { emoji: '☁️' });
  assert.equal(iconFor(config, 'remote', path, '/home/adam'), null);
  assert.equal(iconFor({ repos: {} }, null, path, '/home/adam'), null);
});

test('stack badges isolate each checkout, include health and distinguish unavailable Docker', () => {
  const snapshot = { projects: [
    { checkout: '/repo', running: 2, total: 3, unhealthy: 1 },
    { checkout: '/worktree', running: 8, total: 8 },
  ] };
  assert.deepEqual(badgeFor(snapshot, '/repo', 'cloud'), { text: '[2]', tone: 'ansi1', tip: '2/3 dev-stack containers running · 1 unhealthy' });
  assert.equal(badgeFor(snapshot, '/worktree', 'cloud').text, '[8]');
  assert.equal(badgeFor(snapshot, '/other', 'infra'), null);
  assert.equal(badgeFor({ error: 'Docker unavailable' }, '/repo', 'skysafe-cloud').text, '[?]');
  assert.equal(badgeFor({ projects: [] }, '/repo', 'skysafe-cloud').text, '[0]');
});

test('ticket IDs come from branches without depending on display names', () => {
  assert.equal(ticketFor('adam/sky-6384-external'), 'SKY-6384');
  assert.equal(ticketFor('main'), null);
  assert.equal(ticketFor('pr-481'), null);
});
