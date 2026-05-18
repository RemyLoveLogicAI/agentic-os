import { existsSync, mkdirSync } from "node:fs";
import { appendFile, readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { config } from "./config.ts";
import { createLogger } from "./logger.ts";
import type { EvidenceRecord } from "./types.ts";

const log = createLogger("evidence-ledger");

function currentLedgerFile(): string {
	const date = new Date().toISOString().slice(0, 10);
	return join(config.evidence.dir, `evidence-${date}.jsonl`);
}

export function initEvidenceDir(): void {
	if (!existsSync(config.evidence.dir)) {
		mkdirSync(config.evidence.dir, { recursive: true });
		log.info(`Created evidence directory: ${config.evidence.dir}`);
	}
}

export async function writeEvidence(record: EvidenceRecord): Promise<void> {
	initEvidenceDir();
	const line = `${JSON.stringify(record)}\n`;
	await appendFile(currentLedgerFile(), line, "utf-8");
	log.info(`Evidence recorded: ${record.id} — ${record.action}`);
}

export async function readEvidence(limit = 50): Promise<EvidenceRecord[]> {
	initEvidenceDir();

	const files = await readdir(config.evidence.dir);
	const ledgerFiles = files
		.filter((f) => f.startsWith("evidence-") && f.endsWith(".jsonl"))
		.sort()
		.reverse();

	const records: EvidenceRecord[] = [];

	for (const file of ledgerFiles) {
		if (records.length >= limit) break;
		const content = await readFile(join(config.evidence.dir, file), "utf-8");
		const lines = content.trim().split("\n").filter(Boolean);
		for (const line of lines.reverse()) {
			if (records.length >= limit) break;
			records.push(JSON.parse(line) as EvidenceRecord);
		}
	}

	return records;
}

export async function countEvidence(): Promise<number> {
	initEvidenceDir();
	const files = await readdir(config.evidence.dir);
	let count = 0;
	for (const file of files) {
		if (!file.endsWith(".jsonl")) continue;
		const content = await readFile(join(config.evidence.dir, file), "utf-8");
		count += content.trim().split("\n").filter(Boolean).length;
	}
	return count;
}
