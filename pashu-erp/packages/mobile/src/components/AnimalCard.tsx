import React from 'react';
import { View, StyleSheet, Pressable } from 'react-native';
import { Card, Text } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SpeciesIcon, type Species } from './SpeciesIcon';
import { SPACING, CARD_BORDER_RADIUS, TOUCH_TARGET_MIN } from '../config/theme';

interface Animal {
  id: string;
  name: string;
  species: Species;
  breed: string;
  tagNumber: string;
  healthStatus: 'healthy' | 'sick';
}

interface AnimalCardProps {
  animal: Animal;
  onPress: (id: string) => void;
}

const HEALTH_COLORS = {
  healthy: '#4CAF50',
  sick: '#F44336',
};

export function AnimalCard({ animal, onPress }: AnimalCardProps) {
  const { t } = useTranslation();

  return (
    <Pressable onPress={() => onPress(animal.id)} style={styles.pressable}>
      <Card style={styles.card} mode="elevated">
        <Card.Content style={styles.content}>
          <SpeciesIcon species={animal.species} size={64} />
          <View style={styles.info}>
            <View style={styles.nameRow}>
              <Text variant="titleMedium" style={styles.name}>
                {animal.name}
              </Text>
              <View
                style={[
                  styles.healthDot,
                  { backgroundColor: HEALTH_COLORS[animal.healthStatus] },
                ]}
              />
            </View>
            <Text variant="bodyMedium" style={styles.breed}>
              {t(`animals.${animal.species}`)} - {animal.breed}
            </Text>
            <Text variant="bodySmall" style={styles.tag}>
              {t('animals.tagNumber')}: {animal.tagNumber}
            </Text>
          </View>
        </Card.Content>
      </Card>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  pressable: {
    minHeight: TOUCH_TARGET_MIN,
  },
  card: {
    marginHorizontal: SPACING.md,
    marginVertical: SPACING.sm,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.md,
    paddingVertical: SPACING.md,
  },
  info: {
    flex: 1,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  name: {
    fontWeight: 'bold',
    fontSize: 20,
  },
  healthDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  breed: {
    color: '#616161',
    marginTop: 2,
  },
  tag: {
    color: '#9E9E9E',
    marginTop: 2,
  },
});

export type { Animal };
