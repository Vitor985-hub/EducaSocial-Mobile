import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Modal, Pressable, ScrollView, Text, View, StyleSheet } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useCatalog } from "@/hooks/catalog/useCatalog";
import { theme } from "@/styles/theme";
import {
  rankByPopularity,
  usePopularity,
} from "@/hooks/popularity/PopularityProvider";
import {
  categoryLabels,
  getProgramDetail,
  type ProgramCategory,
  type ProgramDetail,
  type ProgramSummary,
} from "@/services/catalog";
import { normalizeSearchText } from "@/utils/search";

type CardServiceProps = {
  categoryId?: ProgramCategory;
  stateCode?: string;
  initialServiceId?: number;
  limit?: number;
  searchQuery?: string;
};

function getCoverageLabel(service: ProgramSummary) {
  if (service.scope === "nacional") {
    return "Nacional";
  }
  if (service.scope === "estadual") {
    return `Estadual${service.state ? ` — ${service.state}` : ""}`;
  }
  return `Municipal${service.municipality ? ` — ${service.municipality}` : ""}${
    service.state ? ` (${service.state})` : ""
  }`;
}

export default function CardService({
  categoryId,
  stateCode,
  initialServiceId,
  limit,
  searchQuery = "",
}: CardServiceProps) {
  const { programs, loading, error, retry } = useCatalog();
  const { serviceCounts, recordServiceAccess } = usePopularity();
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedService, setSelectedService] = useState<ProgramSummary | null>(
    null,
  );
  const [selectedDetail, setSelectedDetail] = useState<ProgramDetail | null>(
    null,
  );
  const [detailLoading, setDetailLoading] = useState(Boolean(initialServiceId));
  const [detailError, setDetailError] = useState<string | null>(null);
  const detailRequestId = useRef(0);
  const initialServiceRequestedId = useRef<number | null>(null);
  const [dismissedInitialServiceId, setDismissedInitialServiceId] = useState<
    number | null
  >(null);
  const normalizedSearchQuery = normalizeSearchText(searchQuery);

  const visibleServices = useMemo(
    () =>
      programs.filter((service) => {
        const matchesCategory =
          categoryId === undefined || service.category === categoryId;
        const matchesState =
          stateCode === undefined ||
          service.scope === "nacional" ||
          service.state === stateCode;
        const matchesSearch =
          normalizedSearchQuery.length === 0 ||
          normalizeSearchText(`${service.name} ${service.summary}`).includes(
            normalizedSearchQuery,
          );

        return matchesCategory && matchesState && matchesSearch;
      }),
    [categoryId, normalizedSearchQuery, programs, stateCode],
  );
  const rankedServices = useMemo(
    () => rankByPopularity(visibleServices, serviceCounts, limit),
    [limit, serviceCounts, visibleServices],
  );
  const initialService = initialServiceId
    ? visibleServices.find((service) => service.id === initialServiceId)
    : undefined;
  const initialServiceIsOpen =
    Boolean(initialService) &&
    dismissedInitialServiceId !== initialServiceId;
  const displayedService =
    selectedService ?? (initialServiceIsOpen ? initialService ?? null : null);

  const requestDetails = useCallback((service: ProgramSummary) => {
    const requestId = detailRequestId.current + 1;
    detailRequestId.current = requestId;

    getProgramDetail(service.id)
      .then((detail) => {
        if (detailRequestId.current === requestId) {
          setSelectedDetail(detail);
        }
      })
      .catch((requestError: unknown) => {
        if (detailRequestId.current === requestId) {
          setDetailError(
            requestError instanceof Error
              ? requestError.message
              : "Não foi possível carregar os detalhes do serviço.",
          );
        }
      })
      .finally(() => {
        if (detailRequestId.current === requestId) {
          setDetailLoading(false);
        }
      });
  }, []);

  useEffect(() => {
    if (
      !initialService ||
      initialServiceRequestedId.current === initialService.id
    ) {
      return;
    }

    initialServiceRequestedId.current = initialService.id;
    requestDetails(initialService);
  }, [initialService, requestDetails]);

  const openService = useCallback(
    (service: ProgramSummary) => {
      setSelectedService(service);
      setSelectedDetail(null);
      setDetailError(null);
      setDetailLoading(true);
      setModalVisible(true);
      requestDetails(service);
    },
    [requestDetails],
  );

  function closeModal() {
    setModalVisible(false);
    if (initialServiceId) {
      setDismissedInitialServiceId(initialServiceId);
    }
  }

  if (loading) {
    return (
      <Text className="mt-5 text-center" style={styles.body}>
        Carregando serviços...
      </Text>
    );
  }

  if (error) {
    return (
      <View className="mt-5 items-center">
        <Text className="text-center" style={styles.error}>
          {error}
        </Text>
        <Pressable
          accessibilityRole="button"
          onPress={retry}
          className="mt-2 rounded-full px-4 py-2"
          style={styles.primaryButton}
        >
          <Text style={styles.primaryButtonLabel}>Tentar novamente</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View className="mt-5 flex-row flex-wrap justify-center gap-4">
      {visibleServices.length === 0 ? (
        <Text className="w-full text-center" style={styles.body}>
          {normalizedSearchQuery
            ? "Nenhum serviço encontrado para esta pesquisa."
            : "Nenhum serviço associado a esta seleção."}
        </Text>
      ) : (
        rankedServices.map((service) => (
          <Pressable
            key={service.id}
            accessibilityRole="button"
            accessibilityLabel={`Ver detalhes de ${service.name}`}
            onPress={() => {
              recordServiceAccess(service.id);
              openService(service);
            }}
            className="h-auto w-full rounded-3xl border-2 p-4 active:opacity-80"
            style={styles.serviceCard}
          >
            <Text
              className="mb-2"
              style={styles.serviceTitle}
              numberOfLines={1}
              ellipsizeMode="tail"
            >
              {service.name}
            </Text>
            <Text style={styles.serviceSummary} numberOfLines={3}>
              {service.summary}
            </Text>
            <Text className="mt-3" style={styles.serviceMeta}>
              {categoryLabels[service.category]} · {getCoverageLabel(service)}
            </Text>
          </Pressable>
        ))
      )}

      <Modal
        visible={modalVisible || initialServiceIsOpen}
        animationType="slide"
        onRequestClose={closeModal}
      >
        <SafeAreaView className="flex-1" style={styles.screen}>
          <ScrollView
            className="flex-1 px-5 pt-4"
            contentContainerStyle={{ paddingBottom: 40 }}
            showsVerticalScrollIndicator={false}
          >
            <Pressable
              accessibilityRole="button"
              onPress={closeModal}
              className="mb-5 flex-row items-center gap-3 py-2 active:opacity-70"
            >
              <View
                className="h-8 w-8 items-center justify-center rounded-full border-2"
                style={styles.backIconBorder}
              >
                <Text style={styles.backIcon}>
                  ←
                </Text>
              </View>
              <Text style={styles.backLabel}>
                Voltar a página anterior
              </Text>
            </Pressable>

            {displayedService && (
              <View
                className="rounded-3xl border p-6 shadow-sm"
                style={styles.detailCard}
              >
                <Text className="mb-2" style={styles.detailTitle}>
                  {displayedService.name}
                </Text>
                <Text className="mb-5" style={styles.detailMeta}>
                  {categoryLabels[displayedService.category]} ·{" "}
                  {getCoverageLabel(displayedService)}
                </Text>

                {detailLoading && (
                  <Text className="mb-4" style={styles.body}>
                    Carregando detalhes...
                  </Text>
                )}

                {detailError && (
                  <View
                    accessibilityRole="alert"
                    className="mb-5 rounded-2xl border p-4"
                    style={styles.errorCard}
                  >
                    <Text style={styles.error}>{detailError}</Text>
                    <Pressable
                      accessibilityRole="button"
                      onPress={() => {
                        setDetailLoading(true);
                        setDetailError(null);
                        requestDetails(displayedService);
                      }}
                      className="mt-2 self-start"
                    >
                      <Text style={styles.errorAction}>
                        Tentar novamente
                      </Text>
                    </Pressable>
                  </View>
                )}

                <Text className="mb-1" style={styles.sectionTitle}>
                  Descrição
                </Text>
                <Text className="mb-5" style={styles.body}>
                  {selectedDetail?.description ?? displayedService.summary}
                </Text>

                {selectedDetail && (
                  <>
                    <Text className="mb-1" style={styles.sectionTitle}>
                      Órgão responsável
                    </Text>
                    <Text className="mb-5" style={styles.body}>
                      {selectedDetail.managing_body}
                    </Text>

                    <Text className="mb-1" style={styles.sectionTitle}>
                      Elegibilidade
                    </Text>
                    {selectedDetail.eligibility.length > 0 ? (
                      <View className="mb-5 gap-1">
                        {selectedDetail.eligibility.map((item, index) => (
                          <Text
                            key={`${selectedDetail.id}-eligibility-${index}`}
                            style={styles.body}
                          >
                            • {item}
                          </Text>
                        ))}
                      </View>
                    ) : (
                      <Text className="mb-5" style={styles.body}>
                        Não informado.
                      </Text>
                    )}

                    <Text className="mb-1" style={styles.sectionTitle}>
                      Como solicitar
                    </Text>
                    <Text className="mb-5" style={styles.body}>
                      {selectedDetail.how_to_apply}
                    </Text>

                    {selectedDetail.official_url && (
                      <>
                        <Text className="mb-1" style={styles.sectionTitle}>
                          Link oficial
                        </Text>
                        <Text style={styles.link}>
                          {selectedDetail.official_url}
                        </Text>
                      </>
                    )}
                  </>
                )}
              </View>
            )}
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    backgroundColor: theme.colors.background,
  },
  body: {
    ...theme.typography.body,
    color: theme.colors.textSecondary,
  },
  error: {
    fontSize: theme.fontSizes.sm,
    color: theme.colors.error,
  },
  primaryButton: {
    backgroundColor: theme.colors.primary,
  },
  primaryButtonLabel: {
    ...theme.typography.button,
  },
  serviceCard: {
    backgroundColor: theme.colors.surface,
    borderColor: theme.colors.borderSubtle,
  },
  serviceTitle: {
    fontSize: theme.fontSizes.lg,
    lineHeight: theme.fontSizes.lg * 1.3,
    fontWeight: "500",
    color: theme.colors.textPrimary,
  },
  serviceSummary: {
    ...theme.typography.body,
    color: theme.colors.textSecondary,
  },
  serviceMeta: {
    fontSize: theme.fontSizes.xs,
    fontWeight: "600",
    color: theme.colors.primary,
  },
  detailCard: {
    backgroundColor: theme.colors.surface,
    borderColor: theme.colors.borderSubtle,
  },
  backIconBorder: {
    borderColor: theme.colors.primary,
  },
  backIcon: {
    fontSize: theme.fontSizes.md,
    fontWeight: "700",
    lineHeight: theme.fontSizes.md,
    color: theme.colors.primary,
  },
  backLabel: {
    fontSize: theme.fontSizes.md,
    fontWeight: "600",
    color: theme.colors.primary,
  },
  detailTitle: {
    fontSize: theme.typography.title.fontSize,
    lineHeight: theme.typography.title.lineHeight,
    fontWeight: theme.typography.title.fontWeight,
    color: theme.colors.textPrimary,
  },
  detailMeta: {
    fontSize: theme.fontSizes.sm,
    fontWeight: "600",
    color: theme.colors.textMuted,
  },
  errorCard: {
    backgroundColor: theme.colors.errorSurface,
    borderColor: theme.colors.error,
  },
  errorAction: {
    fontSize: theme.fontSizes.sm,
    fontWeight: "700",
    color: theme.colors.error,
  },
  sectionTitle: {
    fontSize: theme.fontSizes.md,
    fontWeight: "700",
    color: theme.colors.textPrimary,
  },
  link: {
    fontSize: theme.fontSizes.md,
    color: theme.colors.primary,
  },
});
