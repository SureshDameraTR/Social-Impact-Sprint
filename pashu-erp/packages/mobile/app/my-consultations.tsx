import React, { useState, useEffect, useCallback } from 'react';
import { View, FlatList, StyleSheet, Linking } from 'react-native';
import { Button, Card, Text, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors, statusColors } from '../src/config/theme';
import { api } from '../src/config/api';

type ConsultationStatus = 'pending' | 'in_review' | 'diagnosed' | 'closed';

interface Consultation {
  id: string;
  animal_name: string;
  species: string;
  status: ConsultationStatus;
  notes: string;
  created_at: string;
  diagnosis?: string;
  prescription?: string;
  follow_up_date?: string;
  video_call_url?: string;
}

const SPECIES_EMOJI: Record<string, string> = {
  cattle: '\uD83D\uDC04',
  goat: '\uD83D\uDC10',
  sheep: '\uD83D\uDC11',
  poultry: '\uD83D\uDC14',
};

const STATUS_COLORS: Record<ConsultationStatus, string> = {
  pending: '#FF8F00',
  in_review: '#1565C0',
  diagnosed: statusColors.healthy,
  closed: '#757575',
};

const STATUS_BG: Record<ConsultationStatus, string> = {
  pending: '#FFF8E1',
  in_review: '#E3F2FD',
  diagnosed: '#E8F5E9',
  closed: '#F5F5F5',
};

export default function MyConsultationsScreen() {
  const { t } = useTranslation();
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchConsultations = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<Consultation[]>('/vet/my-cases')
      .then(res => setConsultations(Array.isArray(res) ? res : (res as any).data ?? []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    setError(null);
    api.get<Consultation[]>('/vet/my-cases')
      .then(res => setConsultations(Array.isArray(res) ? res : (res as any).data ?? []))
      .catch(err => setError(err.message))
      .finally(() => setRefreshing(false));
  }, []);

  useEffect(() => {
    fetchConsultations();
  }, [fetchConsultations]);

  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const getStatusKey = (status: ConsultationStatus): string => {
    const map: Record<ConsultationStatus, string> = {
      pending: 'pending',
      in_review: 'inReview',
      diagnosed: 'diagnosed',
      closed: 'closed',
    };
    return map[status];
  };

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <EmptyState
          icon={'\u26A0\uFE0F'}
          title={t('common.error')}
          subtitle={error}
          actionLabel={t('common.retry')}
          onAction={fetchConsultations}
        />
      </View>
    );
  }

  const renderItem = ({ item }: { item: Consultation }) => {
    const statusColor = STATUS_COLORS[item.status];
    const statusBg = STATUS_BG[item.status];
    const emoji = SPECIES_EMOJI[item.species] || '\uD83D\uDC3E';

    return (
      <Card style={[styles.card, { borderLeftColor: statusColor }]}>
        <Card.Content>
          {/* Top row: animal + status badge */}
          <View style={styles.cardHeader}>
            <Text style={styles.speciesEmoji}>{emoji}</Text>
            <View style={{ flex: 1 }}>
              <Text variant="titleMedium" style={styles.animalName}>
                {item.animal_name}
              </Text>
            </View>
            <View style={[styles.statusBadge, { backgroundColor: statusBg }]}>
              <Text style={[styles.statusText, { color: statusColor }]}>
                {t(`consultations.${getStatusKey(item.status)}`)}
              </Text>
            </View>
          </View>

          {/* Farmer notes */}
          {item.notes ? (
            <Text variant="bodyMedium" style={styles.notes} numberOfLines={2}>
              {item.notes}
            </Text>
          ) : null}

          {/* Date */}
          <Text variant="bodySmall" style={styles.dateText}>
            {t('consultations.submitted')} {formatDate(item.created_at)}
          </Text>

          {/* Diagnosis details (diagnosed or closed) */}
          {(item.status === 'diagnosed' || item.status === 'closed') && (
            <View style={styles.diagnosisSection}>
              {item.diagnosis ? (
                <Text variant="bodyMedium" style={styles.diagnosisRow}>
                  <Text style={styles.diagnosisLabel}>{t('consultations.diagnosis')}: </Text>
                  {item.diagnosis}
                </Text>
              ) : null}
              {item.prescription ? (
                <Text variant="bodyMedium" style={styles.diagnosisRow}>
                  <Text style={styles.diagnosisLabel}>{t('consultations.prescription')}: </Text>
                  {item.prescription}
                </Text>
              ) : null}
              {item.follow_up_date ? (
                <Text variant="bodyMedium" style={styles.diagnosisRow}>
                  <Text style={styles.diagnosisLabel}>{t('consultations.followUp')}: </Text>
                  {formatDate(item.follow_up_date)}
                </Text>
              ) : null}
            </View>
          )}

          {/* Video call button */}
          {item.video_call_url ? (
            <Button
              mode="contained"
              icon="video"
              onPress={() => Linking.openURL(item.video_call_url!)}
              style={styles.videoCallButton}
              contentStyle={{ minHeight: TOUCH_TARGET_MIN }}
              buttonColor={colors.primary}
              accessibilityLabel={t('consultations.joinVideoCall')}
            >
              {t('consultations.joinVideoCall')}
            </Button>
          ) : null}

          {/* Pending message */}
          {item.status === 'pending' && (
            <Text variant="bodySmall" style={styles.pendingMessage}>
              {t('consultations.pendingMessage')}
            </Text>
          )}
        </Card.Content>
      </Card>
    );
  };

  return (
    <FlatList
      data={consultations}
      keyExtractor={(item) => item.id}
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshing={refreshing}
      onRefresh={handleRefresh}
      ListHeaderComponent={
        <Text variant="headlineMedium" style={styles.heading}>
          {t('consultations.title')}
        </Text>
      }
      renderItem={renderItem}
      ListEmptyComponent={
        <EmptyState
          icon={'\uD83D\uDC68\u200D\u2695\uFE0F'}
          title={t('consultations.empty')}
          subtitle={t('consultations.emptySubtitle')}
          actionLabel={t('consultations.sendPhoto')}
          onAction={() => router.push('/vet-photo')}
        />
      }
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  content: {
    padding: SPACING.md,
    paddingBottom: 100,
  },
  heading: {
    color: colors.primary,
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
  card: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
    borderLeftWidth: 4,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  speciesEmoji: {
    fontSize: 32,
    marginRight: SPACING.sm,
  },
  animalName: {
    fontWeight: 'bold',
    color: '#212121',
  },
  statusBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  notes: {
    color: '#424242',
    marginBottom: SPACING.sm,
  },
  dateText: {
    color: '#616161',
    marginBottom: SPACING.sm,
  },
  diagnosisSection: {
    marginTop: SPACING.sm,
    padding: SPACING.sm,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    gap: 4,
  },
  diagnosisRow: {
    color: '#212121',
  },
  diagnosisLabel: {
    fontWeight: 'bold',
  },
  videoCallButton: {
    marginTop: SPACING.md,
    borderRadius: CARD_BORDER_RADIUS,
  },
  pendingMessage: {
    color: '#9E9E9E',
    fontStyle: 'italic',
    marginTop: SPACING.sm,
  },
});
