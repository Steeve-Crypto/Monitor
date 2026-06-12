import { describe, expect, it } from 'vitest';

import { fetchApiHealth, sourceStatuses } from './monitor';

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

describe('sourceStatuses', () => {
  it('includes the live-safe crypto RSS source', () => {
    expect(sourceStatuses.map((source) => source.id)).toContain('crypto_rss');
    expect(sourceStatuses.find((source) => source.id === 'crypto_rss')?.status).toBe('ready');
  });
});
