import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Card, Chip, Searchbar, Text, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';
import { api } from '../src/config/api';

type Evidence = 'validated' | 'studied' | 'traditional';
type SpeciesFilter = 'all' | 'cattle' | 'goat' | 'sheep' | 'poultry';

const EVIDENCE_CONFIG: Record<Evidence, { emoji: string; labelKey: string; color: string }> = {
  validated: { emoji: '\uD83D\uDFE2', labelKey: 'ethnoVet.validated', color: '#2E7D32' },
  studied: { emoji: '\uD83D\uDFE1', labelKey: 'ethnoVet.studied', color: '#FF8F00' },
  traditional: { emoji: '\u26AA', labelKey: 'ethnoVet.traditional', color: '#616161' },
};

interface Remedy {
  id: string;
  nameKn: string;
  nameEn: string;
  ingredientsKn: string;
  ingredientsEn: string;
  conditionsKn: string;
  conditionsEn: string;
  evidence: Evidence;
  species: SpeciesFilter[];
  safetyWarning?: string;
  preparationKn: string;
  preparationEn: string;
  dosage: string;
  source: string;
}

export default function EthnoVetScreen() {
  const { t, i18n } = useTranslation();
  const isKn = i18n.language === 'kn';
  const [remedies, setRemedies] = useState<Remedy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [speciesFilter, setSpeciesFilter] = useState<SpeciesFilter>('all');
  const [evidenceFilter, setEvidenceFilter] = useState<Evidence | 'all'>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchRemedies = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<Remedy[]>('/ethno-vet/remedies')
      .then(res => setRemedies(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchRemedies();
  }, [fetchRemedies]);

  const filtered = remedies.filter((r) => {
    if (speciesFilter !== 'all' && !r.species.includes(speciesFilter)) return false;
    if (evidenceFilter !== 'all' && r.evidence !== evidenceFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        r.nameKn.includes(search) ||
        r.nameEn.toLowerCase().includes(q) ||
        r.conditionsEn.toLowerCase().includes(q) ||
        r.ingredientsEn.toLowerCase().includes(q)
      );
    }
    return true;
  });

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#2E7D32" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <EmptyState
          icon={'\u26A0\uFE0F'}
          title={t('common.error')}
          subtitle={error}
          actionLabel={t('common.retry')}
          onAction={fetchRemedies}
        />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('ethnoVet.title')}
      </Text>

      <Searchbar
        placeholder={t('ethnoVet.searchPlaceholder')}
        value={search}
        onChangeText={setSearch}
        style={styles.searchbar}
      />

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
        <View style={styles.filterRow}>
          {(['all', 'cattle', 'goat', 'sheep', 'poultry'] as SpeciesFilter[]).map((sp) => (
            <Chip
              key={sp}
              selected={speciesFilter === sp}
              onPress={() => setSpeciesFilter(sp)}
              style={[styles.filterChip, speciesFilter === sp && styles.filterChipSelected]}
            >
              {sp === 'all' ? t('animals.all') : t(`animals.${sp}`)}
            </Chip>
          ))}
        </View>
      </ScrollView>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
        <View style={styles.filterRow}>
          <Chip
            selected={evidenceFilter === 'all'}
            onPress={() => setEvidenceFilter('all')}
            style={[styles.filterChip, evidenceFilter === 'all' && styles.filterChipSelected]}
          >
            {t('animals.all')}
          </Chip>
          {(Object.keys(EVIDENCE_CONFIG) as Evidence[]).map((ev) => (
            <Chip
              key={ev}
              selected={evidenceFilter === ev}
              onPress={() => setEvidenceFilter(ev)}
              style={[styles.filterChip, evidenceFilter === ev && styles.filterChipSelected]}
            >
              {EVIDENCE_CONFIG[ev].emoji} {t(EVIDENCE_CONFIG[ev].labelKey)}
            </Chip>
          ))}
        </View>
      </ScrollView>

      {filtered.map((remedy) => {
        const isExpanded = expandedId === remedy.id;
        const ev = EVIDENCE_CONFIG[remedy.evidence];
        return (
          <TouchableOpacity
            key={remedy.id}
            onPress={() => setExpandedId(isExpanded ? null : remedy.id)}
            activeOpacity={0.7}
          >
            <Card style={styles.card}>
              <Card.Content>
                <View style={styles.cardHeader}>
                  <Text variant="titleMedium" style={styles.cardTitle}>
                    {isKn ? remedy.nameKn : remedy.nameEn}
                  </Text>
                  <View style={[styles.evidenceBadge, { backgroundColor: ev.color + '20' }]}>
                    <Text style={{ color: ev.color, fontSize: 12, fontWeight: 'bold' }}>
                      {ev.emoji} {t(ev.labelKey)}
                    </Text>
                  </View>
                </View>

                <Text variant="bodySmall" style={styles.cardMeta}>
                  {isKn ? remedy.ingredientsKn : remedy.ingredientsEn}
                </Text>
                <Text variant="bodyMedium" style={styles.cardConditions}>
                  {t('ethnoVet.treatsLabel')}: {isKn ? remedy.conditionsKn : remedy.conditionsEn}
                </Text>

                {remedy.safetyWarning && (
                  <View style={styles.warningBox}>
                    <Text style={styles.warningText}>
                      {'\u26A0\uFE0F'} {remedy.safetyWarning}
                    </Text>
                  </View>
                )}

                {isExpanded && (
                  <View style={styles.expandedSection}>
                    <Text variant="titleSmall" style={styles.expandedLabel}>
                      {t('ethnoVet.preparation')}
                    </Text>
                    <Text variant="bodyMedium" style={styles.expandedText}>
                      {isKn ? remedy.preparationKn : remedy.preparationEn}
                    </Text>

                    <Text variant="titleSmall" style={styles.expandedLabel}>
                      {t('ethnoVet.dosage')}
                    </Text>
                    <Text variant="bodyMedium" style={styles.expandedText}>
                      {remedy.dosage}
                    </Text>

                    <Text variant="titleSmall" style={styles.expandedLabel}>
                      {t('ethnoVet.source')}
                    </Text>
                    <Text variant="bodySmall" style={styles.sourceRef}>
                      {remedy.source}
                    </Text>
                  </View>
                )}

                <Text variant="bodySmall" style={styles.tapHint}>
                  {isExpanded ? '\u25B2 ' + t('ethnoVet.tapToCollapse') : '\u25BC ' + t('ethnoVet.tapToExpand')}
                </Text>
              </Card.Content>
            </Card>
          </TouchableOpacity>
        );
      })}

      {filtered.length === 0 && (
        <EmptyState
          icon={'\uD83C\uDF3F'}
          title={t('common.noData')}
          subtitle={t('ethnoVet.title')}
        />
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
    marginBottom: SPACING.sm,
  },
  searchbar: {
    marginBottom: SPACING.sm,
    borderRadius: CARD_BORDER_RADIUS,
    elevation: 1,
  },
  filterScroll: {
    marginBottom: SPACING.sm,
  },
  filterRow: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  filterChip: {
    minHeight: TOUCH_TARGET_MIN,
  },
  filterChipSelected: {
    backgroundColor: '#C8E6C9',
  },
  card: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: SPACING.xs,
  },
  cardTitle: {
    color: '#212121',
    fontWeight: 'bold',
    flex: 1,
    marginRight: SPACING.sm,
  },
  evidenceBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: 2,
    borderRadius: 8,
  },
  cardMeta: {
    color: '#9E9E9E',
    marginBottom: SPACING.xs,
  },
  cardConditions: {
    color: '#616161',
    marginBottom: SPACING.sm,
  },
  warningBox: {
    backgroundColor: '#FFF3E0',
    padding: SPACING.sm,
    borderRadius: 8,
    marginBottom: SPACING.sm,
    borderLeftWidth: 3,
    borderLeftColor: '#FF9800',
  },
  warningText: {
    color: '#E65100',
    fontSize: 13,
  },
  expandedSection: {
    marginTop: SPACING.sm,
    paddingTop: SPACING.sm,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  expandedLabel: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginTop: SPACING.sm,
    marginBottom: SPACING.xs,
  },
  expandedText: {
    color: '#424242',
  },
  sourceRef: {
    color: '#1565C0',
    fontStyle: 'italic',
  },
  tapHint: {
    color: '#9E9E9E',
    textAlign: 'center',
    marginTop: SPACING.sm,
    fontSize: 12,
  },
});
