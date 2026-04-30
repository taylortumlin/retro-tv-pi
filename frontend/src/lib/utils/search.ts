import type { Programme } from '../types/epg';

export function fuzzySearch(programmes: Programme[], query: string): Programme[] {
  if (!query.trim()) return [];

  const terms = query.toLowerCase().split(/\s+/);

  return programmes
    .map(p => {
      const text = `${p.title} ${p.subtitle} ${p.categories.join(' ')} ${p.episode}`.toLowerCase();
      let score = 0;

      for (const term of terms) {
        if (p.title.toLowerCase().includes(term)) score += 10;
        else if (p.subtitle.toLowerCase().includes(term)) score += 5;
        else if (p.categories.some(c => c.toLowerCase().includes(term))) score += 3;
        else if (text.includes(term)) score += 1;
        else return { p, score: 0 };
      }

      return { p, score };
    })
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(r => r.p);
}
