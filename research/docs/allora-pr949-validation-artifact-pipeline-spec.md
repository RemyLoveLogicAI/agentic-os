# Allora PR #949 — Validation Artifact pipeline (Go) — Interface & Schema Spec

Last updated: Thursday, April 30, 2026 (PDT)

This document formalizes the technical interfaces and schemas for the Allora PR #949 Validation Artifact pipeline.

All implementation notes below assume TUI/CLI-only execution (e.g., go test/go run/cmd entrypoints). No GUI paths.

---

## 1) ValidationArtifact struct (Go)

All structures MUST be serializable to canonical JSON bytes (UTF-8, stable key ordering) before hashing/signing.

Canonical JSON rule (for any hash/sign):
- Use deterministic key ordering.
- No insignificant whitespace.
- Ensure numbers are encoded consistently.

### ValidationArtifact

Go type (reference):

```go
// ValidationArtifact is the persisted, verifiable record of a spec validation run.
// It is designed to carry both "direct" validation results and metamorphic evidence.
//
// Serialized form MUST be canonical JSON for artifactId computation.
//
// NOTE: Field names are part of the public schema.
type ValidationArtifact struct {
  SchemaVersion string `json:"schemaVersion"` // e.g. "allora.validationArtifact.v1"

  ArtifactID string `json:"artifactId"` // hash(canonicalJSON(ValidationArtifactWithoutArtifactID))

  SpecID string `json:"specId"` // stable identifier for the validated Spec
  SpecDigest string `json:"specDigest"` // sha256(canonicalJSON(spec))

  RunID string `json:"runId"` // caller-generated UUID/ULID for traceability
  ValidatorID string `json:"validatorId"` // logical validator identity
  ValidatorVersion string `json:"validatorVersion"`

  // Inputs and outputs are intentionally opaque to the pipeline.
  // They MUST be JSON values.
  Inputs  map[string]any `json:"inputs"`
  Outputs map[string]any `json:"outputs"`

  // Metamorphic evidence provides "why" the outputs are robust.
  Metamorphic []MetamorphicEvidence `json:"metamorphic"`

  // Direct validation evidence (non-metamorphic checks).
  DirectValidation []DirectValidationEvidence `json:"directValidation"`

  // Integrity and provenance
  ProducedAtUnixMilli int64 `json:"producedAtUnixMilli"` // UNIX time in milliseconds

  // Optional signing metadata.
  // If absent, ArtifactID still provides integrity within the validation pipeline.
  Signature *Signature `json:"signature,omitempty"`

  // Optional error block to preserve partial runs.
  Error *PipelineError `json:"error,omitempty"`
}

type Signature struct {
  Alg string `json:"alg"` // e.g. "ed25519" or "rsa-pss"
  KeyID string `json:"keyId"`
  SignatureBytes string `json:"signatureBytes"` // base64url
}

type PipelineError struct {
  Code string `json:"code"` // stable error code
  Message string `json:"message"`
}

// --- Direct validation evidence ---
type DirectValidationEvidence struct {
  CheckID string `json:"checkId"` // stable ID from the Spec
  Status string `json:"status"` // e.g. "pass" | "fail" | "skipped"
  Details map[string]any `json:"details"`
}

// --- Metamorphic evidence ---
type MetamorphicEvidence struct {
  RelationID string `json:"relationId"` // stable ID from the Spec metamorphic properties
  TransformApplied map[string]any `json:"transformApplied"` // declarative record of the transformation
  Invariants []InvariantEvidence `json:"invariants"`
}

type InvariantEvidence struct {
  InvariantID string `json:"invariantId"`
  Status string `json:"status"` // pass/fail
  // Provide machine-checkable diagnostics.
  Proof map[string]any `json:"proof"`
  // Optional free-form human message.
  Message string `json:"message,omitempty"`
}
```

### ArtifactID

ArtifactID MUST be computed as:
- artifactId = sha256( canonicalJSON(ValidationArtifact with artifactId removed) )
- Represent as lowercase hex.

---

## 2) Spec object schema

A Spec is a declarative description of:
- what inputs are allowed
- what direct checks apply
- what metamorphic relations must hold

### Spec (Go / JSON conceptual schema)

```go
// Spec is an immutable, addressable validation definition.
//
// SpecID MUST be derived from the canonical JSON of the Spec payload.
type Spec struct {
  SchemaVersion string `json:"schemaVersion"` // e.g. "allora.spec.v1"

  SpecID string `json:"specId"` // hash(canonicalJSON(specPayloadWithoutSpecID))
  Name string `json:"name"`
  Description string `json:"description,omitempty"`

  // Input/Output constraints. JSON schema is intentionally strict.
  InputSchema  map[string]any `json:"inputSchema"`
  OutputSchema map[string]any `json:"outputSchema"`

  // Direct checks
  DirectChecks []DirectCheck `json:"directChecks"`

  // Metamorphic properties
  MetamorphicProperties []MetamorphicProperty `json:"metamorphicProperties"`

  // Implementation hints (non-binding):
  // - allowed transform functions
  // - expected execution mode (TUI/CLI)
  ExecutionHints ExecutionHints `json:"executionHints"`
}

type ExecutionHints struct {
  Mode string `json:"mode"` // "tui" (required)
  // If present, validators MAY use these to choose tooling.
  GoTestPattern string `json:"goTestPattern,omitempty"`
}

type DirectCheck struct {
  CheckID string `json:"checkId"` // referenced by ValidationArtifact.directValidation
  Kind string `json:"kind"` // e.g. "json-schema" | "expression" | "custom"
  Params map[string]any `json:"params"`
}

// --- Metamorphic properties ---
type MetamorphicProperty struct {
  RelationID string `json:"relationId"`
  Description string `json:"description,omitempty"`

  // Preconditions: input constraints that must be met before transformation.
  Preconditions map[string]any `json:"preconditions,omitempty"`

  // Transform contract: how the input is transformed for the metamorphic run.
  Transform TransformContract `json:"transform"`

  // Invariants: what must remain true between original and transformed outputs.
  Invariants []InvariantSpec `json:"invariants"`
}

type TransformContract struct {
  Kind string `json:"kind"` // e.g. "shuffle" | "scale" | "noop" | "custom"
  // Declarative parameters for a deterministic transform implementation.
  Params map[string]any `json:"params"`
}

type InvariantSpec struct {
  InvariantID string `json:"invariantId"`
  // Invariant evaluation strategy.
  // Examples: exactMatch, setEquivalence, approxNumeric, monotonicity
  Strategy string `json:"strategy"`

  // Machine-checkable invariant definition.
  // MUST reference paths in input/output JSON values.
  Definition map[string]any `json:"definition"`

  // Optional tolerance when relevant.
  Tolerance *ToleranceSpec `json:"tolerance,omitempty"`
}

type ToleranceSpec struct {
  Metric string `json:"metric"` // e.g. "abs" | "rel"
  Value float64 `json:"value"`
}
```

---

## 3) Metamorphic test properties

Metamorphic test properties are formalized as the Spec.MetamorphicProperties entries.

### Required invariants model

For each MetamorphicProperty:
- RelationID uniquely identifies a metamorphic relation.
- Transform defines a deterministic function f(input)->input' (or may be an empty/no-op transform).
- Invariants define predicates over outputs o = g(input) and o' = g(input') such that invariant predicate holds.

### Invariant evaluation contract

Each invariant MUST provide:
- strategy: how to compare output aspects
- definition: JSON path-based or expression-based definition of invariance
- proof: validator must emit a proof object in ValidationArtifact.MetamorphicEvidence.invariants[].proof

Proof object requirements (minimum):
- proof MUST include at least: { "checked": true|false, "evidence": ... }
- for failures, proof MUST include a diagnostic payload sufficient to reproduce/triage.

### TUI/CLI-only execution notes

Reference execution commands:
- go test ./...
- go test ./... -run <pattern>
- go run ./cmd/<validator>

No GUI paths or interactive GUI tooling.
