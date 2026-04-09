import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { ICON_SIZE_LARGE } from '../config/theme';

type Species = 'cattle' | 'goat' | 'sheep' | 'poultry';

const SPECIES_EMOJIS: Record<Species, string> = {
  cattle: '\uD83D\uDC04',
  goat: '\uD83D\uDC10',
  sheep: '\uD83D\uDC11',
  poultry: '\uD83D\uDC14',
};

interface SpeciesIconProps {
  species: Species;
  size?: number;
}

function SpeciesIconInner({ species, size = ICON_SIZE_LARGE }: SpeciesIconProps) {
  return (
    <Text style={[styles.icon, { fontSize: size }]}>
      {SPECIES_EMOJIS[species] || '\uD83D\uDC3E'}
    </Text>
  );
}

const styles = StyleSheet.create({
  icon: {
    textAlign: 'center',
  },
});

export const SpeciesIcon = React.memo(SpeciesIconInner);
export type { Species };
