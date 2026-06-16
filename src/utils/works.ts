import { getCollection } from 'astro:content';

export async function getWorks() {
  const works = await getCollection('works', ({ data }) => !data.isDraft);
  return works.sort((a, b) => (a.data.order ?? 0) - (b.data.order ?? 0));
}

export async function getChapters(workSlug: string) {
  const all = await getCollection('chapters', ({ data, id }) => {
    if (data.isDraft) return false;
    return id.startsWith(workSlug + '/');
  });
  return all.sort((a, b) => a.data.order - b.data.order);
}

export function extractWorkSlug(chapterId: string): string {
  const idx = chapterId.indexOf('/');
  return idx === -1 ? chapterId : chapterId.slice(0, idx);
}

export function extractChapterSlug(chapterId: string): string {
  const idx = chapterId.indexOf('/');
  let slug = idx === -1 ? chapterId : chapterId.slice(idx + 1);
  slug = slug.replace(/\.(mdx?|markdown|html)$/i, '');
  return slug;
}

export async function getWorksWithChapters() {
  const works = await getWorks();
  const result = [];
  for (const w of works) {
    const chapters = await getChapters(w.slug);
    result.push({ work: w, chapters });
  }
  return result;
}
