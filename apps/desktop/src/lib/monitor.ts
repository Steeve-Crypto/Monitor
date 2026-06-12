export type ApiHealth = {
  service: string;
  status: string;
  version: string;
};

export type SourceStatus = {
  id: 'x' | 'discord' | 'marketplaces' | 'crypto' | 'crypto_rss';
  label: string;
  description: string;
  status: 'ready' | 'planned';
};

export const sourceStatuses: SourceStatus[] = [
  {
    id: 'x',
    label: 'X / Grok',
    description: 'Buying-intent posts, founder hiring signals, project threads.',
    status: 'ready'
  },
  {
    id: 'discord',
    label: 'Discord',
    description: 'Approved servers/channels for gigs, bounties, grants, hiring requests.',
    status: 'ready'
  },
  {
    id: 'marketplaces',
    label: 'Upwork / Fiverr',
    description: 'Marketplace leads via alerts, official surfaces, and compliant workflows.',
    status: 'ready'
  },
  {
    id: 'crypto',
    label: 'Crypto Boards',
    description: 'Web3.career, CryptoJobsList, Remote3, Dework/Gitcoin-style bounties.',
    status: 'ready'
  },
  {
    id: 'crypto_rss',
    label: 'Crypto RSS',
    description: 'Live-safe public RSS/HTTP feed ingestion for crypto job-board leads.',
    status: 'ready'
  }
];

export async function fetchApiHealth(fetcher: typeof fetch = fetch): Promise<ApiHealth> {
  const response = await fetcher('/api/health');
  if (!response.ok) {
    throw new Error(`Monitor API health check failed: ${response.status}`);
  }
  return (await response.json()) as ApiHealth;
}
