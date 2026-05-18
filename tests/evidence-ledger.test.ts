import { beforeAll, describe, expect, it } from "bun:test";
import {
	countEvidence,
	initEvidenceDir,
	readEvidence,
	writeEvidence,
} from "../packages/core/evidence-ledger.ts";
import { generateId } from "../packages/core/id.ts";
import type { EvidenceRecord } from "../packages/core/types.ts";

function makeEvidence(success = true): EvidenceRecord {
	return {
		id: generateId("evi"),
		timestamp: new Date().toISOString(),
		action: "test.action",
		actor: "test-runner",
		input: "test input",
		output: success ? "test output" : "",
		category: "safe_api",
		trustLevel: "medium",
		durationMs: 42,
		success,
	};
}

describe("Evidence Ledger", () => {
	beforeAll(() => {
		initEvidenceDir();
	});

	it("writes and reads evidence records", async () => {
		const record = makeEvidence();
		await writeEvidence(record);
		const records = await readEvidence(1);
		expect(records.length).toBeGreaterThanOrEqual(1);
		expect(records[0].action).toBe("test.action");
	});

	it("counts evidence records", async () => {
		const before = await countEvidence();
		await writeEvidence(makeEvidence());
		const after = await countEvidence();
		expect(after).toBeGreaterThan(before);
	});

	it("writes failed evidence records", async () => {
		const record = makeEvidence(false);
		await writeEvidence(record);
		const records = await readEvidence(1);
		expect(records[0].success).toBe(false);
	});

	it("evidence records have required fields", async () => {
		const record = makeEvidence();
		await writeEvidence(record);
		const records = await readEvidence(1);
		const r = records[0];
		expect(r.id).toMatch(/^evi_/);
		expect(r.timestamp).toBeTruthy();
		expect(r.action).toBeTruthy();
		expect(r.actor).toBeTruthy();
		expect(typeof r.durationMs).toBe("number");
		expect(typeof r.success).toBe("boolean");
	});
});
