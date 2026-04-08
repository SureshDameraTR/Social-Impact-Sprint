import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, Text, Menu } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';

interface Medicine {
  key: string;
  name: string;
  withdrawalDays: { milk: number; meat: number };
}

const MEDICINES: Medicine[] = [
  { key: 'oxytetracycline', name: 'Oxytetracycline', withdrawalDays: { milk: 7, meat: 28 } },
  { key: 'ivermectin', name: 'Ivermectin', withdrawalDays: { milk: 5, meat: 35 } },
  { key: 'penicillin', name: 'Penicillin', withdrawalDays: { milk: 4, meat: 14 } },
  { key: 'enrofloxacin', name: 'Enrofloxacin', withdrawalDays: { milk: 7, meat: 14 } },
  { key: 'albendazole', name: 'Albendazole', withdrawalDays: { milk: 5, meat: 14 } },
  { key: 'meloxicam', name: 'Meloxicam', withdrawalDays: { milk: 5, meat: 15 } },
  { key: 'amoxicillin', name: 'Amoxicillin', withdrawalDays: { milk: 3, meat: 21 } },
];

const ANIMALS = [
  { key: '1', name: 'Lakshmi', emoji: '🐄' },
  { key: '2', name: 'Gowri', emoji: '🐄' },
  { key: '3', name: 'Nandi', emoji: '🐄' },
  { key: '4', name: 'Malli', emoji: '🐐' },
];

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

const TODAY = '2026-04-08';

const MOCK_WITHDRAWALS: WithdrawalEntry[] = [
  {
    id: '1',
    animalName: 'Lakshmi',
    animalEmoji: '🐄',
    medicineName: 'Oxytetracycline',
    adminDate: '2026-04-05',
    milkSafeDate: '2026-04-12',
    meatSafeDate: '2026-05-03',
    milkDaysLeft: 4,
    meatDaysLeft: 25,
  },
  {
    id: '2',
    animalName: 'Gowri',
    animalEmoji: '🐄',
    medicineName: 'Penicillin',
    adminDate: '2026-04-02',
    milkSafeDate: '2026-04-06',
    meatSafeDate: '2026-04-16',
    milkDaysLeft: -2,
    meatDaysLeft: 8,
  },
];

export default function MedicineLogScreen() {
  const { t } = useTranslation();
  const [selectedMedicine, setSelectedMedicine] = useState<Medicine | null>(null);
  const [selectedAnimal, setSelectedAnimal] = useState<typeof ANIMALS[0] | null>(null);
  const [medMenuVisible, setMedMenuVisible] = useState(false);
  const [animalMenuVisible, setAnimalMenuVisible] = useState(false);
  const [withdrawals, setWithdrawals] = useState(MOCK_WITHDRAWALS);

  const administer = () => {
    if (!selectedMedicine || !selectedAnimal) return;
    const newEntry: WithdrawalEntry = {
      id: String(Date.now()),
      animalName: selectedAnimal.name,
      animalEmoji: selectedAnimal.emoji,
      medicineName: selectedMedicine.name,
      adminDate: TODAY,
      milkSafeDate: `+${selectedMedicine.withdrawalDays.milk} days`,
      meatSafeDate: `+${selectedMedicine.withdrawalDays.meat} days`,
      milkDaysLeft: selectedMedicine.withdrawalDays.milk,
      meatDaysLeft: selectedMedicine.withdrawalDays.meat,
    };
    setWithdrawals((prev) => [newEntry, ...prev]);
    setSelectedMedicine(null);
    setSelectedAnimal(null);
  };

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
                {selectedAnimal ? `${selectedAnimal.emoji} ${selectedAnimal.name}` : t('medicineLog.selectAnimal')}
              </Button>
            }
            contentStyle={styles.menuContent}
          >
            {ANIMALS.map((animal) => (
              <Menu.Item
                key={animal.key}
                onPress={() => {
                  setSelectedAnimal(animal);
                  setAnimalMenuVisible(false);
                }}
                title={`${animal.emoji} ${animal.name}`}
                style={{ minHeight: TOUCH_TARGET_MIN }}
              />
            ))}
          </Menu>

          <Button
            mode="contained"
            onPress={administer}
            style={styles.adminButton}
            contentStyle={styles.adminContent}
            disabled={!selectedMedicine || !selectedAnimal}
            icon="needle"
          >
            {t('medicineLog.administer')}
          </Button>
        </Card.Content>
      </Card>

      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('medicineLog.activeWithdrawals')}
      </Text>

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
                  <Text style={{ fontSize: 20 }}>🥛</Text>
                  <Text variant="bodySmall" style={{ color: milkSafe ? '#2E7D32' : '#D32F2F', fontWeight: 'bold' }}>
                    {milkSafe
                      ? t('medicineLog.milkSafe')
                      : `${t('medicineLog.milkUnsafe')} ${entry.milkSafeDate}`}
                  </Text>
                </View>
                <View style={[styles.statusCard, { backgroundColor: meatSafe ? '#E8F5E9' : '#FFEBEE' }]}>
                  <Text style={{ fontSize: 20 }}>🥩</Text>
                  <Text variant="bodySmall" style={{ color: meatSafe ? '#2E7D32' : '#D32F2F', fontWeight: 'bold' }}>
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
  formCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.lg,
  },
  formTitle: {
    color: '#2E7D32',
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
    backgroundColor: '#2E7D32',
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
