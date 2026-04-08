import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Card, Chip, Searchbar, Text } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';

type Evidence = 'validated' | 'studied' | 'traditional';
type SpeciesFilter = 'all' | 'cattle' | 'goat' | 'sheep' | 'poultry';

const EVIDENCE_CONFIG: Record<Evidence, { emoji: string; labelKey: string; color: string }> = {
  validated: { emoji: '🟢', labelKey: 'ethnoVet.validated', color: '#2E7D32' },
  studied: { emoji: '🟡', labelKey: 'ethnoVet.studied', color: '#FF8F00' },
  traditional: { emoji: '⚪', labelKey: 'ethnoVet.traditional', color: '#616161' },
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

const MOCK_REMEDIES: Remedy[] = [
  {
    id: '1',
    nameKn: 'ಅರಿಶಿನ-ಬೆಲ್ಲ ಮಿಶ್ರಣ',
    nameEn: 'Turmeric-Jaggery Mix',
    ingredientsKn: 'ಅರಿಶಿನ, ಬೆಲ್ಲ, ತುಪ್ಪ',
    ingredientsEn: 'Turmeric, Jaggery, Ghee',
    conditionsKn: 'ಗಾಯ ಗುಣಪಡಿಸುವಿಕೆ, ಉರಿಯೂತ',
    conditionsEn: 'Wound healing, Inflammation',
    evidence: 'validated',
    species: ['cattle', 'goat'],
    preparationKn: '50ಗ್ರಾ ಅರಿಶಿನ + 100ಗ್ರಾ ಬೆಲ್ಲ + 2 ಚಮಚ ತುಪ್ಪ ಮಿಶ್ರ ಮಾಡಿ ಗಾಯಕ್ಕೆ ಹಚ್ಚಿ',
    preparationEn: 'Mix 50g turmeric + 100g jaggery + 2 spoons ghee. Apply to wound.',
    dosage: '2x daily for 5 days',
    source: 'ICAR-NBAGR Study 2019',
  },
  {
    id: '2',
    nameKn: 'ಬೇವಿನ ಎಲೆ ಕಷಾಯ',
    nameEn: 'Neem Leaf Decoction',
    ingredientsKn: 'ಬೇವಿನ ಎಲೆ, ನೀರು',
    ingredientsEn: 'Neem leaves, Water',
    conditionsKn: 'ಚರ್ಮ ರೋಗ, ಉಣ್ಣೆ ನಿವಾರಣೆ',
    conditionsEn: 'Skin diseases, Tick control',
    evidence: 'validated',
    species: ['cattle', 'goat', 'sheep'],
    preparationKn: '500ಗ್ರಾ ಬೇವಿನ ಎಲೆಯನ್ನು 5ಲೀ ನೀರಿನಲ್ಲಿ ಕುದಿಸಿ, ತಣ್ಣಗಾದ ಮೇಲೆ ಮೈಗೆ ಹಚ್ಚಿ',
    preparationEn: 'Boil 500g neem leaves in 5L water. Cool and apply to body.',
    dosage: 'External application, 1x daily for 7 days',
    source: 'ICAR-IVRI Bareilly',
  },
  {
    id: '3',
    nameKn: 'ಶುಂಠಿ-ಬೆಳ್ಳುಳ್ಳಿ ಕಷಾಯ',
    nameEn: 'Ginger-Garlic Decoction',
    ingredientsKn: 'ಶುಂಠಿ, ಬೆಳ್ಳುಳ್ಳಿ, ಕಾಳುಮೆಣಸು',
    ingredientsEn: 'Ginger, Garlic, Black pepper',
    conditionsKn: 'ಕೆಮ್ಮು, ಶೀತ, ಜ್ವರ',
    conditionsEn: 'Cough, Cold, Fever',
    evidence: 'studied',
    species: ['cattle', 'goat', 'sheep'],
    preparationKn: '100ಗ್ರಾ ಶುಂಠಿ + 50ಗ್ರಾ ಬೆಳ್ಳುಳ್ಳಿ ಜಜ್ಜಿ, ಬಿಸಿ ನೀರಿನಲ್ಲಿ ಕುಡಿಸಿ',
    preparationEn: 'Crush 100g ginger + 50g garlic. Mix with warm water and drench.',
    dosage: '2x daily for 3 days',
    source: 'Univ. of Agricultural Sciences, Bangalore',
  },
  {
    id: '4',
    nameKn: 'ಎಣ್ಣೆ ಕುಡಿಸುವಿಕೆ (ಉಬ್ಬರಕ್ಕೆ)',
    nameEn: 'Oil Drench for Bloat',
    ingredientsKn: 'ಶೇಂಗಾ ಎಣ್ಣೆ, ಅಡಿಗೆ ಸೋಡಾ',
    ingredientsEn: 'Groundnut oil, Baking soda',
    conditionsKn: 'ಉಬ್ಬರ, ಅಜೀರ್ಣ',
    conditionsEn: 'Bloat, Indigestion',
    evidence: 'validated',
    species: ['cattle'],
    safetyWarning: 'Do not use if animal is unconscious. Consult vet if no improvement in 2 hours.',
    preparationKn: '200ಮಿಲಿ ಶೇಂಗಾ ಎಣ್ಣೆ + 1 ಚಮಚ ಸೋಡಾ ಮಿಶ್ರ ಮಾಡಿ ನಿಧಾನವಾಗಿ ಕುಡಿಸಿ',
    preparationEn: 'Mix 200ml groundnut oil + 1 spoon baking soda. Drench slowly.',
    dosage: 'Single dose. Repeat after 2 hours if needed.',
    source: 'ICAR-NBAGR',
  },
  {
    id: '5',
    nameKn: 'ಅಲೋವೆರಾ ಲೇಪ',
    nameEn: 'Aloe Vera Paste',
    ingredientsKn: 'ಅಲೋವೆರಾ ತಿರುಳು',
    ingredientsEn: 'Aloe vera pulp',
    conditionsKn: 'ಸುಟ್ಟ ಗಾಯ, ಚರ್ಮ ಉರಿಯೂತ',
    conditionsEn: 'Burns, Skin inflammation',
    evidence: 'studied',
    species: ['cattle', 'goat', 'sheep', 'poultry'],
    preparationKn: 'ಅಲೋವೆರಾ ಎಲೆ ಸೀಳಿ ತಿರುಳನ್ನು ನೇರವಾಗಿ ಗಾಯಕ್ಕೆ ಹಚ್ಚಿ',
    preparationEn: 'Split aloe leaf and apply pulp directly to affected area.',
    dosage: '2-3x daily until healed',
    source: 'KVAFSU Bidar Study',
  },
  {
    id: '6',
    nameKn: 'ಮಜ್ಜಿಗೆ ಚಿಕಿತ್ಸೆ',
    nameEn: 'Buttermilk Therapy',
    ingredientsKn: 'ಮಜ್ಜಿಗೆ, ಉಪ್ಪು, ಜೀರಿಗೆ',
    ingredientsEn: 'Buttermilk, Salt, Cumin',
    conditionsKn: 'ಭೇದಿ, ನಿರ್ಜಲೀಕರಣ',
    conditionsEn: 'Diarrhea, Dehydration',
    evidence: 'traditional',
    species: ['cattle', 'goat'],
    preparationKn: '2ಲೀ ಮಜ್ಜಿಗೆ + ಒಂದು ಹಿಡಿ ಉಪ್ಪು + ಜೀರಿಗೆ ಮಿಶ್ರ ಮಾಡಿ ಕುಡಿಸಿ',
    preparationEn: 'Mix 2L buttermilk + pinch of salt + cumin. Drench orally.',
    dosage: '3x daily for 2-3 days',
    source: 'Karnataka folk tradition',
  },
  {
    id: '7',
    nameKn: 'ಬಾಳೆಹಣ್ಣು ಆಹಾರ',
    nameEn: 'Banana Feeding for Weakness',
    ingredientsKn: 'ಮಾಗಿದ ಬಾಳೆಹಣ್ಣು, ಬೆಲ್ಲ',
    ingredientsEn: 'Ripe bananas, Jaggery',
    conditionsKn: 'ದೌರ್ಬಲ್ಯ, ಹೆರಿಗೆ ನಂತರ',
    conditionsEn: 'Weakness, Post-partum recovery',
    evidence: 'traditional',
    species: ['cattle'],
    preparationKn: '5-6 ಬಾಳೆಹಣ್ಣು + 200ಗ್ರಾ ಬೆಲ್ಲ ಮಿಶ್ರ ಮಾಡಿ ತಿನ್ನಿಸಿ',
    preparationEn: 'Mix 5-6 ripe bananas + 200g jaggery. Feed orally.',
    dosage: '1x daily for 7 days post-calving',
    source: 'Mandya farmer practice',
  },
  {
    id: '8',
    nameKn: 'ತೊಗರಿ ಎಲೆ ಸಾರು',
    nameEn: 'Pigeon Pea Leaf Extract',
    ingredientsKn: 'ತೊಗರಿ ಎಲೆ, ನೀರು',
    ingredientsEn: 'Pigeon pea leaves, Water',
    conditionsKn: 'ಹುಳ ನಿವಾರಣೆ',
    conditionsEn: 'Deworming',
    evidence: 'studied',
    species: ['goat', 'sheep'],
    preparationKn: '250ಗ್ರಾ ಎಲೆಯನ್ನು 2ಲೀ ನೀರಿನಲ್ಲಿ ಕುದಿಸಿ, ತಣ್ಣಗಾಗಿಸಿ ಕುಡಿಸಿ',
    preparationEn: 'Boil 250g leaves in 2L water. Cool and drench.',
    dosage: 'Once weekly for 3 weeks',
    source: 'UAS Dharwad Study 2020',
  },
  {
    id: '9',
    nameKn: 'ಅಜ್ವಾನ್ ನೀರು',
    nameEn: 'Ajwain Water',
    ingredientsKn: 'ಅಜ್ವಾನ್, ಬಿಸಿ ನೀರು',
    ingredientsEn: 'Carom seeds, Warm water',
    conditionsKn: 'ಹೊಟ್ಟೆ ನೋವು, ಗ್ಯಾಸ್',
    conditionsEn: 'Stomach ache, Gas',
    evidence: 'traditional',
    species: ['cattle', 'goat', 'sheep'],
    preparationKn: '50ಗ್ರಾ ಅಜ್ವಾನ್ ಬಿಸಿ ನೀರಿನಲ್ಲಿ ನೆನೆಸಿ ಕುಡಿಸಿ',
    preparationEn: 'Soak 50g carom seeds in warm water. Drench.',
    dosage: '2x daily for 2 days',
    source: 'Hassan district practice',
  },
  {
    id: '10',
    nameKn: 'ಕಹಿಬೇವಿನ ಹೊಗೆ',
    nameEn: 'Neem Smoke Fumigation',
    ingredientsKn: 'ಒಣ ಬೇವಿನ ಎಲೆ',
    ingredientsEn: 'Dried neem leaves',
    conditionsKn: 'ಕೋಳಿ ಮನೆ ಸೋಂಕು ನಿವಾರಣೆ',
    conditionsEn: 'Poultry house disinfection',
    evidence: 'studied',
    species: ['poultry'],
    safetyWarning: 'Ensure adequate ventilation. Remove birds during fumigation.',
    preparationKn: 'ಒಣ ಬೇವಿನ ಎಲೆಯನ್ನು ಹೊಗೆ ಹಾಕಿ ಕೋಳಿ ಮನೆ ಶುದ್ಧೀಕರಿಸಿ',
    preparationEn: 'Burn dried neem leaves to fumigate poultry house.',
    dosage: 'Weekly, 15 min per session',
    source: 'KVAFSU Extension Bulletin',
  },
];

export default function EthnoVetScreen() {
  const { t, i18n } = useTranslation();
  const isKn = i18n.language === 'kn';
  const [search, setSearch] = useState('');
  const [speciesFilter, setSpeciesFilter] = useState<SpeciesFilter>('all');
  const [evidenceFilter, setEvidenceFilter] = useState<Evidence | 'all'>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered = MOCK_REMEDIES.filter((r) => {
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
                      ⚠️ {remedy.safetyWarning}
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
                  {isExpanded ? '▲ ' + t('ethnoVet.tapToCollapse') : '▼ ' + t('ethnoVet.tapToExpand')}
                </Text>
              </Card.Content>
            </Card>
          </TouchableOpacity>
        );
      })}

      {filtered.length === 0 && (
        <Text variant="bodyLarge" style={styles.empty}>
          {t('common.noData')}
        </Text>
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
  empty: {
    textAlign: 'center',
    marginTop: SPACING.xl,
    color: '#9E9E9E',
  },
});
