import type { MetadataRoute } from "next";
import { newsPosts } from "@/lib/news";
import { SITE_URL } from "@/lib/config";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes = [
    "",
    "/overview",
    "/how-it-works",
    "/manual",
    "/tutorial",
    "/faq",
    "/news",
    "/terms",
    "/privacy",
  ].map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: new Date(),
  }));

  const newsRoutes = newsPosts.map((post) => ({
    url: `${SITE_URL}/news/${post.slug}`,
    lastModified: new Date(post.date),
  }));

  return [...staticRoutes, ...newsRoutes];
}
