import React from 'react';
import { StyleSheet, Pressable, View } from 'react-native';
import { Card, Text, IconButton } from 'react-native-paper';
import { SPACING, CARD_BORDER_RADIUS, TOUCH_TARGET_MIN } from '../config/theme';

interface ProductCardProps {
  icon: string;
  label: string;
  price?: string;
  quantity?: number;
  onPress: () => void;
  onIncrement?: () => void;
  onDecrement?: () => void;
  selected?: boolean;
}

function ProductCardInner({ icon, label, price, quantity, onPress, onIncrement, onDecrement, selected = false }: ProductCardProps) {
  return (
    <Pressable
      onPress={onPress}
      style={styles.pressable}
      accessibilityLabel={price ? `${label} ${price}` : label}
      accessibilityRole="radio"
      accessibilityState={{ checked: selected }}
    >
      <Card
        style={[styles.card, selected && styles.cardSelected]}
        mode="elevated"
      >
        <Card.Content style={styles.content}>
          <Text style={styles.icon}>{icon}</Text>
          <Text variant="titleSmall" style={[styles.label, selected && styles.labelSelected]} numberOfLines={2}>
            {label}
          </Text>
          {price && (
            <Text variant="bodySmall" style={styles.price}>{price}</Text>
          )}
          {selected && onIncrement && onDecrement && (
            <View style={styles.quantityRow}>
              <Pressable onPress={onDecrement} style={styles.qtyBtn} accessibilityLabel="Decrease quantity" accessibilityRole="button">
                <Text style={styles.qtyBtnText}>-</Text>
              </Pressable>
              <Text style={styles.qtyText}>{quantity || 0}</Text>
              <Pressable onPress={onIncrement} style={styles.qtyBtn} accessibilityLabel="Increase quantity" accessibilityRole="button">
                <Text style={styles.qtyBtnText}>+</Text>
              </Pressable>
            </View>
          )}
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
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 6,
    elevation: 2,
  },
  cardSelected: {
    backgroundColor: '#A8F5C8',
    borderColor: '#1B6B4A',
    borderWidth: 2,
    shadowColor: '#1B6B4A',
    shadowOpacity: 0.2,
    elevation: 4,
  },
  content: {
    alignItems: 'center',
    paddingVertical: SPACING.lg,
    gap: SPACING.xs + 2,
  },
  icon: {
    fontSize: 48,
    textAlign: 'center',
  },
  label: {
    textAlign: 'center',
    fontSize: 15,
    color: '#1A1A1A',
  },
  labelSelected: {
    fontWeight: '700',
    color: '#002112',
  },
  price: {
    color: '#1B6B4A',
    fontWeight: '600',
  },
  quantityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.md,
    marginTop: SPACING.xs,
  },
  qtyBtn: {
    minWidth: 44,
    minHeight: 44,
    borderRadius: 22,
    backgroundColor: '#1B6B4A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  qtyBtnText: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '700',
  },
  qtyText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A1A',
  },
});

export const ProductCard = React.memo(ProductCardInner);
