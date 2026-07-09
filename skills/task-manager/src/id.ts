/**
 * Lightweight ID generator for tasks.
 * Produces IDs like `tsk_1a2b3c4d`.
 */

const ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz";

function randomSegment(length: number): string {
  let result = "";
  for (let i = 0; i < length; i++) {
    result += ALPHABET[Math.floor(Math.random() * ALPHABET.length)];
  }
  return result;
}

export function generateTaskId(): string {
  return `tsk_${randomSegment(8)}`;
}
