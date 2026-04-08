import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Button, Chip, Card } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { TriageCard, type Severity } from '../../src/components/TriageCard';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, TOUCH_TARGET_MIN } from '../../src/config/theme';

const MOCK_ANIMALS = [
  { id: '1', name: 'Lakshmi', emoji: '\uD83D\uDC04' },
  { id: '3', name: 'Malli', emoji: '\uD83D\uDC10' },
  { id: '4', name: 'Chinni', emoji: '\uD83D\uDC11' },
  { id: '5', name: 'Kodi', emoji: '\uD83D\uDC14' },
];

const SYMPTOM_KEYS = [
  'fever', 'noAppetite', 'limping', 'discharge', 'bloating', 'coughing', 'diarrhea',
] as const;

// Mock triage logic
function getTriageResult(symptoms: string[]): { severity: Severity; message: string } | null {
  if (symptoms.length === 0) return null;
  if (symptoms.includes('fever') && symptoms.includes('diarrhea')) {
    return { severity: 'critical', message: 'Possible FMD infection. Immediate vet attention needed.' };
  }
  if (symptoms.includes('bloating')) {
    return { severity: 'high', message: 'Bloating detected. Risk of ruminal acidosis.' };
  }
  if (symptoms.length >= 3) {
    return { severity: 'high', message: 'Multiple symptoms detected. Vet visit recommended.' };
  }
  if (symptoms.length >= 2) {
    return { severity: 'medium', message: 'Monitor closely. If symptoms persist, consult vet.' };
  }
  return { severity: 'low', message: 'Minor symptom. Keep monitoring for 24 hours.' };
}

export default function HealthScreen() {
  const { t } = useTranslation();
  const [selectedAnimal, setSelectedAnimal] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [triageResult, setTriageResult] = useState<{ severity: Severity; message: string } | null>(null);

  const toggleSymptom = (symptom: string) => {
    setSelectedSymptoms((prev) =>
      prev.includes(symptom) ? prev.filter((s) => s !== symptom) : [...prev, symptom]
    );
    setTriageResult(null);
  };

  const handleCheck = () => {
    setTriageResult(getTriageResult(selectedSymptoms));
  };

  const handleReset = () => {
    setSelectedAnimal('');
    setSelectedSymptoms([]);
    setTriageResult(null);
  };

  if (MOCK_ANIMALS.length === 0) {
    return (
      <View style={styles.container}>
        <EmptyState
          icon={'\u2764\uFE0F'}
          title={t('empty.noHealthEvents')}
          subtitle={t('health.healthCheck')}
        />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      <Text variant="headlineSmall" style={styles.heading}>
        {t('health.healthCheck')}
      </Text>

      {/* Animal selector */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('health.selectAnimal')}
      </Text>
      <View style={styles.animalRow}>
        {MOCK_ANIMALS.map((animal) => (
          <Button
            key={animal.id}
            mode={selectedAnimal === animal.id ? 'contained' : 'outlined'}
            onPress={() => setSelectedAnimal(animal.id)}
            style={styles.animalButton}
            contentStyle={styles.animalButtonContent}
            labelStyle={styles.animalButtonLabel}
          >
            {animal.emoji} {animal.name}
          </Button>
        ))}
      </View>

      {/* Symptom picker */}
      {selectedAnimal !== '' && (
        <>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            {t('health.selectSymptoms')}
          </Text>
          <View style={styles.symptomGrid}>
            {SYMPTOM_KEYS.map((symptom) => (
              <Chip
                key={symptom}
                selected={selectedSymptoms.includes(symptom)}
                onPress={() => toggleSymptom(symptom)}
                style={[
                  styles.symptomChip,
                  selectedSymptoms.includes(symptom) && styles.symptomChipSelected,
                ]}
                textStyle={styles.symptomText}
                mode={selectedSymptoms.includes(symptom) ? 'flat' : 'outlined'}
              >
                {t(`health.${symptom}`)}
              </Chip>
            ))}
          </View>

          <Button
            mode="contained"
            onPress={handleCheck}
            disabled={selectedSymptoms.length === 0}
            style={styles.checkButton}
            contentStyle={styles.checkButtonContent}
            labelStyle={styles.checkButtonLabel}
          >
            {t('health.logSymptoms')}
          </Button>
        </>
      )}

      {/* Triage result */}
      {triageResult && (
        <View style={styles.resultSection}>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            {t('health.triageResult')}
          </Text>
          <TriageCard
            severity={triageResult.severity}
            message={triageResult.message}
            onCallVet={() => {}}
          />
          <Button mode="text" onPress={handleReset} style={styles.resetButton}>
            {t('common.cancel')}
          </Button>
        </View>
      )}

      {/* Vaccination card placeholder */}
      <Card style={styles.vaccinationCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.vaccinationTitle}>
            {'\uD83D\uDC89'} {t('health.vaccinations')}
          </Text>
          <Text variant="bodyMedium" style={styles.vaccinationText}>
            FMD - Due: 2026-05-15
          </Text>
          <Text variant="bodyMedium" style={styles.vaccinationText}>
            Brucellosis - Due: 2026-06-01
          </Text>
          <Text variant="bodyMedium" style={styles.vaccinationText}>
            HS/BQ - Due: 2026-07-10
          </Text>
        </Card.Content>
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
    paddingBottom: 100,
  },
  heading: {
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: SPACING.md,
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginTop: SPACING.md,
    marginBottom: SPACING.sm,
  },
  animalRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  animalButton: {
    borderRadius: 12,
  },
  animalButtonContent: {
    height: 56,
  },
  animalButtonLabel: {
    fontSize: 16,
  },
  symptomGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  symptomChip: {
    minHeight: TOUCH_TARGET_MIN,
    justifyContent: 'center',
  },
  symptomChipSelected: {
    backgroundColor: '#FFCDD2',
  },
  symptomText: {
    fontSize: 16,
  },
  checkButton: {
    marginTop: SPACING.lg,
    borderRadius: 12,
    backgroundColor: '#2E7D32',
  },
  checkButtonContent: {
    height: 56,
  },
  checkButtonLabel: {
    fontSize: 18,
  },
  resultSection: {
    marginTop: SPACING.lg,
  },
  resetButton: {
    marginTop: SPACING.sm,
  },
  vaccinationCard: {
    marginTop: SPACING.xl,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#E3F2FD',
  },
  vaccinationTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
  },
  vaccinationText: {
    color: '#424242',
    marginBottom: 4,
  },
});
