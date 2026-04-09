import React, { useState, useEffect, useCallback } from 'react';
import { View, FlatList, StyleSheet, StatusBar, Linking, Alert } from 'react-native';
import { Text, Button, Card, Divider, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { EarningsHero } from '../../src/components/EarningsHero';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, colors } from '../../src/config/theme';
import { api } from '../../src/config/api';

interface IncomeSummary {
  total: number;
  milk: number;
  sale: number;
}

interface Transaction {
  id: string;
  desc: string;
  amount: number;
  date: string;
  type: string;
  icon: string;
}

type Period = 'weekly' | 'monthly' | 'yearly';

export default function IncomeScreen() {
  const { t } = useTranslation();
  const [period, setPeriod] = useState<Period>('monthly');
  const [summary, setSummary] = useState<IncomeSummary | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    const periodParam = period === 'weekly' ? 'week' : period === 'monthly' ? 'month' : 'year';
    Promise.all([
      api.get<any>(`/income/summary?period=${periodParam}`),
      api.get<any>(`/income/transactions?period=${periodParam}`),
    ])
      .then(([summaryData, txResponse]) => {
        setSummary({
          total: summaryData.total_income ?? 0,
          milk: summaryData.transaction_income ?? 0,
          sale: summaryData.marketplace_income ?? 0,
        });
        const txData = Array.isArray(txResponse) ? txResponse : txResponse.data ?? [];
        setTransactions(txData.map((tx: any, idx: number) => ({
          id: tx.id ?? String(idx),
          desc: tx.description ?? tx.category ?? '',
          amount: Math.abs(tx.amount ?? 0),
          date: tx.date ? new Date(tx.date).toLocaleDateString('en-IN') : (tx.created_at ? new Date(tx.created_at).toLocaleDateString('en-IN') : ''),
          type: tx.type ?? 'income',
          icon: tx.type === 'expense' ? '\uD83D\uDCB8' : '\uD83D\uDCB0',
        })));
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [period]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handlePeriodChange = useCallback((p: Period) => {
    setPeriod(p);
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
          onAction={fetchData}
        />
      </View>
    );
  }

  const data = summary || { total: 0, milk: 0, sale: 0 };
  const milkPct = data.total > 0 ? Math.round((data.milk / data.total) * 100) : 0;
  const salePct = data.total > 0 ? 100 - milkPct : 0;

  const renderTransaction = useCallback(({ item: tx }: { item: Transaction }) => (
    <Card
      style={styles.txCard}
      accessible={true}
      accessibilityLabel={`${tx.desc}, ${t('income.earnings')} \u20B9${tx.amount.toLocaleString('en-IN')}, ${tx.date}`}
    >
      <Card.Content style={styles.txContent}>
        <View style={styles.txLeft}>
          <Text style={styles.txIcon}>{tx.icon}</Text>
          <View>
            <Text variant="titleSmall" style={styles.txDesc}>{tx.desc}</Text>
            <Text variant="bodySmall" style={styles.txDate}>{tx.date}</Text>
          </View>
        </View>
        <Text variant="titleMedium" style={styles.txAmount}>
          +{'\u20B9'}{tx.amount.toLocaleString('en-IN')}
        </Text>
      </Card.Content>
    </Card>
  ), [t]);

  return (
    <FlatList
      data={transactions}
      keyExtractor={(item) => item.id}
      renderItem={renderTransaction}
      style={styles.container}
      contentContainerStyle={styles.scroll}
      ListHeaderComponent={
        <>
          <StatusBar barStyle="dark-content" backgroundColor="#F5F5F0" />

          {/* Period selector pills */}
          <View style={styles.periodContainer}>
            {(['weekly', 'monthly', 'yearly'] as Period[]).map((p) => (
              <Button
                key={p}
                mode={period === p ? 'contained' : 'outlined'}
                onPress={() => handlePeriodChange(p)}
                style={[styles.periodPill, period === p && styles.periodPillActive]}
                labelStyle={[styles.periodLabel, period === p && styles.periodLabelActive]}
                buttonColor={period === p ? colors.primary : undefined}
                textColor={period === p ? '#FFFFFF' : '#414941'}
                compact
                accessibilityLabel={t(`income.${p}`)}
                accessibilityRole="radio"
                accessibilityState={{ checked: period === p }}
              >
                {t(`income.${p}`)}
              </Button>
            ))}
          </View>

          {/* Earnings hero */}
          <EarningsHero amount={data.total} period={period} />

          {/* Breakdown with horizontal bars */}
          <View style={styles.breakdown}>
            <Card style={styles.breakdownCard}>
              <Card.Content style={styles.breakdownContent}>
                <View style={styles.breakdownRow}>
                  <Text style={styles.breakdownIcon}>{'\uD83E\uDD5B'}</Text>
                  <View style={styles.breakdownInfo}>
                    <View style={styles.breakdownHeader}>
                      <Text variant="bodyMedium" style={styles.breakdownLabel}>{t('income.milkIncome')}</Text>
                      <Text variant="titleSmall" style={styles.breakdownAmount}>
                        {'\u20B9'}{data.milk.toLocaleString('en-IN')}
                      </Text>
                    </View>
                    <View style={styles.barBg}>
                      <View style={[styles.barFill, { width: `${milkPct}%`, backgroundColor: colors.primary }]} />
                    </View>
                  </View>
                </View>
                <View style={[styles.breakdownRow, { marginTop: SPACING.md }]}>
                  <Text style={styles.breakdownIcon}>{'\uD83D\uDED2'}</Text>
                  <View style={styles.breakdownInfo}>
                    <View style={styles.breakdownHeader}>
                      <Text variant="bodyMedium" style={styles.breakdownLabel}>{t('income.saleIncome')}</Text>
                      <Text variant="titleSmall" style={styles.breakdownAmount}>
                        {'\u20B9'}{data.sale.toLocaleString('en-IN')}
                      </Text>
                    </View>
                    <View style={styles.barBg}>
                      <View style={[styles.barFill, { width: `${salePct}%`, backgroundColor: '#E65100' }]} />
                    </View>
                  </View>
                </View>
              </Card.Content>
            </Card>
          </View>

          {/* Actions */}
          <View style={styles.actions}>
            <Button
              mode="outlined"
              icon="download"
              onPress={() => Alert.alert(t('income.downloadRecord'), 'Download feature coming soon')}
              style={styles.actionButton}
              contentStyle={styles.actionButtonContent}
              textColor={colors.primary}
              accessibilityLabel={t('income.downloadRecord')}
              accessibilityRole="button"
            >
              {t('income.downloadRecord')}
            </Button>
          </View>

          {/* Loan CTA card */}
          <Card style={styles.loanCard}>
            <Card.Content style={styles.loanContent}>
              <View>
                <Text variant="titleMedium" style={styles.loanTitle}>
                  {t('income.applyForLoan')}
                </Text>
                <Text variant="bodySmall" style={styles.loanSubtitle}>
                  {t('income.kisanCreditCardLabel')}
                </Text>
              </View>
              <Button
                mode="contained"
                onPress={() => Linking.openURL('https://www.pmkisan.gov.in/')}
                buttonColor="#FFFFFF"
                textColor="#E65100"
                compact
                style={styles.loanButton}
                accessibilityLabel={t('income.applyNow')}
              >
                {t('income.applyNow')}
              </Button>
            </Card.Content>
          </Card>

          {/* Transactions header */}
          <Divider style={styles.divider} />
          <Text variant="titleMedium" style={styles.sectionTitle}>
            {t('income.transactions')}
          </Text>
          {transactions.length === 0 && (
            <EmptyState
              icon={'\uD83D\uDCB0'}
              title={t('empty.noIncome')}
              subtitle={t('empty.startSelling')}
            />
          )}
        </>
      }
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F0',
  },
  scroll: {
    padding: SPACING.md,
    paddingBottom: 100,
  },
  periodContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: SPACING.sm,
    marginBottom: SPACING.xs,
  },
  periodPill: {
    borderRadius: 20,
    borderColor: '#C1C9BF',
  },
  periodPillActive: {
    borderColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  periodLabel: {
    fontSize: 14,
  },
  periodLabelActive: {
    fontWeight: '700',
  },
  breakdown: {
    marginTop: SPACING.lg,
  },
  breakdownCard: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 6,
    elevation: 2,
  },
  breakdownContent: {
    paddingVertical: SPACING.md,
  },
  breakdownRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm + 4,
  },
  breakdownIcon: {
    fontSize: 28,
  },
  breakdownInfo: {
    flex: 1,
  },
  breakdownHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  breakdownLabel: {
    color: '#414941',
  },
  breakdownAmount: {
    color: '#1A1A1A',
    fontWeight: '700',
  },
  barBg: {
    height: 8,
    borderRadius: 4,
    backgroundColor: '#DCE5DB',
    overflow: 'hidden',
  },
  barFill: {
    height: 8,
    borderRadius: 4,
  },
  actions: {
    flexDirection: 'row',
    gap: SPACING.sm,
    marginTop: SPACING.lg,
  },
  actionButton: {
    flex: 1,
    borderRadius: 12,
    borderColor: colors.primary,
  },
  actionButtonContent: {
    height: 48,
  },
  loanCard: {
    marginTop: SPACING.md,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#E65100',
    shadowColor: '#E65100',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  loanContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  loanTitle: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  loanSubtitle: {
    color: 'rgba(255,255,255,0.8)',
    marginTop: 2,
  },
  loanButton: {
    borderRadius: 12,
  },
  divider: {
    marginVertical: SPACING.lg,
    backgroundColor: '#C1C9BF',
  },
  sectionTitle: {
    fontWeight: '700',
    marginBottom: SPACING.sm,
    color: '#1A1A1A',
  },
  txCard: {
    marginBottom: SPACING.sm + 2,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  txContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  txLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm + 4,
  },
  txIcon: {
    fontSize: 28,
  },
  txDesc: {
    color: '#1A1A1A',
  },
  txDate: {
    color: '#717971',
    marginTop: 2,
  },
  txAmount: {
    color: colors.primary,
    fontWeight: '700',
  },
});
