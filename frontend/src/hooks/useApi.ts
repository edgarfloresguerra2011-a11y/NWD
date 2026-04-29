import { useState, useEffect } from 'react';
import { apiRequest } from '../lib/api';

export function useApi<T>(endpoint: string, immediate = true) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiRequest<T>(endpoint);
      setData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [endpoint, immediate]);

  return { data, loading, error, refetch: fetchData };
}
