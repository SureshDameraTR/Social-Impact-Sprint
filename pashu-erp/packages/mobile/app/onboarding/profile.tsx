import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Text, TextInput, Menu } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../../src/config/theme';

const KARNATAKA_DISTRICTS = [
  'Mysore', 'Mandya', 'Bangalore Rural', 'Hassan', 'Tumkur',
  'Shimoga', 'Belgaum', 'Dharwad', 'Raichur', 'Bellary',
  'Chitradurga', 'Davanagere', 'Haveri', 'Gadag', 'Kolar',
  'Chikmagalur', 'Udupi', 'Dakshina Kannada',
];

export default function ProfileScreen() {
  const { t } = useTranslation();
  const [name, setName] = useState('');
  const [district, setDistrict] = useState('');
  const [village, setVillage] = useState('');
  const [menuVisible, setMenuVisible] = useState(false);

  const mockPhone = '+91 98765 43210';

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
        outlineColor="#BDBDBD"
        activeOutlineColor="#2E7D32"
        left={<TextInput.Icon icon="account" />}
      />

      <TextInput
        label={t('onboarding.phoneLabel')}
        value={mockPhone}
        mode="outlined"
        style={styles.input}
        disabled
        outlineColor="#BDBDBD"
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
        outlineColor="#BDBDBD"
        activeOutlineColor="#2E7D32"
        left={<TextInput.Icon icon="home-group" />}
      />

      <Button
        mode="contained"
        onPress={() => router.push('/onboarding/first-animal')}
        style={styles.saveButton}
        contentStyle={styles.saveContent}
        labelStyle={styles.saveLabel}
        disabled={!name || !district}
      >
        {t('onboarding.saveAndContinue')}
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  content: {
    padding: SPACING.lg,
    paddingBottom: 100,
  },
  heading: {
    color: '#2E7D32',
    fontWeight: 'bold',
    marginBottom: SPACING.xs,
  },
  subheading: {
    color: '#616161',
    marginBottom: SPACING.lg,
  },
  input: {
    marginBottom: SPACING.md,
    backgroundColor: '#FFFFFF',
  },
  dropdownButton: {
    marginBottom: SPACING.md,
    borderRadius: CARD_BORDER_RADIUS,
    borderColor: '#BDBDBD',
  },
  dropdownContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
    justifyContent: 'flex-start',
  },
  menuContent: {
    backgroundColor: '#FFFFFF',
    maxHeight: 300,
  },
  menuItem: {
    minHeight: TOUCH_TARGET_MIN,
  },
  saveButton: {
    backgroundColor: '#2E7D32',
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
