import React, { useState, useEffect, useCallback } from 'react';
import { View, FlatList, ScrollView, StyleSheet, Pressable, StatusBar } from 'react-native';
import { FAB, Text, IconButton, ActivityIndicator, Button } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { FilterChips, type FilterValue } from '../../src/components/FilterChips';
import { AnimalCard, type Animal } from '../../src/components/AnimalCard';
import { EmptyState } from '../../src/components/EmptyState';
import { LoadingSkeleton } from '../../src/components/LoadingSkeleton';
import { SPACING, CARD_BORDER_RADIUS, colors } from '../../src/config/theme';
import { api } from '../../src/config/api';

type QuickAction = {
  key: string;
  icon: string;
  color: string;
  route: string;
  a11yLabel: string;
};

const QUICK_ACTIONS: QuickAction[] = [
  { key: 'addMilk', icon: 'water-plus', color: colors.primary, route: '/(tabs)/milk', a11yLabel: 'Add milk record' },
  { key: 'healthCheck', icon: 'heart-pulse', color: '#C62828', route: '/(tabs)/health', a11yLabel: 'Health check' },
  { key: 'sellProducts', icon: 'cart-arrow-right', color: '#E65100', route: '/(tabs)/sell', a11yLabel: 'Sell products' },
  { key: 'viewIncome', icon: 'currency-inr', color: '#3B6470', route: '/(tabs)/income', a11yLabel: 'View income' },
  { key: 'vaccination', icon: 'needle', color: colors.primary, route: '/vaccinations', a11yLabel: 'Vaccinations' },
  { key: 'feeding', icon: 'food-apple', color: '#E65100', route: '/feed-calculator', a11yLabel: 'Feeding schedule' },
  { key: 'weather', icon: 'weather-partly-cloudy', color: '#3B6470', route: '/weather', a11yLabel: 'Weather forecast' },
  { key: 'insurance', icon: 'shield-check', color: '#C62828', route: '/insurance', a11yLabel: 'Insurance' },
];

export default function HomeScreen() {
  const { t } = useTranslation();
  const [filter, setFilter] = useState<FilterValue>('all');
  const [animals, setAnimals] = useState<Animal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnimals = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<any>('/animals')
      .then(res => setAnimals(Array.isArray(res) ? res : res.data ?? []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchAnimals();
  }, [fetchAnimals]);

  const filteredAnimals =
    filter === 'all'
      ? animals
      : animals.filter((a) => a.species === filter);

  const handleAnimalPress = useCallback((id: string) => {
    router.push(`/animal/${id}`);
  }, []);

  const handleAddAnimal = useCallback(() => {
    router.push('/animal/add');
  }, []);

  const renderAnimalItem = useCallback(({ item }: { item: Animal }) => (
    <AnimalCard
      animal={item}
      onPress={handleAnimalPress}
    />
  ), [handleAnimalPress]);

  const getItemLayout = useCallback((_: unknown, index: number) => ({
    length: 120,
    offset: 120 * index,
    index,
  }), []);

  if (loading) {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F5F5F0" />
        <View style={styles.greetingSection}>
          <Text variant="headlineSmall" style={styles.greetingName}>
            {t('common.loading')}
          </Text>
        </View>
        <LoadingSkeleton count={3} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F5F5F0" />
        <EmptyState
          icon={'\u26A0\uFE0F'}
          title={t('common.error')}
          subtitle={error}
          actionLabel={t('common.retry')}
          onAction={fetchAnimals}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F0" />

      <FlatList
        data={filteredAnimals}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={
          <>
            {/* Greeting */}
            <View style={styles.greetingSection}>
              <Text variant="headlineMedium" style={styles.greetingName}>
                {t('home.greeting')} {'\uD83D\uDE4F'}
              </Text>
              <Text variant="bodyLarge" style={styles.greetingSubtitle}>
                {t('home.subtitle')}
              </Text>
            </View>

            {/* Quick Actions */}
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.quickActionsContainer}
            >
              {QUICK_ACTIONS.map((action) => (
                <Pressable
                  key={action.key}
                  onPress={() => router.push(action.route as any)}
                  style={styles.quickActionItem}
                  accessibilityLabel={action.a11yLabel}
                  accessibilityRole="button"
                >
                  <View style={[styles.quickActionCircle, { backgroundColor: action.color }]}>
                    <IconButton
                      icon={action.icon}
                      size={28}
                      iconColor="#FFFFFF"
                      style={styles.quickActionIcon}
                    />
                  </View>
                  <Text variant="labelSmall" style={styles.quickActionLabel} numberOfLines={2}>
                    {t(`home.${action.key}`)}
                  </Text>
                </Pressable>
              ))}
            </ScrollView>

            {/* Summary */}
            <View style={styles.summaryRow}>
              <Text variant="titleMedium" style={styles.sectionTitle}>
                {t('animals.myAnimals')}
              </Text>
              <Text variant="bodyMedium" style={styles.countBadge}>
                {animals.length} {t('animals.totalAnimals')}
              </Text>
            </View>

            {/* Filter */}
            <FilterChips selected={filter} onSelect={setFilter} />
          </>
        }
        renderItem={renderAnimalItem}
        getItemLayout={getItemLayout}
        windowSize={5}
        maxToRenderPerBatch={10}
        removeClippedSubviews={true}
        initialNumToRender={5}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <EmptyState
            icon={'\uD83D\uDC04'}
            title={t('empty.noAnimals')}
            subtitle={t('empty.addFirst')}
            actionLabel={t('animals.addAnimal')}
            onAction={handleAddAnimal}
          />
        }
      />

      <FAB
        icon="plus"
        label={t('animals.addAnimal')}
        onPress={handleAddAnimal}
        style={styles.fab}
        color="#FFFFFF"
        customSize={56}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F0',
  },
  greetingSection: {
    paddingHorizontal: SPACING.md + 4,
    paddingTop: SPACING.md,
    paddingBottom: SPACING.sm,
  },
  greetingName: {
    color: '#1A1A1A',
    fontWeight: '700',
  },
  greetingSubtitle: {
    color: '#414941',
    marginTop: 2,
  },
  quickActionsContainer: {
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    gap: SPACING.md,
  },
  quickActionItem: {
    alignItems: 'center',
    width: 72,
  },
  quickActionCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 4,
  },
  quickActionIcon: {
    margin: 0,
  },
  quickActionLabel: {
    textAlign: 'center',
    color: '#1A1A1A',
    marginTop: 6,
    fontSize: 13,
    lineHeight: 17,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SPACING.md + 4,
    paddingTop: SPACING.lg,
  },
  sectionTitle: {
    fontWeight: '700',
    color: '#1A1A1A',
  },
  countBadge: {
    color: colors.primary,
    fontWeight: '600',
  },
  list: {
    paddingBottom: 100,
  },
  fab: {
    position: 'absolute',
    right: SPACING.md,
    bottom: SPACING.md,
    backgroundColor: colors.primary,
    borderRadius: CARD_BORDER_RADIUS,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
});
