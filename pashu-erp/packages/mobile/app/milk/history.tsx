import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, DataTable } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, CARD_BORDER_RADIUS } from '../../src/config/theme';

// Mock weekly data for bar chart representation
const WEEKLY_DATA = [
  { day: 'Mon', liters: 10.5 },
  { day: 'Tue', liters: 11.2 },
  { day: 'Wed', liters: 9.8 },
  { day: 'Thu', liters: 12.5 },
  { day: 'Fri', liters: 11.0 },
  { day: 'Sat', liters: 10.3 },
  { day: 'Sun', liters: 12.0 },
];

const MOCK_HISTORY = [
  { date: '2026-04-07', animal: 'Lakshmi', session: 'morning', liters: 5.2 },
  { date: '2026-04-07', animal: 'Gowri', session: 'morning', liters: 4.8 },
  { date: '2026-04-07', animal: 'Lakshmi', session: 'evening', liters: 4.5 },
  { date: '2026-04-07', animal: 'Gowri', session: 'evening', liters: 4.0 },
  { date: '2026-04-06', animal: 'Lakshmi', session: 'morning', liters: 5.0 },
  { date: '2026-04-06', animal: 'Gowri', session: 'morning', liters: 4.5 },
  { date: '2026-04-06', animal: 'Lakshmi', session: 'evening', liters: 4.2 },
  { date: '2026-04-06', animal: 'Gowri', session: 'evening', liters: 3.8 },
];

const MAX_LITERS = Math.max(...WEEKLY_DATA.map((d) => d.liters));

export default function MilkHistoryScreen() {
  const { t } = useTranslation();
  const weeklyTotal = WEEKLY_DATA.reduce((sum, d) => sum + d.liters, 0);

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
      <Card style={styles.chartCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.chartTitle}>
            {t('income.weekly')} {t('milk.history')}
          </Text>
          <View style={styles.barChart}>
            {WEEKLY_DATA.map((d) => (
              <View key={d.day} style={styles.barColumn}>
                <Text variant="labelSmall" style={styles.barValue}>
                  {d.liters}
                </Text>
                <View
                  style={[
                    styles.bar,
                    { height: (d.liters / MAX_LITERS) * 120 },
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

      {/* History table */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('milk.history')}
      </Text>
      <Card style={styles.tableCard}>
        <DataTable>
          <DataTable.Header>
            <DataTable.Title>{'\uD83D\uDCC5'}</DataTable.Title>
            <DataTable.Title>{'\uD83D\uDC04'}</DataTable.Title>
            <DataTable.Title>{t('milk.session')}</DataTable.Title>
            <DataTable.Title numeric>{t('milk.liters')}</DataTable.Title>
          </DataTable.Header>
          {MOCK_HISTORY.map((entry, idx) => (
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
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
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
