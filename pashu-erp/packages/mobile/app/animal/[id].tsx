import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Button, Divider } from 'react-native-paper';
import { useLocalSearchParams } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SpeciesIcon } from '../../src/components/SpeciesIcon';
import { SPACING, CARD_BORDER_RADIUS } from '../../src/config/theme';
import type { Species } from '../../src/components/SpeciesIcon';

// Mock data - keyed by ID
const MOCK_DETAILS: Record<string, {
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
}> = {
  '1': {
    name: 'Lakshmi',
    species: 'cattle',
    breed: 'Hallikar',
    tagNumber: 'KA-001',
    pashuAadhaar: 'PA-2026-0001',
    age: '4 years',
    weight: '350 kg',
    gender: 'female',
    healthStatus: 'healthy',
    lastMilk: '5.2L (today morning)',
    lastVaccination: 'FMD - 2026-01-15',
  },
  '2': {
    name: 'Gowri',
    species: 'cattle',
    breed: 'Amrit Mahal',
    tagNumber: 'KA-002',
    pashuAadhaar: 'PA-2026-0002',
    age: '3 years',
    weight: '320 kg',
    gender: 'female',
    healthStatus: 'healthy',
    lastMilk: '4.8L (today morning)',
    lastVaccination: 'FMD - 2026-01-15',
  },
  '3': {
    name: 'Malli',
    species: 'goat',
    breed: 'Osmanabadi',
    tagNumber: 'KA-003',
    pashuAadhaar: 'PA-2026-0003',
    age: '2 years',
    weight: '35 kg',
    gender: 'female',
    healthStatus: 'sick',
    lastMilk: 'N/A',
    lastVaccination: 'PPR - 2025-12-01',
  },
};

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

  const animal = MOCK_DETAILS[id || '1'] || MOCK_DETAILS['1'];

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
            { color: animal.healthStatus === 'healthy' ? '#2E7D32' : '#D32F2F' },
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
            <Text variant="titleSmall" style={styles.quickValue}>{animal.lastMilk}</Text>
          </Card.Content>
        </Card>
        <Card style={styles.quickCard}>
          <Card.Content style={styles.quickContent}>
            <Text style={styles.quickIcon}>{'\uD83D\uDC89'}</Text>
            <Text variant="bodySmall">{t('health.vaccinations')}</Text>
            <Text variant="titleSmall" style={styles.quickValue}>{animal.lastVaccination}</Text>
          </Card.Content>
        </Card>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <Button mode="outlined" icon="pencil" onPress={() => {}} style={styles.actionButton}>
          {t('common.edit')}
        </Button>
        <Button mode="outlined" icon="delete" onPress={() => {}} style={styles.actionButton} textColor="#D32F2F">
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
