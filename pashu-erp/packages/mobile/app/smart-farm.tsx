import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Banner, Chip, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, colors } from '../src/config/theme';
import { api } from '../src/config/api';

interface IoTDevice {
  id: string;
  name: string;
  status: string;
  animal: string;
  battery: string;
}

export default function SmartFarmScreen() {
  const { t } = useTranslation();
  const [devices, setDevices] = useState<IoTDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDevices = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<IoTDevice[]>('/iot/devices')
      .then(res => setDevices(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#2E7D32" />
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
          onAction={fetchDevices}
        />
      </View>
    );
  }

  const offlineDevices = devices.filter(d => d.status === 'offline');
  const onlineDevices = devices.filter(d => d.status === 'online');

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
          {'\uD83D\uDEA7'} {t('smartFarm.comingSoon')}
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
            {t('smartFarm.gpsTracking')}
          </Text>
          <Text variant="bodyMedium" style={styles.mapSubtitle}>
            {t('smartFarm.gpsDescription')}
          </Text>
        </Card.Content>
      </Card>

      {/* Device cards */}
      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('smartFarm.iotDevices')}
      </Text>

      {devices.length === 0 && (
        <EmptyState
          icon={'\uD83D\uDCE1'}
          title={t('common.noData')}
          subtitle={t('common.smartFarm')}
        />
      )}

      {devices.map((device) => (
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
      {(offlineDevices.length > 0 || onlineDevices.length > 0) && (
        <>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            Smart Alerts
          </Text>
          {offlineDevices.map((device) => (
            <Card key={`alert-${device.id}`} style={styles.alertCard}>
              <Card.Content>
                <Text variant="bodyLarge">
                  {'\u26A0\uFE0F'} {device.name} is offline - {device.battery} battery
                </Text>
              </Card.Content>
            </Card>
          ))}
          {offlineDevices.length === 0 && (
            <Card style={styles.alertCardGreen}>
              <Card.Content>
                <Text variant="bodyLarge">
                  {'\u2705'} All devices reporting normally
                </Text>
              </Card.Content>
            </Card>
          )}
        </>
      )}
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
