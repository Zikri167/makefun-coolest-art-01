import { copyFile, mkdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
// Default to the competition mount unless a local output folder is supplied.
const outputDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
// Resolve the source beside this script so it works from any working directory.
const source = join(here, "entry.png");
// Validate the generated asset before copying it into the competition output.
const png = await readFile(source);
// Reject an empty source before attempting to inspect its PNG header.
if (png.length === 0) {
  throw new Error(`Expected entry.png to be non-empty; observed 0 bytes at ${source}`);
}
const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
if (!png.subarray(0, 8).equals(signature)) {
  throw new Error(`Expected a PNG signature in entry.png at ${source}; observed an invalid signature`);
}
if (png.readUInt32BE(16) !== 1024 || png.readUInt32BE(20) !== 1024) {
  const width = png.readUInt32BE(16);
  const height = png.readUInt32BE(20);
  throw new Error(`Expected entry.png dimensions 1024×1024 pixels; observed ${width}×${height}`);
}
if (png.length > 1048576) {
  throw new Error(`Expected entry.png size at most 1048576 bytes; observed ${png.length} bytes`);
}
// Keep all checks ahead of directory creation so invalid art fails cleanly.
await mkdir(outputDir, { recursive: true });
// Copy from the same resolved path that was read and validated above.
await copyFile(source, join(outputDir, "entry.png"));
