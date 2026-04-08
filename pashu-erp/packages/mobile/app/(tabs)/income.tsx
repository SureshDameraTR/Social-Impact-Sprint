import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, SegmentedButtons, Card, Button, Divider } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { EarningsHero } from '../../src/components/EarningsHero';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS } from '../../src/config/theme';

const MOCK_DATA = {
  weekly: { total: 3250, milk: 2100, sale: 1150 },
  monthly: { total: 14500, milk: 9200, sale: 5300 },
  yearly: { total: 168000, milk: 108000, sale: 60000 },
};

const MOCK_TRANSACTIONS = [
  { id: '1', desc: 'Milk - KMF', amount: 450, date: '2026-04-07', type: 'milk' },
  { id: '2', desc: 'Eggs - Market', amount: 210, date: '2026-04-06', type: 'sale' },
  { id: '3', desc: 'Milk - KMF', amount: 420, date: '2026-04-05', type: 'milk' },
  { id: '4', desc: 'Manure - Ravi Farm', amount: 300, date: '2026-04-04', type: 'sale' },
  { id: '5', desc: 'Milk - KMF', amount: 480, date: '2026-04-03', type: 'milk' },
  { id: '6', desc: 'Goat meat - Butcher', amount: 3500, date: '2026-04-01', type: 'sale' },
];

type Period = 'weekly' | 'monthly' | 'yearly';

export default function IncomeScreen() {
  const { t } = useTranslation();
  const [period, setPeriod] = useState<Period>('monthly');

  const data = MOCK_DATA[period];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      {/* Period selector */}
      <SegmentedButtons
        value={period}
        onValueChange={(v) => setPeriod(v as Period)}
        buttons={[
          { value: 'weekly', label: t('income.weekly') },
          { value: 'monthly', label: t('income.monthly') },
          { value: 'yearly', label: t('income.yearly') },
        ]}
        style={styles.segmented}
      />

      {/* Earnings hero */}
      <EarningsHero amount={data.total} period={period} />

      {/* Breakdown */}
      <View style={styles.breakdown}>
        <Card style={styles.breakdownCard}>
          <Card.Content style={styles.breakdownContent}>
            <Text style={styles.breakdownIcon}>{'\uD83E\uDD5B'}</Text>
            <Text variant="bodyLarge">{t('income.milkIncome')}</Text>
            <Text variant="titleMedium" style={styles.breakdownAmount}>
              {'\u20B9'}{data.milk.toLocaleString('en-IN')}
            </Text>
          </Card.Content>
        </Card>
        <Card style={styles.breakdownCard}>
          <Card.Content style={styles.breakdownContent}>
            <Text style={styles.breakdownIcon}>{'\uD83D\uDED2'}</Text>
            <Text variant="bodyLarge">{t('income.saleIncome')}</Text>
            <Text variant="titleMedium" style={styles.breakdownAmount}>
              {'\u20B9'}{data.sale.toLocaleString('en-IN')}
            </Text>
          </Card.Content>
        </Card>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <Button
          mode="outlined"
          icon="download"
          onPress={() => {}}
          style={styles.actionButton}
          contentStyle={styles.actionButtonContent}
        >
          {t('income.downloadRecord')}
        </Button>
        <Button
          mode="contained"
          icon="bank"
          onPress={() => {}}
          style={styles.actionButton}
          contentStyle={styles.actionButtonContent}
          buttonColor="#FF8F00"
        >
          {t('income.applyForLoan')}
        </Button>
      </View>

      {/* Transactions */}
      <Divider style={styles.divider} />
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('income.transactions')}
      </Text>
      {MOCK_TRANSACTIONS.length === 0 ? (
        <EmptyState
          icon={'\uD83D\uDCB0'}
          title={t('empty.noIncome')}
          subtitle={t('empty.startSelling')}
        />
      ) : (
        MOCK_TRANSACTIONS.map((tx) => (
          <Card key={tx.id} style={styles.txCard}>
            <Card.Content style={styles.txContent}>
              <View>
                <Text variant="titleSmall">{tx.desc}</Text>
                <Text variant="bodySmall" style={styles.txDate}>{tx.date}</Text>
              </View>
              <Text variant="titleMedium" style={styles.txAmount}>
                +{'\u20B9'}{tx.amount.toLocaleString('en-IN')}
              </Text>
            </Card.Content>
          </Card>
        ))
      )}
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
    paddingBottom: 100,
  },
  segmented: {
    marginBottom: SPACING.sm,
  },
  breakdown: {
    flexDirection: 'row',
    gap: SPACING.sm,
    marginTop: SPACING.lg,
  },
  breakdownCard: {
    flex: 1,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
  },
  breakdownContent: {
    alignItems: 'center',
    gap: SPACING.xs,
    paddingVertical: SPACING.md,
  },
  breakdownIcon: {
    fontSize: 32,
  },
  breakdownAmount: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  actions: {
    flexDirection: 'row',
    gap: SPACING.sm,
    marginTop: SPACING.lg,
  },
  actionButton: {
    flex: 1,
    borderRadius: 12,
  },
  actionButtonContent: {
    height: 48,
  },
  divider: {
    marginVertical: SPACING.lg,
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
  },
  txCard: {
    marginBottom: SPACING.sm,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
  },
  txContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  txDate: {
    color: '#9E9E9E',
    marginTop: 2,
  },
  txAmount: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
});
