import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, TextInput, Button, SegmentedButtons, Snackbar } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { SPACING, TOUCH_TARGET_MIN } from '../../src/config/theme';
import { api } from '../../src/config/api';

type Species = 'cattle' | 'goat' | 'sheep' | 'poultry';

const SPECIES_OPTIONS: { value: Species; emoji: string }[] = [
  { value: 'cattle', emoji: '\uD83D\uDC04' },
  { value: 'goat', emoji: '\uD83D\uDC10' },
  { value: 'sheep', emoji: '\uD83D\uDC11' },
  { value: 'poultry', emoji: '\uD83D\uDC14' },
];

export default function AddAnimalScreen() {
  const { t } = useTranslation();
  const [species, setSpecies] = useState<Species>('cattle');
  const [name, setName] = useState('');
  const [breed, setBreed] = useState('');
  const [tagNumber, setTagNumber] = useState('');
  const [age, setAge] = useState('');
  const [weight, setWeight] = useState('');
  const [gender, setGender] = useState('female');
  const [snackVisible, setSnackVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [saveError, setSaveError] = useState<string | null>(null);

  const handleSave = async () => {
    setIsSubmitting(true);
    setSaveError(null);
    try {
      const dob = age ? new Date(Date.now() - parseInt(age) * 365.25 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] : undefined;
      await api.post('/animals', {
        species,
        breed: breed || 'Unknown',
        breed_type: 'indigenous',
        sex: gender,
        name: name || undefined,
        tag_id: tagNumber || undefined,
        date_of_birth: dob,
      });
      setSnackVisible(true);
      setTimeout(() => router.back(), 1500);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : 'Failed to save');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text variant="headlineSmall" style={styles.heading}>
          {t('animals.addAnimal')}
        </Text>

        {/* Species picker */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          {t('animals.species')}
        </Text>
        <View style={styles.speciesRow}>
          {SPECIES_OPTIONS.map((opt) => (
            <Button
              key={opt.value}
              mode={species === opt.value ? 'contained' : 'outlined'}
              onPress={() => setSpecies(opt.value)}
              style={styles.speciesButton}
              contentStyle={styles.speciesButtonContent}
              labelStyle={styles.speciesButtonLabel}
            >
              {opt.emoji} {t(`animals.${opt.value}`)}
            </Button>
          ))}
        </View>

        {/* Form fields */}
        <TextInput
          label={t('animals.name')}
          value={name}
          onChangeText={setName}
          mode="outlined"
          style={styles.input}
        />

        <TextInput
          label={t('animals.breed')}
          value={breed}
          onChangeText={setBreed}
          mode="outlined"
          style={styles.input}
        />

        <TextInput
          label={t('animals.tagNumber')}
          value={tagNumber}
          onChangeText={setTagNumber}
          mode="outlined"
          style={styles.input}
        />

        <View style={styles.row}>
          <TextInput
            label={t('animals.age')}
            value={age}
            onChangeText={setAge}
            keyboardType="number-pad"
            mode="outlined"
            style={[styles.input, styles.halfInput]}
          />
          <TextInput
            label={`${t('animals.weight')} (kg)`}
            value={weight}
            onChangeText={setWeight}
            keyboardType="decimal-pad"
            mode="outlined"
            style={[styles.input, styles.halfInput]}
          />
        </View>

        <Text variant="titleMedium" style={styles.sectionTitle}>
          {t('animals.gender')}
        </Text>
        <SegmentedButtons
          value={gender}
          onValueChange={setGender}
          buttons={[
            { value: 'female', label: t('animals.female') },
            { value: 'male', label: t('animals.male') },
          ]}
          style={styles.genderButtons}
        />

        {/* Error message */}
        {saveError && (
          <Text style={{ color: '#D32F2F', marginTop: SPACING.sm, textAlign: 'center' }}>{saveError}</Text>
        )}

        {/* Save / Cancel */}
        <View style={styles.actions}>
          <Button
            mode="outlined"
            onPress={() => router.back()}
            style={styles.actionButton}
            contentStyle={styles.actionButtonContent}
          >
            {t('common.cancel')}
          </Button>
          <Button
            mode="contained"
            onPress={handleSave}
            disabled={isSubmitting || !name || !breed}
            loading={isSubmitting}
            style={styles.actionButton}
            contentStyle={styles.actionButtonContent}
            labelStyle={styles.saveLabel}
          >
            {t('common.save')}
          </Button>
        </View>
      </ScrollView>

      <Snackbar
        visible={snackVisible}
        onDismiss={() => setSnackVisible(false)}
        duration={1500}
        style={styles.snackbar}
      >
        {t('common.success')}
      </Snackbar>
    </View>
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
  speciesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
    marginBottom: SPACING.md,
  },
  speciesButton: {
    borderRadius: 12,
  },
  speciesButtonContent: {
    height: 56,
  },
  speciesButtonLabel: {
    fontSize: 16,
  },
  input: {
    marginBottom: SPACING.sm,
    fontSize: 18,
  },
  row: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  halfInput: {
    flex: 1,
  },
  genderButtons: {
    marginBottom: SPACING.md,
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
  actionButtonContent: {
    height: 56,
    minHeight: TOUCH_TARGET_MIN,
  },
  saveLabel: {
    fontSize: 18,
  },
  snackbar: {
    backgroundColor: '#2E7D32',
  },
});
