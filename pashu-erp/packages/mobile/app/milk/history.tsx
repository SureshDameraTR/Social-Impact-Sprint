import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, DataTable, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, colors } from '../../src/config/theme';
import { api } from '../../src/config/api';

interface WeeklyDataPoint {
  day: string;
  liters: number;
}

interface HistoryEntry {
  date: string;
  animal: string;
  session: string;
  liters: number;
}

interface MilkHistoryResponse {
  weekly: WeeklyDataPoint[];
  records: HistoryEntry[];
}

export default function MilkHistoryScreen() {
  const { t } = useTranslation();
  const [weeklyData, setWeeklyData] = useState<WeeklyDataPoint[]>([]);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<MilkHistoryResponse>('/milk/history')
      .then(res => {
        setWeeklyData(res.weekly || []);
        setHistory(res.records || []);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#2E7D32" />
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
          onAction={fetchHistory}
        />
      </View>
    );
  }

  const maxLiters = weeklyData.length > 0 ? Math.max(...weeklyData.map((d) => d.liters)) : 1;
  const weeklyTotal = weeklyData.reduce((sum, d) => sum + d.liters, 0);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      <Text variant="headlineSmall" style={styles.heading}>
        {t('milk.history')}
      </Text>

      {/* Weekly total */}
      <Card style={styles.totalCard}>
        <Card.Content style={styles.totalContent}>
          <Text variant="bodyLarge" style={styles.totalLabel}>
            {t('income.weekly')} {t('sell.total')}
          </Text>
          <Text variant="displaySmall" style={styles.totalAmount}>
            {weeklyTotal.toFixed(1)} {t('milk.liters')}
          </Text>
        </Card.Content>
      </Card>

      {/* Simple bar chart using View heights */}
      {weeklyData.length > 0 && (
        <Card style={styles.chartCard}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.chartTitle}>
              {t('income.weekly')} {t('milk.history')}
            </Text>
            <View style={styles.barChart}>
              {weeklyData.map((d) => (
                <View key={d.day} style={styles.barColumn}>
                  <Text variant="labelSmall" style={styles.barValue}>
                    {d.liters}
                  </Text>
                  <View
                    style={[
                      styles.bar,
                      { height: (d.liters / maxLiters) * 120 },
                    ]}
                  />
                  <Text variant="labelSmall" style={styles.barLabel}>
                    {d.day}
                  </Text>
                </View>
              ))}
            </View>
          </Card.Content>
        </Card>
      )}

      {/* History table */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('milk.history')}
      </Text>

      {history.length === 0 ? (
        <EmptyState
          icon={'\uD83E\uDD5B'}
          title={t('empty.noMilkRecords')}
          subtitle={t('milk.recordMilk')}
        />
      ) : (
        <Card style={styles.tableCard}>
          <DataTable>
            <DataTable.Header>
              <DataTable.Title>{'\uD83D\uDCC5'}</DataTable.Title>
              <DataTable.Title>{'\uD83D\uDC04'}</DataTable.Title>
              <DataTable.Title>{t('milk.session')}</DataTable.Title>
              <DataTable.Title numeric>{t('milk.liters')}</DataTable.Title>
            </DataTable.Header>
            {history.map((entry, idx) => (
              <DataTable.Row key={idx}>
                <DataTable.Cell>{entry.date.slice(5)}</DataTable.Cell>
                <DataTable.Cell>{entry.animal}</DataTable.Cell>
                <DataTable.Cell>
                  {entry.session === 'morning' ? `\u2600\uFE0F ${t('milk.morning')}` : `\uD83C\uDF19 ${t('milk.evening')}`}
                </DataTable.Cell>
                <DataTable.Cell numeric>{entry.liters}</DataTable.Cell>
              </DataTable.Row>
            ))}
          </DataTable>
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  scroll: {
    padding: SPACING.md,
    paddingBottom: 40,
  },
  heading: {
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: SPACING.md,
  },
  totalCard: {
    backgroundColor: '#2E7D32',
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.lg,
  },
  totalContent: {
    alignItems: 'center',
    paddingVertical: SPACING.lg,
  },
  totalLabel: {
    color: '#C8E6C9',
  },
  totalAmount: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  chartCard: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
    marginBottom: SPACING.lg,
  },
  chartTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
  barChart: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'flex-end',
    height: 160,
    paddingTop: 20,
  },
  barColumn: {
    alignItems: 'center',
    gap: 4,
  },
  bar: {
    width: 28,
    backgroundColor: '#2E7D32',
    borderRadius: 4,
    minHeight: 4,
  },
  barValue: {
    color: '#616161',
    fontSize: 11,
  },
  barLabel: {
    color: '#9E9E9E',
    fontWeight: '600',
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
  },
  tableCard: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
  },
});
