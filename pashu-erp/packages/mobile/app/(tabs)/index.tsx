import React, { useState, useEffect } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { FAB, Text } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { FilterChips, type FilterValue } from '../../src/components/FilterChips';
import { AnimalCard, type Animal } from '../../src/components/AnimalCard';
import { EmptyState } from '../../src/components/EmptyState';
import { LoadingSkeleton } from '../../src/components/LoadingSkeleton';
import { SPACING } from '../../src/config/theme';

// Mock data for prototype
const MOCK_ANIMALS: Animal[] = [
  { id: '1', name: 'Lakshmi', species: 'cattle', breed: 'Hallikar', tagNumber: 'KA-001', healthStatus: 'healthy' },
  { id: '2', name: 'Gowri', species: 'cattle', breed: 'Amrit Mahal', tagNumber: 'KA-002', healthStatus: 'healthy' },
  { id: '3', name: 'Malli', species: 'goat', breed: 'Osmanabadi', tagNumber: 'KA-003', healthStatus: 'sick' },
  { id: '4', name: 'Chinni', species: 'sheep', breed: 'Bannur', tagNumber: 'KA-004', healthStatus: 'healthy' },
  { id: '5', name: 'Kodi', species: 'poultry', breed: 'Giriraja', tagNumber: 'KA-005', healthStatus: 'healthy' },
  { id: '6', name: 'Nandi', species: 'cattle', breed: 'Khillari', tagNumber: 'KA-006', healthStatus: 'healthy' },
  { id: '7', name: 'Rekha', species: 'goat', breed: 'Beetal', tagNumber: 'KA-007', healthStatus: 'healthy' },
];

export default function HomeScreen() {
  const { t } = useTranslation();
  const [filter, setFilter] = useState<FilterValue>('all');
  const [isLoading, setIsLoading] = useState(true);

  // Simulate initial data fetch
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  const filteredAnimals =
    filter === 'all'
      ? MOCK_ANIMALS
      : MOCK_ANIMALS.filter((a) => a.species === filter);

  if (isLoading) {
    return (
      <View style={styles.container}>
        <View style={styles.summary}>
          <Text variant="titleMedium" style={styles.summaryText}>
            {t('common.loading')}
          </Text>
        </View>
        <LoadingSkeleton count={3} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.summary}>
        <Text variant="titleMedium" style={styles.summaryText}>
          {t('animals.totalAnimals')}: {MOCK_ANIMALS.length}
        </Text>
      </View>

      <FilterChips selected={filter} onSelect={setFilter} />

      <FlatList
        data={filteredAnimals}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <AnimalCard
            animal={item}
            onPress={(id) => router.push(`/animal/${id}`)}
          />
        )}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <EmptyState
            icon={'\uD83D\uDC04'}
            title={t('empty.noAnimals')}
            subtitle={t('empty.addFirst')}
            actionLabel={t('animals.addAnimal')}
            onAction={() => router.push('/animal/add')}
          />
        }
      />

      <FAB
        icon="plus"
        label={t('animals.addAnimal')}
        onPress={() => router.push('/animal/add')}
        style={styles.fab}
        color="#FFFFFF"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  summary: {
    paddingHorizontal: SPACING.md,
    paddingTop: SPACING.md,
  },
  summaryText: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  list: {
    paddingBottom: 100,
  },
  empty: {
    textAlign: 'center',
    marginTop: SPACING.xl,
    color: '#9E9E9E',
  },
  fab: {
    position: 'absolute',
    right: SPACING.md,
    bottom: SPACING.md,
    backgroundColor: '#2E7D32',
    borderRadius: 16,
  },
});
