import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, Pressable, Alert } from 'react-native';
import { Button, Text, TextInput, Chip } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { api } from '../../src/config/api';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors, statusColors } from '../../src/config/theme';
import { useSpecies, useBreeds } from '../../src/hooks/useReferenceData';

export default function FirstAnimalScreen() {
  const { t } = useTranslation();
  const { data: speciesData } = useSpecies();
  const [selectedSpecies, setSelectedSpecies] = useState<string | null>(null);
  const [selectedBreed, setSelectedBreed] = useState<string | null>(null);
  const [animalName, setAnimalName] = useState('');
  const [saving, setSaving] = useState(false);

  const speciesOptions = (speciesData?.data ?? []).map((s) => ({
    key: s.code,
    emoji: s.emoji || '🐾',
    label: s.name_en,
  }));

  const { data: breedsData } = useBreeds(selectedSpecies ?? undefined);
  const breeds = breedsData?.data?.map((b) => b.name) ?? [];

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
        {speciesOptions.map((sp) => (
          <Pressable
            key={sp.key}
            style={[
              styles.speciesCard,
              selectedSpecies === sp.key && styles.speciesCardSelected,
            ]}
            onPress={() => {
              setSelectedSpecies(sp.key);
              setSelectedBreed(null);
            }}
            accessibilityLabel={t(`animals.${sp.key}`)}
            accessibilityRole="radio"
            accessibilityState={{ checked: selectedSpecies === sp.key }}
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
          </Pressable>
        ))}
      </View>

      {selectedSpecies && breeds.length > 0 && (
        <>
          <Text variant="titleMedium" style={styles.sectionLabel}>
            {t('animals.breed')}
          </Text>
          <View style={styles.breedRow}>
            {breeds.map((breed) => (
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
        outlineColor={colors.outlineVariant}
        activeOutlineColor={colors.primary}
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
            Alert.alert(t('common.error'), t('onboarding.saveFailed'));
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
    color: statusColors.healthy,
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
    borderColor: statusColors.healthy,
    backgroundColor: colors.secondaryContainer,
  },
  speciesEmoji: {
    fontSize: 48,
    marginBottom: SPACING.xs,
  },
  speciesLabel: {
    color: '#616161',
  },
  speciesLabelSelected: {
    color: colors.onPrimaryContainer,
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
    backgroundColor: colors.secondaryContainer,
  },
  breedTextSelected: {
    color: colors.onPrimaryContainer,
  },
  input: {
    marginTop: SPACING.lg,
    marginBottom: SPACING.md,
    backgroundColor: '#FFFFFF',
  },
  addButton: {
    backgroundColor: statusColors.healthy,
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
