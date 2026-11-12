import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const source = join(dirname(fileURLToPath(import.meta.url)), "entry.png");
const destinationDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const destination = join(destinationDir, "entry.png");
const image = await readFile(source);

function reject(reason: string): never {
  throw new Error(`Invalid image: ${reason}`);
}

if (image.length === 0) reject("the file is empty");
if (image.length > 1_048_576) reject("the file exceeds 1 MiB");
if (image[0] !== 0xff || image[1] !== 0xd8 || image[2] !== 0xff) {
  reject("the file does not begin with a JPEG signature");
}

let width = 0;
let height = 0;
let position = 2;
while (position < image.length) {
  if (image[position] !== 0xff) reject("a JPEG marker is missing");
  while (image[position] === 0xff) position++;
  const marker = image[position++];
  if (marker === undefined || marker === 0x00) reject("a JPEG marker is malformed");
  if (marker === 0xd9 || marker === 0xda) break;
  if (marker === 0xd8 || (marker >= 0xd0 && marker <= 0xd7) || marker === 0x01) continue;
  if (position + 2 > image.length) reject("a JPEG segment is truncated");
  const segmentLength = image.readUInt16BE(position);
  if (segmentLength < 2 || position + segmentLength > image.length) {
    reject("a JPEG segment has an invalid length");
  }
  if (marker === 0xc0 || marker === 0xc1 || marker === 0xc2) {
    if (segmentLength < 7) reject("the JPEG frame header is truncated");
    height = image.readUInt16BE(position + 3);
    width = image.readUInt16BE(position + 5);
    break;
  }
  position += segmentLength;
}

if (width === 0 || height === 0) reject("no supported JPEG frame was found");
if (width > 1024 || height > 1024) reject("image dimensions exceed 1024 pixels");
if (image[image.length - 2] !== 0xff || image[image.length - 1] !== 0xd9) {
  reject("the JPEG end marker is missing");
}

await mkdir(destinationDir, { recursive: true });
await copyFile(source, destination);
const digest = createHash("sha256").update(image).digest("hex");
console.log(`Wrote ${destination} (${image.length} bytes, ${width}x${height}, sha256 ${digest})`);
