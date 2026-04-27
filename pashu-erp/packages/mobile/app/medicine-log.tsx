import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, Text, Menu, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '../src/hooks/useSnackbar';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors, statusColors } from '../src/config/theme';
import { api } from '../src/config/api';
import { MEDICINES, type Medicine } from '../src/config/medicines';

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

interface WithdrawalEntry {
  id: string;
  animalName: string;
  animalEmoji: string;
  medicineName: string;
  adminDate: string;
  milkSafeDate: string;
  meatSafeDate: string;
  milkDaysLeft: number;
  meatDaysLeft: number;
}

export default function MedicineLogScreen() {
  const { t } = useTranslation();
  const { showError } = useSnackbar();
  const [animals, setAnimals] = useState<AnimalOption[]>([]);
  const [withdrawals, setWithdrawals] = useState<WithdrawalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMedicine, setSelectedMedicine] = useState<Medicine | null>(null);
  const [selectedAnimal, setSelectedAnimal] = useState<AnimalOption | null>(null);
  const [medMenuVisible, setMedMenuVisible] = useState(false);
  const [animalMenuVisible, setAnimalMenuVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      api.get<AnimalOption[]>('/animals'),
      api.get<WithdrawalEntry[]>('/medicine-log/withdrawals'),
    ])
      .then(([animalsData, withdrawalsData]) => {
        setAnimals(Array.isArray(animalsData) ? animalsData : (animalsData as any).data ?? []);
        setWithdrawals(Array.isArray(withdrawalsData) ? withdrawalsData : (withdrawalsData as any).data ?? []);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const administer = async () => {
    if (!selectedMedicine || !selectedAnimal) return;
    setIsSubmitting(true);
    try {
      const result = await api.post<WithdrawalEntry>('/medicine-log/administer', {
        animalId: selectedAnimal.id,
        medicineKey: selectedMedicine.key,
      });
      setWithdrawals((prev) => [result, ...prev]);
      setSelectedMedicine(null);
      setSelectedAnimal(null);
    } catch (e) {
      showError(t('medicinelog.saveFailed'));
    } finally {
      setIsSubmitting(false);
    }
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
          onAction={fetchData}
        />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('medicineLog.title')}
      </Text>

      <Card style={styles.formCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.formTitle}>
            {t('medicineLog.administerMedicine')}
          </Text>

          <Menu
            visible={medMenuVisible}
            onDismiss={() => setMedMenuVisible(false)}
            anchor={
              <Button
                mode="outlined"
                onPress={() => setMedMenuVisible(true)}
                style={styles.dropdown}
                contentStyle={styles.dropdownContent}
                icon="pill"
              >
                {selectedMedicine?.name || t('medicineLog.selectMedicine')}
              </Button>
            }
            contentStyle={styles.menuContent}
          >
            {MEDICINES.map((med) => (
              <Menu.Item
                key={med.key}
                onPress={() => {
                  setSelectedMedicine(med);
                  setMedMenuVisible(false);
                }}
                title={`${med.name} (${t('medicineLog.milkWithdrawal')}: ${med.withdrawalDays.milk}d)`}
                style={{ minHeight: TOUCH_TARGET_MIN }}
              />
            ))}
          </Menu>

          <Menu
            visible={animalMenuVisible}
            onDismiss={() => setAnimalMenuVisible(false)}
            anchor={
              <Button
                mode="outlined"
                onPress={() => setAnimalMenuVisible(true)}
                style={styles.dropdown}
                contentStyle={styles.dropdownContent}
                icon="cow"
              >
                {selectedAnimal ? `${SPECIES_EMOJI[selectedAnimal.species] || '\uD83D\uDC3E'} ${selectedAnimal.name}` : t('medicineLog.selectAnimal')}
              </Button>
            }
            contentStyle={styles.menuContent}
          >
            {animals.map((animal) => (
              <Menu.Item
                key={animal.id}
                onPress={() => {
                  setSelectedAnimal(animal);
                  setAnimalMenuVisible(false);
                }}
                title={`${SPECIES_EMOJI[animal.species] || '\uD83D\uDC3E'} ${animal.name}`}
                style={{ minHeight: TOUCH_TARGET_MIN }}
              />
            ))}
          </Menu>

          <Button
            mode="contained"
            onPress={administer}
            style={styles.adminButton}
            contentStyle={styles.adminContent}
            disabled={isSubmitting || !selectedMedicine || !selectedAnimal}
            loading={isSubmitting}
            icon="needle"
          >
            {t('medicineLog.administer')}
          </Button>
        </Card.Content>
      </Card>

      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('medicineLog.activeWithdrawals')}
      </Text>

      {withdrawals.length === 0 && (
        <EmptyState
          icon={'\uD83D\uDC8A'}
          title={t('common.noData')}
          subtitle={t('medicineLog.activeWithdrawals')}
        />
      )}

      {withdrawals.map((entry) => {
        const milkSafe = entry.milkDaysLeft <= 0;
        const meatSafe = entry.meatDaysLeft <= 0;
        return (
          <Card key={entry.id} style={styles.withdrawalCard}>
            <Card.Content>
              <View style={styles.withdrawalHeader}>
                <Text style={styles.withdrawalEmoji}>{entry.animalEmoji}</Text>
                <View style={{ flex: 1 }}>
                  <Text variant="titleSmall" style={styles.withdrawalAnimal}>
                    {entry.animalName} — {entry.medicineName}
                  </Text>
                  <Text variant="bodySmall" style={styles.withdrawalDate}>
                    {t('medicineLog.administered')}: {entry.adminDate}
                  </Text>
                </View>
              </View>

              <View style={styles.statusRow}>
                <View style={[styles.statusCard, { backgroundColor: milkSafe ? '#E8F5E9' : '#FFEBEE' }]}>
                  <Text style={{ fontSize: 20 }}>{'\uD83E\uDD5B'}</Text>
                  <Text variant="bodySmall" style={{ color: milkSafe ? statusColors.healthy : statusColors.urgent, fontWeight: 'bold' }}>
                    {milkSafe
                      ? t('medicineLog.milkSafe')
                      : `${t('medicineLog.milkUnsafe')} ${entry.milkSafeDate}`}
                  </Text>
                </View>
                <View style={[styles.statusCard, { backgroundColor: meatSafe ? '#E8F5E9' : '#FFEBEE' }]}>
                  <Text style={{ fontSize: 20 }}>{'\uD83E\uDD69'}</Text>
                  <Text variant="bodySmall" style={{ color: meatSafe ? statusColors.healthy : statusColors.urgent, fontWeight: 'bold' }}>
                    {meatSafe
                      ? t('medicineLog.meatSafe')
                      : `${t('medicineLog.meatUnsafe')} ${entry.meatSafeDate}`}
                  </Text>
                </View>
              </View>
            </Card.Content>
          </Card>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
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
  formCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.lg,
  },
  formTitle: {
    color: colors.primary,
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
  dropdown: {
    marginBottom: SPACING.md,
    borderRadius: CARD_BORDER_RADIUS,
    borderColor: '#BDBDBD',
  },
  dropdownContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
    justifyContent: 'flex-start',
  },
  menuContent: {
    backgroundColor: '#FFFFFF',
    maxHeight: 300,
  },
  adminButton: {
    backgroundColor: colors.primary,
    borderRadius: CARD_BORDER_RADIUS,
  },
  adminContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  sectionTitle: {
    color: '#212121',
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
  },
  withdrawalCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
  },
  withdrawalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  withdrawalEmoji: {
    fontSize: 32,
    marginRight: SPACING.sm,
  },
  withdrawalAnimal: {
    color: '#212121',
    fontWeight: 'bold',
  },
  withdrawalDate: {
    color: '#616161',
  },
  statusRow: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  statusCard: {
    flex: 1,
    padding: SPACING.sm,
    borderRadius: 12,
    alignItems: 'center',
    gap: 4,
  },
});
