import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING } from '../config/theme';

interface EarningsHeroProps {
  amount: number;
  period: string;
}

function EarningsHeroInner({ amount, period }: EarningsHeroProps) {
  const { t } = useTranslation();

  const formattedAmount = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);

  return (
    <View style={styles.container}>
      <View style={styles.gradient}>
        <Text variant="bodyLarge" style={styles.label}>
          {t('income.totalEarnings')} ({t(`income.${period}`)})
        </Text>
        <Text style={styles.amount}>
          {formattedAmount}
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          {t('income.earnings')}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: SPACING.md,
    borderRadius: 24,
    overflow: 'hidden',
    shadowColor: '#1B6B4A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 6,
  },
  gradient: {
    alignItems: 'center',
    paddingVertical: SPACING.xl,
    paddingHorizontal: SPACING.md,
    backgroundColor: '#1B6B4A',
  },
  label: {
    color: '#A8F5C8',
    marginBottom: SPACING.xs,
  },
  amount: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 48,
    lineHeight: 56,
  },
  subtitle: {
    color: '#A8F5C8',
    marginTop: SPACING.xs,
    opacity: 0.9,
  },
});

export const EarningsHero = React.memo(EarningsHeroInner);
