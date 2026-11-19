import { useEffect, useState } from 'react';
import { listHistory } from '../api';
import type { History } from '../types';

export function useHistory(projectKey: string) {
  const [history, setHistory] = useState<History | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listHistory(projectKey).then((result) => {
      setHistory(result);
      setLoading(false);
    });
  }, [projectKey]);

  return { history, loading };
}
