import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Button, SegmentedButtons, TextInput, Card, Snackbar } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { MicButton } from '../../src/components/MicButton';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS } from '../../src/config/theme';

const MOCK_COWS = [
  { id: '1', name: 'Lakshmi', emoji: '\uD83D\uDC04' },
  { id: '2', name: 'Gowri', emoji: '\uD83D\uDC04' },
  { id: '6', name: 'Nandi', emoji: '\uD83D\uDC04' },
];

export default function MilkScreen() {
  const { t } = useTranslation();
  const [session, setSession] = useState('morning');
  const [selectedAnimal, setSelectedAnimal] = useState('');
  const [quantity, setQuantity] = useState('');
  const [snackVisible, setSnackVisible] = useState(false);
  const [snackMessage, setSnackMessage] = useState('');

  const handleRecord = () => {
    setSnackMessage(t('milk.recorded'));
    setSnackVisible(true);
    setQuantity('');
    setSelectedAnimal('');
  };

  const handleVoiceResult = (value: number) => {
    setQuantity(String(value));
    setSnackMessage(`${value}L`);
  };

  const handleVoiceTranscript = (text: string) => {
    // Update snack to show "transcribed text -- parsed value"
    setSnackMessage((prev) => `${text} \u2014 ${prev || '...'}`);
    setSnackVisible(true);
  };

  if (MOCK_COWS.length === 0) {
    return (
      <View style={styles.container}>
        <EmptyState
          icon={'\uD83E\uDD5B'}
          title={t('empty.noMilkRecords')}
          subtitle={t('milk.recordMilk')}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Today's total */}
        <Card style={styles.totalCard}>
          <Card.Content style={styles.totalContent}>
            <Text variant="bodyLarge" style={styles.totalLabel}>
              {t('milk.todayTotal')}
            </Text>
            <Text variant="displaySmall" style={styles.totalAmount}>
              12.5 {t('milk.liters')}
            </Text>
          </Card.Content>
        </Card>

        {/* Session picker */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          {t('milk.session')}
        </Text>
        <SegmentedButtons
          value={session}
          onValueChange={setSession}
          buttons={[
            { value: 'morning', label: `\u2600\uFE0F ${t('milk.morning')}` },
            { value: 'evening', label: `\uD83C\uDF19 ${t('milk.evening')}` },
          ]}
          style={styles.segmented}
        />

        {/* Animal picker */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          {t('milk.selectAnimal')}
        </Text>
        <View style={styles.animalPicker}>
          {MOCK_COWS.map((cow) => (
            <Button
              key={cow.id}
              mode={selectedAnimal === cow.id ? 'contained' : 'outlined'}
              onPress={() => setSelectedAnimal(cow.id)}
              style={styles.animalButton}
              contentStyle={styles.animalButtonContent}
              labelStyle={styles.animalButtonLabel}
            >
              {cow.emoji} {cow.name}
            </Button>
          ))}
        </View>

        {/* Quantity input */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          {t('milk.quantity')} ({t('milk.liters')})
        </Text>
        <View style={styles.quantityRow}>
          <TextInput
            value={quantity}
            onChangeText={setQuantity}
            keyboardType="decimal-pad"
            mode="outlined"
            style={styles.quantityInput}
            placeholder="0.0"
          />
          <MicButton
            context="milk_quantity"
            onResult={handleVoiceResult}
            onTranscript={handleVoiceTranscript}
          />
        </View>

        {/* Record button */}
        <Button
          mode="contained"
          onPress={handleRecord}
          disabled={!selectedAnimal || !quantity}
          style={styles.recordButton}
          contentStyle={styles.recordButtonContent}
          labelStyle={styles.recordButtonLabel}
        >
          {t('milk.recordMilk')}
        </Button>

        {/* History link */}
        <Button
          mode="text"
          onPress={() => router.push('/milk/history')}
          icon="history"
          style={styles.historyButton}
          labelStyle={styles.historyLabel}
        >
          {t('milk.history')}
        </Button>
      </ScrollView>

      <Snackbar
        visible={snackVisible}
        onDismiss={() => setSnackVisible(false)}
        duration={2000}
        style={styles.snackbar}
      >
        {snackMessage}
      </Snackbar>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  scroll: {
    padding: SPACING.md,
    paddingBottom: 100,
  },
  totalCard: {
    backgroundColor: '#2E7D32',
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.lg,
  },
  totalContent: {
    alignItems: 'center',
    paddingVertical: SPACING.lg,
  },
  totalLabel: {
    color: '#C8E6C9',
  },
  totalAmount: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  sectionTitle: {
    marginTop: SPACING.md,
    marginBottom: SPACING.sm,
    fontWeight: 'bold',
    color: '#212121',
  },
  segmented: {
    marginBottom: SPACING.sm,
  },
  animalPicker: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  animalButton: {
    borderRadius: 12,
  },
  animalButtonContent: {
    height: 56,
  },
  animalButtonLabel: {
    fontSize: 16,
  },
  quantityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.md,
  },
  quantityInput: {
    flex: 1,
    fontSize: 24,
  },
  recordButton: {
    marginTop: SPACING.lg,
    borderRadius: 12,
    backgroundColor: '#2E7D32',
  },
  recordButtonContent: {
    height: 56,
  },
  recordButtonLabel: {
    fontSize: 18,
  },
  historyButton: {
    marginTop: SPACING.md,
  },
  historyLabel: {
    fontSize: 16,
  },
  snackbar: {
    backgroundColor: '#2E7D32',
  },
});
