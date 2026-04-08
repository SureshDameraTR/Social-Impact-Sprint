import React from 'react';
import { ScrollView, StyleSheet } from 'react-native';
import { Chip } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN } from '../config/theme';

type FilterValue = 'all' | 'cattle' | 'goat' | 'sheep' | 'poultry';

interface FilterChipsProps {
  selected: FilterValue;
  onSelect: (value: FilterValue) => void;
}

const FILTERS: { key: FilterValue; i18nKey: string; emoji: string }[] = [
  { key: 'all', i18nKey: 'animals.all', emoji: '\uD83D\uDCCB' },
  { key: 'cattle', i18nKey: 'animals.cattle', emoji: '\uD83D\uDC04' },
  { key: 'goat', i18nKey: 'animals.goat', emoji: '\uD83D\uDC10' },
  { key: 'sheep', i18nKey: 'animals.sheep', emoji: '\uD83D\uDC11' },
  { key: 'poultry', i18nKey: 'animals.poultry', emoji: '\uD83D\uDC14' },
];

export function FilterChips({ selected, onSelect }: FilterChipsProps) {
  const { t } = useTranslation();

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {FILTERS.map((filter) => (
        <Chip
          key={filter.key}
          selected={selected === filter.key}
          onPress={() => onSelect(filter.key)}
          style={[styles.chip, selected === filter.key && styles.chipSelected]}
          textStyle={styles.chipText}
          mode={selected === filter.key ? 'flat' : 'outlined'}
        >
          {filter.emoji} {t(filter.i18nKey)}
        </Chip>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    gap: SPACING.sm,
  },
  chip: {
    minHeight: TOUCH_TARGET_MIN,
    justifyContent: 'center',
  },
  chipSelected: {
    backgroundColor: '#C8E6C9',
  },
  chipText: {
    fontSize: 16,
  },
});

export type { FilterValue };
