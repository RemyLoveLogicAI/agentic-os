# v4 Universal Initializer — Zero-Trust Lazy JIT stack — Interface & Schema Spec

Last updated: Thursday, April 30, 2026 (PDT)

This document formalizes the technical interfaces and schemas for the v4 Universal Initializer Zero-Trust Lazy JIT stack.

All implementation notes below assume TUI/CLI-only execution (e.g., node/tsc/cmd entrypoints). No GUI paths.

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
- canonicalJSON MUST use stable key ordering and no insignificant whitespace.
- capabilityIds MUST be normalized (unique, sorted lexicographically) before hashing.
- Represent output as lowercase hex.

### Normalization helpers (TUI/CLI reference)

When implementing hashing in code, ensure canonicalization is performed in code paths only (no GUI), and provide CLI test vectors:
- node ./scripts/receiptKeyTestVectors.ts

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
  // What was actually authorized and what happened
  authorization: {
    operation: string;
    capabilityIds: string[];
    issuedBy: string; // identity of initializer/validator
  };

  // Cost/risk accounting evidence
  risk: {
    riskTokenId?: string;
    costCharged: number; // numeric cost
    budgetRemainingAfter: number;
  };

  // Bindings
  inputDigest: string;

  // Optional outputs / proof / evidence
  result?: {
    status: "pass" | "fail" | "partial";
    evidence?: Record<string, unknown>;
  };

  // CAS content reference
  contentDigest: string; // sha256 hex of canonicalJSON(receipt)
}

// CAS record stored in the ledger.
export interface ReceiptLedgerEntry {
  schemaVersion: "v4.receiptLedgerEntry.v1";

  receiptKey: string; // primary lookup

  // CAS pointers
  receiptContentDigest: string; // must match receipt.contentDigest
  previousEntryDigest?: string; // hash link for tamper-evidence

  // Ledger versioning
  ledgerIndex: number; // monotonically increasing

  // CAS metadata
  cas: {
    // The ledger CAS condition key/value.
    // Implementations MUST verify before committing.
    expectedPreviousReceiptContentDigest?: string;
    expectedLedgerIndex?: number;
  };
}

export interface ReceiptLedgerState {
  schemaVersion: "v4.receiptLedgerState.v1";
  ledgerId: string; // sha256 of ledger configuration preimage

  // Optional digest of entire ledger state for checkpoints.
  checkpointDigest?: string;

  // Index namespace separation.
  receipts: {
    // key -> latest entry digest
    byReceiptKey: Record<string, string>; // receiptKey -> entryDigest
    // content digest -> receipt
    casStore: Record<string, Receipt>; // receipt content-addressed
  };
}
```

### Entry digest

entryDigest MUST be sha256(canonicalJSON(ReceiptLedgerEntry without any computed digest field)).

### CAS write procedure (conceptual)

To append/write a receipt:
1) Compute receiptKey and receiptContentDigest.
2) Create ReceiptLedgerEntry candidate with:
   - previousEntryDigest = current latest digest (if any)
   - cas.expectedPreviousReceiptContentDigest = current latest digest (if any)
   - cas.expectedLedgerIndex = current ledgerIndex (if any)
3) Atomically verify CAS preconditions.
4) If CAS passes, commit:
   - store receipt in casStore keyed by receiptContentDigest
   - update byReceiptKey receiptKey -> entryDigest
   - update ledgerIndex and checkpointDigest as defined

Failure modes:
- if CAS fails, do not mutate state; return conflict error.

TUI/CLI-only notes:
- Provide ledger consistency checks as CLI commands.
  e.g., node ./scripts/ledgerVerify.ts --ledgerId <id>

---

## 3) RiskToken budget gating

RiskToken enforces budget constraints for zero-trust authorization. It prevents spending beyond allowed budgets and supports lazy JIT.

### RiskToken schema

```ts
export interface RiskToken {
  schemaVersion: "v4.riskToken.v1";

  riskTokenId: string; // unique identifier

  // Budget policy
  budget: {
    // Maximum total cost allowed for this token.
    maxCost: number;

    // Optional hard ceiling for specific cost classes.
    // If omitted, all costs share one bucket.
    perClassMaxCost?: Record<string, number>;
  };

  // Current consumption evidence (monotonic)
  consumption: {
    consumedCost: number; // must be <= maxCost
  };

  // Replay resistance
  nonce: string;
  issuedAtUnixMilli: number;
  expiresAtUnixMilli?: number;

  // Integrity/provenance
  issuer: {
    id: string;
    keyId?: string;
    signatureBytes?: string; // base64url over canonicalRiskTokenPreimage
  };

  // Optional cost classifier mapping hints
  costClasses?: {
    // e.g. "jit.compile" -> "compile".
    [operation: string]: string;
  };
}
```

### Budget gating algorithm

Provide a pure function gateBudget(token, cost, class?) => {allowed, updatedToken}.

Reference interface:

```ts
export interface BudgetGateInput {
  token: RiskToken;
  costToCharge: number; // non-negative
  costClass?: string; // if perClassMaxCost used
  currentUnixMilli: number;
}

export interface BudgetGateOutput {
  allowed: boolean;
  // If allowed, consumption MUST update monotonically.
  updatedConsumption?: { consumedCost: number };
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
- If costToCharge < 0 => denied.
- If cost exceeds remaining budget => denied.
- updatedConsumption.consumedCost = token.consumption.consumedCost + costToCharge.

Operational note (TUI/CLI-only):
- Add CLI tests for boundary conditions:
  - exactly maxCost
  - just over maxCost
  - expired token

---

## 4) CapabilityVector negotiation interfaces

CapabilityVector negotiation ensures the initializer only activates capabilities that both sides support and that are allowed under risk gating.

### CapabilityVector types

```ts
export type CapabilityVersion = string;

export interface CapabilityEntry {
  capabilityId: string; // stable identifier
  version: CapabilityVersion;
  // Flags describe behavior contracts; missing flags default to false.
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
  // normalized unique capabilityId set
  capabilities: CapabilityEntry[];
}
```

### Negotiation handshake

Two sides:
- Client/Initializer-producer: Universal Initializer
- Server/Runtime-acceptor: capability runtime

Reference interfaces:

```ts
export interface CapabilityNegotiationRequest {
  schemaVersion: "v4.capabilityNegotiationRequest.v1";
  negotiationId: string; // UUID/ULID

  // Capabilities offered by the client.
  clientVector: CapabilityVector;

  // Trust and risk binding.
  risk: {
    riskTokenId?: string;
    // If riskTokenId omitted, runtime may require token fetch.
    riskPolicyDigest?: string;
  };

  // Lazy JIT mode selection.
  lazyJit: {
    enabled: boolean;
    // Maximum number of JIT compilations allowed for this negotiation scope.
    maxLazyJitOps?: number;
  };
}

export interface CapabilityNegotiationResponse {
  schemaVersion: "v4.capabilityNegotiationResponse.v1";
  negotiationId: string;

  // Capabilities that runtime agrees to activate.
  activatedCapabilities: CapabilityEntry[];

  // Capabilities rejected with reasons.
  rejectedCapabilities?: Array<{
    capabilityId: string;
    reason: string; // stable reason code
  }>;

  // Contract about JIT receipts.
  receiptPolicy: {
    receiptDomain: string;
    // e.g., whether to require ReceiptLedger CAS writes for each op.
    requireReceiptLedgerCAS: boolean;
  };
}
```

### Negotiation algorithm (conceptual)

1) Compute common capability set by capabilityId.
2) For each common capabilityId:
   - select the highest mutually compatible version (or declared preferred)
   - intersect flags (runtime flags constrain client flags)
3) Apply lazy JIT constraints:
   - if lazyJit.enabled=false => activated capabilities must not require lazy JIT receipts
4) Apply risk constraints:
   - only allow activation that can be covered by budget gate for anticipated costs

TUI/CLI-only notes:
- Provide deterministic negotiation tests:
  node ./scripts/capabilityNegotiationVectors.ts

---

## Summary of interfaces to implement

- ReceiptKey hashing from ReceiptKeyPreimage via canonical JSON + sha256.
- ReceiptLedgerEntry schema with explicit CAS expectations.
- RiskToken gating contract gateBudget(token, cost, class?).
- CapabilityVector negotiation request/response and activated/rejected sets.

No GUI paths; all tests and verification MUST be runnable via CLI.
