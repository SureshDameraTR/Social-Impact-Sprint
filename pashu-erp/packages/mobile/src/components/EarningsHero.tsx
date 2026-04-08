import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING } from '../config/theme';

interface EarningsHeroProps {
  amount: number;
  period: string;
}

export function EarningsHero({ amount, period }: EarningsHeroProps) {
  const { t } = useTranslation();

  const formattedAmount = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);

  return (
    <View style={styles.container}>
      <Text variant="bodyLarge" style={styles.label}>
        {t('income.totalEarnings')} ({t(`income.${period}`)})
      </Text>
      <Text variant="displayMedium" style={styles.amount}>
        {formattedAmount}
      </Text>
      <Text variant="bodyMedium" style={styles.subtitle}>
        {t('income.earnings')}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: SPACING.xl,
    paddingHorizontal: SPACING.md,
    backgroundColor: '#2E7D32',
    borderRadius: 24,
    marginHorizontal: SPACING.md,
    marginTop: SPACING.md,
  },
  label: {
    color: '#C8E6C9',
    marginBottom: SPACING.xs,
  },
  amount: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 48,
  },
  subtitle: {
    color: '#A5D6A7',
    marginTop: SPACING.xs,
  },
});
