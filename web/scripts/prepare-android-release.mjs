import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";

// Run only for an approved artifact. Version/build/min-sdk must come from its
// Android manifest, not from a filename or the current Flutter source version.
const { values } = parseArgs({
  options: {
    source: { type: "string" },
    version: { type: "string" },
    build: { type: "string" },
    "min-sdk": { type: "string" },
    "release-date": { type: "string" },
    channel: { type: "string" },
  },
});

if (!values.source || !/^\d+\.\d+\.\d+$/.test(values.version ?? "") || !/^\d+$/.test(values.build ?? "") || !/^\d+$/.test(values["min-sdk"] ?? "")) {
  throw new Error("Usage: npm run release:prepare -- --source <approved.apk> --version <x.y.z> --build <n> --min-sdk <n> [--release-date YYYY-MM-DD] [--channel demo|beta|production]");
}
if (values.channel && !["demo", "beta", "production"].includes(values.channel)) {
  throw new Error("Release channel must be demo, beta, or production.");
}
if (values["release-date"] && (!/^\d{4}-\d{2}-\d{2}$/.test(values["release-date"]) || Number.isNaN(Date.parse(values["release-date"])) || new Date(values["release-date"]).toISOString().slice(0, 10) !== values["release-date"])) {
  throw new Error("Release date must be a valid YYYY-MM-DD date.");
}

const web = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = path.resolve(values.source);
const bytes = await readFile(source);
if (bytes[0] !== 0x50 || bytes[1] !== 0x4b) {
  throw new Error("The artifact is not an APK/ZIP archive.");
}
const filename = `agal-${values.version}-build${values.build}.apk`;
const destination = path.join(web, "public", "downloads");
const checksum = createHash("sha256").update(bytes).digest("hex");
await mkdir(destination, { recursive: true });
await copyFile(source, path.join(destination, filename));
await writeFile(path.join(destination, `${filename}.sha256`), `${checksum}  ${filename}\n`);
await writeFile(path.join(web, "lib", "android-release.json"), `${JSON.stringify({
  version: values.version,
  build: Number(values.build),
  minSdk: Number(values["min-sdk"]),
  filename,
  url: `/downloads/${filename}`,
  bytes: (await stat(source)).size,
  sha256: checksum,
  releaseDate: values["release-date"] ?? null,
  channel: values.channel ?? null,
}, null, 2)}\n`);
console.log(`Prepared ${filename}: ${(bytes.length / (1024 * 1024)).toFixed(1)} MiB`);
console.log(`SHA-256: ${checksum}`);
