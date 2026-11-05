import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";

const input = JSON.parse(readFileSync(process.argv[2], "utf8"));
if (input.isError) throw new Error("MCP response failed");
const batch = JSON.parse(input.content.find(block => block.type === "text").text);
const output = resolve("state/rednote-private/image-audit");
mkdirSync(output, { recursive: true });
for (const note of batch.notes) {
  if (!/^[a-zA-Z0-9]{20,40}$/.test(note.noteId)) throw new Error("Invalid note ID");
  const paths = [];
  for (const [index, image] of note.images.slice(0, 3).entries()) {
    const path = `${output}/${note.noteId}-${index + 1}.jpg`;
    writeFileSync(path, Buffer.from(image.base64, "base64"), { mode: 0o600 });
    paths.push(path);
  }
  console.log(JSON.stringify({ note_id: note.noteId, paths }));
}
