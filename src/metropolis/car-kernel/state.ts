// CAR Kernel — Pure Reducer
// WorldState transitions are pure functions — no side effects, fully replayable

import type { WorldState, WorldEvent, AgentRecord } from './types.js';

export const INITIAL_STATE: WorldState = {
  tick: 0,
  agents: {},
  pendingTools: [],
  lastEventId: null,
};

export function reduce(state: WorldState, event: WorldEvent): WorldState {
  switch (event.type) {
    case 'AGENT_REGISTERED': {
      const p = event.payload as { agentId: string; capabilities: string[] };
      const record: AgentRecord = {
        agentId: p.agentId,
        capabilities: p.capabilities,
        registeredAt: event.timestamp,
        active: true,
      };
      return {
        ...state,
        agents: { ...state.agents, [p.agentId]: record },
        lastEventId: event.id,
      };
    }

    case 'AGENT_DEREGISTERED': {
      const p = event.payload as { agentId: string };
      const existing = state.agents[p.agentId];
      if (!existing) return state;
      return {
        ...state,
        agents: {
          ...state.agents,
          [p.agentId]: { ...existing, active: false },
        },
        lastEventId: event.id,
      };
    }

    case 'TOOL_INVOKED': {
      const p = event.payload as { agentId: string; tool: string; args: Record<string, unknown> };
      return {
        ...state,
        pendingTools: [...state.pendingTools, p],
        lastEventId: event.id,
      };
    }

    case 'TOOL_RESULT_RECEIVED': {
      const p = event.payload as { agentId: string; tool: string };
      return {
        ...state,
        pendingTools: state.pendingTools.filter(
          (t) => !(t.agentId === p.agentId && t.tool === p.tool)
        ),
        lastEventId: event.id,
      };
    }

    case 'TICK_PROCESSED': {
      return {
        ...state,
        tick: event.tick,
        lastEventId: event.id,
      };
    }

    case 'WORLD_RESET': {
      return { ...INITIAL_STATE };
    }

    default:
      return state;
  }
}

export function replay(events: WorldEvent[]): WorldState {
  return events.reduce(reduce, INITIAL_STATE);
}
