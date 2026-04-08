import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Button, Switch, Divider, List } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { SPACING, CARD_BORDER_RADIUS } from '../src/config/theme';

export default function ProfileScreen() {
  const { t, i18n } = useTranslation();
  const [isKannada, setIsKannada] = useState(i18n.language === 'kn');

  const toggleLanguage = () => {
    const newLang = isKannada ? 'en' : 'kn';
    i18n.changeLanguage(newLang);
    setIsKannada(!isKannada);
  };

  const handleLogout = async () => {
    await SecureStore.deleteItemAsync('auth_token');
    router.replace('/(auth)/login');
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      {/* User info */}
      <View style={styles.header}>
        <View style={styles.avatarLarge}>
          <Text style={styles.avatarText}>{'\uD83D\uDC68\u200D\uD83C\uDF3E'}</Text>
        </View>
        <Text variant="headlineMedium" style={styles.name}>
          Ramesh Kumar
        </Text>
        <Text variant="bodyLarge" style={styles.phone}>
          +91 98765 43210
        </Text>
        <Text variant="bodyMedium" style={styles.village}>
          Hoskote, Karnataka
        </Text>
      </View>

      {/* Language toggle */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.settingRow}>
            <View>
              <Text variant="titleMedium">
                {isKannada ? 'ಕನ್ನಡ' : 'English'}
              </Text>
              <Text variant="bodySmall" style={styles.settingHint}>
                {isKannada ? 'Switch to English' : 'ಕನ್ನಡಕ್ಕೆ ಬದಲಿಸಿ'}
              </Text>
            </View>
            <Switch
              value={isKannada}
              onValueChange={toggleLanguage}
              color="#2E7D32"
            />
          </View>
        </Card.Content>
      </Card>

      {/* Farm info */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.cardTitle}>
            {'\uD83C\uDFE1'} Farm Details
          </Text>
          <Divider style={styles.cardDivider} />
          <List.Item
            title={t('animals.totalAnimals')}
            description="7"
            left={(props) => <List.Icon {...props} icon="paw" />}
          />
          <List.Item
            title="Farm Size"
            description="5 acres"
            left={(props) => <List.Icon {...props} icon="terrain" />}
          />
          <List.Item
            title="Member Since"
            description="January 2026"
            left={(props) => <List.Icon {...props} icon="calendar" />}
          />
        </Card.Content>
      </Card>

      {/* Quick stats */}
      <View style={styles.statsRow}>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Text style={styles.statIcon}>{'\uD83E\uDD5B'}</Text>
            <Text variant="headlineSmall" style={styles.statValue}>12.5L</Text>
            <Text variant="bodySmall">{t('milk.todayTotal')}</Text>
          </Card.Content>
        </Card>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Text style={styles.statIcon}>{'\uD83D\uDCB0'}</Text>
            <Text variant="headlineSmall" style={styles.statValue}>{'\u20B9'}14.5K</Text>
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
        textColor="#D32F2F"
        icon="logout"
      >
        Logout
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
    color: '#2E7D32',
  },
  logoutButton: {
    borderRadius: 12,
    borderColor: '#D32F2F',
    marginTop: SPACING.md,
  },
  logoutContent: {
    height: 48,
  },
});
