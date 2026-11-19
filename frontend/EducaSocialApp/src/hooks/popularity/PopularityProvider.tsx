import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

type PopularityContextValue = {
  categoryCounts: Record<string, number>;
  serviceCounts: Record<string, number>;
  recordCategoryAccess: (categoryId: string) => void;
  recordServiceAccess: (serviceId: number) => void;
};

const PopularityContext = createContext<PopularityContextValue | null>(null);

export function PopularityProvider({ children }: { children: ReactNode }) {
  const [categoryCounts, setCategoryCounts] = useState<Record<string, number>>(
    {},
  );
  const [serviceCounts, setServiceCounts] = useState<Record<string, number>>(
    {},
  );

  const recordCategoryAccess = useCallback((categoryId: string) => {
    setCategoryCounts((current) => ({
      ...current,
      [categoryId]: (current[categoryId] ?? 0) + 1,
    }));
  }, []);

  const recordServiceAccess = useCallback((serviceId: number) => {
    const key = String(serviceId);
    setServiceCounts((current) => ({
      ...current,
      [key]: (current[key] ?? 0) + 1,
    }));
  }, []);

  const value = useMemo(
    () => ({
      categoryCounts,
      serviceCounts,
      recordCategoryAccess,
      recordServiceAccess,
    }),
    [
      categoryCounts,
      recordCategoryAccess,
      recordServiceAccess,
      serviceCounts,
    ],
  );

  return (
    <PopularityContext.Provider value={value}>
      {children}
    </PopularityContext.Provider>
  );
}

export function usePopularity() {
  const context = useContext(PopularityContext);
  if (!context) {
    throw new Error("usePopularity deve ser usado dentro de PopularityProvider.");
  }
  return context;
}

export function rankByPopularity<T extends { id: string | number }>(
  items: T[],
  counts: Record<string, number>,
  limit?: number,
): T[] {
  const ranked = items
    .map((item, index) => ({ item, index }))
    .sort(
      (left, right) =>
        (counts[String(right.item.id)] ?? 0) -
          (counts[String(left.item.id)] ?? 0) ||
        left.index - right.index,
    )
    .map(({ item }) => item);

  return limit === undefined ? ranked : ranked.slice(0, limit);
}
