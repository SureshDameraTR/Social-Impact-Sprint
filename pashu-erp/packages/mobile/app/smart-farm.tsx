import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Banner, Chip } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, CARD_BORDER_RADIUS } from '../src/config/theme';

const MOCK_DEVICES = [
  { id: '1', name: 'GPS Tracker #1', status: 'online', animal: 'Lakshmi', battery: '85%' },
  { id: '2', name: 'GPS Tracker #2', status: 'online', animal: 'Gowri', battery: '72%' },
  { id: '3', name: 'Temperature Sensor', status: 'offline', animal: 'Shed A', battery: '12%' },
  { id: '4', name: 'Water Level Monitor', status: 'online', animal: 'Trough #1', battery: '95%' },
];

export default function SmartFarmScreen() {
  const { t } = useTranslation();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scroll}>
      {/* Phase 2 banner */}
      <Banner
        visible
        icon="information"
        style={styles.banner}
        actions={[]}
      >
        <Text variant="bodyLarge" style={styles.bannerText}>
          {'\uD83D\uDEA7'} Phase 2 Feature - IoT integration coming soon
        </Text>
      </Banner>

      <Text variant="headlineSmall" style={styles.heading}>
        {t('common.smartFarm')}
      </Text>

      {/* GPS Map Placeholder */}
      <Card style={styles.mapCard}>
        <Card.Content style={styles.mapContent}>
          <Text style={styles.mapIcon}>{'\uD83D\uDDFA\uFE0F'}</Text>
          <Text variant="titleMedium" style={styles.mapTitle}>
            GPS Animal Tracking
          </Text>
          <Text variant="bodyMedium" style={styles.mapSubtitle}>
            Live map will show animal locations from GPS collars
          </Text>
          <View style={styles.mapPlaceholder}>
            <Text style={styles.mapPlaceholderText}>
              {'\uD83D\uDCCD'} Lakshmi - Grazing Field A{'\n'}
              {'\uD83D\uDCCD'} Gowri - Near Water Tank{'\n'}
              {'\uD83D\uDCCD'} Nandi - Shed B
            </Text>
          </View>
        </Card.Content>
      </Card>

      {/* Device cards */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        IoT Devices
      </Text>
      {MOCK_DEVICES.map((device) => (
        <Card key={device.id} style={styles.deviceCard}>
          <Card.Content style={styles.deviceContent}>
            <View style={styles.deviceInfo}>
              <Text variant="titleSmall">{device.name}</Text>
              <Text variant="bodySmall" style={styles.deviceAnimal}>
                {device.animal}
              </Text>
            </View>
            <View style={styles.deviceMeta}>
              <Chip
                mode="flat"
                style={[
                  styles.statusChip,
                  { backgroundColor: device.status === 'online' ? '#C8E6C9' : '#FFCDD2' },
                ]}
                textStyle={{
                  color: device.status === 'online' ? '#2E7D32' : '#D32F2F',
                  fontSize: 12,
                }}
              >
                {device.status}
              </Chip>
              <Text variant="labelSmall" style={styles.battery}>
                {'\uD83D\uDD0B'} {device.battery}
              </Text>
            </View>
          </Card.Content>
        </Card>
      ))}

      {/* Alerts section */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        Smart Alerts
      </Text>
      <Card style={styles.alertCard}>
        <Card.Content>
          <Text variant="bodyLarge">
            {'\u26A0\uFE0F'} Temperature Sensor in Shed A is offline - low battery
          </Text>
        </Card.Content>
      </Card>
      <Card style={styles.alertCardGreen}>
        <Card.Content>
          <Text variant="bodyLarge">
            {'\u2705'} All GPS trackers reporting normally
          </Text>
        </Card.Content>
      </Card>
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
  banner: {
    backgroundColor: '#FFF3E0',
    borderRadius: 12,
    marginBottom: SPACING.md,
  },
  bannerText: {
    color: '#E65100',
  },
  heading: {
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: SPACING.md,
  },
  mapCard: {
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#E8F5E9',
    marginBottom: SPACING.lg,
  },
  mapContent: {
    alignItems: 'center',
    paddingVertical: SPACING.lg,
  },
  mapIcon: {
    fontSize: 48,
    marginBottom: SPACING.sm,
  },
  mapTitle: {
    fontWeight: 'bold',
  },
  mapSubtitle: {
    color: '#616161',
    textAlign: 'center',
    marginBottom: SPACING.md,
  },
  mapPlaceholder: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: SPACING.md,
    width: '100%',
    borderWidth: 2,
    borderColor: '#C8E6C9',
    borderStyle: 'dashed',
  },
  mapPlaceholderText: {
    fontSize: 16,
    lineHeight: 28,
    textAlign: 'center',
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
    marginTop: SPACING.md,
  },
  deviceCard: {
    marginBottom: SPACING.sm,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
  },
  deviceContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  deviceInfo: {
    flex: 1,
  },
  deviceAnimal: {
    color: '#9E9E9E',
    marginTop: 2,
  },
  deviceMeta: {
    alignItems: 'flex-end',
    gap: 4,
  },
  statusChip: {
    height: 28,
  },
  battery: {
    color: '#616161',
  },
  alertCard: {
    marginBottom: SPACING.sm,
    borderRadius: 12,
    backgroundColor: '#FFF3E0',
  },
  alertCardGreen: {
    marginBottom: SPACING.sm,
    borderRadius: 12,
    backgroundColor: '#E8F5E9',
  },
});
