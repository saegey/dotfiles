// Fuzzy search. Every space-separated term must appear in the text as an
// in-order subsequence; matches that are contiguous, start a path segment or
// are exact substrings rank higher.

const SEPARATORS = "/-_. ";

/** How well `term` matches `text` (both lowercase), or -1 if it doesn't. */
function score(text, term) {
  let total = text.includes(term) ? 10 : 0;
  let at = 0;
  let prev = -2;
  for (const ch of term) {
    const i = text.indexOf(ch, at);
    if (i < 0) return -1;
    total += 1 + (i === prev + 1 ? 4 : 0) + (i === 0 || SEPARATORS.includes(text[i - 1]) ? 3 : 0);
    prev = i;
    at = i + 1;
  }
  return total;
}

/** Items whose text matches `query`, best first. An empty query keeps the order. */
export function search(items, query) {
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return items;
  const ranked = [];
  for (const item of items) {
    const text = item.toLowerCase();
    let total = 0;
    for (const term of terms) {
      const s = score(text, term);
      if (s < 0) { total = -1; break; }
      total += s;
    }
    if (total >= 0) ranked.push({ item, total });
  }
  return ranked.sort((a, b) => b.total - a.total || a.item.length - b.item.length).map((r) => r.item);
}
