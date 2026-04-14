import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Button, Divider, List, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import * as Storage from '../src/config/storage';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, colors, statusColors } from '../src/config/theme';
import { api } from '../src/config/api';
import { loadLanguage } from '../src/i18n';

interface UserProfile {
  name: string;
  phone: string;
  village: string;
  totalAnimals: number;
  farmSize: string;
  memberSince: string;
  todayMilk: number;
  monthlyIncome: number;
}

export default function ProfileScreen() {
  const { t, i18n } = useTranslation();
  const [language, setLanguage] = useState(i18n.language || 'en');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<UserProfile>('/users/profile')
      .then(res => setProfile(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
    loadLanguage(lang);
  };

  const handleLogout = async () => {
    await Storage.deleteItemAsync('auth_token');
    router.replace('/(auth)/login');
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
          onAction={fetchProfile}
        />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      {/* User info */}
      <View style={styles.header}>
        <View style={styles.avatarLarge}>
          <Text style={styles.avatarText}>{'\uD83D\uDC68\u200D\uD83C\uDF3E'}</Text>
        </View>
        <Text variant="headlineMedium" style={styles.name}>
          {profile?.name || '\u2014'}
        </Text>
        <Text variant="bodyLarge" style={styles.phone}>
          {profile?.phone || '\u2014'}
        </Text>
        <Text variant="bodyMedium" style={styles.village}>
          {profile?.village || '\u2014'}
        </Text>
      </View>

      {/* Language selector */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.cardTitle}>
            {t('onboarding.selectLanguage')}
          </Text>
          <View style={styles.langGrid}>
            {[
              { value: 'en', label: 'English' },
              { value: 'hi', label: '\u0939\u093F\u0928\u094D\u0926\u0940' },
              { value: 'kn', label: '\u0C95\u0CA8\u0CCD\u0CA8\u0CA1' },
              { value: 'ta', label: '\u0BA4\u0BAE\u0BBF\u0BB4\u0BCD' },
              { value: 'te', label: '\u0C24\u0C46\u0C32\u0C41\u0C17\u0C41' },
              { value: 'gu', label: '\u0A97\u0AC1\u0A9C\u0AB0\u0ABE\u0AA4\u0AC0' },
            ].map((lang) => (
              <Button
                key={lang.value}
                mode={language === lang.value ? 'contained' : 'outlined'}
                onPress={() => handleLanguageChange(lang.value)}
                style={styles.langButton}
                compact
              >
                {lang.label}
              </Button>
            ))}
          </View>
        </Card.Content>
      </Card>

      {/* Farm info */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.cardTitle}>
            {'\uD83C\uDFE1'} {t('profile.farmDetails')}
          </Text>
          <Divider style={styles.cardDivider} />
          <List.Item
            title={t('animals.totalAnimals')}
            description={profile ? String(profile.totalAnimals) : '\u2014'}
            left={(props) => <List.Icon {...props} icon="paw" />}
          />
          <List.Item
            title={t('profile.farmSize')}
            description={profile?.farmSize || '\u2014'}
            left={(props) => <List.Icon {...props} icon="terrain" />}
          />
          <List.Item
            title={t('profile.memberSince')}
            description={profile?.memberSince || '\u2014'}
            left={(props) => <List.Icon {...props} icon="calendar" />}
          />
        </Card.Content>
      </Card>

      {/* Quick stats */}
      <View style={styles.statsRow}>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Text style={styles.statIcon}>{'\uD83E\uDD5B'}</Text>
            <Text variant="headlineSmall" style={styles.statValue}>
              {profile ? `${profile.todayMilk}L` : '\u2014'}
            </Text>
            <Text variant="bodySmall">{t('milk.todayTotal')}</Text>
          </Card.Content>
        </Card>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Text style={styles.statIcon}>{'\uD83D\uDCB0'}</Text>
            <Text variant="headlineSmall" style={styles.statValue}>
              {profile ? `\u20B9${(profile.monthlyIncome / 1000).toFixed(1)}K` : '\u2014'}
            </Text>
            <Text variant="bodySmall">{t('income.monthly')}</Text>
          </Card.Content>
        </Card>
      </View>

      {/* Logout */}
      <Button
        mode="outlined"
        onPress={handleLogout}
        style={styles.logoutButton}
        contentStyle={styles.logoutContent}
        textColor={statusColors.urgent}
        icon="logout"
      >
        {t('profile.logout')}
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  scroll: {
    padding: SPACING.md,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    paddingVertical: SPACING.lg,
  },
  avatarLarge: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: '#E8F5E9',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SPACING.md,
  },
  avatarText: {
    fontSize: 48,
  },
  name: {
    fontWeight: 'bold',
  },
  phone: {
    color: '#616161',
    marginTop: SPACING.xs,
  },
  village: {
    color: '#9E9E9E',
    marginTop: 2,
  },
  card: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
    marginBottom: SPACING.md,
  },
  cardTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.xs,
  },
  cardDivider: {
    marginVertical: SPACING.sm,
  },
  langGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
    marginTop: SPACING.sm,
  },
  langButton: {
    borderRadius: 12,
    minWidth: '30%' as unknown as number,
    flexGrow: 1,
  },
  statsRow: {
    flexDirection: 'row',
    gap: SPACING.sm,
    marginBottom: SPACING.md,
  },
  statCard: {
    flex: 1,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
  },
  statContent: {
    alignItems: 'center',
    paddingVertical: SPACING.md,
    gap: SPACING.xs,
  },
  statIcon: {
    fontSize: 32,
  },
  statValue: {
    fontWeight: 'bold',
    color: statusColors.healthy,
  },
  logoutButton: {
    borderRadius: 12,
    borderColor: statusColors.urgent,
    marginTop: SPACING.md,
  },
  logoutContent: {
    height: 48,
  },
});
