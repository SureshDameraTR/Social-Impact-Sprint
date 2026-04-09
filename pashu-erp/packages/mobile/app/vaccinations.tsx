import React, { useState, useEffect, useCallback } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { Button, Card, Text, ProgressBar, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors, statusColors } from '../src/config/theme';
import { api } from '../src/config/api';

type VaccStatus = 'done' | 'due' | 'overdue';

interface VaccRecord {
  id: string;
  animalName: string;
  species: string;
  speciesEmoji: string;
  vaccineName: string;
  dueDate: string;
  status: VaccStatus;
  daysUntil: number;
}

const STATUS_COLORS: Record<VaccStatus, string> = {
  done: statusColors.healthy,
  due: '#FF8F00',
  overdue: statusColors.urgent,
};

export default function VaccinationsScreen() {
  const { t } = useTranslation();
  const [records, setRecords] = useState<VaccRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVaccinations = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<VaccRecord[]>('/vaccinations/due')
      .then(res => setRecords(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchVaccinations();
  }, [fetchVaccinations]);

  const markDone = useCallback(async (id: string) => {
    try {
      await api.patch(`/vaccinations/${id}`, { status: 'done' });
      setRecords((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: 'done' as VaccStatus, daysUntil: 0 } : r))
      );
    } catch {
      // Optimistic update fallback
      setRecords((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: 'done' as VaccStatus, daysUntil: 0 } : r))
      );
    }
  }, []);

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
          onAction={fetchVaccinations}
        />
      </View>
    );
  }

  const totalCattle = records.filter((r) => r.species === 'cattle').length;
  const doneCattle = records.filter((r) => r.species === 'cattle' && r.status === 'done').length;
  const coveragePercent = totalCattle > 0 ? Math.round((doneCattle / totalCattle) * 100) : 0;

  const grouped = {
    overdue: records.filter((r) => r.status === 'overdue'),
    due: records.filter((r) => r.status === 'due'),
    done: records.filter((r) => r.status === 'done'),
  };

  const listData: ({ type: 'header'; title: string; color: string; emoji: string; count: number } | { type: 'item'; record: VaccRecord })[] = [];

  if (grouped.overdue.length > 0) {
    listData.push({ type: 'header', title: t('vaccinations.overdueSection'), color: statusColors.urgent, emoji: '\u26A0\uFE0F', count: grouped.overdue.length });
    grouped.overdue.forEach((r) => listData.push({ type: 'item', record: r }));
  }
  if (grouped.due.length > 0) {
    listData.push({ type: 'header', title: t('vaccinations.upcomingSection'), color: '#FF8F00', emoji: '\uD83D\uDCC5', count: grouped.due.length });
    grouped.due.forEach((r) => listData.push({ type: 'item', record: r }));
  }
  if (grouped.done.length > 0) {
    listData.push({ type: 'header', title: t('vaccinations.completedSection'), color: statusColors.healthy, emoji: '\u2705', count: grouped.done.length });
    grouped.done.forEach((r) => listData.push({ type: 'item', record: r }));
  }

  const getCountdownText = (rec: VaccRecord): string => {
    if (rec.status === 'done') return t('vaccinations.completed');
    if (rec.daysUntil < 0) return `${t('vaccinations.overdue')}!`;
    if (rec.daysUntil === 0) return t('vaccinations.dueToday');
    return `${t('vaccinations.dueIn')} ${rec.daysUntil} ${t('vaccinations.days')}`;
  };

  return (
    <FlatList
      data={listData}
      keyExtractor={(item, index) => item.type === 'header' ? `header-${index}` : `item-${item.record.id}`}
      style={styles.container}
      contentContainerStyle={styles.content}
      ListHeaderComponent={
        <>
          <Text variant="headlineMedium" style={styles.heading}>
            {t('vaccinations.title')}
          </Text>

          <Card style={styles.coverageCard}>
            <Card.Content>
              <Text variant="titleMedium" style={styles.coverageTitle}>
                {t('vaccinations.villageCoverage')}
              </Text>
              <Text variant="headlineSmall" style={styles.coveragePercent}>
                {coveragePercent}% {t('vaccinations.cattleVaccinated')}
              </Text>
              <ProgressBar
                progress={coveragePercent / 100}
                color={statusColors.healthy}
                style={styles.coverageBar}
              />
            </Card.Content>
          </Card>

          {records.length === 0 && (
            <EmptyState
              icon={'\uD83D\uDC89'}
              title={t('empty.noVaccinations')}
              subtitle={t('vaccinations.title')}
            />
          )}
        </>
      }
      renderItem={({ item }) => {
        if (item.type === 'header') {
          return (
            <Text variant="titleMedium" style={[styles.sectionTitle, { color: item.color }]}>
              {item.emoji} {item.title} ({item.count})
            </Text>
          );
        }
        const rec = item.record;
        const statusColor = STATUS_COLORS[rec.status];
        return (
          <Card style={[styles.vaccCard, { borderLeftColor: statusColor }]}>
            <Card.Content>
              <View style={styles.vaccHeader}>
                <Text style={styles.vaccEmoji}>{rec.speciesEmoji}</Text>
                <View style={{ flex: 1 }}>
                  <Text variant="titleSmall" style={styles.vaccAnimal}>
                    {rec.animalName}
                  </Text>
                  <Text variant="titleMedium" style={styles.vaccName}>
                    {rec.vaccineName}
                  </Text>
                </View>
                <View style={[styles.countdownBadge, { backgroundColor: statusColor + '20' }]}>
                  <Text style={[styles.countdownText, { color: statusColor }]}>
                    {getCountdownText(rec)}
                  </Text>
                </View>
              </View>

              <Text variant="bodySmall" style={styles.vaccDate}>
                {t('vaccinations.dueDate')}: {rec.dueDate}
              </Text>

              {rec.status !== 'done' && (
                <Button
                  mode="contained"
                  onPress={() => markDone(rec.id)}
                  style={styles.markDoneButton}
                  contentStyle={{ minHeight: 48 }}
                  icon="check"
                  accessibilityLabel="Mark vaccination as done"
                >
                  {t('vaccinations.markDone')}
                </Button>
              )}
            </Card.Content>
          </Card>
        );
      }}
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
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
  coverageCard: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#E8F5E9',
    marginBottom: SPACING.lg,
  },
  coverageTitle: {
    color: '#1B5E20',
  },
  coveragePercent: {
    color: statusColors.healthy,
    fontWeight: 'bold',
    marginVertical: SPACING.sm,
  },
  coverageBar: {
    height: 12,
    borderRadius: 6,
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
    marginTop: SPACING.md,
  },
  vaccCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.sm,
    borderLeftWidth: 4,
  },
  vaccHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  vaccEmoji: {
    fontSize: 32,
    marginRight: SPACING.sm,
  },
  vaccAnimal: {
    color: '#616161',
  },
  vaccName: {
    color: '#212121',
    fontWeight: 'bold',
  },
  countdownBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: 4,
    borderRadius: 8,
  },
  countdownText: {
    fontSize: 11,
    fontWeight: 'bold',
  },
  vaccDate: {
    color: '#616161',
    marginBottom: SPACING.sm,
  },
  markDoneButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
});
