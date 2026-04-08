import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Card, Chip, Text, Button, Badge } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';

type Category = 'all' | 'health' | 'feeding' | 'breeding' | 'government';
type Source = 'ICAR' | 'KMF' | 'NABARD' | 'Community';

const SOURCE_COLORS: Record<Source, string> = {
  ICAR: '#1565C0',
  KMF: '#2E7D32',
  NABARD: '#FF8F00',
  Community: '#7B1FA2',
};

interface Advisory {
  id: string;
  titleKn: string;
  titleEn: string;
  bodyKn: string;
  bodyEn: string;
  category: Category;
  source: Source;
  isScheme: boolean;
}

const MOCK_ADVISORIES: Advisory[] = [
  {
    id: '1',
    titleKn: 'ಬೇಸಿಗೆಯಲ್ಲಿ ಹಸುಗಳ ಆರೈಕೆ',
    titleEn: 'Summer care for cattle',
    bodyKn: 'ಬೇಸಿಗೆಯಲ್ಲಿ ಹಸುಗಳಿಗೆ ದಿನಕ್ಕೆ 60-80 ಲೀಟರ್ ನೀರು ಬೇಕು. ನೆರಳಿನ ಏರ್ಪಾಡು ಮಾಡಿ.',
    bodyEn: 'Cattle need 60-80 liters of water per day in summer. Ensure shade availability.',
    category: 'health',
    source: 'ICAR',
    isScheme: false,
  },
  {
    id: '2',
    titleKn: 'ಅಜೋಲಾ ಬೆಳೆಸುವ ವಿಧಾನ',
    titleEn: 'How to grow Azolla',
    bodyKn: 'ಅಜೋಲಾ ಪ್ರೋಟೀನ್ ಸಮೃದ್ಧ ಮೇವು. 2x2 ಮೀಟರ್ ತೊಟ್ಟಿಯಲ್ಲಿ 1 ಕೆಜಿ ಅಜೋಲಾ ಬೆಳೆಸಬಹುದು.',
    titleEn: 'How to grow Azolla',
    bodyEn: 'Azolla is a protein-rich feed supplement. Grow 1kg in a 2x2m pit easily.',
    category: 'feeding',
    source: 'KMF',
    isScheme: false,
  },
  {
    id: '3',
    titleKn: 'ಕೃತಕ ಗರ್ಭಧಾರಣೆ ಸಮಯ',
    titleEn: 'AI timing for best results',
    bodyKn: 'ಬೆದೆ ಕಂಡ 12-18 ಗಂಟೆಯೊಳಗೆ ಕೃತಕ ಗರ್ಭಧಾರಣೆ ಮಾಡಿ.',
    titleEn: 'AI timing for best results',
    bodyEn: 'Perform artificial insemination within 12-18 hours of heat detection.',
    category: 'breeding',
    source: 'ICAR',
    isScheme: false,
  },
  {
    id: '4',
    titleKn: 'ರಾಷ್ಟ್ರೀಯ ಗೋಕುಲ ಮಿಷನ್ - ₹5 ಲಕ್ಷ ಸಹಾಯಧನ',
    titleEn: 'Rashtriya Gokul Mission - ₹5L subsidy',
    bodyKn: 'ದೇಶಿ ತಳಿ ಸಾಕಾಣಿಕೆಗೆ ₹5 ಲಕ್ಷದವರೆಗೆ ಸಹಾಯಧನ. ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.',
    titleEn: 'Rashtriya Gokul Mission - ₹5L subsidy',
    bodyEn: 'Up to ₹5 lakh subsidy for indigenous breed rearing. Apply now.',
    category: 'government',
    source: 'NABARD',
    isScheme: true,
  },
  {
    id: '5',
    titleKn: 'ಕಾಲುಬಾಯಿ ರೋಗ ತಡೆಗಟ್ಟುವಿಕೆ',
    titleEn: 'FMD prevention tips',
    bodyKn: 'ವರ್ಷಕ್ಕೆ 2 ಬಾರಿ ಲಸಿಕೆ ಹಾಕಿಸಿ. ಹೊಸ ಪ್ರಾಣಿಗಳನ್ನು 2 ವಾರ ಪ್ರತ್ಯೇಕಿಸಿ.',
    titleEn: 'FMD prevention tips',
    bodyEn: 'Vaccinate twice a year. Isolate new animals for 2 weeks.',
    category: 'health',
    source: 'ICAR',
    isScheme: false,
  },
  {
    id: '6',
    titleKn: 'ರಾಗಿ ಹುಲ್ಲು ಸಂಸ್ಕರಣೆ',
    titleEn: 'Ragi straw treatment with urea',
    bodyKn: '100 ಕೆಜಿ ರಾಗಿ ಹುಲ್ಲಿಗೆ 4 ಕೆಜಿ ಯೂರಿಯಾ + 40 ಲೀ ನೀರು. 21 ದಿನ ಮುಚ್ಚಿಡಿ.',
    titleEn: 'Ragi straw treatment with urea',
    bodyEn: 'Mix 4kg urea + 40L water per 100kg ragi straw. Seal for 21 days.',
    category: 'feeding',
    source: 'Community',
    isScheme: false,
  },
  {
    id: '7',
    titleKn: 'ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ - ₹3 ಲಕ್ಷ ಸಾಲ',
    titleEn: 'Kisan Credit Card - ₹3L loan for livestock',
    bodyKn: 'ಪಶುಪಾಲನೆಗೆ KCC ಮೂಲಕ 4% ಬಡ್ಡಿಯಲ್ಲಿ ₹3 ಲಕ್ಷ ಸಾಲ ಸಿಗುತ್ತದೆ.',
    titleEn: 'Kisan Credit Card - ₹3L loan for livestock',
    bodyEn: 'Get ₹3L loan at 4% interest via KCC for animal husbandry.',
    category: 'government',
    source: 'NABARD',
    isScheme: true,
  },
  {
    id: '8',
    titleKn: 'ಆಡುಗಳಲ್ಲಿ ಹುಳ ನಿವಾರಣೆ',
    titleEn: 'Deworming schedule for goats',
    bodyKn: 'ಪ್ರತಿ 3 ತಿಂಗಳಿಗೊಮ್ಮೆ ಹುಳ ಮಾತ್ರೆ ಕೊಡಿ. ಮಳೆಗಾಲದ ಮೊದಲು ಕಡ್ಡಾಯ.',
    titleEn: 'Deworming schedule for goats',
    bodyEn: 'Deworm every 3 months. Mandatory before monsoon season.',
    category: 'health',
    source: 'Community',
    isScheme: false,
  },
];

const CATEGORIES: { key: Category; labelKey: string }[] = [
  { key: 'all', labelKey: 'animals.all' },
  { key: 'health', labelKey: 'common.health' },
  { key: 'feeding', labelKey: 'advisory.feeding' },
  { key: 'breeding', labelKey: 'advisory.breeding' },
  { key: 'government', labelKey: 'advisory.government' },
];

export default function AdvisoryScreen() {
  const { t, i18n } = useTranslation();
  const [category, setCategory] = useState<Category>('all');
  const [expandedLang, setExpandedLang] = useState<Record<string, 'kn' | 'en'>>({});

  const isKannada = i18n.language === 'kn';
  const filtered = category === 'all'
    ? MOCK_ADVISORIES
    : MOCK_ADVISORIES.filter((a) => a.category === category);

  const getCardLang = (id: string): 'kn' | 'en' => {
    return expandedLang[id] || (isKannada ? 'kn' : 'en');
  };

  const toggleCardLang = (id: string) => {
    const current = getCardLang(id);
    setExpandedLang((prev) => ({ ...prev, [id]: current === 'kn' ? 'en' : 'kn' }));
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('advisory.title')}
      </Text>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipScroll}>
        <View style={styles.chipRow}>
          {CATEGORIES.map((cat) => (
            <Chip
              key={cat.key}
              selected={category === cat.key}
              onPress={() => setCategory(cat.key)}
              style={[styles.chip, category === cat.key && styles.chipSelected]}
              textStyle={category === cat.key ? styles.chipTextSelected : undefined}
            >
              {t(cat.labelKey)}
            </Chip>
          ))}
        </View>
      </ScrollView>

      {filtered.map((advisory) => {
        const lang = getCardLang(advisory.id);
        return (
          <Card
            key={advisory.id}
            style={[styles.card, advisory.isScheme && styles.schemeCard]}
          >
            <Card.Content>
              {advisory.isScheme && (
                <View style={styles.schemeBadge}>
                  <Text style={styles.schemeBadgeText}>
                    {t('advisory.governmentScheme')}
                  </Text>
                </View>
              )}
              <View style={styles.cardHeader}>
                <Text variant="titleMedium" style={styles.cardTitle}>
                  {lang === 'kn' ? advisory.titleKn : advisory.titleEn}
                </Text>
                <View style={[styles.sourceBadge, { backgroundColor: SOURCE_COLORS[advisory.source] + '20' }]}>
                  <Text style={[styles.sourceText, { color: SOURCE_COLORS[advisory.source] }]}>
                    {advisory.source}
                  </Text>
                </View>
              </View>
              <Text variant="bodyMedium" style={styles.cardBody}>
                {lang === 'kn' ? advisory.bodyKn : advisory.bodyEn}
              </Text>
              <View style={styles.cardFooter}>
                <TouchableOpacity
                  onPress={() => toggleCardLang(advisory.id)}
                  style={styles.langToggle}
                >
                  <Text style={styles.langToggleText}>
                    {lang === 'kn' ? 'English' : 'ಕನ್ನಡ'} ↔
                  </Text>
                </TouchableOpacity>
                {advisory.isScheme && (
                  <Button mode="contained" compact style={styles.applyButton}>
                    {t('advisory.applyNow')}
                  </Button>
                )}
              </View>
            </Card.Content>
          </Card>
        );
      })}
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
  chipScroll: {
    marginBottom: SPACING.md,
  },
  chipRow: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  chip: {
    minHeight: TOUCH_TARGET_MIN,
  },
  chipSelected: {
    backgroundColor: '#C8E6C9',
  },
  chipTextSelected: {
    color: '#1B5E20',
    fontWeight: 'bold',
  },
  card: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
  },
  schemeCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#FF8F00',
    backgroundColor: '#FFF8E1',
  },
  schemeBadge: {
    backgroundColor: '#FF8F00',
    alignSelf: 'flex-start',
    paddingHorizontal: SPACING.sm,
    paddingVertical: 2,
    borderRadius: 8,
    marginBottom: SPACING.sm,
  },
  schemeBadgeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
  },
  cardTitle: {
    color: '#212121',
    fontWeight: 'bold',
    flex: 1,
    marginRight: SPACING.sm,
  },
  sourceBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: 2,
    borderRadius: 8,
  },
  sourceText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  cardBody: {
    color: '#616161',
    marginBottom: SPACING.sm,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  langToggle: {
    minHeight: TOUCH_TARGET_MIN,
    justifyContent: 'center',
  },
  langToggleText: {
    color: '#1565C0',
    fontWeight: 'bold',
  },
  applyButton: {
    backgroundColor: '#FF8F00',
    borderRadius: 8,
  },
});
