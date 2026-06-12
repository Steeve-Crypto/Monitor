export type Platform = 'x' | 'discord' | 'upwork' | 'fiverr' | 'web3_career' | 'other';
export type RiskLevel = 'low' | 'medium' | 'high';

export type ApiHealth = {
  service: 'monitor-api';
  status: 'ok';
  version: string;
};

export type ProjectSignal = {
  id: string;
  source_platform: Platform;
  source_id: string;
  title: string;
  raw_text: string;
  risk_level: RiskLevel;
  detected_keywords: string[];
};

export type ListResponse<T> = {
  items: T[];
  count: number;
};
