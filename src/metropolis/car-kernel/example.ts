import { CARKernel } from './kernel.js';

async function main() {
  const kernel = new CARKernel();

  kernel.registerTool('ping', async (args: Record<string, unknown>) => ({
    pong: true,
    args,
  }));

  // Register an agent
  await kernel.dispatch({
    type: 'AGENT_REGISTER',
    payload: {
      agentId: 'operator-1',
      capabilities: ['ping'],
    },
    issuedAt: new Date().toISOString(),
    issuedBy: 'system',
  });

  // Invoke a tool
  const events = await kernel.dispatch({
    type: 'TOOL_INVOKE',
    payload: {
      agentId: 'operator-1',
      tool: 'ping',
      args: { message: 'hello world' },
    },
    issuedAt: new Date().toISOString(),
    issuedBy: 'operator-1',
  });

  console.log('Events:', events);
  console.log('State:', kernel.getState());
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
