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

async function readJson<T>(response: Response, errorMessage: string): Promise<T> {
  if (!response.ok) {
    throw new Error(`${errorMessage}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function fetchApiHealth(fetcher: typeof fetch = fetch): Promise<ApiHealth> {
  const response = await fetcher('/api/health');
  return readJson<ApiHealth>(response, 'Monitor API health check failed');
}

export async function fetchStoreStats(fetcher: typeof fetch = fetch): Promise<StoreStats> {
  const response = await fetcher('/api/store/stats');
  return readJson<StoreStats>(response, 'Monitor API store stats fetch failed');
}

export async function fetchSignals(fetcher: typeof fetch = fetch): Promise<SignalListResponse> {
  const response = await fetcher('/api/signals');
  return readJson<SignalListResponse>(response, 'Monitor API signals fetch failed');
}

export async function fetchOpportunities(fetcher: typeof fetch = fetch): Promise<OpportunityListResponse> {
  const response = await fetcher('/api/opportunities');
  return readJson<OpportunityListResponse>(response, 'Monitor API opportunities fetch failed');
}

export async function runScan(
  source: SignalSource,
  query: string,
  limit: number,
  fetcher: typeof fetch = fetch
): Promise<ScanResponse> {
  const response = await fetcher(`/api/scans/${source}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit })
  });
  return readJson<ScanResponse>(response, `Monitor API scan failed for ${source}`);
}
