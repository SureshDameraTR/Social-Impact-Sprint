import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, Checkbox, Chip, Text, TextInput, ProgressBar, RadioButton } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';

const LACTATION_STAGES = ['dry', 'early', 'mid', 'late'] as const;
type LactationStage = (typeof LACTATION_STAGES)[number];

interface Ingredient {
  key: string;
  nameKn: string;
  nameEn: string;
  costPerKg: number;
  protein: number;
  energy: number;
}

const INGREDIENTS: Ingredient[] = [
  { key: 'riceBran', nameKn: 'ಅಕ್ಕಿ ತವುಡು', nameEn: 'Rice Bran', costPerKg: 18, protein: 12, energy: 2.5 },
  { key: 'groundnutCake', nameKn: 'ಕಡಲೆ ಹಿಂಡಿ', nameEn: 'Groundnut Cake', costPerKg: 35, protein: 45, energy: 2.8 },
  { key: 'ragiStraw', nameKn: 'ರಾಗಿ ಹುಲ್ಲು', nameEn: 'Ragi Straw', costPerKg: 5, protein: 4, energy: 1.5 },
  { key: 'cottonSeedCake', nameKn: 'ಹತ್ತಿ ಹಿಂಡಿ', nameEn: 'Cotton Seed Cake', costPerKg: 28, protein: 22, energy: 2.6 },
  { key: 'maizeGrain', nameKn: 'ಮೆಕ್ಕೆಜೋಳ', nameEn: 'Maize Grain', costPerKg: 22, protein: 9, energy: 3.3 },
  { key: 'greenGrass', nameKn: 'ಹಸಿರು ಹುಲ್ಲು', nameEn: 'Green Grass', costPerKg: 3, protein: 8, energy: 2.0 },
  { key: 'jowarStraw', nameKn: 'ಜೋಳದ ಹುಲ್ಲು', nameEn: 'Jowar Straw', costPerKg: 4, protein: 3, energy: 1.4 },
  { key: 'mineralMix', nameKn: 'ಖನಿಜ ಮಿಶ್ರಣ', nameEn: 'Mineral Mixture', costPerKg: 80, protein: 0, energy: 0 },
];

interface RationResult {
  ingredients: { name: string; qty: number; cost: number }[];
  totalCost: number;
  proteinBalance: number;
  energyBalance: number;
}

export default function FeedCalculatorScreen() {
  const { t, i18n } = useTranslation();
  const isKn = i18n.language === 'kn';
  const [species, setSpecies] = useState('cattle');
  const [weight, setWeight] = useState('');
  const [stage, setStage] = useState<LactationStage>('mid');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<RationResult | null>(null);

  const toggleIngredient = (key: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const calculate = () => {
    const w = parseInt(weight) || 300;
    const stageMultipliers: Record<LactationStage, number> = {
      dry: 0.6, early: 1.2, mid: 1.0, late: 0.8,
    };
    const mult = stageMultipliers[stage];
    const baseIntake = w * 0.025 * mult;

    const activeIngredients = INGREDIENTS.filter((ing) => selected.has(ing.key));
    if (activeIngredients.length === 0) return;

    const perIngredient = baseIntake / activeIngredients.length;
    const items = activeIngredients.map((ing) => ({
      name: isKn ? ing.nameKn : ing.nameEn,
      qty: Math.round(perIngredient * 10) / 10,
      cost: Math.round(perIngredient * ing.costPerKg),
    }));

    const totalCost = items.reduce((s, i) => s + i.cost, 0);
    const totalProtein = activeIngredients.reduce((s, ing) => s + ing.protein, 0) / activeIngredients.length;
    const totalEnergy = activeIngredients.reduce((s, ing) => s + ing.energy, 0) / activeIngredients.length;

    setResult({
      ingredients: items,
      totalCost,
      proteinBalance: Math.min(totalProtein / 20, 1),
      energyBalance: Math.min(totalEnergy / 3, 1),
    });
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('feed.title')}
      </Text>

      <Text variant="titleSmall" style={styles.label}>
        {t('animals.species')}
      </Text>
      <View style={styles.speciesRow}>
        {[
          { key: 'cattle', emoji: '🐄' },
          { key: 'goat', emoji: '🐐' },
          { key: 'sheep', emoji: '🐑' },
        ].map((sp) => (
          <Chip
            key={sp.key}
            selected={species === sp.key}
            onPress={() => setSpecies(sp.key)}
            style={[styles.speciesChip, species === sp.key && styles.speciesChipSelected]}
          >
            {sp.emoji} {t(`animals.${sp.key}`)}
          </Chip>
        ))}
      </View>

      <TextInput
        label={t('feed.weightKg')}
        value={weight}
        onChangeText={setWeight}
        mode="outlined"
        keyboardType="numeric"
        style={styles.input}
        outlineColor="#BDBDBD"
        activeOutlineColor="#2E7D32"
      />

      <Text variant="titleSmall" style={styles.label}>
        {t('feed.lactationStage')}
      </Text>
      <View style={styles.stageRow}>
        {LACTATION_STAGES.map((s) => (
          <Chip
            key={s}
            selected={stage === s}
            onPress={() => setStage(s)}
            style={[styles.stageChip, stage === s && styles.stageChipSelected]}
            textStyle={stage === s ? { color: '#1B5E20', fontWeight: 'bold' } : undefined}
          >
            {t(`feed.stage.${s}`)}
          </Chip>
        ))}
      </View>

      <Text variant="titleSmall" style={styles.label}>
        {t('feed.selectIngredients')}
      </Text>
      {INGREDIENTS.map((ing) => (
        <Checkbox.Item
          key={ing.key}
          label={`${isKn ? ing.nameKn : ing.nameEn} (₹${ing.costPerKg}/kg)`}
          status={selected.has(ing.key) ? 'checked' : 'unchecked'}
          onPress={() => toggleIngredient(ing.key)}
          color="#2E7D32"
          style={styles.checkItem}
        />
      ))}

      <Button
        mode="contained"
        onPress={calculate}
        style={styles.calcButton}
        contentStyle={styles.calcContent}
        labelStyle={styles.calcLabel}
        disabled={selected.size === 0 || !weight}
        icon="calculator"
      >
        {t('feed.calculateRation')}
      </Button>

      {result && (
        <View style={styles.resultSection}>
          <Text variant="titleMedium" style={styles.resultTitle}>
            {t('feed.dailyRation')}
          </Text>

          {result.ingredients.map((item, i) => (
            <Card key={i} style={styles.resultCard}>
              <Card.Content style={styles.resultCardContent}>
                <Text variant="titleSmall" style={{ flex: 1 }}>{item.name}</Text>
                <Text variant="titleSmall" style={styles.resultQty}>{item.qty} kg</Text>
                <Text variant="bodySmall" style={styles.resultCost}>₹{item.cost}</Text>
              </Card.Content>
            </Card>
          ))}

          <Card style={styles.totalCard}>
            <Card.Content style={styles.totalContent}>
              <Text variant="titleMedium">{t('feed.totalDailyCost')}</Text>
              <Text variant="headlineSmall" style={styles.totalAmount}>
                ₹{result.totalCost}
              </Text>
            </Card.Content>
          </Card>

          <Text variant="titleSmall" style={styles.label}>
            {t('feed.nutritionalBalance')}
          </Text>
          <View style={styles.balanceRow}>
            <Text variant="bodyMedium">{t('feed.protein')}</Text>
            <ProgressBar
              progress={result.proteinBalance}
              color={result.proteinBalance > 0.6 ? '#4CAF50' : '#FF9800'}
              style={styles.balanceBar}
            />
          </View>
          <View style={styles.balanceRow}>
            <Text variant="bodyMedium">{t('feed.energy')}</Text>
            <ProgressBar
              progress={result.energyBalance}
              color={result.energyBalance > 0.6 ? '#4CAF50' : '#FF9800'}
              style={styles.balanceBar}
            />
          </View>
        </View>
      )}
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
  label: {
    color: '#212121',
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
    marginTop: SPACING.md,
  },
  speciesRow: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  speciesChip: {
    minHeight: TOUCH_TARGET_MIN,
  },
  speciesChipSelected: {
    backgroundColor: '#C8E6C9',
  },
  input: {
    marginTop: SPACING.md,
    backgroundColor: '#FFFFFF',
  },
  stageRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  stageChip: {
    minHeight: TOUCH_TARGET_MIN,
  },
  stageChipSelected: {
    backgroundColor: '#C8E6C9',
  },
  checkItem: {
    minHeight: TOUCH_TARGET_MIN,
  },
  calcButton: {
    backgroundColor: '#2E7D32',
    borderRadius: CARD_BORDER_RADIUS,
    marginTop: SPACING.lg,
  },
  calcContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  calcLabel: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultSection: {
    marginTop: SPACING.lg,
  },
  resultTitle: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
  },
  resultCard: {
    borderRadius: 12,
    marginBottom: SPACING.sm,
  },
  resultCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  resultQty: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginRight: SPACING.md,
  },
  resultCost: {
    color: '#616161',
  },
  totalCard: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#E8F5E9',
    marginTop: SPACING.sm,
    marginBottom: SPACING.md,
  },
  totalContent: {
    alignItems: 'center',
  },
  totalAmount: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  balanceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
    marginBottom: SPACING.sm,
  },
  balanceBar: {
    flex: 1,
    height: 12,
    borderRadius: 6,
  },
});
