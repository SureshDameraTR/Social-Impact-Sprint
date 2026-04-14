import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet, Image, Platform, Alert, Pressable } from 'react-native';
import { Button, Card, Text, TextInput, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors, statusColors } from '../src/config/theme';
import { api } from '../src/config/api';
import { useSnackbar } from '../src/hooks/useSnackbar';

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

export default function VetPhotoScreen() {
  const { t } = useTranslation();
  const { showError, showSuccess } = useSnackbar();
  const [animals, setAnimals] = useState<AnimalOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnimal, setSelectedAnimal] = useState('');
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const fetchAnimals = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<AnimalOption[]>('/animals?species=all')
      .then(res => setAnimals(Array.isArray(res) ? res : (res as any).data ?? []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchAnimals();
  }, [fetchAnimals]);

  const takePhoto = async () => {
    try {
      const permission = await ImagePicker.requestCameraPermissionsAsync();
      if (!permission.granted) {
        showError(t('vetPhoto.cameraPermissionRequired'));
        return;
      }
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        quality: 0.8,
      });
      if (result.canceled) return;
      setPhotoUri(result.assets[0].uri);
    } catch {
      showError(t('vetPhoto.photoFailed'));
    }
  };

  const pickFromGallery = async () => {
    try {
      const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permission.granted) {
        showError(t('vetPhoto.galleryPermissionRequired'));
        return;
      }
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        quality: 0.8,
      });
      if (result.canceled) return;
      setPhotoUri(result.assets[0].uri);
    } catch {
      showError(t('vetPhoto.photoFailed'));
    }
  };

  const handlePhotoAction = () => {
    if (Platform.OS === 'web') {
      pickFromGallery();
      return;
    }
    Alert.alert(
      t('vetPhoto.selectPhotoSource'),
      '',
      [
        { text: t('vetPhoto.takePhoto'), onPress: takePhoto },
        { text: t('vetPhoto.chooseFromGallery'), onPress: pickFromGallery },
        { text: t('common.cancel'), style: 'cancel' },
      ]
    );
  };

  const handleSubmit = async () => {
    if (!selectedAnimal) {
      showError(t('health.selectAnimal'));
      return;
    }
    if (!photoUri) {
      showError(t('vetPhoto.photoRequired'));
      return;
    }

    setSubmitting(true);
    try {
      // Upload photo to /files
      const formData = new FormData();
      formData.append('file', {
        uri: photoUri,
        type: 'image/jpeg',
        name: 'vet_diagnosis_photo.jpg',
      } as any);
      formData.append('category', 'vet_diagnosis');
      formData.append('entity_type', 'animal');
      formData.append('entity_id', selectedAnimal);
      const uploadRes = await api.upload<{ id: string }>('/files', formData);

      // Log health event with photo reference
      await api.post('/health/log', {
        animal_id: selectedAnimal,
        type: 'vet_photo_diagnosis',
        photo_id: uploadRes?.id,
        notes: notes || undefined,
      });

      setSubmitted(true);
      showSuccess(t('vetPhoto.sentSuccess'));
    } catch (e) {
      showError(e instanceof Error ? e.message : t('vetPhoto.sendFailed'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setSelectedAnimal('');
    setPhotoUri(null);
    setNotes('');
    setSubmitted(false);
  };

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

  if (submitted) {
    return (
      <View style={[styles.container, styles.successContainer]}>
        <Text style={styles.successIcon}>{'\u2705'}</Text>
        <Text variant="headlineSmall" style={styles.successTitle}>
          {t('vetPhoto.sentSuccess')}
        </Text>
        <Text variant="bodyLarge" style={styles.successSubtitle}>
          {t('consultations.sentToVet')}
        </Text>
        <Button
          mode="contained"
          onPress={() => router.push('/my-consultations')}
          style={styles.submitButton}
          contentStyle={styles.submitContent}
          buttonColor={colors.primary}
        >
          {t('consultations.viewAll')}
        </Button>
        <Button
          mode="outlined"
          onPress={handleReset}
          style={styles.sendAnotherButton}
          contentStyle={styles.submitContent}
          textColor={colors.primary}
        >
          {t('vetPhoto.sendAnother')}
        </Button>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      <Text variant="headlineSmall" style={styles.heading}>
        {t('vetPhoto.title')}
      </Text>
      <Text variant="bodyLarge" style={styles.subtitle}>
        {t('vetPhoto.subtitle')}
      </Text>

      {/* Animal selector */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('health.selectAnimal')}
      </Text>
      <View style={styles.animalRow}>
        {animals.map((animal) => (
          <Pressable
            key={animal.id}
            onPress={() => setSelectedAnimal(animal.id)}
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

      {/* Photo section */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('vetPhoto.photoSection')}
      </Text>
      <Card style={styles.photoCard}>
        <Card.Content>
          {photoUri ? (
            <View style={styles.previewContainer}>
              <Image source={{ uri: photoUri }} style={styles.previewImage} />
              <Button
                mode="text"
                onPress={handlePhotoAction}
                textColor={colors.primary}
                style={styles.changePhotoButton}
              >
                {t('vetPhoto.changePhoto')}
              </Button>
            </View>
          ) : (
            <View style={styles.photoButtons}>
              <Button
                mode="contained"
                icon="camera"
                onPress={takePhoto}
                style={styles.photoButton}
                contentStyle={styles.photoButtonContent}
                buttonColor={colors.primary}
              >
                {t('vetPhoto.takePhoto')}
              </Button>
              <Button
                mode="outlined"
                icon="image"
                onPress={pickFromGallery}
                style={[styles.photoButton, styles.galleryButton]}
                contentStyle={styles.photoButtonContent}
                textColor={colors.primary}
              >
                {t('vetPhoto.chooseFromGallery')}
              </Button>
            </View>
          )}
        </Card.Content>
      </Card>

      {/* Notes input */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('vetPhoto.describeLabel')}
      </Text>
      <TextInput
        label={t('vetPhoto.describePlaceholder')}
        value={notes}
        onChangeText={setNotes}
        mode="outlined"
        multiline
        numberOfLines={4}
        style={styles.notesInput}
        outlineColor="#BDBDBD"
        activeOutlineColor={colors.primary}
      />

      {/* Submit */}
      <Button
        mode="contained"
        onPress={handleSubmit}
        loading={submitting}
        disabled={submitting || !selectedAnimal || !photoUri}
        style={styles.submitButton}
        contentStyle={styles.submitContent}
        labelStyle={styles.submitLabel}
        buttonColor={colors.primary}
        accessibilityLabel={t('vetPhoto.sendForDiagnosis')}
      >
        {t('vetPhoto.sendForDiagnosis')}
      </Button>
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
    marginBottom: SPACING.xs,
  },
  subtitle: {
    color: '#414941',
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
  photoCard: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
  },
  photoButtons: {
    gap: SPACING.sm,
  },
  photoButton: {
    borderRadius: CARD_BORDER_RADIUS,
  },
  galleryButton: {
    borderColor: colors.primary,
  },
  photoButtonContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  previewContainer: {
    alignItems: 'center',
  },
  previewImage: {
    width: '100%',
    height: 240,
    borderRadius: 12,
    backgroundColor: '#E0E0E0',
  },
  changePhotoButton: {
    marginTop: SPACING.sm,
  },
  notesInput: {
    backgroundColor: '#FFFFFF',
    marginBottom: SPACING.md,
  },
  submitButton: {
    marginTop: SPACING.lg,
    borderRadius: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  submitContent: {
    height: 56,
  },
  submitLabel: {
    fontSize: 18,
    fontWeight: '700',
  },
  successContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: SPACING.lg,
  },
  successIcon: {
    fontSize: 72,
    marginBottom: SPACING.md,
  },
  successTitle: {
    fontWeight: '700',
    color: colors.primary,
    textAlign: 'center',
    marginBottom: SPACING.sm,
  },
  successSubtitle: {
    color: '#414941',
    textAlign: 'center',
    marginBottom: SPACING.xl,
  },
  sendAnotherButton: {
    marginTop: SPACING.md,
    borderRadius: 16,
    borderColor: colors.primary,
  },
});
