import { randomUUID } from "node:crypto";

export function generateId(prefix: string): string {
	const short = randomUUID().slice(0, 8);
	return `${prefix}_${short}`;
}
