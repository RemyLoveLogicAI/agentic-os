# v4 Universal Initializer — Zero-Trust Lazy JIT stack — Interface & Schema Spec

Last updated: Thursday, April 30, 2026 (PDT)

This document formalizes the technical interfaces and schemas for the v4 Universal Initializer Zero-Trust Lazy JIT stack.

All implementation notes below assume TUI/CLI-only execution (e.g., node/tsc/cmd entrypoints). No GUI paths.

---

## 0) Canonical JSON and digest rules (authoritative)

Any digest defined in this document MUST be computed using canonicalJSON as specified in:
- research/docs/canonical-json-spec.md

Digest representation MUST be lowercase hex.

If a definition states to exclude a field (e.g., “exclude contentDigest from the hash input”), then that field MUST be removed before applying canonicalJSON.

---

## 1) ReceiptKey hashing

ReceiptKey is a deterministic identifier for a receipt that binds:
- which operation was authorized/invoked
- which inputs/capability context were used
- which risk/cost budget constraints applied

### ReceiptKey input fields

Reference TypeScript conceptual model:

```ts
export type ReceiptDomain = "allora" | "initializer" | "runtime" | string;

export interface ReceiptKeyPreimage {
  schemaVersion: "v4.receiptKey.preimage.v1";

  // Identity
  domain: ReceiptDomain;
  operation: string; // e.g. "lazyJit.compile" | "lazyJit.execute" | ...

  // Binding context
  specId?: string;
  specDigest?: string; // sha256 hex of canonical spec
  capabilityIds: string[]; // normalized/sorted unique list

  // Input binding (opaque digest)
  inputDigest: string; // sha256 hex of canonical JSON inputs

  // Risk binding (opaque digest to avoid leaking budget state)
  riskPolicyDigest: string; // sha256 hex

  // Replay resistance
  nonce: string; // caller-generated random/unique string

  // Optional
  issuedAtUnixMilli?: number;
}
```

### Hashing algorithm

ReceiptKey = sha256( canonicalJSON(ReceiptKeyPreimage) )

Rules:
- capabilityIds MUST be normalized (unique, sorted lexicographically) before hashing.
- Represent output as lowercase hex.

---

## 2) ReceiptLedger schema with CAS

ReceiptLedger is a log of receipts stored with content-addressable semantics (CAS) plus compare-and-swap (CAS) control to prevent:
- replay
- out-of-order overwrites
- ledger fork inconsistencies

### Ledger storage model

Receipt object is stored by CAS content hash; ledger entries reference it.

Reference TypeScript interfaces:

```ts
export interface Receipt {
  schemaVersion: "v4.receipt.v1";

  receiptKey: string; // ReceiptKey hex

  authorization: {
    operation: string;
    capabilityIds: string[];
    issuedBy: string; // identity of initializer/validator
  };

  // Cost/risk accounting evidence
  risk: {
    riskTokenId?: string;

    // Fixed-point cost units (integers).
    // See RiskToken budget semantics below.
    costChargedUnits: bigint;
    budgetRemainingAfterUnits: bigint;
  };

  inputDigest: string;

  // Optional outputs / proof / evidence
  result?: {
    status: "pass" | "fail" | "partial";
    evidence?: Record<string, unknown>;
  };

  // CAS content reference
  // Circularity resolution:
  // contentDigest MUST be computed without the contentDigest field itself.
  contentDigest: string; // sha256 hex of canonicalJSON(Receipt WITHOUT contentDigest)
}

export interface ReceiptLedgerEntry {
  schemaVersion: "v4.receiptLedgerEntry.v1";

  receiptKey: string; // primary lookup

  receiptContentDigest: string; // must match receipt.contentDigest
  previousEntryDigest?: string; // hash link for tamper-evidence

  ledgerIndex: number; // monotonically increasing

  cas: {
    expectedPreviousReceiptContentDigest?: string;
    expectedLedgerIndex?: number;
  };
}

export interface ReceiptLedgerState {
  schemaVersion: "v4.receiptLedgerState.v1";

  ledgerId: string; // sha256 of ledger configuration preimage

  checkpointDigest?: string;

  receipts: {
    byReceiptKey: Record<string, string>; // receiptKey -> entryDigest
    casStore: Record<string, Receipt>; // receipt content-addressed by receipt.contentDigest
  };
}
```

### Entry digest

entryDigest MUST be sha256(canonicalJSON(ReceiptLedgerEntry without any computed digest field)).

### CAS write procedure (conceptual)

To append/write a receipt:
1) Compute receiptKey.
2) Compute receipt.contentDigest using canonicalJSON(Receipt with contentDigest removed).
3) Create ReceiptLedgerEntry candidate:
   - previousEntryDigest = current latest entryDigest (if any)
   - cas.expectedPreviousReceiptContentDigest = current latest receipt.contentDigest (if any)
   - cas.expectedLedgerIndex = current ledgerIndex
4) Atomically verify CAS preconditions.
5) If CAS passes, commit:
   - store receipt in casStore keyed by receiptContentDigest
   - update byReceiptKey[receiptKey] = entryDigest
   - update ledgerIndex and checkpointDigest as defined

Failure modes:
- if CAS fails, do not mutate state; return conflict error.

TUI/CLI-only notes:
- Provide ledger consistency checks as CLI commands.
  e.g., node ./scripts/ledgerVerify.ts --ledgerId <id>

---

## 3) RiskToken budget gating (numeric semantics clarified)

RiskToken enforces budget constraints for zero-trust authorization. It prevents spending beyond allowed budgets and supports lazy JIT.

### Fixed-point cost semantics

All cost and budget fields are integers representing fixed-point “cost units”.

RiskToken defines:
- costDecimals: number (>= 0)

Interpretation:
- realCost = costUnits / 10^costDecimals

---

### RiskToken schema

```ts
export interface RiskToken {
  schemaVersion: "v4.riskToken.v1";

  riskTokenId: string;

  // Fixed-point definition for all budget arithmetic in this token.
  costDecimals: number;

  budget: {
    // Maximum total cost allowed (fixed-point integer units)
    maxCostUnits: bigint;

    // Optional hard ceiling for specific cost classes.
    perClassMaxCostUnits?: Record<string, bigint>;
  };

  // Monotonic consumption evidence
  consumption: {
    consumedCostUnits: bigint; // must be <= maxCostUnits
  };

  // Replay resistance
  nonce: string;
  issuedAtUnixMilli: number;
  expiresAtUnixMilli?: number;

  issuer: {
    id: string;
    keyId?: string;
    signatureBytes?: string; // base64url over canonicalRiskTokenPreimage
  };

  costClasses?: {
    [operation: string]: string;
  };
}
```

### Budget gating algorithm

```ts
export interface BudgetGateInput {
  token: RiskToken;
  costToChargeUnits: bigint; // MUST be non-negative
  costClass?: string;
  currentUnixMilli: number;
}

export interface BudgetGateOutput {
  allowed: boolean;
  updatedToken?: {
    consumption: { consumedCostUnits: bigint };
  };
  reason?: {
    code:
      | "expired"
      | "insufficientBudget"
      | "invalidToken"
      | "negativeCost"
      | "unknownCostClass";
    message: string;
  };
}

export function gateBudget(input: BudgetGateInput): BudgetGateOutput;
```

Constraints:
- If expiresAtUnixMilli present and currentUnixMilli > expiresAtUnixMilli => denied.
- If costToChargeUnits < 0 => denied.
- If per-class policy is used and costClass unknown => denied.
- If cost exceeds remaining budget (in units) => denied.
- updatedToken.consumption.consumedCostUnits = token.consumption.consumedCostUnits + costToChargeUnits.

Operational note (TUI/CLI-only):
- Add CLI tests for boundary conditions (exactly maxCostUnits, just over, expired token).

---

## 4) CapabilityVector negotiation interfaces

CapabilityVector negotiation ensures the initializer only activates capabilities that both sides support and that are allowed under risk gating.

### CapabilityVector types

```ts
export type CapabilityVersion = string;

export interface CapabilityEntry {
  capabilityId: string;
  version: CapabilityVersion;

  flags?: {
    lazyJit?: boolean;
    deterministic?: boolean;
    streaming?: boolean;
    tools?: boolean;
    [k: string]: boolean | undefined;
  };
}

export interface CapabilityVector {
  schemaVersion: "v4.capabilityVector.v1";
  capabilities: CapabilityEntry[];
}
```

### Negotiation handshake

```ts
export interface CapabilityNegotiationRequest {
  schemaVersion: "v4.capabilityNegotiationRequest.v1";
  negotiationId: string;

  clientVector: CapabilityVector;

  risk: {
    riskTokenId?: string;
    riskPolicyDigest?: string;
  };

  lazyJit: {
    enabled: boolean;
    maxLazyJitOps?: number;
  };
}

export interface CapabilityNegotiationResponse {
  schemaVersion: "v4.capabilityNegotiationResponse.v1";
  negotiationId: string;

  activatedCapabilities: CapabilityEntry[];

  rejectedCapabilities?: Array<{
    capabilityId: string;
    reason: string;
  }>;

  receiptPolicy: {
    receiptDomain: string;
    requireReceiptLedgerCAS: boolean;
  };
}
```

TUI/CLI-only notes:
- Provide deterministic negotiation tests via CLI.
  e.g., node ./scripts/capabilityNegotiationVectors.ts

---

## Summary of interface fixes in this revision

- Receipt.contentDigest computed without the contentDigest field itself.
- canonicalJSON rules factored into a single authoritative file.
- Risk/cost/budget numeric semantics clarified as fixed-point integer units.

No GUI paths; all tests and verification MUST be runnable via CLI.
