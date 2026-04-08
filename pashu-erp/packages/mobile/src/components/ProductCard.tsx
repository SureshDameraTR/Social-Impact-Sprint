import React from 'react';
import { StyleSheet, Pressable } from 'react-native';
import { Card, Text } from 'react-native-paper';
import { SPACING, CARD_BORDER_RADIUS, TOUCH_TARGET_MIN } from '../config/theme';

interface ProductCardProps {
  icon: string;
  label: string;
  onPress: () => void;
  selected?: boolean;
}

export function ProductCard({ icon, label, onPress, selected = false }: ProductCardProps) {
  return (
    <Pressable onPress={onPress} style={styles.pressable}>
      <Card
        style={[styles.card, selected && styles.cardSelected]}
        mode={selected ? 'elevated' : 'outlined'}
      >
        <Card.Content style={styles.content}>
          <Text style={styles.icon}>{icon}</Text>
          <Text variant="titleSmall" style={styles.label} numberOfLines={2}>
            {label}
          </Text>
        </Card.Content>
      </Card>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  pressable: {
    flex: 1,
    minHeight: TOUCH_TARGET_MIN,
  },
  card: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
  },
  cardSelected: {
    backgroundColor: '#C8E6C9',
    borderColor: '#2E7D32',
    borderWidth: 2,
  },
  content: {
    alignItems: 'center',
    paddingVertical: SPACING.lg,
    gap: SPACING.sm,
  },
  icon: {
    fontSize: 48,
    textAlign: 'center',
  },
  label: {
    textAlign: 'center',
    fontSize: 16,
  },
});
