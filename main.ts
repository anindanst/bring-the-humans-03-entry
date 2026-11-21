// bring-the-humans-03 entry (Node 22, standard library only).
//
// All this program does is hand VIDEO.json to the grader: it copies
// VIDEO.json from the repository root to /output/VIDEO.json, where the
// gate reads it. The entry itself is the video: an original 17-second
// vertical ad for make.fun, made programmatically in this session
// (see gen_video.py), posted publicly on TikTok from a public account
// with the bounty's line and the play code in its caption. The house
// reads the video's views from TikTok; nothing this program writes
// about the video is scored.
//
// The ad shows make.fun's brand badge (mascot mark + make.fun wordmark)
// from its very first frame and ends on make.fun's referral end card
// with the entrant's own referral code in its field. Both come from
// make.fun's press pack (https://make.fun/press/manifest.json,
// guide at https://make.fun/press/llms.txt) and are used as they are;
// this repository holds no copy of any press file.
//
// VIDEO.json still holds the placeholder address, so the gate refuses
// this commit as it stands (valid 0). Replace it with the posted
// video's full address before submitting.
//
// Run it the way the grader does:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const source = join(botDir, 'VIDEO.json');
const target = join(outDir, 'VIDEO.json');

let raw;
try {
  raw = readFileSync(source, 'utf8');
} catch (err) {
  console.error(`VIDEO.json could not be read from ${source}: ${(err as Error).message}`);
  process.exit(1);
}

let parsed;
try {
  parsed = JSON.parse(raw);
} catch (err) {
  console.error(`VIDEO.json is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}
if (typeof parsed !== 'object' || parsed === null || typeof parsed.url !== 'string') {
  console.error('VIDEO.json must be an object with a string "url" field.');
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
try {
  copyFileSync(source, target);
} catch (err) {
  console.error(`VIDEO.json could not be copied to ${target}: ${(err as Error).message}`);
  process.exit(1);
}

// Confirm the copy landed byte for byte: the gate reads /output/VIDEO.json,
// so a partial or stale copy must fail loudly here, not silently.
const copied = readFileSync(target, 'utf8');
if (copied !== raw) {
  console.error('VIDEO.json in /output does not match the repository copy.');
  process.exit(1);
}
