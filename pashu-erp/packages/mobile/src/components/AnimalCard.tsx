import React from 'react';
import { View, StyleSheet, Pressable } from 'react-native';
import { Card, Text, IconButton } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SpeciesIcon, type Species } from './SpeciesIcon';
import { SPACING, CARD_BORDER_RADIUS, TOUCH_TARGET_MIN, speciesColors, statusColors } from '../config/theme';

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

const HEALTH_DOT = {
  healthy: statusColors.healthy,
  sick: statusColors.urgent,
};

function AnimalCardInner({ animal, onPress }: AnimalCardProps) {
  const { t } = useTranslation();
  const speciesStyle = speciesColors[animal.species] || speciesColors.cattle;

  return (
    <Pressable
      onPress={() => onPress(animal.id)}
      style={styles.pressable}
      accessibilityLabel={`${animal.name}, ${t(`animals.${animal.species}`)}, ${t(`animals.${animal.healthStatus}`)}`}
      accessibilityRole="button"
    >
      <Card style={styles.card} mode="elevated">
        <Card.Content style={styles.content}>
          {/* Avatar with health dot */}
          <View style={styles.avatarContainer}>
            <View style={[styles.avatar, { backgroundColor: speciesStyle.bg }]}>
              <SpeciesIcon species={animal.species} size={48} />
            </View>
            <View
              style={[styles.healthDot, { backgroundColor: HEALTH_DOT[animal.healthStatus] }]}
              accessible={true}
              accessibilityLabel={t(`animals.${animal.healthStatus}`)}
            >
              {animal.healthStatus === 'sick' && (
                <Text style={styles.healthDotLabel}>!</Text>
              )}
            </View>
          </View>

          {/* Info */}
          <View style={styles.info}>
            <Text variant="titleMedium" style={styles.name}>
              {animal.name}
            </Text>
            <View style={styles.badgeRow}>
              <View style={[styles.speciesBadge, { backgroundColor: speciesStyle.bg }]}>
                <Text style={[styles.speciesText, { color: speciesStyle.text }]}>
                  {t(`animals.${animal.species}`)}
                </Text>
              </View>
              <Text variant="bodySmall" style={styles.breed}>
                {animal.breed}
              </Text>
            </View>
            <Text variant="bodySmall" style={styles.tag}>
              {animal.tagNumber}
            </Text>
          </View>

          {/* Arrow */}
          <IconButton
            icon="chevron-right"
            size={24}
            iconColor="#717971"
            style={styles.arrow}
          />
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
    marginVertical: SPACING.xs + 2,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.md,
    paddingVertical: SPACING.sm + 4,
  },
  avatarContainer: {
    position: 'relative',
  },
  avatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  healthDot: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  info: {
    flex: 1,
  },
  name: {
    fontWeight: '700',
    fontSize: 20,
    color: '#1A1A1A',
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
    marginTop: 4,
  },
  speciesBadge: {
    paddingHorizontal: 10,
    paddingVertical: 2,
    borderRadius: 12,
  },
  speciesText: {
    fontSize: 13,
    fontWeight: '600',
  },
  breed: {
    color: '#414941',
  },
  tag: {
    color: '#717971',
    marginTop: 2,
  },
  arrow: {
    margin: 0,
  },
  healthDotLabel: {
    color: '#FFFFFF',
    fontSize: 9,
    fontWeight: '700',
    textAlign: 'center',
    lineHeight: 16,
  },
});

const AnimalCard = React.memo(AnimalCardInner);
export { AnimalCard };
export default AnimalCard;
export type { Animal };
