# Canonical JSON — authoritative definition for hashing/signing (Go + TS)

Last updated: Thursday, April 30, 2026 (PDT)

This repository uses a single canonicalJSON definition for any place we compute digests (e.g., sha256 inputs for ArtifactID, SpecDigest, ReceiptKey, contentDigests, and entryDigest).

canonicalJSON(x) MUST implement the same deterministic encoding across Go and TypeScript.

Operational note (TUI/CLI-only): all verification/tests for this canonicalization MUST be runnable via CLI (node/go test), not GUI.

---

## 1) Scope

Inputs to canonicalJSON are restricted to JSON-compatible values:
- objects (string keys)
- arrays
- strings
- numbers
- booleans
- null

All values MUST be representable without custom classes.

Bigint note (for serialization compatibility):
- For any bigint/integer field value used in hashing/signing inputs, canonicalJSON MUST encode it as a JSON string containing its base-10 decimal representation (not a JSON number).
- The decimal representation MUST be canonical:
  - no leading plus sign
  - no exponent (no "e" notation)
  - no leading zeros (except the value "0" itself)
  - a negative value MUST use a leading "-" sign.

---

## 2) Canonicalization algorithm (deterministic)

Implementations MUST follow these rules:

### 2.1 Objects
- Serialize as JSON object with:
  - keys in strictly increasing lexicographic order according to RFC 8785 (JCS) object key ordering.
    This is based on Unicode character order (JCS-compatible comparison of key strings), not raw UTF-8 byte order.
  - no extra fields.
- No re-ordering beyond this key sort.

### 2.2 Arrays
- Serialize in the original array order.

### 2.3 Strings
- Serialize strings using JSON string escaping with:
  - backslash (\\), quote (\"), and control characters escaped per JSON rules.
  - the exact escape sequences must be canonical (i.e., choose one deterministic escaping form).

### 2.4 Numbers
Numbers MUST be encoded deterministically and consistently:
- Input numeric values MUST be finite.
- Use the JSON number grammar with a canonical representation.
- Do not emit trailing zeros in a decimal representation.
- Do not emit unnecessary exponent formatting.
- Equivalent numeric values must produce identical canonical string encodings.

If you choose an existing implementation (recommended):
- Use a JSON Canonicalization Scheme (JCS)-compatible encoder (RFC 8785 semantics) or an equivalent algorithm that satisfies the above determinism requirements.

---

## 3) Hashing input contract

Any digest MUST be computed as:
- digest = sha256( canonicalJSON(value) )
- digest representation MUST be lowercase hex.

If a digest definition says to “exclude field F”, then the excluded field MUST be removed from the object prior to canonicalJSON.

---

## 4) CLI verification requirement

Repository MUST provide CLI test vectors to confirm Go and TS canonicalJSON are identical for:
- nested objects with differently-ordered keys
- arrays
- edge-case numbers used by cost/risk fields
- strings with escape sequences
- bigint-as-decimal-string fields

(Implementers should add/extend a test file such as scripts/canonicalJsonTestVectors.ts and/or equivalent Go tests.)
