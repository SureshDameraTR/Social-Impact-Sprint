import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, Text, ProgressBar } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';

type VaccStatus = 'done' | 'due' | 'overdue';

interface VaccRecord {
  id: string;
  animalName: string;
  species: string;
  speciesEmoji: string;
  vaccineName: string;
  dueDate: string;
  status: VaccStatus;
  daysUntil: number;
}

const MOCK_VACCINATIONS: VaccRecord[] = [
  { id: '1', animalName: 'Lakshmi', species: 'cattle', speciesEmoji: '🐄', vaccineName: 'FMD', dueDate: '2026-04-11', status: 'due', daysUntil: 3 },
  { id: '2', animalName: 'Gowri', species: 'cattle', speciesEmoji: '🐄', vaccineName: 'HS-BQ', dueDate: '2026-04-05', status: 'overdue', daysUntil: -3 },
  { id: '3', animalName: 'Nandi', species: 'cattle', speciesEmoji: '🐄', vaccineName: 'Brucellosis', dueDate: '2026-04-20', status: 'due', daysUntil: 12 },
  { id: '4', animalName: 'Malli', species: 'goat', speciesEmoji: '🐐', vaccineName: 'PPR', dueDate: '2026-04-15', status: 'due', daysUntil: 7 },
  { id: '5', animalName: 'Malli', species: 'goat', speciesEmoji: '🐐', vaccineName: 'Goat Pox', dueDate: '2026-03-28', status: 'overdue', daysUntil: -11 },
  { id: '6', animalName: 'Chinni', species: 'sheep', speciesEmoji: '🐑', vaccineName: 'Enterotoxaemia', dueDate: '2026-04-18', status: 'due', daysUntil: 10 },
  { id: '7', animalName: 'Kodi', species: 'poultry', speciesEmoji: '🐔', vaccineName: 'Ranikhet (ND)', dueDate: '2026-04-02', status: 'done', daysUntil: -6 },
  { id: '8', animalName: 'Lakshmi', species: 'cattle', speciesEmoji: '🐄', vaccineName: 'Anthrax', dueDate: '2026-04-01', status: 'done', daysUntil: -7 },
];

const STATUS_COLORS: Record<VaccStatus, string> = {
  done: '#2E7D32',
  due: '#FF8F00',
  overdue: '#D32F2F',
};

export default function VaccinationsScreen() {
  const { t } = useTranslation();
  const [records, setRecords] = useState(MOCK_VACCINATIONS);

  const markDone = (id: string) => {
    setRecords((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: 'done' as VaccStatus, daysUntil: 0 } : r))
    );
  };

  const totalCattle = records.filter((r) => r.species === 'cattle').length;
  const doneCattle = records.filter((r) => r.species === 'cattle' && r.status === 'done').length;
  const coveragePercent = totalCattle > 0 ? Math.round((doneCattle / totalCattle) * 100) : 0;

  const grouped = {
    overdue: records.filter((r) => r.status === 'overdue'),
    due: records.filter((r) => r.status === 'due'),
    done: records.filter((r) => r.status === 'done'),
  };

  const getCountdownText = (rec: VaccRecord): string => {
    if (rec.status === 'done') return t('vaccinations.completed');
    if (rec.daysUntil < 0) return `${t('vaccinations.overdue')}!`;
    if (rec.daysUntil === 0) return t('vaccinations.dueToday');
    return `${t('vaccinations.dueIn')} ${rec.daysUntil} ${t('vaccinations.days')}`;
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('vaccinations.title')}
      </Text>

      <Card style={styles.coverageCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.coverageTitle}>
            {t('vaccinations.villageCoverage')}
          </Text>
          <Text variant="headlineSmall" style={styles.coveragePercent}>
            {coveragePercent}% {t('vaccinations.cattleVaccinated')}
          </Text>
          <ProgressBar
            progress={coveragePercent / 100}
            color="#2E7D32"
            style={styles.coverageBar}
          />
        </Card.Content>
      </Card>

      {grouped.overdue.length > 0 && (
        <>
          <Text variant="titleMedium" style={[styles.sectionTitle, { color: '#D32F2F' }]}>
            ⚠️ {t('vaccinations.overdueSection')} ({grouped.overdue.length})
          </Text>
          {grouped.overdue.map((rec) => (
            <VaccCard key={rec.id} record={rec} onMarkDone={markDone} countdownText={getCountdownText(rec)} t={t} />
          ))}
        </>
      )}

      {grouped.due.length > 0 && (
        <>
          <Text variant="titleMedium" style={[styles.sectionTitle, { color: '#FF8F00' }]}>
            📅 {t('vaccinations.upcomingSection')} ({grouped.due.length})
          </Text>
          {grouped.due.map((rec) => (
            <VaccCard key={rec.id} record={rec} onMarkDone={markDone} countdownText={getCountdownText(rec)} t={t} />
          ))}
        </>
      )}

      {grouped.done.length > 0 && (
        <>
          <Text variant="titleMedium" style={[styles.sectionTitle, { color: '#2E7D32' }]}>
            ✅ {t('vaccinations.completedSection')} ({grouped.done.length})
          </Text>
          {grouped.done.map((rec) => (
            <VaccCard key={rec.id} record={rec} onMarkDone={markDone} countdownText={getCountdownText(rec)} t={t} />
          ))}
        </>
      )}
    </ScrollView>
  );
}

function VaccCard({
  record,
  onMarkDone,
  countdownText,
  t,
}: {
  record: VaccRecord;
  onMarkDone: (id: string) => void;
  countdownText: string;
  t: (key: string) => string;
}) {
  const statusColor = STATUS_COLORS[record.status];
  return (
    <Card style={[styles.vaccCard, { borderLeftColor: statusColor }]}>
      <Card.Content>
        <View style={styles.vaccHeader}>
          <Text style={styles.vaccEmoji}>{record.speciesEmoji}</Text>
          <View style={{ flex: 1 }}>
            <Text variant="titleSmall" style={styles.vaccAnimal}>
              {record.animalName}
            </Text>
            <Text variant="titleMedium" style={styles.vaccName}>
              {record.vaccineName}
            </Text>
          </View>
          <View style={[styles.countdownBadge, { backgroundColor: statusColor + '20' }]}>
            <Text style={[styles.countdownText, { color: statusColor }]}>
              {countdownText}
            </Text>
          </View>
        </View>

        <Text variant="bodySmall" style={styles.vaccDate}>
          {t('vaccinations.dueDate')}: {record.dueDate}
        </Text>

        {record.status !== 'done' && (
          <Button
            mode="contained"
            compact
            onPress={() => onMarkDone(record.id)}
            style={styles.markDoneButton}
            contentStyle={{ minHeight: TOUCH_TARGET_MIN }}
            icon="check"
          >
            {t('vaccinations.markDone')}
          </Button>
        )}
      </Card.Content>
    </Card>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  content: {
    padding: SPACING.md,
    paddingBottom: 100,
  },
  heading: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
  coverageCard: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#E8F5E9',
    marginBottom: SPACING.lg,
  },
  coverageTitle: {
    color: '#1B5E20',
  },
  coveragePercent: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginVertical: SPACING.sm,
  },
  coverageBar: {
    height: 12,
    borderRadius: 6,
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
    marginTop: SPACING.md,
  },
  vaccCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.sm,
    borderLeftWidth: 4,
  },
  vaccHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  vaccEmoji: {
    fontSize: 32,
    marginRight: SPACING.sm,
  },
  vaccAnimal: {
    color: '#616161',
  },
  vaccName: {
    color: '#212121',
    fontWeight: 'bold',
  },
  countdownBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: 4,
    borderRadius: 8,
  },
  countdownText: {
    fontSize: 11,
    fontWeight: 'bold',
  },
  vaccDate: {
    color: '#616161',
    marginBottom: SPACING.sm,
  },
  markDoneButton: {
    backgroundColor: '#2E7D32',
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
});
