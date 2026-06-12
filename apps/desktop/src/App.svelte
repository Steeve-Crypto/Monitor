<script lang="ts">
  import { onMount } from 'svelte';
  import {
    fetchApiHealth,
    fetchOpportunities,
    fetchSignals,
    fetchStoreStats,
    runScan,
    sourceStatuses,
    type ApiHealth,
    type Opportunity,
    type ProjectSignal,
    type SignalSource,
    type StoreStats
  } from '$lib/monitor';

  let health: ApiHealth | null = null;
  let stats: StoreStats | null = null;
  let signals: ProjectSignal[] = [];
  let opportunities: Opportunity[] = [];
  let apiError: string | null = 'Start apps/api to connect live data.';
  let dataError: string | null = null;
  let scanError: string | null = null;
  let scanMessage: string | null = null;
  let loading = true;
  let scanning = false;
  let selectedSource: SignalSource = 'crypto_rss';
  let scanQuery = 'python web3 automation dashboard';
  let scanLimit = 10;

  const priorityMissions = [
    'Run X/Grok buying-intent hunt for Python + web3 dashboard gigs',
    'Scan approved Discord communities for bounty and grant signals',
    'Pull Upwork/Fiverr marketplace leads into Signal Mesh',
    'Qualify leads by stack fit, buyer intent, budget quality, and scam risk'
  ];

  $: latestSignals = signals.slice(0, 6);
  $: latestOpportunities = opportunities.slice(0, 6);
  $: selectedSourceStatus = sourceStatuses.find((source) => source.id === selectedSource);

  async function refreshData() {
    loading = true;
    dataError = null;
    try {
      const [nextHealth, nextStats, nextSignals, nextOpportunities] = await Promise.all([
        fetchApiHealth(),
        fetchStoreStats(),
        fetchSignals(),
        fetchOpportunities()
      ]);
      health = nextHealth;
      stats = nextStats;
      signals = nextSignals.items;
      opportunities = nextOpportunities.items;
      apiError = null;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown Monitor API error';
      apiError = message;
      dataError = message;
    } finally {
      loading = false;
    }
  }

  async function submitScan() {
    scanning = true;
    scanError = null;
    scanMessage = null;
    try {
      const response = await runScan(selectedSource, scanQuery, scanLimit);
      scanMessage = `Scan complete: ${response.count} new ${response.count === 1 ? 'signal' : 'signals'} captured from ${response.source}.`;
      await refreshData();
    } catch (error) {
      scanError = error instanceof Error ? error.message : 'Unknown scan error';
    } finally {
      scanning = false;
    }
  }

  function formatDate(value: string) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return new Intl.DateTimeFormat(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  }

  function formatPercent(value: number | undefined) {
    if (value === undefined) {
      return 'n/a';
    }
    return `${Math.round(value * 100)}%`;
  }

  onMount(refreshData);
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
      {#if dataError}
        <p class="alert">{dataError}</p>
      {/if}
    </div>

    <div class="api-card" class:online={health?.status === 'ok'}>
      <span class="pulse" aria-hidden="true"></span>
      <div>
        <p>Local API</p>
        {#if health}
          <strong>{health.status.toUpperCase()}</strong>
          <small>{health.service} v{health.version}</small>
        {:else if loading}
          <strong>CHECKING</strong>
          <small>Loading API health…</small>
        {:else}
          <strong>OFFLINE</strong>
          <small>{apiError}</small>
        {/if}
      </div>
    </div>
  </section>

  <section class="stats-grid" aria-label="Store counts">
    <article class="panel stat-card">
      <p class="eyebrow">Signals</p>
      <strong>{stats?.signals_count ?? '—'}</strong>
      <span>captured project signals</span>
    </article>
    <article class="panel stat-card">
      <p class="eyebrow">Opportunities</p>
      <strong>{stats?.opportunities_count ?? '—'}</strong>
      <span>qualified opportunity records</span>
    </article>
    <article class="panel stat-card storage">
      <p class="eyebrow">Store</p>
      <strong>{stats?.storage_exists ? 'READY' : 'EMPTY'}</strong>
      <span>{stats?.storage_path ?? 'Waiting for /api/store/stats'}</span>
    </article>
  </section>

  <section class="grid two">
    <article class="panel scan-panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Signal Mesh</p>
          <h2>Run source scan</h2>
        </div>
        <button class="ghost-button" type="button" on:click={refreshData} disabled={loading || scanning}>
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      <form class="scan-form" on:submit|preventDefault={submitScan}>
        <label>
          Source
          <select bind:value={selectedSource}>
            {#each sourceStatuses as source}
              <option value={source.id}>{source.label}</option>
            {/each}
          </select>
        </label>
        <label>
          Query
          <input bind:value={scanQuery} placeholder="python web3 automation dashboard" />
        </label>
        <label>
          Limit
          <input type="number" min="0" max="50" bind:value={scanLimit} />
        </label>
        <button type="submit" disabled={scanning || !scanQuery.trim()}>
          {scanning ? 'Scanning…' : 'Run scan'}
        </button>
      </form>

      {#if selectedSourceStatus}
        <p class="muted source-note">{selectedSourceStatus.description}</p>
      {/if}
      {#if scanMessage}
        <p class="success">{scanMessage}</p>
      {/if}
      {#if scanError}
        <p class="alert">{scanError}</p>
      {/if}
    </article>

    <article class="panel approval-placeholder">
      <p class="eyebrow">Approval Cockpit</p>
      <h2>Human gate placeholder</h2>
      <p>
        Qualification and signal-to-opportunity conversion are now live. Draft generation,
        action proposals, approval decisions, and external execution remain intentionally
        disabled until the Tailor, audit, and approval APIs are implemented.
      </p>
      <div class="status-pill">No pending approvals loaded</div>
    </article>
  </section>

  <section class="grid two lists">
    <article class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Latest Signals</p>
          <h2>Signal intake</h2>
        </div>
        <span class="constellation-label">{signals.length} total</span>
      </div>
      {#if latestSignals.length}
        <div class="item-list">
          {#each latestSignals as signal}
            <article class="item-card">
              <div class="item-topline">
                <span>{signal.source_platform}</span>
                <span>{formatDate(signal.captured_at)}</span>
              </div>
              <h3>{signal.title}</h3>
              <p>{signal.raw_text}</p>
              <div class="chip-row">
                <span>{signal.signal_kind}</span>
                <span>{signal.contact_route}</span>
                <span class:risk={signal.risk_level !== 'low'}>{signal.risk_level} risk</span>
              </div>
            </article>
          {/each}
        </div>
      {:else}
        <p class="empty">No signals yet. Run a source scan to populate the mesh.</p>
      {/if}
    </article>

    <article class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Latest Opportunities</p>
          <h2>Qualified leads</h2>
        </div>
        <span class="constellation-label">{opportunities.length} total</span>
      </div>
      {#if latestOpportunities.length}
        <div class="item-list">
          {#each latestOpportunities as opportunity}
            <article class="item-card opportunity-card">
              <div class="item-topline">
                <span>{opportunity.source_platform}</span>
                <span>{formatDate(opportunity.created_at)}</span>
              </div>
              <h3>{opportunity.title}</h3>
              <p>{opportunity.description}</p>
              <div class="score-row">
                <span>Fit {formatPercent(opportunity.qualification_score)}</span>
                <span>Python {formatPercent(opportunity.python_fit_score)}</span>
                <span>Scam {formatPercent(opportunity.scam_risk_score)}</span>
              </div>
            </article>
          {/each}
        </div>
      {:else}
        <p class="empty">No opportunities yet. Conversion/scoring can populate this list when ready.</p>
      {/if}
    </article>
  </section>

  <section class="panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Mission Queue</p>
        <h2>Next best actions</h2>
      </div>
      <span class="constellation-label">Source constellation baseline</span>
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
    <ol class="mission-list">
      {#each priorityMissions as mission}
        <li>{mission}</li>
      {/each}
    </ol>
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
  h3 { margin-bottom: 10px; }
  .lede, .approval-placeholder p, .muted { color: #d6ccf4; font-size: 1.04rem; line-height: 1.7; }
  .lede { max-width: 760px; }
  .api-card { display: flex; gap: 16px; align-items: center; border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 22px; padding: 22px; background: rgba(8, 7, 14, 0.78); }
  .api-card p, .api-card small { color: #a7a2b8; display: block; margin: 0; }
  .api-card strong { display: block; font-size: 2rem; letter-spacing: 0.05em; }
  .pulse { width: 18px; height: 18px; border-radius: 999px; background: #fb7185; box-shadow: 0 0 24px #fb7185; }
  .api-card.online .pulse { background: #8b5cf6; box-shadow: 0 0 28px #8b5cf6; }
  .stats-grid { display: grid; grid-template-columns: 0.7fr 0.7fr 1.6fr; gap: 18px; margin-bottom: 24px; }
  .stat-card strong { display: block; font-size: 2.5rem; letter-spacing: -0.04em; }
  .stat-card span { color: #bdb4d7; overflow-wrap: anywhere; }
  .grid.two { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 24px; margin-bottom: 24px; }
  .section-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 18px; }
  .scan-form { display: grid; grid-template-columns: 0.9fr 1.7fr 0.6fr auto; gap: 12px; align-items: end; }
  label { display: grid; gap: 8px; color: #c4b5fd; font-size: 0.82rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
  input, select, button { min-height: 44px; border-radius: 14px; border: 1px solid rgba(168, 85, 247, 0.3); color: #f5f0ff; background: rgba(8, 7, 14, 0.82); padding: 0 14px; font: inherit; }
  button { cursor: pointer; font-weight: 800; background: linear-gradient(135deg, #7c3aed, #a855f7); }
  button:disabled { cursor: not-allowed; opacity: 0.55; }
  .ghost-button { background: rgba(88, 28, 135, 0.24); }
  .source-note, .success, .alert { margin: 16px 0 0; }
  .success { color: #86efac; }
  .alert { color: #fecdd3; }
  .status-pill, .source-card span, .constellation-label, .chip-row span, .score-row span {
    display: inline-flex; border: 1px solid rgba(168, 85, 247, 0.35); border-radius: 999px; color: #ddd6fe; background: rgba(88, 28, 135, 0.26); padding: 8px 12px; font-size: 0.78rem; font-weight: 800; text-transform: uppercase;
  }
  .item-list { display: grid; gap: 14px; }
  .item-card { border: 1px solid rgba(148, 163, 184, 0.16); border-radius: 20px; background: rgba(8, 7, 14, 0.54); padding: 16px; }
  .item-card p { color: #bdb4d7; line-height: 1.55; }
  .item-topline, .chip-row, .score-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between; }
  .item-topline { color: #a7a2b8; font-size: 0.78rem; margin-bottom: 10px; text-transform: uppercase; }
  .chip-row, .score-row { justify-content: flex-start; }
  .chip-row span.risk { border-color: rgba(251, 113, 133, 0.5); color: #fecdd3; }
  .empty { color: #a7a2b8; border: 1px dashed rgba(168, 85, 247, 0.28); border-radius: 18px; padding: 18px; }
  .source-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin-bottom: 24px; }
  .source-card { min-height: 210px; border: 1px solid rgba(148, 163, 184, 0.16); border-radius: 22px; background: radial-gradient(circle at top, rgba(124, 58, 237, 0.2), rgba(15, 10, 28, 0.76)); padding: 18px; }
  .source-card p { color: #bdb4d7; line-height: 1.55; min-height: 76px; }
  .orb { width: 42px; height: 42px; border-radius: 999px; margin-bottom: 16px; background: radial-gradient(circle, #f5f3ff, #8b5cf6 48%, rgba(139, 92, 246, 0.08)); box-shadow: 0 0 42px rgba(139, 92, 246, 0.72); }
  .mission-list { display: grid; gap: 12px; margin: 0; padding-left: 22px; color: #ddd6fe; }
  @media (max-width: 980px) { .hero, .grid.two, .stats-grid, .scan-form, .source-grid { grid-template-columns: 1fr; } }
</style>
