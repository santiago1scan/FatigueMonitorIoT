/**
 * Hook personalizado para llamadas a la API
 *
 * Responsabilidad única: Gestionar el ciclo de vida de llamadas HTTP
 * (loading, error, success).
 * Abstrae la complejidad async/await para los componentes.
 */

import { useState, useCallback } from "react";

interface UseApiReturn {
  isLoading: boolean;
  error: Error | null;
  execute: <T>(
    fn: () => Promise<T>
  ) => Promise<T | null>;
}

export function useApi(): UseApiReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(
    async <T,>(fn: () => Promise<T>): Promise<T | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await fn();
        return result;
      } catch (err) {
        const apiError = err instanceof Error ? err : new Error(String(err));
        setError(apiError);
        console.error("API Error:", apiError);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { isLoading, error, execute };
}
