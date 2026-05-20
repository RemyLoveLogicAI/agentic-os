// CAR Kernel — Command, Action, Result contracts
// Event-sourced world state | Metropolis Replica

export type AgentId = string;
export type TickId = number;
export type EventId = string;

// ─── Commands ────────────────────────────────────────────────────────────────

export type CommandType =
  | 'AGENT_REGISTER'
  | 'AGENT_DEREGISTER'
  | 'TOOL_INVOKE'
  | 'TICK_ADVANCE'
  | 'WORLD_RESET';

export interface Command<T extends CommandType = CommandType, P = unknown> {
  type: T;
  payload: P;
  issuedAt: string; // ISO-8601
  issuedBy: AgentId;
}

export interface AgentRegisterPayload {
  agentId: AgentId;
  capabilities: string[];
  meta?: Record<string, unknown>;
}

export interface ToolInvokePayload {
  agentId: AgentId;
  tool: string;
  args: Record<string, unknown>;
}

export interface TickAdvancePayload {
  tick: TickId;
}

// ─── Events ──────────────────────────────────────────────────────────────────

export type EventType =
  | 'AGENT_REGISTERED'
  | 'AGENT_DEREGISTERED'
  | 'TOOL_INVOKED'
  | 'TOOL_RESULT_RECEIVED'
  | 'TICK_PROCESSED'
  | 'WORLD_RESET';

export interface WorldEvent<T extends EventType = EventType, P = unknown> {
  id: EventId;
  type: T;
  payload: P;
  tick: TickId;
  timestamp: string; // ISO-8601
}

export interface AgentRegisteredPayload {
  agentId: AgentId;
  capabilities: string[];
}

export interface ToolResultPayload {
  agentId: AgentId;
  tool: string;
  result: unknown;
  error?: string;
}

// ─── World State ─────────────────────────────────────────────────────────────

export interface AgentRecord {
  agentId: AgentId;
  capabilities: string[];
  registeredAt: string;
  active: boolean;
}

export interface WorldState {
  tick: TickId;
  agents: Record<AgentId, AgentRecord>;
  pendingTools: ToolInvokePayload[];
  lastEventId: EventId | null;
}
