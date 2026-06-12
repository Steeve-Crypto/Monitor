import { describe, expect, it, vi } from 'vitest';

import {
  fetchActionProposals,
  fetchApiHealth,
  executeActionProposal,
  fetchAuditEvents,
  fetchOpportunities,
  fetchSignals,
  fetchStoreStats,
  runScan,
  sourceStatuses
} from './monitor';

describe('fetchApiHealth', () => {
  it('returns typed health JSON when the API responds successfully', async () => {
    const fetcher = async () =>
      new Response(JSON.stringify({ service: 'monitor-api', status: 'ok', version: '0.1.0' }), {
        status: 200
      });

    await expect(fetchApiHealth(fetcher as typeof fetch)).resolves.toEqual({
      service: 'monitor-api',
      status: 'ok',
      version: '0.1.0'
    });
  });

  it('raises an actionable error when health fails', async () => {
    const fetcher = async () => new Response('offline', { status: 503 });

    await expect(fetchApiHealth(fetcher as typeof fetch)).rejects.toThrow(
      'Monitor API health check failed: 503'
    );
  });
});

describe('fetchStoreStats', () => {
  it('returns typed store stats JSON when the API responds successfully', async () => {
    const stats = {
      signals_count: 12,
      opportunities_count: 4,
      storage_path: '.monitor/signal_mesh_store.json',
      storage_exists: true
    };
    const fetcher = vi.fn(async () => new Response(JSON.stringify(stats), { status: 200 }));

    await expect(fetchStoreStats(fetcher as unknown as typeof fetch)).resolves.toEqual(stats);
    expect(fetcher).toHaveBeenCalledWith('http://127.0.0.1:8765/api/store/stats');
  });

  it('raises an actionable error when stats fail', async () => {
    const fetcher = async () => new Response('missing', { status: 500 });

    await expect(fetchStoreStats(fetcher as typeof fetch)).rejects.toThrow(
      'Monitor API store stats fetch failed: 500'
    );
  });
});

describe('fetchSignals', () => {
  it('returns the typed signal list response', async () => {
    const payload = {
      items: [
        {
          id: 'sig_1',
          source_platform: 'rss',
          source_id: 'rss-1',
          source_url: 'https://example.com/job',
          title: 'Python web3 dashboard',
          raw_text: 'Need Python web3 dashboard automation',
          signal_kind: 'hiring',
          status: 'new',
          detected_keywords: ['python', 'web3'],
          project_name: null,
          budget_hint: '$2k',
          contact_route: 'application_form',
          risk_level: 'low',
          captured_at: '2026-06-12T00:00:00Z'
        }
      ],
      count: 1
    };
    const fetcher = vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 }));

    await expect(fetchSignals(fetcher as unknown as typeof fetch)).resolves.toEqual(payload);
    expect(fetcher).toHaveBeenCalledWith('http://127.0.0.1:8765/api/signals');
  });
});

describe('fetchOpportunities', () => {
  it('returns the typed opportunity list response', async () => {
    const payload = {
      items: [
        {
          id: 'opp_1',
          source_signal_id: 'sig_1',
          source_platform: 'upwork',
          source_id: 'upwork-1',
          source_url: null,
          title: 'Automation build',
          description: 'Build an automation dashboard',
          required_skills: ['python'],
          budget_min: 500,
          budget_max: 1500,
          currency: 'USD',
          contact_route: 'platform_proposal',
          status: 'qualified',
          python_fit_score: 0.9,
          web3_fit_score: 0.4,
          buyer_intent_score: 0.8,
          budget_quality_score: 0.7,
          urgency_score: 0.5,
          response_likelihood_score: 0.6,
          scam_risk_score: 0.1,
          qualification_score: 0.795,
          is_target_fit: true,
          created_at: '2026-06-12T00:00:00Z'
        }
      ],
      count: 1
    };
    const fetcher = vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 }));

    await expect(fetchOpportunities(fetcher as unknown as typeof fetch)).resolves.toEqual(payload);
    expect(fetcher).toHaveBeenCalledWith('http://127.0.0.1:8765/api/opportunities');
  });
});

describe('runScan', () => {
  it('posts source, query, and limit to the scan endpoint', async () => {
    const payload = { source: 'crypto_rss', items: [], count: 0 };
    const fetcher = vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 }));

    await expect(runScan('crypto_rss', 'python web3', 7, fetcher as unknown as typeof fetch)).resolves.toEqual(
      payload
    );
    expect(fetcher).toHaveBeenCalledWith('http://127.0.0.1:8765/api/scans/crypto_rss/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'python web3', limit: 7 })
    });
  });

  it('raises an actionable error when a scan fails', async () => {
    const fetcher = async () => new Response('bad source', { status: 404 });

    await expect(runScan('crypto_rss', 'python web3', 10, fetcher as typeof fetch)).rejects.toThrow(
      'Monitor API scan failed for crypto_rss: 404'
    );
  });
});

describe('sourceStatuses', () => {
  it('includes the live-safe crypto RSS source', () => {
    expect(sourceStatuses.map((source) => source.id)).toContain('crypto_rss');
    expect(sourceStatuses.find((source) => source.id === 'crypto_rss')?.status).toBe('ready');
  });
});

describe('fetchActionProposals', () => {
  it('returns typed action proposal responses from the approval cockpit API', async () => {
    const payload = {
      items: [
        {
          id: 'act_1',
          action_kind: 'proposal_submit',
          platform: 'rss',
          destination: 'https://example.org/jobs/1',
          payload_preview: { subject: 'Re: Python Web3 Backend Engineer' },
          payload_hash: 'abc123',
          risk_level: 'medium',
          match_score: 0.91,
          scam_risk_score: 0.03,
          bid_amount: null,
          currency: 'USD',
          requires_approval: true,
          autopilot_policy_id: null,
          created_at: '2026-06-12T00:00:00Z'
        }
      ],
      count: 1
    };
    const fetcher = vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 }));

    await expect(fetchActionProposals(fetcher as unknown as typeof fetch)).resolves.toEqual(payload);
    expect(fetcher).toHaveBeenCalledWith('http://127.0.0.1:8765/api/actions/proposals');
  });
});

describe('fetchAuditEvents', () => {
  it('returns typed audit event responses', async () => {
    const payload = {
      items: [
        {
          id: 'evt_1',
          event_type: 'action_proposal.created',
          actor: 'monitor-api',
          entity_id: 'act_1',
          metadata: { opportunity_id: 'opp_1' },
          occurred_at: '2026-06-12T00:00:00Z'
        }
      ],
      count: 1
    };
    const fetcher = vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 }));

    await expect(fetchAuditEvents(fetcher as unknown as typeof fetch)).resolves.toEqual(payload);
    expect(fetcher).toHaveBeenCalledWith('http://127.0.0.1:8765/api/audit');
  });
});

describe('executeActionProposal', () => {
  it('posts to the real execution endpoint for an approved configured action', async () => {
    const payload = {
      id: 'app_1',
      opportunity_id: 'opp_1',
      outreach_draft_id: null,
      action_proposal_id: 'act_1',
      status: 'submitted',
      submitted_at: null,
      outcome_notes: 'Executed via configured webhook with status 200.',
      created_at: '2026-06-12T00:00:00Z'
    };
    const fetcher = vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 }));

    await expect(
      executeActionProposal('act_1', fetcher as unknown as typeof fetch)
    ).resolves.toEqual(payload);
    expect(fetcher).toHaveBeenCalledWith('http://127.0.0.1:8765/api/actions/act_1/execute', { method: 'POST' });
  });
});
