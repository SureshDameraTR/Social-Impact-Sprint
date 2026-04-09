import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, Text, TextInput, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';
import { api } from '../src/config/api';

interface PashuRecord {
  id: string;
  animalName: string;
  species: string;
  speciesEmoji: string;
  breed: string;
  gender: string;
  age: string;
  ownerName: string;
  ownerPhone: string;
  district: string;
  village: string;
  vaccinations: { name: string; date: string; status: string }[];
  synced: boolean;
}

export default function PashuAadhaarScreen() {
  const { t } = useTranslation();
  const [idInput, setIdInput] = useState('');
  const [result, setResult] = useState<PashuRecord | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLookup = async () => {
    const cleaned = idInput.replace(/\s/g, '');
    setLoading(true);
    setError(null);
    setNotFound(false);
    setResult(null);
    try {
      const record = await api.get<PashuRecord>(`/bharat-pashudhan/lookup?id=${cleaned}`);
      setResult(record);
    } catch (err: any) {
      if (err.message && err.message.includes('404')) {
        setNotFound(true);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('pashuAadhaar.title')}
      </Text>
      <Text variant="bodyMedium" style={styles.subtitle}>
        {t('pashuAadhaar.subtitle')}
      </Text>

      <TextInput
        label={t('pashuAadhaar.enterID')}
        value={idInput}
        onChangeText={setIdInput}
        mode="outlined"
        keyboardType="numeric"
        maxLength={14}
        style={styles.input}
        outlineColor="#BDBDBD"
        activeOutlineColor="#2E7D32"
        left={<TextInput.Icon icon="card-account-details" />}
        placeholder="XXXX XXXX XXXX"
      />

      <Button
        mode="contained"
        onPress={handleLookup}
        style={styles.lookupButton}
        contentStyle={styles.lookupContent}
        labelStyle={styles.lookupLabel}
        disabled={idInput.replace(/\s/g, '').length < 12 || loading}
        loading={loading}
        icon="magnify"
      >
        {t('pashuAadhaar.lookUp')}
      </Button>

      {error && (
        <Card style={styles.notFoundCard}>
          <Card.Content style={styles.notFoundContent}>
            <Text style={styles.notFoundEmoji}>{'\u26A0\uFE0F'}</Text>
            <Text variant="titleMedium" style={styles.notFoundText}>
              {error}
            </Text>
          </Card.Content>
        </Card>
      )}

      {notFound && (
        <Card style={styles.notFoundCard}>
          <Card.Content style={styles.notFoundContent}>
            <Text style={styles.notFoundEmoji}>{'\uD83D\uDD0D'}</Text>
            <Text variant="titleMedium" style={styles.notFoundText}>
              {t('pashuAadhaar.notFound')}
            </Text>
          </Card.Content>
        </Card>
      )}

      {result && (
        <View style={styles.resultSection}>
          <Card style={styles.resultCard}>
            <Card.Content>
              <View style={styles.resultHeader}>
                <Text style={styles.resultEmoji}>{result.speciesEmoji}</Text>
                <View style={{ flex: 1 }}>
                  <Text variant="headlineSmall" style={styles.resultName}>
                    {result.animalName}
                  </Text>
                  <Text variant="bodySmall" style={styles.resultId}>
                    ID: {result.id}
                  </Text>
                </View>
              </View>

              <View style={styles.detailGrid}>
                <DetailRow label={t('animals.species')} value={result.species} />
                <DetailRow label={t('animals.breed')} value={result.breed} />
                <DetailRow label={t('animals.gender')} value={result.gender} />
                <DetailRow label={t('animals.age')} value={result.age} />
              </View>
            </Card.Content>
          </Card>

          <Card style={styles.ownerCard}>
            <Card.Content>
              <Text variant="titleMedium" style={styles.sectionTitle}>
                {t('pashuAadhaar.ownerInfo')}
              </Text>
              <DetailRow label={t('onboarding.nameLabel')} value={result.ownerName} />
              <DetailRow label={t('onboarding.phoneLabel')} value={result.ownerPhone} />
              <DetailRow label={t('pashuAadhaar.district')} value={result.district} />
              <DetailRow label={t('pashuAadhaar.village')} value={result.village} />
            </Card.Content>
          </Card>

          <Card style={styles.vaccCard}>
            <Card.Content>
              <Text variant="titleMedium" style={styles.sectionTitle}>
                {t('pashuAadhaar.vaccinationHistory')}
              </Text>
              {result.vaccinations.map((v, i) => (
                <View key={i} style={styles.vaccRow}>
                  <Text variant="bodyMedium" style={{ flex: 1 }}>{v.name}</Text>
                  <Text variant="bodySmall" style={styles.vaccDate}>{v.date}</Text>
                  <View style={[
                    styles.vaccStatus,
                    { backgroundColor: v.status === 'done' ? '#E8F5E9' : '#FFF3E0' },
                  ]}>
                    <Text style={{
                      color: v.status === 'done' ? '#2E7D32' : '#FF8F00',
                      fontSize: 12,
                      fontWeight: 'bold',
                    }}>
                      {v.status === 'done' ? '\u2713' : '\u23F3'}
                    </Text>
                  </View>
                </View>
              ))}
            </Card.Content>
          </Card>

          <Card style={[styles.syncCard, { backgroundColor: result.synced ? '#E8F5E9' : '#FFF3E0' }]}>
            <Card.Content style={styles.syncContent}>
              <Text variant="bodyLarge" style={{ color: result.synced ? '#2E7D32' : '#E65100' }}>
                {result.synced
                  ? t('pashuAadhaar.synced')
                  : t('pashuAadhaar.notRegistered')}
              </Text>
            </Card.Content>
          </Card>
        </View>
      )}
    </ScrollView>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={detailStyles.row}>
      <Text variant="bodySmall" style={detailStyles.label}>{label}</Text>
      <Text variant="bodyMedium" style={detailStyles.value}>{value}</Text>
    </View>
  );
}

const detailStyles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
  },
  label: {
    color: '#616161',
  },
  value: {
    color: '#212121',
    fontWeight: 'bold',
  },
});

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
  },
  subtitle: {
    color: '#616161',
    marginBottom: SPACING.lg,
  },
  input: {
    marginBottom: SPACING.md,
    backgroundColor: '#FFFFFF',
  },
  lookupButton: {
    backgroundColor: '#2E7D32',
    borderRadius: CARD_BORDER_RADIUS,
  },
  lookupContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  lookupLabel: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  notFoundCard: {
    marginTop: SPACING.lg,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFF3E0',
  },
  notFoundContent: {
    alignItems: 'center',
    padding: SPACING.lg,
  },
  notFoundEmoji: {
    fontSize: 48,
    marginBottom: SPACING.sm,
  },
  notFoundText: {
    color: '#E65100',
  },
  resultSection: {
    marginTop: SPACING.lg,
  },
  resultCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  resultEmoji: {
    fontSize: 48,
    marginRight: SPACING.md,
  },
  resultName: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  resultId: {
    color: '#616161',
  },
  detailGrid: {},
  ownerCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
  },
  vaccCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
  },
  sectionTitle: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
  },
  vaccRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
  },
  vaccDate: {
    color: '#616161',
    marginRight: SPACING.sm,
  },
  vaccStatus: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  syncCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
  },
  syncContent: {
    alignItems: 'center',
    padding: SPACING.md,
  },
});
