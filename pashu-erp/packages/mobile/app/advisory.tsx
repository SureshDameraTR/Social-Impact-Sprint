import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet, Pressable } from 'react-native';
import { Card, Chip, Text, Button, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors } from '../src/config/theme';
import { api } from '../src/config/api';

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

const CATEGORIES: { key: Category; labelKey: string }[] = [
  { key: 'all', labelKey: 'animals.all' },
  { key: 'health', labelKey: 'common.health' },
  { key: 'feeding', labelKey: 'advisory.feeding' },
  { key: 'breeding', labelKey: 'advisory.breeding' },
  { key: 'government', labelKey: 'advisory.government' },
];

export default function AdvisoryScreen() {
  const { t, i18n } = useTranslation();
  const [advisories, setAdvisories] = useState<Advisory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState<Category>('all');
  const [expandedLang, setExpandedLang] = useState<Record<string, 'kn' | 'en'>>({});

  const fetchAdvisories = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<any>('/advisory/tips')
      .then(res => setAdvisories(Array.isArray(res) ? res : res.data ?? []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchAdvisories();
  }, [fetchAdvisories]);

  const isKannada = i18n.language === 'kn';
  const filtered = category === 'all'
    ? advisories
    : advisories.filter((a) => a.category === category);

  const getCardLang = (id: string): 'kn' | 'en' => {
    return expandedLang[id] || (isKannada ? 'kn' : 'en');
  };

  const toggleCardLang = (id: string) => {
    const current = getCardLang(id);
    setExpandedLang((prev) => ({ ...prev, [id]: current === 'kn' ? 'en' : 'kn' }));
  };

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={colors.primary} />
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
          onAction={fetchAdvisories}
        />
      </View>
    );
  }

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

      {filtered.length === 0 && (
        <EmptyState
          icon={'\uD83D\uDCCB'}
          title={t('common.noData')}
          subtitle={t('advisory.title')}
        />
      )}

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
                <View style={[styles.sourceBadge, { backgroundColor: (SOURCE_COLORS[advisory.source] || '#616161') + '20' }]}>
                  <Text style={[styles.sourceText, { color: SOURCE_COLORS[advisory.source] || '#616161' }]}>
                    {advisory.source}
                  </Text>
                </View>
              </View>
              <Text variant="bodyMedium" style={styles.cardBody}>
                {lang === 'kn' ? advisory.bodyKn : advisory.bodyEn}
              </Text>
              <View style={styles.cardFooter}>
                <Pressable
                  onPress={() => toggleCardLang(advisory.id)}
                  style={styles.langToggle}
                  accessibilityLabel={lang === 'kn' ? t('common.english') : t('common.kannada')}
                  accessibilityRole="button"
                >
                  <Text style={styles.langToggleText}>
                    {lang === 'kn' ? t('common.english') : t('common.kannada')} \u21C6
                  </Text>
                </Pressable>
                {advisory.isScheme && (
                  <Button mode="contained" compact style={styles.applyButton} accessibilityLabel={`Apply now for ${lang === 'kn' ? advisory.titleKn : advisory.titleEn}`}>
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
    backgroundColor: colors.surface,
  },
  content: {
    padding: SPACING.md,
    paddingBottom: 100,
  },
  heading: {
    color: colors.primary,
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
