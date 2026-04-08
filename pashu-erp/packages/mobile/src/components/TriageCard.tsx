import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, Button } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, CARD_BORDER_RADIUS } from '../config/theme';

type Severity = 'critical' | 'high' | 'medium' | 'low';

const SEVERITY_CONFIG: Record<Severity, { color: string; bgColor: string; icon: string }> = {
  critical: { color: '#D32F2F', bgColor: '#FFCDD2', icon: 'alert-circle' },
  high: { color: '#E65100', bgColor: '#FFE0B2', icon: 'alert' },
  medium: { color: '#F9A825', bgColor: '#FFF9C4', icon: 'alert-outline' },
  low: { color: '#2E7D32', bgColor: '#C8E6C9', icon: 'check-circle' },
};

interface TriageCardProps {
  severity: Severity;
  message: string;
  onCallVet?: () => void;
}

export function TriageCard({ severity, message, onCallVet }: TriageCardProps) {
  const { t } = useTranslation();
  const config = SEVERITY_CONFIG[severity];

  return (
    <Card style={[styles.card, { backgroundColor: config.bgColor }]}>
      <Card.Content>
        <View style={styles.header}>
          <Text variant="headlineSmall" style={[styles.severity, { color: config.color }]}>
            {t(`health.${severity}`)}
          </Text>
        </View>
        <Text variant="bodyLarge" style={styles.message}>
          {message}
        </Text>
        {(severity === 'critical' || severity === 'high') && onCallVet && (
          <Button
            mode="contained"
            onPress={onCallVet}
            style={styles.vetButton}
            buttonColor={config.color}
            textColor="#FFFFFF"
            icon="phone"
          >
            {t('health.callVet')}
          </Button>
        )}
      </Card.Content>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: SPACING.md,
    marginVertical: SPACING.sm,
    borderRadius: CARD_BORDER_RADIUS,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
    marginBottom: SPACING.sm,
  },
  severity: {
    fontWeight: 'bold',
    fontSize: 22,
  },
  message: {
    marginBottom: SPACING.md,
  },
  vetButton: {
    marginTop: SPACING.sm,
  },
});

export type { Severity };
