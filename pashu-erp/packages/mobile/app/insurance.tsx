import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet, Alert, Platform } from 'react-native';
import { Button, Card, Text, TextInput, Modal, Portal, RadioButton, IconButton, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import * as ImagePicker from 'expo-image-picker';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors, statusColors } from '../src/config/theme';
import { api } from '../src/config/api';
import { useSnackbar } from '../src/hooks/useSnackbar';

interface Policy {
  id: string;
  animalName: string;
  species: string;
  policyNumber: string;
  provider: string;
  status: 'active' | 'expired';
  premiumDue: string;
  daysUntilDue: number;
  sumInsured: number;
}

// TODO: Fetch premium rates from API /insurance/rates in future
const BASE_PREMIUMS: Record<string, number> = { cattle: 1200, goat: 400, sheep: 350, poultry: 50 };

export default function InsuranceScreen() {
  const { t } = useTranslation();
  const { showError, showSuccess } = useSnackbar();
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [claimVisible, setClaimVisible] = useState(false);
  const [claimDesc, setClaimDesc] = useState('');
  const [claimAnimalId, setClaimAnimalId] = useState<string | null>(null);
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [calcSpecies, setCalcSpecies] = useState('cattle');
  const [calcAge, setCalcAge] = useState('');
  const [calcResult, setCalcResult] = useState<number | null>(null);

  const uploadPhoto = async (uri: string, animalId: string) => {
    const formData = new FormData();
    formData.append('file', {
      uri,
      type: 'image/jpeg',
      name: 'insurance_photo.jpg',
    } as any);
    formData.append('category', 'insurance_photo');
    formData.append('entity_type', 'animal');
    formData.append('entity_id', animalId);
    await api.upload('/files', formData);
  };

  const takePhoto = async () => {
    try {
      const permission = await ImagePicker.requestCameraPermissionsAsync();
      if (!permission.granted) {
        showError(t('insurance.cameraPermissionRequired'));
        return;
      }
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        quality: 0.8,
      });
      if (result.canceled) return;
      setPhotoUri(result.assets[0].uri);
      showSuccess(t('insurance.photoAttached'));
    } catch {
      showError(t('insurance.photoFailed'));
    }
  };

  const pickFromGallery = async () => {
    try {
      const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permission.granted) {
        showError(t('insurance.galleryPermissionRequired'));
        return;
      }
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        quality: 0.8,
      });
      if (result.canceled) return;
      setPhotoUri(result.assets[0].uri);
      showSuccess(t('insurance.photoAttached'));
    } catch {
      showError(t('insurance.photoFailed'));
    }
  };

  const showPhotoOptions = () => {
    if (Platform.OS === 'web') {
      pickFromGallery();
      return;
    }
    Alert.alert(
      t('insurance.addPhoto'),
      t('insurance.photoSourcePrompt'),
      [
        { text: t('insurance.takePhoto'), onPress: takePhoto },
        { text: t('insurance.chooseFromGallery'), onPress: pickFromGallery },
        { text: t('common.cancel'), style: 'cancel' },
      ]
    );
  };

  const fetchPolicies = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<Policy[]>('/insurance/policies')
      .then(res => setPolicies(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchPolicies();
  }, [fetchPolicies]);

  const calculatePremium = () => {
    const base = BASE_PREMIUMS[calcSpecies] || 500;
    const age = parseInt(calcAge) || 3;
    const multiplier = age > 5 ? 1.5 : age > 3 ? 1.2 : 1.0;
    setCalcResult(Math.round(base * multiplier));
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
          onAction={fetchPolicies}
        />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('insurance.title')}
      </Text>

      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('insurance.activePolicies')}
      </Text>

      {policies.length === 0 && (
        <EmptyState
          icon={'\uD83D\uDEE1\uFE0F'}
          title={t('common.noData')}
          subtitle={t('insurance.activePolicies')}
        />
      )}

      {policies.map((policy) => (
        <Card
          key={policy.id}
          style={[
            styles.policyCard,
            policy.status === 'active' ? styles.activeCard : styles.expiredCard,
          ]}
        >
          <Card.Content>
            <View style={styles.policyHeader}>
              <Text style={styles.speciesEmoji}>{policy.species}</Text>
              <View style={styles.policyInfo}>
                <Text variant="titleMedium" style={styles.animalName}>
                  {policy.animalName}
                </Text>
                <Text variant="bodySmall" style={styles.policyNum}>
                  {policy.policyNumber}
                </Text>
              </View>
              <View style={[
                styles.statusBadge,
                { backgroundColor: policy.status === 'active' ? '#E8F5E9' : '#FFEBEE' },
              ]}>
                <Text style={{
                  color: policy.status === 'active' ? statusColors.healthy : statusColors.urgent,
                  fontWeight: 'bold',
                  fontSize: 12,
                }}>
                  {t(`insurance.${policy.status}`)}
                </Text>
              </View>
            </View>

            <View style={styles.policyDetails}>
              <Text variant="bodyMedium">
                {t('insurance.sumInsured')}: \u20B9{policy.sumInsured.toLocaleString()}
              </Text>
              <Text variant="bodyMedium">
                {t('insurance.provider')}: {policy.provider}
              </Text>
              {policy.status === 'active' && (
                <Text variant="bodyMedium" style={styles.dueDate}>
                  {t('insurance.premiumDue')}: {policy.premiumDue} ({policy.daysUntilDue} {t('insurance.daysLeft')})
                </Text>
              )}
            </View>
          </Card.Content>
        </Card>
      ))}

      <Button
        mode="contained"
        icon="file-document-edit"
        onPress={() => {
          const activePolicy = policies.find(p => p.status === 'active');
          if (activePolicy) setClaimAnimalId(activePolicy.id);
          setClaimVisible(true);
        }}
        style={styles.claimButton}
        contentStyle={styles.claimContent}
      >
        {t('insurance.fileClaim')}
      </Button>

      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('insurance.premiumCalculator')}
      </Text>
      <Card style={styles.calcCard}>
        <Card.Content>
          <Text variant="titleSmall" style={{ marginBottom: SPACING.sm }}>
            {t('animals.species')}
          </Text>
          <RadioButton.Group onValueChange={setCalcSpecies} value={calcSpecies}>
            <View style={styles.radioRow}>
              {['cattle', 'goat', 'sheep', 'poultry'].map((sp) => (
                <View key={sp} style={styles.radioItem} accessibilityLabel={`${t(`animals.${sp}`)} species`} accessibilityRole="radio" accessibilityState={{ checked: calcSpecies === sp }}>
                  <RadioButton value={sp} color={colors.primary} />
                  <Text>{t(`animals.${sp}`)}</Text>
                </View>
              ))}
            </View>
          </RadioButton.Group>

          <TextInput
            label={t('animals.age')}
            value={calcAge}
            onChangeText={setCalcAge}
            mode="outlined"
            keyboardType="numeric"
            style={styles.calcInput}
            outlineColor="#BDBDBD"
            activeOutlineColor={colors.primary}
          />

          <Button
            mode="contained"
            onPress={calculatePremium}
            style={styles.calcButton}
            contentStyle={{ minHeight: TOUCH_TARGET_MIN }}
          >
            {t('insurance.calculate')}
          </Button>

          {calcResult !== null && (
            <View style={styles.resultBox}>
              <Text variant="bodyLarge">{t('insurance.estimatedPremium')}</Text>
              <Text variant="headlineMedium" style={styles.resultAmount}>
                \u20B9{calcResult}/year
              </Text>
            </View>
          )}
        </Card.Content>
      </Card>

      <Portal>
        <Modal
          visible={claimVisible}
          onDismiss={() => { setClaimVisible(false); setPhotoUri(null); }}
          contentContainerStyle={styles.modal}
        >
          <View style={styles.modalHeader}>
            <Text variant="titleLarge" style={styles.modalTitle}>
              {t('insurance.fileClaim')}
            </Text>
            <IconButton
              icon="close"
              size={24}
              onPress={() => setClaimVisible(false)}
              accessibilityLabel="Close claim form"
            />
          </View>
          <TextInput
            label={t('insurance.claimDescription')}
            value={claimDesc}
            onChangeText={setClaimDesc}
            mode="outlined"
            multiline
            numberOfLines={4}
            style={styles.calcInput}
            outlineColor="#BDBDBD"
            activeOutlineColor={colors.primary}
          />
          <Button
            mode="outlined"
            icon="camera"
            onPress={showPhotoOptions}
            style={{ marginBottom: SPACING.md, borderColor: colors.primary }}
            contentStyle={{ minHeight: TOUCH_TARGET_MIN }}
          >
            {photoUri ? t('insurance.changePhoto') : t('insurance.addPhoto')}
          </Button>
          {photoUri && (
            <Text variant="bodySmall" style={{ marginBottom: SPACING.md, color: statusColors.healthy }}>
              {t('insurance.photoAttached')}
            </Text>
          )}
          <Button
            mode="contained"
            loading={uploading}
            disabled={uploading}
            onPress={async () => {
              setUploading(true);
              try {
                const claimRes = await api.post<{ id: string }>('/insurance/claims', { description: claimDesc });
                if (photoUri && claimAnimalId) {
                  await uploadPhoto(photoUri, claimAnimalId);
                }
                showSuccess(t('insurance.claimSubmitted'));
              } catch (e) {
                showError(e instanceof Error ? e.message : t('insurance.claimFailed'));
              } finally {
                setUploading(false);
              }
              setClaimVisible(false);
              setClaimDesc('');
              setPhotoUri(null);
              setClaimAnimalId(null);
            }}
            style={styles.calcButton}
            contentStyle={{ minHeight: TOUCH_TARGET_MIN }}
          >
            {t('common.submit')}
          </Button>
        </Modal>
      </Portal>
    </ScrollView>
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
    color: colors.primary,
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
  sectionTitle: {
    color: '#212121',
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
    marginTop: SPACING.lg,
  },
  policyCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
    borderLeftWidth: 4,
  },
  activeCard: {
    borderLeftColor: statusColors.healthy,
  },
  expiredCard: {
    borderLeftColor: statusColors.urgent,
  },
  policyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  speciesEmoji: {
    fontSize: 32,
    marginRight: SPACING.sm,
  },
  policyInfo: {
    flex: 1,
  },
  animalName: {
    fontWeight: 'bold',
    color: '#212121',
  },
  policyNum: {
    color: '#616161',
  },
  statusBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: 4,
    borderRadius: 8,
  },
  policyDetails: {
    gap: 4,
  },
  dueDate: {
    color: '#FF8F00',
    fontWeight: 'bold',
  },
  claimButton: {
    backgroundColor: statusColors.urgent,
    borderRadius: CARD_BORDER_RADIUS,
    marginTop: SPACING.md,
  },
  claimContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  calcCard: {
    borderRadius: CARD_BORDER_RADIUS,
  },
  radioRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: SPACING.sm,
  },
  radioItem: {
    flexDirection: 'row',
    alignItems: 'center',
    minWidth: '45%',
    minHeight: TOUCH_TARGET_MIN,
  },
  calcInput: {
    marginBottom: SPACING.md,
    backgroundColor: '#FFFFFF',
  },
  calcButton: {
    backgroundColor: colors.primary,
    borderRadius: CARD_BORDER_RADIUS,
  },
  resultBox: {
    marginTop: SPACING.md,
    padding: SPACING.md,
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    alignItems: 'center',
  },
  resultAmount: {
    color: statusColors.healthy,
    fontWeight: 'bold',
  },
  modal: {
    backgroundColor: '#FFFFFF',
    margin: SPACING.lg,
    padding: SPACING.lg,
    borderRadius: CARD_BORDER_RADIUS,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  modalTitle: {
    color: colors.primary,
    fontWeight: 'bold',
    flex: 1,
  },
});
