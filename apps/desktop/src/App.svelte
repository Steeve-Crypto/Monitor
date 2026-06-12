<script lang="ts">
  import { onMount } from 'svelte';
  import {
    approveActionProposal,
    createDraft,
    executeActionProposal,
    fetchActionProposals,
    fetchApiHealth,
    fetchAuditEvents,
    fetchOpportunities,
    fetchSignals,
    fetchStoreStats,
    proposeAction,
    qualifySignal,
    rejectActionProposal,
    runScan,
    type ActionProposal,
    type ApiHealth,
    type AuditEvent,
    type Opportunity,
    type ProjectSignal,
    type StoreStats
  } from '$lib/monitor';

  let health: ApiHealth | null = null;
  let stats: StoreStats | null = null;
  let signals: ProjectSignal[] = [];
  let opportunities: Opportunity[] = [];
  let proposals: ActionProposal[] = [];
  let audit: AuditEvent[] = [];
  let statusLine = 'READY';
  let busy = false;

  $: online = health?.status === 'ok';
  $: signal = signals[0];
  $: opportunity = opportunities[0];
  $: proposal = proposals[0];

  async function sync() {
    busy = true;
    try {
      const [h, st, si, op, pr, au] = await Promise.all([
        fetchApiHealth(),
        fetchStoreStats(),
        fetchSignals(),
        fetchOpportunities(),
        fetchActionProposals(),
        fetchAuditEvents()
      ]);
      health = h;
      stats = st;
      signals = si.items;
      opportunities = op.items;
      proposals = pr.items;
      audit = au.items;
      statusLine = 'SYNCED';
    } catch (error) {
      statusLine = error instanceof Error ? error.message : 'API OFFLINE';
    } finally {
      busy = false;
    }
  }

  async function scan() {
    busy = true;
    try {
      const result = await runScan('crypto_rss', 'python web3 automation dashboard', 10);
      statusLine = result.count ? `SCANNED ${result.count}` : 'NO NEW SIGNALS';
      await sync();
    } catch (error) {
      statusLine = error instanceof Error ? error.message : 'SCAN FAILED';
    } finally {
      busy = false;
    }
  }

  async function qualify() {
    if (!signal) {
      statusLine = 'NO SIGNAL';
      return;
    }
    busy = true;
    try {
      await qualifySignal(signal.id);
      statusLine = 'QUALIFIED';
      await sync();
    } catch (error) {
      statusLine = error instanceof Error ? error.message : 'QUALIFY FAILED';
    } finally {
      busy = false;
    }
  }

  async function draft() {
    if (!opportunity) {
      statusLine = 'NO OPPORTUNITY';
      return;
    }
    busy = true;
    try {
      await createDraft(opportunity.id);
      await proposeAction(opportunity.id);
      statusLine = 'DRAFTED';
      await sync();
    } catch (error) {
      statusLine = error instanceof Error ? error.message : 'DRAFT FAILED';
    } finally {
      busy = false;
    }
  }

  async function action(kind: 'approve' | 'reject' | 'execute') {
    if (!proposal) {
      statusLine = 'NO PROPOSAL';
      return;
    }
    busy = true;
    try {
      if (kind === 'approve') await approveActionProposal(proposal.id);
      if (kind === 'reject') await rejectActionProposal(proposal.id);
      if (kind === 'execute') await executeActionProposal(proposal.id);
      statusLine = kind.toUpperCase();
      await sync();
    } catch (error) {
      statusLine = error instanceof Error ? error.message : `${kind.toUpperCase()} FAILED`;
    } finally {
      busy = false;
    }
  }

  onMount(sync);
</script>

<svelte:head>
  <title>Monitor</title>
</svelte:head>

<div class="space" aria-hidden="true">
  <div class="starfield a"></div>
  <div class="starfield b"></div>
  <div class="nebula n1"></div>
  <div class="nebula n2"></div>
  <div class="horizon"></div>
</div>

<main class="deck">
  <header class="top">
    <div class="mark">MONITOR</div>
    <div class:online class="pulse">{online ? 'ONLINE' : 'OFFLINE'}</div>
  </header>

  <section class="orbital">
    <div class="ring r1"></div>
    <div class="ring r2"></div>
    <div class="ring r3"></div>
    <button class="planet" on:click={sync} disabled={busy} aria-label="Sync">
      <span>{busy ? '...' : stats?.signals_count ?? 0}</span>
      <small>SIGNALS</small>
    </button>
    <div class="moon m1">X</div>
    <div class="moon m2">RSS</div>
    <div class="moon m3">UPWORK</div>
    <div class="moon m4">DISCORD</div>
  </section>

  <section class="commands" aria-label="Commands">
    <button on:click={scan} disabled={busy}>SCAN</button>
    <button on:click={qualify} disabled={busy || !signal}>QUALIFY</button>
    <button on:click={draft} disabled={busy || !opportunity}>DRAFT</button>
    <button on:click={() => action('approve')} disabled={busy || !proposal}>APPROVE</button>
    <button on:click={() => action('execute')} disabled={busy || !proposal}>EXECUTE</button>
    <button class="reject" on:click={() => action('reject')} disabled={busy || !proposal}>REJECT</button>
  </section>

  <section class="readout" aria-label="Status">
    <div>{statusLine}</div>
    <div>{stats?.opportunities_count ?? 0} OPP</div>
    <div>{stats?.action_proposals_count ?? 0} ACTIONS</div>
    <div>{audit[0]?.event_type ?? 'NO AUDIT'}</div>
  </section>
</main>

<style>
  :global(*) { box-sizing: border-box; }
  :global(body) {
    margin: 0;
    min-height: 100vh;
    overflow: hidden;
    color: #eff6ff;
    background: #000;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  }

  .space { position: fixed; inset: 0; z-index: -10; background: radial-gradient(circle at 50% 120%, #172554 0%, #020617 38%, #000 74%); }
  .space::after { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at center, transparent 0%, rgba(0,0,0,.36) 45%, rgba(0,0,0,.9) 100%); }
  .starfield { position: absolute; inset: -20%; background-image: radial-gradient(circle, rgba(255,255,255,.9) 0 1px, transparent 1.5px); opacity: .7; animation: drift 60s linear infinite; }
  .starfield.a { background-size: 130px 130px; }
  .starfield.b { background-size: 210px 210px; animation-duration: 95s; opacity: .4; }
  .nebula { position: absolute; width: 55vw; height: 55vw; border-radius: 50%; filter: blur(90px); opacity: .34; mix-blend-mode: screen; }
  .n1 { left: -18vw; top: -10vh; background: #2563eb; }
  .n2 { right: -20vw; top: 4vh; background: #7c3aed; }
  .horizon { position: absolute; left: -15vw; right: -15vw; bottom: -22vh; height: 54vh; background: linear-gradient(rgba(96,165,250,.18) 1px, transparent 1px), linear-gradient(90deg, rgba(96,165,250,.14) 1px, transparent 1px); background-size: 70px 70px; transform: perspective(520px) rotateX(64deg); animation: grid 7s linear infinite; opacity: .5; }
  @keyframes drift { to { transform: translate3d(-160px, 90px, 0); } }
  @keyframes grid { to { background-position: 0 70px, 70px 0; } }

  .deck { width: min(1180px, calc(100vw - 32px)); height: 100vh; margin: 0 auto; display: grid; grid-template-rows: auto 1fr auto auto; gap: 18px; padding: 22px 0; }
  .top { display: flex; justify-content: space-between; align-items: center; height: 54px; border: 1px solid rgba(147,197,253,.18); background: rgba(2,6,23,.52); backdrop-filter: blur(18px); padding: 0 18px; letter-spacing: .2em; }
  .mark { font-size: 1.05rem; font-weight: 900; }
  .pulse { color: #fecdd3; }
  .pulse::before { content: ''; display: inline-block; width: 8px; height: 8px; margin-right: 10px; border-radius: 50%; background: #fb7185; box-shadow: 0 0 20px #fb7185; }
  .pulse.online { color: #bfdbfe; }
  .pulse.online::before { background: #38bdf8; box-shadow: 0 0 20px #38bdf8; }

  .orbital { position: relative; display: grid; place-items: center; min-height: 0; }
  .ring { position: absolute; border: 1px solid rgba(147,197,253,.22); border-radius: 50%; transform: rotateX(65deg) rotateZ(-20deg); }
  .r1 { width: min(38vw, 430px); height: min(38vw, 430px); animation: spin 18s linear infinite; }
  .r2 { width: min(54vw, 620px); height: min(54vw, 620px); animation: spin 30s linear infinite reverse; border-color: rgba(196,181,253,.18); }
  .r3 { width: min(70vw, 800px); height: min(70vw, 800px); animation: spin 48s linear infinite; border-color: rgba(125,211,252,.12); }
  @keyframes spin { to { transform: rotateX(65deg) rotateZ(340deg); } }

  .planet { position: relative; z-index: 3; width: clamp(190px, 24vw, 300px); height: clamp(190px, 24vw, 300px); border-radius: 50%; display: grid; place-items: center; border: 1px solid rgba(191,219,254,.62); color: #fff; background: radial-gradient(circle at 32% 25%, #fff 0 3%, #38bdf8 8%, #1d4ed8 28%, #020617 68%); box-shadow: 0 0 110px rgba(37,99,235,.52), inset -34px -38px 80px rgba(0,0,0,.86); cursor: pointer; }
  .planet span { font-size: clamp(4rem, 10vw, 8rem); font-weight: 900; letter-spacing: -.12em; line-height: .75; }
  .planet small { position: absolute; bottom: 28%; left: 50%; transform: translateX(-50%); letter-spacing: .28em; color: rgba(239,246,255,.72); }
  .planet:disabled { opacity: .78; }

  .moon { position: absolute; z-index: 4; min-width: 74px; padding: 10px 12px; border: 1px solid rgba(147,197,253,.28); background: rgba(2,6,23,.7); backdrop-filter: blur(14px); color: #dbeafe; text-align: center; font-size: .7rem; letter-spacing: .14em; box-shadow: 0 0 24px rgba(56,189,248,.16); }
  .m1 { top: 10%; left: 20%; }
  .m2 { top: 18%; right: 19%; }
  .m3 { bottom: 15%; right: 14%; }
  .m4 { bottom: 18%; left: 13%; }

  .commands { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
  button { min-height: 64px; border: 1px solid rgba(147,197,253,.22); color: #eff6ff; background: rgba(15,23,42,.72); backdrop-filter: blur(16px); font: 900 .86rem/1 ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .18em; cursor: pointer; transition: transform .16s, border-color .16s, background .16s; }
  button:hover:not(:disabled) { transform: translateY(-2px); border-color: rgba(125,211,252,.75); background: rgba(14,165,233,.22); }
  button:disabled { opacity: .36; cursor: not-allowed; }
  button.reject:hover:not(:disabled) { border-color: rgba(251,113,133,.75); background: rgba(127,29,29,.32); }

  .readout { display: grid; grid-template-columns: 2fr 1fr 1fr 1.4fr; gap: 10px; }
  .readout div { min-height: 54px; display: flex; align-items: center; border: 1px solid rgba(147,197,253,.16); background: rgba(2,6,23,.64); color: #bfdbfe; padding: 0 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; letter-spacing: .08em; }

  @media (max-width: 860px) {
    :global(body) { overflow: auto; }
    .deck { height: auto; min-height: 100vh; }
    .commands, .readout { grid-template-columns: 1fr 1fr; }
    .orbital { min-height: 460px; }
    .moon { font-size: .62rem; min-width: 60px; }
  }
</style>
