import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, FAB, Modal, Portal, Text, TextInput, Menu } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';

type Severity = 'critical' | 'high' | 'medium' | 'low';

const SEVERITY_CONFIG: Record<Severity, { color: string; bgColor: string; emoji: string }> = {
  critical: { color: '#D32F2F', bgColor: '#FFEBEE', emoji: '🔴' },
  high: { color: '#E65100', bgColor: '#FFF3E0', emoji: '🟠' },
  medium: { color: '#FF8F00', bgColor: '#FFF8E1', emoji: '🟡' },
  low: { color: '#2E7D32', bgColor: '#E8F5E9', emoji: '🟢' },
};

interface DiseaseAlert {
  id: string;
  disease: string;
  location: string;
  distanceKm: number;
  daysAgo: number;
  severity: Severity;
  affectedCount: number;
  species: string;
  notes: string;
}

const DISEASES = [
  'Foot & Mouth Disease (FMD)',
  'Hemorrhagic Septicemia (HS)',
  'Black Quarter (BQ)',
  'PPR (Goats)',
  'Ranikhet Disease (Poultry)',
  'Lumpy Skin Disease',
  'Brucellosis',
  'Mastitis',
];

const MOCK_ALERTS: DiseaseAlert[] = [
  {
    id: '1',
    disease: 'Foot & Mouth Disease (FMD)',
    location: 'Bannur, Mysore',
    distanceKm: 3,
    daysAgo: 2,
    severity: 'critical',
    affectedCount: 12,
    species: '🐄 Cattle',
    notes: '12 cattle affected in 3 farms. Vaccination drive scheduled.',
  },
  {
    id: '2',
    disease: 'PPR (Goats)',
    location: 'K.R. Pet, Mandya',
    distanceKm: 15,
    daysAgo: 5,
    severity: 'high',
    affectedCount: 8,
    species: '🐐 Goats',
    notes: '8 goats showing symptoms. Quarantine in place.',
  },
  {
    id: '3',
    disease: 'Lumpy Skin Disease',
    location: 'Nagamangala, Mandya',
    distanceKm: 25,
    daysAgo: 10,
    severity: 'medium',
    affectedCount: 5,
    species: '🐄 Cattle',
    notes: 'Contained. Vaccination ongoing in surrounding villages.',
  },
  {
    id: '4',
    disease: 'Mastitis',
    location: 'Hullahalli, Mysore',
    distanceKm: 1,
    daysAgo: 1,
    severity: 'low',
    affectedCount: 2,
    species: '🐄 Cattle',
    notes: 'Non-contagious. Treatment ongoing.',
  },
];

export default function CommunityAlertsScreen() {
  const { t } = useTranslation();
  const [reportVisible, setReportVisible] = useState(false);
  const [reportDisease, setReportDisease] = useState('');
  const [reportNotes, setReportNotes] = useState('');
  const [diseaseMenuVisible, setDiseaseMenuVisible] = useState(false);

  const nearbyAlert = MOCK_ALERTS.find((a) => a.distanceKm <= 5 && a.severity === 'critical');

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text variant="headlineMedium" style={styles.heading}>
          {t('communityAlerts.title')}
        </Text>

        {nearbyAlert && (
          <Card style={styles.urgentBanner}>
            <Card.Content style={styles.urgentContent}>
              <Text style={styles.urgentEmoji}>⚠️</Text>
              <View style={{ flex: 1 }}>
                <Text variant="titleMedium" style={styles.urgentTitle}>
                  {nearbyAlert.disease}
                </Text>
                <Text variant="bodyMedium" style={styles.urgentBody}>
                  {t('communityAlerts.reportedNearby', {
                    distance: nearbyAlert.distanceKm,
                    days: nearbyAlert.daysAgo,
                  })}
                </Text>
              </View>
            </Card.Content>
          </Card>
        )}

        <View style={styles.mapPlaceholder}>
          <Text style={styles.mapEmoji}>🗺️</Text>
          <Text variant="bodyMedium" style={styles.mapText}>
            {t('communityAlerts.mapPlaceholder')}
          </Text>
          {MOCK_ALERTS.map((alert) => {
            const sev = SEVERITY_CONFIG[alert.severity];
            return (
              <View key={alert.id} style={styles.mapPin}>
                <Text>{sev.emoji} {alert.location} ({alert.distanceKm}km)</Text>
              </View>
            );
          })}
        </View>

        <Text variant="titleMedium" style={styles.sectionTitle}>
          {t('communityAlerts.recentAlerts')}
        </Text>

        {MOCK_ALERTS.map((alert) => {
          const sev = SEVERITY_CONFIG[alert.severity];
          return (
            <Card
              key={alert.id}
              style={[styles.alertCard, { borderLeftColor: sev.color, backgroundColor: sev.bgColor }]}
            >
              <Card.Content>
                <View style={styles.alertHeader}>
                  <Text style={{ fontSize: 24 }}>{sev.emoji}</Text>
                  <View style={{ flex: 1, marginLeft: SPACING.sm }}>
                    <Text variant="titleSmall" style={[styles.alertDisease, { color: sev.color }]}>
                      {alert.disease}
                    </Text>
                    <Text variant="bodySmall" style={styles.alertLocation}>
                      📍 {alert.location} — {alert.distanceKm}km {t('communityAlerts.away')}
                    </Text>
                  </View>
                  <View style={[styles.severityBadge, { backgroundColor: sev.color }]}>
                    <Text style={styles.severityText}>
                      {t(`health.${alert.severity}`)}
                    </Text>
                  </View>
                </View>

                <Text variant="bodyMedium" style={styles.alertMeta}>
                  {alert.species} | {alert.affectedCount} {t('communityAlerts.affected')} | {alert.daysAgo} {t('communityAlerts.daysAgo')}
                </Text>
                <Text variant="bodySmall" style={styles.alertNotes}>
                  {alert.notes}
                </Text>
              </Card.Content>
            </Card>
          );
        })}
      </ScrollView>

      <FAB
        icon="alert-plus"
        label={t('communityAlerts.reportDisease')}
        onPress={() => setReportVisible(true)}
        style={styles.fab}
        color="#FFFFFF"
      />

      <Portal>
        <Modal
          visible={reportVisible}
          onDismiss={() => setReportVisible(false)}
          contentContainerStyle={styles.modal}
        >
          <Text variant="titleLarge" style={styles.modalTitle}>
            {t('communityAlerts.reportDisease')}
          </Text>

          <Menu
            visible={diseaseMenuVisible}
            onDismiss={() => setDiseaseMenuVisible(false)}
            anchor={
              <Button
                mode="outlined"
                onPress={() => setDiseaseMenuVisible(true)}
                style={styles.dropdown}
                contentStyle={{ minHeight: TOUCH_TARGET_MIN, justifyContent: 'flex-start' }}
              >
                {reportDisease || t('communityAlerts.selectDisease')}
              </Button>
            }
            contentStyle={{ backgroundColor: '#FFFFFF', maxHeight: 300 }}
          >
            {DISEASES.map((d) => (
              <Menu.Item
                key={d}
                onPress={() => {
                  setReportDisease(d);
                  setDiseaseMenuVisible(false);
                }}
                title={d}
                style={{ minHeight: TOUCH_TARGET_MIN }}
              />
            ))}
          </Menu>

          <View style={styles.gpsRow}>
            <Text variant="bodyMedium">📍 GPS: 12.3156° N, 76.6553° E</Text>
            <Text variant="bodySmall" style={styles.gpsAuto}>({t('communityAlerts.autoDetected')})</Text>
          </View>

          <TextInput
            label={t('communityAlerts.notes')}
            value={reportNotes}
            onChangeText={setReportNotes}
            mode="outlined"
            multiline
            numberOfLines={3}
            style={styles.notesInput}
            outlineColor="#BDBDBD"
            activeOutlineColor="#2E7D32"
          />

          <Button
            mode="contained"
            onPress={() => setReportVisible(false)}
            style={styles.submitButton}
            contentStyle={{ minHeight: TOUCH_TARGET_MIN }}
          >
            {t('communityAlerts.submitReport')}
          </Button>
        </Modal>
      </Portal>
    </View>
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
    marginBottom: SPACING.md,
  },
  urgentBanner: {
    backgroundColor: '#FFEBEE',
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
    borderWidth: 2,
    borderColor: '#D32F2F',
  },
  urgentContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  urgentEmoji: {
    fontSize: 32,
  },
  urgentTitle: {
    color: '#D32F2F',
    fontWeight: 'bold',
  },
  urgentBody: {
    color: '#D32F2F',
  },
  mapPlaceholder: {
    backgroundColor: '#E8F5E9',
    borderRadius: CARD_BORDER_RADIUS,
    padding: SPACING.md,
    marginBottom: SPACING.lg,
    alignItems: 'center',
  },
  mapEmoji: {
    fontSize: 48,
    marginBottom: SPACING.sm,
  },
  mapText: {
    color: '#616161',
    marginBottom: SPACING.sm,
  },
  mapPin: {
    paddingVertical: 4,
  },
  sectionTitle: {
    color: '#212121',
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
  },
  alertCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
    borderLeftWidth: 4,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
  },
  alertDisease: {
    fontWeight: 'bold',
  },
  alertLocation: {
    color: '#616161',
  },
  severityBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: 4,
    borderRadius: 8,
  },
  severityText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: 'bold',
  },
  alertMeta: {
    color: '#424242',
    marginBottom: SPACING.xs,
  },
  alertNotes: {
    color: '#616161',
    fontStyle: 'italic',
  },
  fab: {
    position: 'absolute',
    right: SPACING.md,
    bottom: SPACING.md,
    backgroundColor: '#D32F2F',
    borderRadius: 16,
  },
  modal: {
    backgroundColor: '#FFFFFF',
    margin: SPACING.lg,
    padding: SPACING.lg,
    borderRadius: CARD_BORDER_RADIUS,
  },
  modalTitle: {
    color: '#D32F2F',
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
  dropdown: {
    marginBottom: SPACING.md,
    borderRadius: CARD_BORDER_RADIUS,
    borderColor: '#BDBDBD',
  },
  gpsRow: {
    marginBottom: SPACING.md,
  },
  gpsAuto: {
    color: '#9E9E9E',
  },
  notesInput: {
    marginBottom: SPACING.md,
    backgroundColor: '#FFFFFF',
  },
  submitButton: {
    backgroundColor: '#D32F2F',
    borderRadius: CARD_BORDER_RADIUS,
  },
});
