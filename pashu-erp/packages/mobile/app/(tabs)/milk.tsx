import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet, Pressable, StatusBar, AccessibilityInfo } from 'react-native';
import { Text, Button, SegmentedButtons, Card, Snackbar, HelperText, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { MicButton } from '../../src/components/MicButton';
import { useSnackbar } from '../../src/hooks/useSnackbar';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, colors } from '../../src/config/theme';
import { api } from '../../src/config/api';

interface CattleAnimal {
  id: string;
  name: string;
  species: string;
}

const NUMPAD = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', '\u232B'];

const MIN_QUANTITY = 0.1;
const MAX_QUANTITY = 999;

function validateQuantity(value: string, t: (key: string, opts?: Record<string, unknown>) => string): string | null {
  const num = parseFloat(value);
  if (isNaN(num) || num < 0) return t('errors.invalidQuantity');
  if (num < MIN_QUANTITY) return t('errors.minimumQuantity', { min: MIN_QUANTITY });
  if (num > MAX_QUANTITY) return t('errors.maximumQuantity', { max: MAX_QUANTITY });
  return null;
}

export default function MilkScreen() {
  const { t } = useTranslation();
  const { showError } = useSnackbar();
  const [cows, setCows] = useState<CattleAnimal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [todayTotal, setTodayTotal] = useState<number | null>(null);
  const [session, setSession] = useState('morning');
  const [selectedAnimal, setSelectedAnimal] = useState('');
  const [quantity, setQuantity] = useState('');
  const [quantityError, setQuantityError] = useState<string | null>(null);
  const [snackVisible, setSnackVisible] = useState(false);
  const [snackMessage, setSnackMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      api.get<CattleAnimal[]>('/animals?species=cattle'),
      api.get<{ total_liters: number }>('/milk/today').catch(() => ({ total_liters: 0 })),
    ])
      .then(([animals, milkToday]) => {
        setCows(Array.isArray(animals) ? animals : (animals as any).data ?? []);
        setTodayTotal(milkToday.total_liters);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSelectAnimal = useCallback((id: string) => {
    setSelectedAnimal(id);
  }, []);

  const handleRecord = useCallback(async () => {
    const err = validateQuantity(quantity, t);
    if (err) {
      setQuantityError(err);
      return;
    }
    setQuantityError(null);
    setIsSubmitting(true);
    try {
      await api.post('/milk/yield', {
        animal_id: selectedAnimal,
        session,
        quantity_liters: parseFloat(quantity),
      });
      const msg = t('milk.recorded');
      setSnackMessage(msg);
      setSnackVisible(true);
      AccessibilityInfo.announceForAccessibility(msg);
      setQuantity('');
      setSelectedAnimal('');
      // Refresh today total
      api.get<{ total_liters: number }>('/milk/today').then(res => setTodayTotal(res.total_liters)).catch(() => {});
    } catch (e) {
      showError(t('milk.recordFailed'));
    } finally {
      setIsSubmitting(false);
    }
  }, [quantity, selectedAnimal, session, t, showError]);

  const handleVoiceResult = useCallback((value: number) => {
    const clamped = Math.max(MIN_QUANTITY, Math.min(MAX_QUANTITY, value));
    setQuantity(String(clamped));
    setQuantityError(null);
    setSnackMessage(`${clamped}L`);
  }, []);

  const handleVoiceTranscript = useCallback((text: string) => {
    setSnackMessage((prev) => `${text} \u2014 ${prev || '...'}`);
    setSnackVisible(true);
  }, []);

  const handleNumpad = useCallback((key: string) => {
    if (key === '\u232B') {
      setQuantity((prev) => prev.slice(0, -1));
      setQuantityError(null);
    } else if (key === '.' && quantity.includes('.')) {
      return;
    } else {
      if (quantity.length >= 5) return;
      if (quantity.includes('.') && quantity.split('.')[1].length >= 1) return;
      const newVal = quantity + key;
      setQuantity(newVal);
      const num = parseFloat(newVal);
      if (!isNaN(num) && num >= MIN_QUANTITY && num <= MAX_QUANTITY) {
        setQuantityError(null);
      }
    }
  }, [quantity]);

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
          onAction={fetchData}
        />
      </View>
    );
  }

  if (cows.length === 0) {
    return (
      <View style={styles.container}>
        <EmptyState
          icon={'\uD83E\uDD5B'}
          title={t('empty.noMilkRecords')}
          subtitle={t('milk.recordMilk')}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F0" />
      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Header card */}
        <View style={styles.headerCard}>
          <Text variant="bodyMedium" style={styles.headerLabel}>
            {t('milk.todayTotal')}
          </Text>
          <Text style={styles.headerAmount}>
            {todayTotal !== null ? todayTotal.toFixed(1) : '\u2014'} <Text style={styles.headerUnit}>{t('milk.liters')}</Text>
          </Text>
        </View>

        {/* Session picker (AM/PM) */}
        <SegmentedButtons
          value={session}
          onValueChange={setSession}
          buttons={[
            {
              value: 'morning',
              label: `\u2600\uFE0F ${t('milk.morning')}`,
              style: session === 'morning' ? styles.segActiveBtn : undefined,
            },
            {
              value: 'evening',
              label: `\uD83C\uDF19 ${t('milk.evening')}`,
              style: session === 'evening' ? styles.segActiveBtn : undefined,
            },
          ]}
          style={styles.segmented}
        />

        {/* Animal picker */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          {t('milk.selectAnimal')}
        </Text>
        <View style={styles.animalPicker}>
          {cows.map((cow) => (
            <Pressable
              key={cow.id}
              onPress={() => handleSelectAnimal(cow.id)}
              style={[
                styles.animalChip,
                selectedAnimal === cow.id && styles.animalChipSelected,
              ]}
              accessibilityLabel={cow.name}
              accessibilityRole="radio"
              accessibilityState={{ checked: selectedAnimal === cow.id }}
            >
              <Text style={styles.animalEmoji}>{'\uD83D\uDC04'}</Text>
              <Text style={[
                styles.animalChipText,
                selectedAnimal === cow.id && styles.animalChipTextSelected,
              ]}>
                {cow.name}
              </Text>
            </Pressable>
          ))}
        </View>

        {/* Quantity display + mic */}
        <View style={styles.quantitySection}>
          <View style={styles.quantityDisplay}>
            <Text
              style={styles.quantityText}
              accessibilityLabel={`${t('milk.quantity')}: ${quantity || '0.0'} ${t('milk.liters')}`}
            >
              {quantity || '0.0'}
            </Text>
            <Text style={styles.quantityUnit}>{t('milk.liters')}</Text>
          </View>
          <MicButton
            context="milk_quantity"
            onResult={handleVoiceResult}
            onTranscript={handleVoiceTranscript}
          />
        </View>
        {!!quantityError && (
          <HelperText type="error" visible={!!quantityError} style={styles.errorText}>
            {quantityError}
          </HelperText>
        )}

        {/* Numpad */}
        <View style={styles.numpadGrid}>
          {NUMPAD.map((key) => (
            <Pressable
              key={key}
              onPress={() => handleNumpad(key)}
              style={styles.numpadKey}
              accessibilityLabel={key === '\u232B' ? t('common.delete') : key}
              accessibilityRole="button"
            >
              <Text style={styles.numpadText}>{key}</Text>
            </Pressable>
          ))}
        </View>

        {/* Record button */}
        <Button
          mode="contained"
          onPress={handleRecord}
          disabled={isSubmitting || !selectedAnimal || !quantity}
          loading={isSubmitting}
          style={styles.recordButton}
          contentStyle={styles.recordButtonContent}
          labelStyle={styles.recordButtonLabel}
          buttonColor={colors.primary}
          accessibilityLabel={t('milk.recordMilk')}
        >
          {t('milk.recordMilk')}
        </Button>

        {/* History link */}
        <Button
          mode="text"
          onPress={() => router.push('/milk/history')}
          icon="history"
          style={styles.historyButton}
          labelStyle={styles.historyLabel}
          textColor={colors.primary}
        >
          {t('milk.history')}
        </Button>
      </ScrollView>

      <Snackbar
        visible={snackVisible}
        onDismiss={() => setSnackVisible(false)}
        duration={2000}
        style={styles.snackbar}
      >
        {snackMessage}
      </Snackbar>
    </View>
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
  headerCard: {
    backgroundColor: '#A8F5C8',
    borderRadius: CARD_BORDER_RADIUS + 4,
    paddingVertical: SPACING.lg,
    paddingHorizontal: SPACING.lg,
    alignItems: 'center',
    marginBottom: SPACING.lg,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  headerLabel: {
    color: '#002112',
    opacity: 0.8,
  },
  headerAmount: {
    fontSize: 56,
    fontWeight: '700',
    color: colors.primary,
    lineHeight: 64,
  },
  headerUnit: {
    fontSize: 24,
    fontWeight: '500',
    color: colors.primary,
  },
  segmented: {
    marginBottom: SPACING.md,
  },
  segActiveBtn: {
    backgroundColor: '#A8F5C8',
  },
  sectionTitle: {
    marginTop: SPACING.sm,
    marginBottom: SPACING.sm,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  animalPicker: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
    marginBottom: SPACING.md,
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
  quantitySection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: SPACING.lg,
    marginVertical: SPACING.md,
  },
  quantityDisplay: {
    alignItems: 'center',
  },
  quantityText: {
    fontSize: 64,
    fontWeight: '700',
    color: colors.primary,
    lineHeight: 72,
  },
  quantityUnit: {
    fontSize: 16,
    color: '#414941',
    marginTop: -4,
  },
  errorText: {
    textAlign: 'center',
  },
  numpadGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: SPACING.sm,
    marginBottom: SPACING.lg,
  },
  numpadKey: {
    width: '30%',
    aspectRatio: 2,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 2,
  },
  numpadText: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  recordButton: {
    borderRadius: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  recordButtonContent: {
    height: 56,
  },
  recordButtonLabel: {
    fontSize: 18,
    fontWeight: '700',
  },
  historyButton: {
    marginTop: SPACING.md,
  },
  historyLabel: {
    fontSize: 16,
  },
  snackbar: {
    backgroundColor: colors.primary,
  },
});
