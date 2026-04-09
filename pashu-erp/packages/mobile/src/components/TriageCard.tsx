import React from 'react';
import { View, StyleSheet, Linking } from 'react-native';
import { Card, Text, Button } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import * as Speech from 'expo-speech';
import { SPACING, CARD_BORDER_RADIUS, statusColors } from '../config/theme';

type Severity = 'critical' | 'high' | 'medium' | 'low';

const SEVERITY_CONFIG: Record<Severity, { color: string; bgColor: string; icon: string }> = {
  critical: { color: statusColors.urgent, bgColor: statusColors.urgentBg, icon: 'alert-circle' },
  high: { color: '#E65100', bgColor: '#FFF3E0', icon: 'alert' },
  medium: { color: statusColors.watch, bgColor: statusColors.watchBg, icon: 'alert-outline' },
  low: { color: statusColors.healthy, bgColor: statusColors.healthyBg, icon: 'check-circle' },
};

interface TriageCardProps {
  severity: Severity;
  messageKey: string;  // was: message: string
  onCallVet?: () => void;
}

function TriageCardInner({ severity, messageKey, onCallVet }: TriageCardProps) {
  const { t } = useTranslation();
  const config = SEVERITY_CONFIG[severity];

  return (
    <Card style={[styles.card, { backgroundColor: config.bgColor }]}>
      <Card.Content>
        <View style={styles.header}>
          <View style={[styles.severityBadge, { backgroundColor: config.color }]}>
            <Text style={styles.severityText}>
              {t(`health.${severity}`)}
            </Text>
          </View>
        </View>
        <Text variant="bodyLarge" style={styles.message}>
          {t(messageKey)}
        </Text>
        <Button
          mode="text"
          icon="volume-high"
          onPress={() => Speech.speak(t(messageKey), { language: 'kn-IN' })}
          style={styles.listenButton}
          labelStyle={styles.listenLabel}
          textColor={config.color}
          accessibilityLabel={t('health.readAloud')}
        >
          {t('common.listen')}
        </Button>
        {(severity === 'critical' || severity === 'high') && onCallVet && (
          <Button
            mode="contained"
            onPress={onCallVet}
            style={styles.vetButton}
            contentStyle={styles.vetButtonContent}
            buttonColor={statusColors.urgent}
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
    marginVertical: SPACING.sm,
    borderRadius: CARD_BORDER_RADIUS,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
    marginBottom: SPACING.sm,
  },
  severityBadge: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
  },
  severityText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 15,
  },
  message: {
    marginBottom: SPACING.md,
    color: '#1A1A1A',
  },
  listenButton: {
    alignSelf: 'flex-start',
    marginTop: 0,
    marginBottom: 4,
  },
  listenLabel: {
    fontSize: 14,
  },
  vetButton: {
    marginTop: SPACING.sm,
    borderRadius: 12,
  },
  vetButtonContent: {
    height: 52,
  },
});

export const TriageCard = React.memo(TriageCardInner);
export type { Severity };
