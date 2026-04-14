import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet, Pressable, StatusBar, Linking } from 'react-native';
import { router } from 'expo-router';
import { Text, Button, Card, IconButton, Snackbar, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { TriageCard, type Severity } from '../../src/components/TriageCard';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, TOUCH_TARGET_MIN, statusColors, colors } from '../../src/config/theme';
import { api } from '../../src/config/api';

interface AnimalOption {
  id: string;
  name: string;
  species: string;
}

const SPECIES_EMOJI: Record<string, string> = {
  cattle: '\uD83D\uDC04',
  goat: '\uD83D\uDC10',
  sheep: '\uD83D\uDC11',
  poultry: '\uD83D\uDC14',
};

// UI options for symptom selection (not mock data)
const SYMPTOMS = [
  { key: 'fever', icon: '\uD83C\uDF21\uFE0F' },
  { key: 'noAppetite', icon: '\uD83C\uDF3F\u274C' },
  { key: 'limping', icon: '\uD83D\uDC3E' },
  { key: 'discharge', icon: '\uD83D\uDCA7\uD83D\uDD34' },
  { key: 'bloating', icon: '\uD83D\uDCA8' },
  { key: 'coughing', icon: '\uD83E\uDD27' },
  { key: 'diarrhea', icon: '\u26A0\uFE0F' },
] as const;

// Triage logic (runs locally based on symptom combinations)
function getTriageResult(symptoms: string[]): { severity: Severity; messageKey: string } | null {
  if (symptoms.length === 0) return null;
  if (symptoms.includes('fever') && symptoms.includes('diarrhea')) {
    return { severity: 'critical', messageKey: 'health.triageFMD' };
  }
  if (symptoms.includes('bloating')) {
    return { severity: 'high', messageKey: 'health.triageBloat' };
  }
  if (symptoms.includes('fever') && symptoms.includes('discharge')) {
    return { severity: 'high', messageKey: 'health.triageMastitis' };
  }
  if (symptoms.length >= 3) {
    return { severity: 'high', messageKey: 'health.triageMultipleHigh' };
  }
  if (symptoms.length >= 2) {
    return { severity: 'medium', messageKey: 'health.triageMultipleMedium' };
  }
  return { severity: 'low', messageKey: 'health.triageGeneral' };
}

export default function HealthScreen() {
  const { t } = useTranslation();
  const [animals, setAnimals] = useState<AnimalOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnimal, setSelectedAnimal] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [triageResult, setTriageResult] = useState<{ severity: Severity; messageKey: string } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSnackbar, setShowSnackbar] = useState(false);

  const fetchAnimals = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<AnimalOption[]>('/animals')
      .then(res => setAnimals(Array.isArray(res) ? res : (res as any).data ?? []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchAnimals();
  }, [fetchAnimals]);

  const toggleSymptom = useCallback((symptom: string) => {
    setSelectedSymptoms((prev) =>
      prev.includes(symptom) ? prev.filter((s) => s !== symptom) : [...prev, symptom]
    );
    setTriageResult(null);
  }, []);

  const handleSelectAnimal = useCallback((id: string) => {
    setSelectedAnimal(id);
  }, []);

  const handleCheck = useCallback(async () => {
    setIsSubmitting(true);
    try {
      const result = getTriageResult(selectedSymptoms);
      setTriageResult(result);
      if (result) {
        setShowSnackbar(true);
      }
    } finally {
      setIsSubmitting(false);
    }
  }, [selectedSymptoms]);

  const handleReset = useCallback(() => {
    setSelectedAnimal('');
    setSelectedSymptoms([]);
    setTriageResult(null);
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
          onAction={fetchAnimals}
        />
      </View>
    );
  }

  if (animals.length === 0) {
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
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F0" />

      <Text variant="headlineSmall" style={styles.heading}>
        {t('health.healthCheck')}
      </Text>

      {/* Animal selector */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('health.selectAnimal')}
      </Text>
      <View style={styles.animalRow}>
        {animals.map((animal) => (
          <Pressable
            key={animal.id}
            onPress={() => handleSelectAnimal(animal.id)}
            style={[
              styles.animalChip,
              selectedAnimal === animal.id && styles.animalChipSelected,
            ]}
            accessibilityLabel={animal.name}
            accessibilityRole="radio"
            accessibilityState={{ checked: selectedAnimal === animal.id }}
          >
            <Text style={styles.animalEmoji}>{SPECIES_EMOJI[animal.species] || '\uD83D\uDC3E'}</Text>
            <Text style={[
              styles.animalChipText,
              selectedAnimal === animal.id && styles.animalChipTextSelected,
            ]}>
              {animal.name}
            </Text>
          </Pressable>
        ))}
      </View>

      {/* Symptom grid (3 columns) */}
      {selectedAnimal !== '' && (
        <>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            {t('health.selectSymptoms')}
          </Text>
          <View style={styles.symptomGrid}>
            {SYMPTOMS.map((symptom) => {
              const isSelected = selectedSymptoms.includes(symptom.key);
              return (
                <Pressable
                  key={symptom.key}
                  onPress={() => toggleSymptom(symptom.key)}
                  style={[
                    styles.symptomCard,
                    isSelected && styles.symptomCardSelected,
                  ]}
                  accessibilityLabel={`${t(`health.${symptom.key}`)}${isSelected ? ', selected' : ''}`}
                  accessibilityRole="checkbox"
                  accessibilityState={{ checked: isSelected }}
                >
                  <Text style={styles.symptomIcon}>{symptom.icon}</Text>
                  <Text style={[
                    styles.symptomLabel,
                    isSelected && styles.symptomLabelSelected,
                  ]} numberOfLines={2}>
                    {t(`health.${symptom.key}`)}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          <Button
            mode="contained"
            onPress={handleCheck}
            disabled={isSubmitting || selectedSymptoms.length === 0}
            loading={isSubmitting}
            style={styles.checkButton}
            contentStyle={styles.checkButtonContent}
            labelStyle={styles.checkButtonLabel}
            buttonColor={colors.primary}
            accessibilityLabel={t('health.logSymptoms')}
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
            messageKey={triageResult.messageKey}
            onCallVet={() => Linking.openURL('tel:1962')}
          />
          <Button mode="text" onPress={handleReset} style={styles.resetButton} textColor={colors.primary}>
            {t('common.cancel')}
          </Button>
        </View>
      )}

      {/* Send photo to vet */}
      <Button
        mode="contained"
        icon="camera"
        onPress={() => router.push('/vet-photo')}
        style={styles.vetPhotoButton}
        contentStyle={styles.vetPhotoContent}
        labelStyle={styles.vetPhotoLabel}
        buttonColor={colors.tertiary}
        accessibilityLabel={t('vetPhoto.title')}
      >
        {t('vetPhoto.title')}
      </Button>

      {/* Emergency vet call */}
      <Pressable
        onPress={() => Linking.openURL('tel:1962')}
        accessibilityLabel={`${t('health.callVet')} - ${t('health.emergencyLine')}`}
        accessibilityRole="button"
      >
        <Card style={styles.emergencyCard}>
          <Card.Content style={styles.emergencyContent}>
            <View style={styles.emergencyLeft}>
              <IconButton icon="phone" size={28} iconColor="#FFFFFF" style={styles.emergencyIcon} />
              <View>
                <Text variant="titleMedium" style={styles.emergencyTitle}>
                  {t('health.callVet')}
                </Text>
                <Text variant="bodySmall" style={styles.emergencySubtitle}>
                  {t('health.emergencyLine')}
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      </Pressable>

      <Snackbar
        visible={showSnackbar}
        onDismiss={() => setShowSnackbar(false)}
        duration={2000}
        style={styles.snackbar}
      >
        {triageResult ? t(triageResult.messageKey) : t('health.healthCheck')}
      </Snackbar>
    </ScrollView>
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
  heading: {
    fontWeight: '700',
    color: colors.primary,
    marginBottom: SPACING.md,
  },
  sectionTitle: {
    fontWeight: '700',
    marginTop: SPACING.lg,
    marginBottom: SPACING.sm,
    color: '#1A1A1A',
  },
  animalRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  animalChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#C1C9BF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  animalChipSelected: {
    backgroundColor: '#A8F5C8',
    borderColor: colors.primary,
    borderWidth: 2,
  },
  animalEmoji: {
    fontSize: 24,
  },
  animalChipText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1A1A1A',
  },
  animalChipTextSelected: {
    fontWeight: '700',
    color: '#002112',
  },
  symptomGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  symptomCard: {
    width: '31%',
    alignItems: 'center',
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xs,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#C1C9BF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  symptomCardSelected: {
    backgroundColor: '#FFDAD6',
    borderColor: '#C62828',
    borderWidth: 2,
  },
  symptomIcon: {
    fontSize: 28,
    marginBottom: 6,
  },
  symptomLabel: {
    fontSize: 13,
    textAlign: 'center',
    color: '#1A1A1A',
    fontWeight: '500',
  },
  symptomLabelSelected: {
    color: '#C62828',
    fontWeight: '700',
  },
  checkButton: {
    marginTop: SPACING.lg,
    borderRadius: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  checkButtonContent: {
    height: 56,
  },
  checkButtonLabel: {
    fontSize: 18,
    fontWeight: '700',
  },
  resultSection: {
    marginTop: SPACING.lg,
  },
  resetButton: {
    marginTop: SPACING.sm,
  },
  vetPhotoButton: {
    marginTop: SPACING.lg,
    borderRadius: 16,
  },
  vetPhotoContent: {
    height: 56,
  },
  vetPhotoLabel: {
    fontSize: 18,
    fontWeight: '700',
  },
  emergencyCard: {
    marginTop: SPACING.xl,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#C62828',
    shadowColor: '#C62828',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  emergencyContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  emergencyLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  emergencyIcon: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 24,
    margin: 0,
  },
  emergencyTitle: {
    fontWeight: '700',
    color: '#FFFFFF',
    fontSize: 18,
  },
  emergencySubtitle: {
    color: 'rgba(255,255,255,0.8)',
  },
  snackbar: {
    backgroundColor: colors.primary,
  },
});
