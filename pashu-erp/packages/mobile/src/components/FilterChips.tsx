import React from 'react';
import { ScrollView, StyleSheet } from 'react-native';
import { Chip } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, speciesColors } from '../config/theme';

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

const FILTER_COLORS: Record<FilterValue, { bg: string; text: string }> = {
  all: { bg: '#D1E8D6', text: '#1B6B4A' },
  cattle: speciesColors.cattle,
  goat: speciesColors.goat,
  sheep: speciesColors.sheep,
  poultry: speciesColors.poultry,
};

function FilterChipsInner({ selected, onSelect }: FilterChipsProps) {
  const { t } = useTranslation();

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {FILTERS.map((filter) => {
        const isSelected = selected === filter.key;
        const colors = FILTER_COLORS[filter.key];
        return (
          <Chip
            key={filter.key}
            selected={isSelected}
            onPress={() => onSelect(filter.key)}
            style={[
              styles.chip,
              isSelected && { backgroundColor: colors.bg, borderColor: colors.text },
            ]}
            textStyle={[
              styles.chipText,
              isSelected && { color: colors.text, fontWeight: '700' },
            ]}
            mode={isSelected ? 'flat' : 'outlined'}
            showSelectedOverlay={false}
            accessibilityLabel={t(filter.i18nKey)}
            accessibilityRole="radio"
            accessibilityState={{ checked: isSelected }}
          >
            {filter.emoji} {t(filter.i18nKey)}
          </Chip>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm + 4,
    gap: SPACING.sm,
  },
  chip: {
    minHeight: TOUCH_TARGET_MIN,
    justifyContent: 'center',
    borderRadius: 24,
    borderColor: '#C1C9BF',
  },
  chipText: {
    fontSize: 15,
    color: '#414941',
  },
});

export const FilterChips = React.memo(FilterChipsInner);
export type { FilterValue };
