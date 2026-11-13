import { useCallback, useEffect, useState } from 'react';
import { listFlags } from '../api';
import type { Flag } from '../types';

export function useFlags(projectKey: string) {
  const [flags, setFlags] = useState<Flag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setFlags(await listFlags(projectKey));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load flags');
    } finally {
      setLoading(false);
    }
  }, [projectKey]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { flags, loading, error, reload };
}
