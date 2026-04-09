import React, { useState } from 'react';
import { View, StyleSheet, Image } from 'react-native';
import { Button, Text, ToggleButton } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { SPACING, TOUCH_TARGET_MIN, ICON_SIZE_LARGE } from '../../src/config/theme';

export default function WelcomeScreen() {
  const { t, i18n } = useTranslation();
  const [language, setLanguage] = useState<string>(i18n.language || 'kn');
  const [highContrast, setHighContrast] = useState(false);

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
    i18n.changeLanguage(lang);
  };

  return (
    <View style={[styles.container, highContrast && styles.highContrast]}>
      <View style={styles.logoSection}>
        <View style={[styles.logoPlaceholder, highContrast && styles.logoPlaceholderHC]}>
          <Text style={styles.logoEmoji}>🐄</Text>
        </View>
        <Text variant="headlineLarge" style={[styles.title, highContrast && styles.titleHC]}>
          PashuRaksha
        </Text>
        <Text variant="bodyLarge" style={[styles.subtitle, highContrast && styles.subtitleHC]}>
          {t('onboarding.welcomeSubtitle')}
        </Text>
      </View>

      <View style={styles.languageSection}>
        <Text variant="titleMedium" style={[styles.sectionLabel, highContrast && styles.sectionLabelHC]}>
          {t('onboarding.selectLanguage')}
        </Text>
        <View style={styles.languageRow}>
          <Button
            mode={language === 'kn' ? 'contained' : 'outlined'}
            onPress={() => handleLanguageChange('kn')}
            style={styles.langButton}
            contentStyle={styles.langButtonContent}
            labelStyle={styles.langLabel}
          >
            ಕನ್ನಡ
          </Button>
          <Button
            mode={language === 'en' ? 'contained' : 'outlined'}
            onPress={() => handleLanguageChange('en')}
            style={styles.langButton}
            contentStyle={styles.langButtonContent}
            labelStyle={styles.langLabel}
          >
            English
          </Button>
        </View>
      </View>

      <View style={styles.accessibilitySection}>
        <Text variant="titleMedium" style={[styles.sectionLabel, highContrast && styles.sectionLabelHC]}>
          {t('onboarding.accessibility')}
        </Text>
        <Button
          mode={highContrast ? 'contained' : 'outlined'}
          onPress={() => setHighContrast(!highContrast)}
          style={styles.accessButton}
          contentStyle={styles.accessButtonContent}
          icon={highContrast ? 'eye' : 'eye-outline'}
        >
          {t('onboarding.highContrast')}
        </Button>
      </View>

      <Button
        mode="contained"
        onPress={() => router.push('/onboarding/profile')}
        style={styles.continueButton}
        contentStyle={styles.continueContent}
        labelStyle={styles.continueLabel}
      >
        {t('onboarding.continue')}
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
    paddingHorizontal: SPACING.lg,
    justifyContent: 'center',
  },
  highContrast: {
    backgroundColor: '#000000',
  },
  logoSection: {
    alignItems: 'center',
    marginBottom: SPACING.xl,
  },
  logoPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#C8E6C9',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  logoEmoji: {
    fontSize: ICON_SIZE_LARGE,
  },
  title: {
    color: '#2E7D32',
    fontWeight: 'bold',
    textAlign: 'center',
  },
  subtitle: {
    color: '#616161',
    textAlign: 'center',
    marginTop: SPACING.xs,
  },
  languageSection: {
    marginBottom: SPACING.lg,
  },
  sectionLabel: {
    color: '#212121',
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  languageRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: SPACING.md,
  },
  langButton: {
    borderRadius: 16,
    minWidth: 140,
  },
  langButtonContent: {
    minHeight: TOUCH_TARGET_MIN + 16,
  },
  langLabel: {
    fontSize: 20,
  },
  accessibilitySection: {
    marginBottom: SPACING.xl,
    alignItems: 'center',
  },
  accessButton: {
    borderRadius: 16,
  },
  accessButtonContent: {
    minHeight: TOUCH_TARGET_MIN,
  },
  continueButton: {
    backgroundColor: '#2E7D32',
    borderRadius: 16,
  },
  continueContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  continueLabel: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  titleHC: {
    color: '#FFFFFF',
  },
  subtitleHC: {
    color: '#DDDDDD',
  },
  sectionLabelHC: {
    color: '#FFFFFF',
  },
  logoPlaceholderHC: {
    backgroundColor: '#333333',
  },
});
