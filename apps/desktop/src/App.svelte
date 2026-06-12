<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchApiHealth, sourceStatuses, type ApiHealth } from '$lib/monitor';

  let health: ApiHealth | null = null;
  let apiError: string | null = 'Start apps/api to connect live data.';

  const priorityMissions = [
    'Run X/Grok buying-intent hunt for Python + web3 dashboard gigs',
    'Scan approved Discord communities for bounty and grant signals',
    'Pull Upwork/Fiverr marketplace leads into Signal Mesh',
    'Qualify leads by stack fit, buyer intent, budget quality, and scam risk'
  ];

  onMount(async () => {
    try {
      health = await fetchApiHealth();
      apiError = null;
    } catch (error) {
      apiError = error instanceof Error ? error.message : 'Unknown API health error';
    }
  });
</script>

<svelte:head>
  <title>Monitor Command Deck</title>
  <meta
    name="description"
    content="Monitor local-first command deck for Python, AI automation, and web3 opportunity acquisition."
  />
</svelte:head>

<main class="shell">
  <section class="hero panel" aria-labelledby="mission-control-title">
    <div>
      <p class="eyebrow">Sovereign Opportunity Acquisition</p>
      <h1 id="mission-control-title">Monitor Command Deck</h1>
      <p class="lede">
        Signal mesh for X, Discord, Upwork, Fiverr, and crypto job boards — qualifying
        Python/web3 gigs and preparing proposal-grade outreach under risk-based autonomy.
      </p>
    </div>

    <div class="api-card" class:online={health?.status === 'ok'}>
      <span class="pulse" aria-hidden="true"></span>
      <div>
        <p>Local API</p>
        {#if health}
          <strong>{health.status.toUpperCase()}</strong>
          <small>{health.service} v{health.version}</small>
        {:else}
          <strong>OFFLINE</strong>
          <small>{apiError}</small>
        {/if}
      </div>
    </div>
  </section>

  <section class="grid two">
    <article class="panel">
      <p class="eyebrow">Mission Queue</p>
      <h2>Next best actions</h2>
      <ol class="mission-list">
        {#each priorityMissions as mission}
          <li>{mission}</li>
        {/each}
      </ol>
    </article>

    <article class="panel autopilot">
      <p class="eyebrow">Risk Layer</p>
      <h2>Scoped Autopilot</h2>
      <p>
        Reputation-risk sends stay gated unless an explicit AutopilotPolicy matches platform,
        template family, score thresholds, cooldowns, bid limits, and scam-risk ceilings.
      </p>
      <div class="status-pill">Kill switch: armed</div>
    </article>
  </section>

  <section class="panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Signal Mesh</p>
        <h2>Source adapters</h2>
      </div>
      <span class="constellation-label">Opportunity constellation baseline</span>
    </div>

    <div class="source-grid">
      {#each sourceStatuses as source}
        <article class="source-card">
          <div class="orb" aria-hidden="true"></div>
          <h3>{source.label}</h3>
          <p>{source.description}</p>
          <span>{source.status}</span>
        </article>
      {/each}
    </div>
  </section>
</main>

<style>
  :global(*) { box-sizing: border-box; }
  :global(body) {
    margin: 0;
    min-height: 100vh;
    color: #f5f0ff;
    background:
      radial-gradient(circle at top left, rgba(126, 58, 242, 0.28), transparent 32rem),
      radial-gradient(circle at 70% 20%, rgba(71, 85, 105, 0.22), transparent 26rem),
      #05030a;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
  .shell { width: min(1180px, calc(100vw - 32px)); margin: 0 auto; padding: 40px 0; }
  .panel {
    border: 1px solid rgba(168, 85, 247, 0.22);
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(15, 10, 28, 0.92), rgba(10, 9, 18, 0.78));
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    padding: 28px;
  }
  .hero { display: grid; grid-template-columns: 1fr minmax(260px, 340px); gap: 28px; align-items: stretch; margin-bottom: 24px; }
  .eyebrow { color: #c4b5fd; font-size: 0.76rem; font-weight: 800; letter-spacing: 0.16em; margin: 0 0 10px; text-transform: uppercase; }
  h1, h2, h3, p { margin-top: 0; }
  h1 { font-size: clamp(2.6rem, 8vw, 6.4rem); line-height: 0.92; margin-bottom: 18px; letter-spacing: -0.08em; }
  h2 { font-size: 1.45rem; margin-bottom: 16px; }
  .lede { color: #d6ccf4; font-size: 1.08rem; line-height: 1.7; max-width: 760px; }
  .api-card { display: flex; gap: 16px; align-items: center; border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 22px; padding: 22px; background: rgba(8, 7, 14, 0.78); }
  .api-card p, .api-card small { color: #a7a2b8; display: block; margin: 0; }
  .api-card strong { display: block; font-size: 2rem; letter-spacing: 0.05em; }
  .pulse { width: 18px; height: 18px; border-radius: 999px; background: #fb7185; box-shadow: 0 0 24px #fb7185; }
  .api-card.online .pulse { background: #8b5cf6; box-shadow: 0 0 28px #8b5cf6; }
  .grid.two { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 24px; margin-bottom: 24px; }
  .mission-list { display: grid; gap: 12px; margin: 0; padding-left: 22px; color: #ddd6fe; }
  .autopilot p { color: #d6ccf4; line-height: 1.65; }
  .status-pill, .source-card span, .constellation-label { display: inline-flex; border: 1px solid rgba(168, 85, 247, 0.35); border-radius: 999px; color: #ddd6fe; background: rgba(88, 28, 135, 0.26); padding: 8px 12px; font-size: 0.78rem; font-weight: 800; text-transform: uppercase; }
  .section-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 18px; }
  .source-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
  .source-card { min-height: 210px; border: 1px solid rgba(148, 163, 184, 0.16); border-radius: 22px; background: radial-gradient(circle at top, rgba(124, 58, 237, 0.2), rgba(15, 10, 28, 0.76)); padding: 18px; }
  .source-card p { color: #bdb4d7; line-height: 1.55; min-height: 76px; }
  .orb { width: 42px; height: 42px; border-radius: 999px; margin-bottom: 16px; background: radial-gradient(circle, #f5f3ff, #8b5cf6 48%, rgba(139, 92, 246, 0.08)); box-shadow: 0 0 42px rgba(139, 92, 246, 0.72); }
  @media (max-width: 860px) { .hero, .grid.two, .source-grid { grid-template-columns: 1fr; } }
</style>
