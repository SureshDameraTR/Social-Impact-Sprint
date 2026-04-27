import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, Alert } from 'react-native';
import { Button, Text, TextInput, Menu } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import * as Storage from '../../src/config/storage';
import { api } from '../../src/config/api';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors } from '../../src/config/theme';

const KARNATAKA_DISTRICTS = [
  'Bagalkote', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
  'Bidar', 'Chamarajanagara', 'Chikballapura', 'Chikkamagaluru', 'Chitradurga',
  'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan',
  'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal',
  'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
  'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayapura', 'Vijayanagara',
  'Yadgir',
];

export default function ProfileScreen() {
  const { t } = useTranslation();
  const [name, setName] = useState('');
  const [district, setDistrict] = useState('');
  const [village, setVillage] = useState('');
  const [menuVisible, setMenuVisible] = useState(false);
  const [phone, setPhone] = useState('');
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    Storage.getItemAsync('user_phone').then((val) => {
      if (val) setPhone(val);
    });
  }, []);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('onboarding.profileTitle')}
      </Text>
      <Text variant="bodyLarge" style={styles.subheading}>
        {t('onboarding.profileSubtitle')}
      </Text>

      <TextInput
        label={t('onboarding.nameLabel')}
        value={name}
        onChangeText={setName}
        mode="outlined"
        style={styles.input}
        outlineColor={colors.outlineVariant}
        activeOutlineColor={colors.primary}
        left={<TextInput.Icon icon="account" />}
      />

      <TextInput
        label={t('onboarding.phoneLabel')}
        value={phone}
        mode="outlined"
        style={styles.input}
        disabled
        outlineColor={colors.outlineVariant}
        left={<TextInput.Icon icon="phone" />}
      />

      <Menu
        visible={menuVisible}
        onDismiss={() => setMenuVisible(false)}
        anchor={
          <Button
            mode="outlined"
            onPress={() => setMenuVisible(true)}
            style={styles.dropdownButton}
            contentStyle={styles.dropdownContent}
            icon="map-marker"
          >
            {district || t('onboarding.selectDistrict')}
          </Button>
        }
        contentStyle={styles.menuContent}
      >
        {KARNATAKA_DISTRICTS.map((d) => (
          <Menu.Item
            key={d}
            onPress={() => {
              setDistrict(d);
              setMenuVisible(false);
            }}
            title={d}
            style={styles.menuItem}
          />
        ))}
      </Menu>

      <TextInput
        label={t('onboarding.villageSearch')}
        value={village}
        onChangeText={setVillage}
        mode="outlined"
        style={styles.input}
        outlineColor={colors.outlineVariant}
        activeOutlineColor={colors.primary}
        left={<TextInput.Icon icon="home-group" />}
      />

      <Button
        mode="contained"
        onPress={async () => {
          setSaving(true);
          try {
            await api.post('/onboarding/profile', { name, district, village });
            router.push('/onboarding/first-animal');
          } catch (e) {
            Alert.alert(t('common.error'), t('onboarding.saveFailed'));
          } finally {
            setSaving(false);
          }
        }}
        style={styles.saveButton}
        contentStyle={styles.saveContent}
        labelStyle={styles.saveLabel}
        disabled={!name || !district || saving}
        loading={saving}
      >
        {t('onboarding.saveAndContinue')}
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  content: {
    padding: SPACING.lg,
    paddingBottom: 100,
  },
  heading: {
    color: colors.primary,
    fontWeight: 'bold',
    marginBottom: SPACING.xs,
  },
  subheading: {
    color: colors.onSurfaceVariant,
    marginBottom: SPACING.lg,
  },
  input: {
    marginBottom: SPACING.md,
    backgroundColor: colors.onPrimary,
  },
  dropdownButton: {
    marginBottom: SPACING.md,
    borderRadius: CARD_BORDER_RADIUS,
    borderColor: colors.outlineVariant,
  },
  dropdownContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
    justifyContent: 'flex-start',
  },
  menuContent: {
    backgroundColor: colors.onPrimary,
    maxHeight: 300,
  },
  menuItem: {
    minHeight: TOUCH_TARGET_MIN,
  },
  saveButton: {
    backgroundColor: colors.primary,
    borderRadius: CARD_BORDER_RADIUS,
    marginTop: SPACING.lg,
  },
  saveContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  saveLabel: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});
