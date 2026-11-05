/**
 * Store listing URLs. Left empty until each is actually published --
 * DownloadCard renders a "Coming soon" badge instead of a link for any
 * entry left blank here. Fill these in once the listings exist.
 */
export const PLAY_STORE_URL = process.env.NEXT_PUBLIC_PLAY_STORE_URL?.trim() || "";
export const MICROSOFT_STORE_URL = process.env.NEXT_PUBLIC_MICROSOFT_STORE_URL?.trim() || "";
/** iOS is a later platform target, not yet in active development. */
export const APPLE_STORE_URL = process.env.NEXT_PUBLIC_APPLE_STORE_URL?.trim() || "";

export const SITE_NAME = "Agal";
export const SITE_TAGLINE = "Fair prices. Verified harvests. Straight from Tawi-Tawi.";
export const BACKEND_HEALTH_URL = "https://api-agal.msutcto.dev/health";
export const SEPOLIA_CONTRACT_ADDRESS = "0x3B7E22F9F7f323AB4E95AEDea84BDBf13465A3d3";
export const SEPOLIA_CONTRACT_URL = `https://sepolia.etherscan.io/address/${SEPOLIA_CONTRACT_ADDRESS}`;
const deploymentHost = process.env.VERCEL_PROJECT_PRODUCTION_URL || process.env.VERCEL_URL;
const configuredSiteUrl = process.env.NEXT_PUBLIC_SITE_URL?.trim()
  || (deploymentHost ? `https://${deploymentHost}` : "http://localhost:3000");
const siteUrl = new URL(configuredSiteUrl);
if (!["http:", "https:"].includes(siteUrl.protocol)) {
  throw new Error("NEXT_PUBLIC_SITE_URL must use http:// or https://");
}
export const SITE_URL = siteUrl.origin;
