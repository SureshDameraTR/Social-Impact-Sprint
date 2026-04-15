import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { Button, Text, TextInput, Chip } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { api } from '../../src/config/api';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../../src/config/theme';

const SPECIES_OPTIONS = [
  { key: 'cattle', emoji: '🐄', breeds: ['Hallikar', 'Amrit Mahal', 'Khillari', 'Deoni', 'Krishna Valley', 'HF Cross'] },
  { key: 'goat', emoji: '🐐', breeds: ['Osmanabadi', 'Beetal', 'Jamunapari', 'Sirohi', 'Black Bengal'] },
  { key: 'sheep', emoji: '🐑', breeds: ['Bannur', 'Deccani', 'Nellore', 'Hassan', 'Bellary'] },
  { key: 'poultry', emoji: '🐔', breeds: ['Giriraja', 'Swarnadhara', 'Vanaraja', 'Desi', 'BV 380'] },
];

export default function FirstAnimalScreen() {
  const { t } = useTranslation();
  const [selectedSpecies, setSelectedSpecies] = useState<string | null>(null);
  const [selectedBreed, setSelectedBreed] = useState<string | null>(null);
  const [animalName, setAnimalName] = useState('');
  const [saving, setSaving] = useState(false);

  const speciesData = SPECIES_OPTIONS.find((s) => s.key === selectedSpecies);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('onboarding.firstAnimalTitle')}
      </Text>
      <Text variant="bodyLarge" style={styles.subheading}>
        {t('onboarding.firstAnimalSubtitle')}
      </Text>

      <Text variant="titleMedium" style={styles.sectionLabel}>
        {t('animals.species')}
      </Text>
      <View style={styles.speciesGrid}>
        {SPECIES_OPTIONS.map((sp) => (
          <TouchableOpacity
            key={sp.key}
            style={[
              styles.speciesCard,
              selectedSpecies === sp.key && styles.speciesCardSelected,
            ]}
            onPress={() => {
              setSelectedSpecies(sp.key);
              setSelectedBreed(null);
            }}
            activeOpacity={0.7}
          >
            <Text style={styles.speciesEmoji}>{sp.emoji}</Text>
            <Text
              variant="titleSmall"
              style={[
                styles.speciesLabel,
                selectedSpecies === sp.key && styles.speciesLabelSelected,
              ]}
            >
              {t(`animals.${sp.key}`)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {speciesData && (
        <>
          <Text variant="titleMedium" style={styles.sectionLabel}>
            {t('animals.breed')}
          </Text>
          <View style={styles.breedRow}>
            {speciesData.breeds.map((breed) => (
              <Chip
                key={breed}
                selected={selectedBreed === breed}
                onPress={() => setSelectedBreed(breed)}
                style={[
                  styles.breedChip,
                  selectedBreed === breed && styles.breedChipSelected,
                ]}
                textStyle={selectedBreed === breed ? styles.breedTextSelected : undefined}
              >
                {breed}
              </Chip>
            ))}
          </View>
        </>
      )}

      <TextInput
        label={t('onboarding.animalNameLabel')}
        value={animalName}
        onChangeText={setAnimalName}
        mode="outlined"
        style={styles.input}
        outlineColor="#BDBDBD"
        activeOutlineColor="#2E7D32"
        placeholder={t('onboarding.animalNamePlaceholder')}
      />

      <Button
        mode="contained"
        onPress={async () => {
          setSaving(true);
          try {
            await api.post('/animals', { species: selectedSpecies, breed: selectedBreed, name: animalName });
            router.push('/onboarding/tutorial');
          } catch (e) {
            Alert.alert(t('common.error'), t('onboarding.saveFailed') ?? 'Failed to save animal. Please try again.');
          } finally {
            setSaving(false);
          }
        }}
        style={styles.addButton}
        contentStyle={styles.addButtonContent}
        labelStyle={styles.addButtonLabel}
        disabled={!selectedSpecies || !animalName || saving}
        loading={saving}
        icon="plus"
      >
        {t('onboarding.addFirstAnimal')}
      </Button>

      <Button
        mode="text"
        onPress={() => router.push('/onboarding/tutorial')}
        style={styles.skipButton}
      >
        {t('onboarding.skipForNow')}
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  content: {
    padding: SPACING.lg,
    paddingBottom: 100,
  },
  heading: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginBottom: SPACING.xs,
  },
  subheading: {
    color: '#616161',
    marginBottom: SPACING.lg,
  },
  sectionLabel: {
    color: '#212121',
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
    marginTop: SPACING.md,
  },
  speciesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.md,
    justifyContent: 'center',
  },
  speciesCard: {
    width: 140,
    height: 120,
    backgroundColor: '#FFFFFF',
    borderRadius: CARD_BORDER_RADIUS,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E0E0E0',
    elevation: 1,
  },
  speciesCardSelected: {
    borderColor: '#2E7D32',
    backgroundColor: '#C8E6C9',
  },
  speciesEmoji: {
    fontSize: 48,
    marginBottom: SPACING.xs,
  },
  speciesLabel: {
    color: '#616161',
  },
  speciesLabelSelected: {
    color: '#1B5E20',
    fontWeight: 'bold',
  },
  breedRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  breedChip: {
    marginBottom: SPACING.xs,
    minHeight: TOUCH_TARGET_MIN,
  },
  breedChipSelected: {
    backgroundColor: '#C8E6C9',
  },
  breedTextSelected: {
    color: '#1B5E20',
  },
  input: {
    marginTop: SPACING.lg,
    marginBottom: SPACING.md,
    backgroundColor: '#FFFFFF',
  },
  addButton: {
    backgroundColor: '#2E7D32',
    borderRadius: CARD_BORDER_RADIUS,
    marginTop: SPACING.md,
  },
  addButtonContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  addButtonLabel: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  skipButton: {
    marginTop: SPACING.sm,
  },
});
