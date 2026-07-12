type Query = { filter: string; page: number };

const cache = new Map<number, string[]>();

export async function loadPage(query: Query): Promise<string[]> {
  if (cache.has(query.page)) return cache.get(query.page)!;
  const rows = await api.list({ filter: query.filter, page: query.page });
  cache.set(query.page, rows);
  return rows;
}

export function onFilterChanged(state: Query, filter: string): Query {
  return { ...state, filter, page: 1 };
}
