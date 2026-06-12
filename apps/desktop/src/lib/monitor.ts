export type ApiHealth = {
  service: string;
  status: string;
  version: string;
};

export type SignalSource = 'x' | 'discord' | 'marketplaces' | 'crypto' | 'crypto_rss';

export type SourceStatus = {
  id: SignalSource;
  label: string;
  description: string;
  status: 'ready' | 'planned';
};

export type StoreStats = {
  signals_count: number;
  opportunities_count: number;
  drafts_count?: number;
  action_proposals_count?: number;
  audit_events_count?: number;
  storage_path: string;
  storage_exists: boolean;
};

export type ProjectSignal = {
  id: string;
  source_platform: string;
  source_id: string;
  source_url?: string | null;
  title: string;
  raw_text: string;
  signal_kind: string;
  status: string;
  detected_keywords: string[];
  project_name?: string | null;
  budget_hint?: string | null;
  contact_route: string;
  risk_level: string;
  captured_at: string;
};

export type SignalListResponse = {
  items: ProjectSignal[];
  count: number;
};

export type Opportunity = {
  id: string;
  source_signal_id?: string | null;
  source_platform: string;
  source_id: string;
  source_url?: string | null;
  title: string;
  description: string;
  required_skills: string[];
  budget_min?: number | null;
  budget_max?: number | null;
  currency: string;
  contact_route: string;
  status: string;
  python_fit_score: number;
  web3_fit_score: number;
  buyer_intent_score: number;
  budget_quality_score: number;
  urgency_score: number;
  response_likelihood_score: number;
  scam_risk_score: number;
  qualification_score?: number;
  is_target_fit?: boolean;
  created_at: string;
};

export type OpportunityListResponse = {
  items: Opportunity[];
  count: number;
};

export type ScanResponse = {
  source: string;
  items: ProjectSignal[];
  count: number;
};

export type OutreachDraft = {
  id: string;
  opportunity_id: string;
  platform: string;
  contact_route: string;
  template_family: string;
  subject?: string | null;
  body: string;
  payload_hash: string;
  model_provenance: {
    provider: string;
    model: string;
    prompt_version?: string | null;
    generated_at: string;
  };
  created_at: string;
};

export type ActionProposal = {
  id: string;
  action_kind: string;
  platform: string;
  destination: string;
  payload_preview: Record<string, unknown>;
  payload_hash: string;
  risk_level: string;
  match_score: number;
  scam_risk_score: number;
  bid_amount?: number | null;
  currency: string;
  requires_approval: boolean;
  autopilot_policy_id?: string | null;
  created_at: string;
};

export type ActionProposalListResponse = {
  items: ActionProposal[];
  count: number;
};

export type AuditEvent = {
  id: string;
  event_type: string;
  actor: string;
  entity_id: string;
  metadata: Record<string, unknown>;
  occurred_at: string;
};

export type AuditEventListResponse = {
  items: AuditEvent[];
  count: number;
};

export type Application = {
  id: string;
  opportunity_id: string;
  outreach_draft_id?: string | null;
  action_proposal_id?: string | null;
  status: string;
  submitted_at?: string | null;
  outcome_notes?: string | null;
  created_at: string;
};

export type ApprovalDecision = {
  id: string;
  action_proposal_id: string;
  status: string;
  decided_by: string;
  notes?: string | null;
  decided_at: string;
};

export const sourceStatuses: SourceStatus[] = [
  {
    id: 'x',
    label: 'X / Grok',
    description: 'Buying-intent posts, founder hiring signals, project threads. Requires live API configuration.',
    status: 'planned'
  },
  {
    id: 'discord',
    label: 'Discord',
    description: 'Approved servers/channels for gigs, bounties, grants, hiring requests. Requires bot/API configuration.',
    status: 'planned'
  },
  {
    id: 'marketplaces',
    label: 'Upwork / Fiverr',
    description: 'Marketplace leads via alerts, official surfaces, and compliant workflows. Requires live adapter configuration.',
    status: 'planned'
  },
  {
    id: 'crypto',
    label: 'Crypto Boards',
    description: 'Web3.career, CryptoJobsList, Remote3, Dework/Gitcoin-style bounties. Use Crypto RSS until board-specific adapters are configured.',
    status: 'planned'
  },
  {
    id: 'crypto_rss',
    label: 'Crypto RSS',
    description: 'Live-safe public RSS/HTTP feed ingestion for crypto job-board leads.',
    status: 'ready'
  }
];

const API_BASE = 'http://127.0.0.1:8765';

function apiPath(path: string): string {
  return `${API_BASE}${path}`;
}

async function readJson<T>(response: Response, errorMessage: string): Promise<T> {
  if (!response.ok) {
    throw new Error(`${errorMessage}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function fetchApiHealth(fetcher: typeof fetch = fetch): Promise<ApiHealth> {
  const response = await fetcher(apiPath('/api/health'));
  return readJson<ApiHealth>(response, 'Monitor API health check failed');
}

export async function fetchStoreStats(fetcher: typeof fetch = fetch): Promise<StoreStats> {
  const response = await fetcher(apiPath('/api/store/stats'));
  return readJson<StoreStats>(response, 'Monitor API store stats fetch failed');
}

export async function fetchSignals(fetcher: typeof fetch = fetch): Promise<SignalListResponse> {
  const response = await fetcher(apiPath('/api/signals'));
  return readJson<SignalListResponse>(response, 'Monitor API signals fetch failed');
}

export async function fetchOpportunities(fetcher: typeof fetch = fetch): Promise<OpportunityListResponse> {
  const response = await fetcher(apiPath('/api/opportunities'));
  return readJson<OpportunityListResponse>(response, 'Monitor API opportunities fetch failed');
}

export async function fetchActionProposals(
  fetcher: typeof fetch = fetch
): Promise<ActionProposalListResponse> {
  const response = await fetcher(apiPath('/api/actions/proposals'));
  return readJson<ActionProposalListResponse>(
    response,
    'Monitor API action proposals fetch failed'
  );
}

export async function fetchAuditEvents(fetcher: typeof fetch = fetch): Promise<AuditEventListResponse> {
  const response = await fetcher(apiPath('/api/audit'));
  return readJson<AuditEventListResponse>(response, 'Monitor API audit fetch failed');
}

export async function executeActionProposal(
  actionId: string,
  fetcher: typeof fetch = fetch
): Promise<Application> {
  const response = await fetcher(apiPath(`/api/actions/${actionId}/execute`), { method: 'POST' });
  return readJson<Application>(response, 'Monitor API external action execution failed');
}

export async function approveActionProposal(
  actionId: string,
  fetcher: typeof fetch = fetch
): Promise<ApprovalDecision> {
  const response = await fetcher(apiPath(`/api/actions/${actionId}/approve`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decided_by: 'operator' })
  });
  return readJson<ApprovalDecision>(response, 'Monitor API action approval failed');
}

export async function rejectActionProposal(
  actionId: string,
  fetcher: typeof fetch = fetch
): Promise<ApprovalDecision> {
  const response = await fetcher(apiPath(`/api/actions/${actionId}/reject`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decided_by: 'operator' })
  });
  return readJson<ApprovalDecision>(response, 'Monitor API action rejection failed');
}

export async function qualifySignal(
  signalId: string,
  fetcher: typeof fetch = fetch
): Promise<Opportunity> {
  const response = await fetcher(apiPath(`/api/signals/${signalId}/qualify`), { method: 'POST' });
  return readJson<Opportunity>(response, 'Monitor API qualification failed');
}

export async function createDraft(
  opportunityId: string,
  fetcher: typeof fetch = fetch
): Promise<OutreachDraft> {
  const response = await fetcher(apiPath(`/api/opportunities/${opportunityId}/draft`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
  return readJson<OutreachDraft>(response, 'Monitor API draft creation failed');
}

export async function proposeAction(
  opportunityId: string,
  fetcher: typeof fetch = fetch
): Promise<ActionProposal> {
  const response = await fetcher(apiPath(`/api/opportunities/${opportunityId}/actions/propose`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
  return readJson<ActionProposal>(response, 'Monitor API action proposal failed');
}

export async function runScan(
  source: SignalSource,
  query: string,
  limit: number,
  fetcher: typeof fetch = fetch
): Promise<ScanResponse> {
  const response = await fetcher(apiPath(`/api/scans/${source}/run`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit })
  });
  return readJson<ScanResponse>(response, `Monitor API scan failed for ${source}`);
}
