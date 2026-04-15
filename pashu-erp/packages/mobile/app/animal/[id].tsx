import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet, Alert } from 'react-native';
import { Text, Card, Button, Divider, ActivityIndicator } from 'react-native-paper';
import { useLocalSearchParams, router } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SpeciesIcon } from '../../src/components/SpeciesIcon';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, statusColors, colors } from '../../src/config/theme';
import { api } from '../../src/config/api';
import type { Species } from '../../src/components/SpeciesIcon';

interface AnimalDetail {
  name: string;
  species: Species;
  breed: string;
  tagNumber: string;
  pashuAadhaar: string;
  age: string;
  weight: string;
  gender: string;
  healthStatus: string;
  lastMilk: string;
  lastVaccination: string;
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.detailRow}>
      <Text variant="bodyMedium" style={styles.detailLabel}>{label}</Text>
      <Text variant="bodyLarge" style={styles.detailValue}>{value}</Text>
    </View>
  );
}

export default function AnimalDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { t } = useTranslation();
  const [animal, setAnimal] = useState<AnimalDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnimal = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<AnimalDetail>(`/animals/${id}`)
      .then(res => setAnimal(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    fetchAnimal();
  }, [fetchAnimal]);

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
          onAction={fetchAnimal}
        />
      </View>
    );
  }

  if (!animal) {
    return (
      <View style={styles.container}>
        <EmptyState
          icon={'\uD83D\uDC04'}
          title={t('common.noData')}
          subtitle={t('animals.myAnimals')}
        />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      {/* Hero */}
      <View style={styles.hero}>
        <SpeciesIcon species={animal.species} size={80} />
        <Text variant="headlineMedium" style={styles.name}>{animal.name}</Text>
        <View style={[
          styles.healthBadge,
          { backgroundColor: animal.healthStatus === 'healthy' ? '#C8E6C9' : '#FFCDD2' },
        ]}>
          <Text style={[
            styles.healthText,
            { color: animal.healthStatus === 'healthy' ? statusColors.healthy : statusColors.urgent },
          ]}>
            {t(`animals.${animal.healthStatus}`)}
          </Text>
        </View>
      </View>

      {/* Details card */}
      <Card style={styles.card}>
        <Card.Content>
          <DetailRow label={t('animals.species')} value={t(`animals.${animal.species}`)} />
          <Divider style={styles.rowDivider} />
          <DetailRow label={t('animals.breed')} value={animal.breed} />
          <Divider style={styles.rowDivider} />
          <DetailRow label={t('animals.tagNumber')} value={animal.tagNumber} />
          <Divider style={styles.rowDivider} />
          <DetailRow label={t('animals.pashuAadhaar')} value={animal.pashuAadhaar} />
          <Divider style={styles.rowDivider} />
          <DetailRow label={t('animals.age')} value={animal.age} />
          <Divider style={styles.rowDivider} />
          <DetailRow label={t('animals.weight')} value={animal.weight} />
          <Divider style={styles.rowDivider} />
          <DetailRow label={t('animals.gender')} value={t(`animals.${animal.gender}`)} />
        </Card.Content>
      </Card>

      {/* Quick info cards */}
      <View style={styles.quickInfo}>
        <Card style={styles.quickCard}>
          <Card.Content style={styles.quickContent}>
            <Text style={styles.quickIcon}>{'\uD83E\uDD5B'}</Text>
            <Text variant="bodySmall">{t('milk.todayTotal')}</Text>
            <Text variant="titleSmall" style={styles.quickValue}>{animal.lastMilk || '\u2014'}</Text>
          </Card.Content>
        </Card>
        <Card style={styles.quickCard}>
          <Card.Content style={styles.quickContent}>
            <Text style={styles.quickIcon}>{'\uD83D\uDC89'}</Text>
            <Text variant="bodySmall">{t('health.vaccinations')}</Text>
            <Text variant="titleSmall" style={styles.quickValue}>{animal.lastVaccination || '\u2014'}</Text>
          </Card.Content>
        </Card>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <Button mode="outlined" icon="pencil" onPress={() => router.push(`/animal/add?edit=${id}`)} style={styles.actionButton}>
          {t('common.edit')}
        </Button>
        <Button
          mode="outlined"
          icon="delete"
          onPress={() => {
            Alert.alert(
              t('animal.deleteTitle') ?? 'Delete Animal',
              t('animal.deleteConfirm') ?? 'Are you sure? This cannot be undone.',
              [
                { text: t('common.cancel') ?? 'Cancel', style: 'cancel' },
                {
                  text: t('common.delete') ?? 'Delete',
                  style: 'destructive',
                  onPress: async () => {
                    try {
                      await api.delete(`/animals/${id}`);
                      router.back();
                    } catch (e) {
                      setError(e instanceof Error ? e.message : 'An error occurred');
                    }
                  },
                },
              ]
            );
          }}
          style={styles.actionButton}
          textColor={statusColors.urgent}
        >
          {t('common.delete')}
        </Button>
      </View>
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
  hero: {
    alignItems: 'center',
    paddingVertical: SPACING.lg,
  },
  name: {
    fontWeight: 'bold',
    marginTop: SPACING.sm,
  },
  healthBadge: {
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.xs,
    borderRadius: 20,
    marginTop: SPACING.sm,
  },
  healthText: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  card: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
  },
  detailLabel: {
    color: '#616161',
  },
  detailValue: {
    fontWeight: '600',
  },
  rowDivider: {
    marginVertical: 2,
  },
  quickInfo: {
    flexDirection: 'row',
    gap: SPACING.sm,
    marginTop: SPACING.lg,
  },
  quickCard: {
    flex: 1,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
  },
  quickContent: {
    alignItems: 'center',
    gap: SPACING.xs,
    paddingVertical: SPACING.md,
  },
  quickIcon: {
    fontSize: 32,
  },
  quickValue: {
    fontWeight: 'bold',
    textAlign: 'center',
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
});
