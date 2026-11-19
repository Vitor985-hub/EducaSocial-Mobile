import { useEffect, useMemo, useState } from "react";
import {
  getProgramCategories,
  getPrograms,
  type ProgramSummary,
} from "@/services/catalog";

export function useCatalog() {
  const [programs, setPrograms] = useState<ProgramSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    getPrograms()
      .then((result) => {
        if (active) {
          setPrograms(result);
        }
      })
      .catch((requestError: unknown) => {
        if (active) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : "Não foi possível carregar o catálogo.",
          );
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [attempt]);

  const categories = useMemo(() => getProgramCategories(programs), [programs]);

  return {
    programs,
    categories,
    loading,
    error,
    retry: () => {
      setLoading(true);
      setError(null);
      setAttempt((currentAttempt) => currentAttempt + 1);
    },
  };
}
