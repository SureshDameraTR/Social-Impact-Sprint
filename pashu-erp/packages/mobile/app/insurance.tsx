import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, Text, TextInput, Modal, Portal, RadioButton } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';

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

const MOCK_POLICIES: Policy[] = [
  {
    id: '1',
    animalName: 'Lakshmi',
    species: '🐄',
    policyNumber: 'LIC-KA-2026-4521',
    provider: 'LIC',
    status: 'active',
    premiumDue: '2026-05-01',
    daysUntilDue: 23,
    sumInsured: 80000,
  },
  {
    id: '2',
    animalName: 'Gowri',
    species: '🐄',
    policyNumber: 'NAIS-KA-2025-8932',
    provider: 'NAIS',
    status: 'expired',
    premiumDue: '2026-03-15',
    daysUntilDue: -24,
    sumInsured: 60000,
  },
];

export default function InsuranceScreen() {
  const { t } = useTranslation();
  const [claimVisible, setClaimVisible] = useState(false);
  const [claimDesc, setClaimDesc] = useState('');
  const [calcSpecies, setCalcSpecies] = useState('cattle');
  const [calcAge, setCalcAge] = useState('');
  const [calcResult, setCalcResult] = useState<number | null>(null);

  const calculatePremium = () => {
    const baseRates: Record<string, number> = { cattle: 1200, goat: 400, sheep: 350, poultry: 50 };
    const base = baseRates[calcSpecies] || 500;
    const age = parseInt(calcAge) || 3;
    const multiplier = age > 5 ? 1.5 : age > 3 ? 1.2 : 1.0;
    setCalcResult(Math.round(base * multiplier));
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('insurance.title')}
      </Text>

      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('insurance.activePolicies')}
      </Text>

      {MOCK_POLICIES.map((policy) => (
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
                  color: policy.status === 'active' ? '#2E7D32' : '#D32F2F',
                  fontWeight: 'bold',
                  fontSize: 12,
                }}>
                  {t(`insurance.${policy.status}`)}
                </Text>
              </View>
            </View>

            <View style={styles.policyDetails}>
              <Text variant="bodyMedium">
                {t('insurance.sumInsured')}: ₹{policy.sumInsured.toLocaleString()}
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
        onPress={() => setClaimVisible(true)}
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
                <View key={sp} style={styles.radioItem}>
                  <RadioButton value={sp} color="#2E7D32" />
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
            activeOutlineColor="#2E7D32"
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
                ₹{calcResult}/year
              </Text>
            </View>
          )}
        </Card.Content>
      </Card>

      <Portal>
        <Modal
          visible={claimVisible}
          onDismiss={() => setClaimVisible(false)}
          contentContainerStyle={styles.modal}
        >
          <Text variant="titleLarge" style={styles.modalTitle}>
            {t('insurance.fileClaim')}
          </Text>
          <TextInput
            label={t('insurance.claimDescription')}
            value={claimDesc}
            onChangeText={setClaimDesc}
            mode="outlined"
            multiline
            numberOfLines={4}
            style={styles.calcInput}
            outlineColor="#BDBDBD"
            activeOutlineColor="#2E7D32"
          />
          <Button
            mode="outlined"
            icon="camera"
            onPress={() => {}}
            style={{ marginBottom: SPACING.md, borderColor: '#2E7D32' }}
            contentStyle={{ minHeight: TOUCH_TARGET_MIN }}
          >
            {t('insurance.addPhoto')}
          </Button>
          <Button
            mode="contained"
            onPress={() => setClaimVisible(false)}
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
    color: '#2E7D32',
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
    borderLeftColor: '#2E7D32',
  },
  expiredCard: {
    borderLeftColor: '#D32F2F',
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
    backgroundColor: '#D32F2F',
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
    backgroundColor: '#2E7D32',
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
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  modal: {
    backgroundColor: '#FFFFFF',
    margin: SPACING.lg,
    padding: SPACING.lg,
    borderRadius: CARD_BORDER_RADIUS,
  },
  modalTitle: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
});
