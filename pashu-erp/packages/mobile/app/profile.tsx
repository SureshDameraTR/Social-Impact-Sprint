import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Button, Switch, Divider, List, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, colors, statusColors } from '../src/config/theme';
import { api } from '../src/config/api';

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
  const [isKannada, setIsKannada] = useState(i18n.language === 'kn');
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

  const toggleLanguage = () => {
    const newLang = isKannada ? 'en' : 'kn';
    i18n.changeLanguage(newLang);
    setIsKannada(!isKannada);
  };

  const handleLogout = async () => {
    await SecureStore.deleteItemAsync('auth_token');
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

      {/* Language toggle */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.settingRow}>
            <View>
              <Text variant="titleMedium">
                {isKannada ? t('common.kannada') : t('common.english')}
              </Text>
              <Text variant="bodySmall" style={styles.settingHint}>
                {isKannada ? 'Switch to English' : '\u0C95\u0CA8\u0CCD\u0CA8\u0CA1\u0C95\u0CCD\u0C95\u0CC6 \u0CAC\u0CA6\u0CB2\u0CBF\u0CB8\u0CBF'}
              </Text>
            </View>
            <Switch
              value={isKannada}
              onValueChange={toggleLanguage}
              color={colors.primary}
            />
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
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingHint: {
    color: '#9E9E9E',
    marginTop: 2,
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
