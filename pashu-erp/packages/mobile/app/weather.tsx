import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, Text, ProgressBar } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../src/config/theme';

const TODAY_WEATHER = {
  temp: 32,
  humidity: 68,
  rainfall: 0,
  wind: 12,
  condition: 'Partly Cloudy',
  emoji: '⛅',
};

const FORECAST = [
  { day: 'Tue', temp: 33, emoji: '☀️', rain: 0 },
  { day: 'Wed', temp: 31, emoji: '🌤️', rain: 10 },
  { day: 'Thu', temp: 28, emoji: '🌧️', rain: 80 },
  { day: 'Fri', temp: 29, emoji: '🌦️', rain: 40 },
  { day: 'Sat', temp: 30, emoji: '⛅', rain: 20 },
];

function getHeatStress(temp: number, humidity: number): { level: string; color: string; thi: number } {
  const thi = temp - (0.55 - 0.0055 * humidity) * (temp - 14.5);
  if (thi < 72) return { level: 'normal', color: '#4CAF50', thi: Math.round(thi) };
  if (thi < 79) return { level: 'mild', color: '#FF9800', thi: Math.round(thi) };
  return { level: 'severe', color: '#D32F2F', thi: Math.round(thi) };
}

export default function WeatherScreen() {
  const { t } = useTranslation();
  const heatStress = getHeatStress(TODAY_WEATHER.temp, TODAY_WEATHER.humidity);
  const hasRainAlert = FORECAST.some((d) => d.rain >= 60);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('weather.title')}
      </Text>
      <Text variant="bodyMedium" style={styles.location}>
        📍 Mysore, Karnataka
      </Text>

      {hasRainAlert && (
        <Card style={styles.alertBanner}>
          <Card.Content style={styles.alertContent}>
            <Text style={styles.alertEmoji}>🌧️</Text>
            <Text variant="titleSmall" style={styles.alertText}>
              {t('weather.rainfallAlert')}
            </Text>
          </Card.Content>
        </Card>
      )}

      <Card style={styles.heroCard}>
        <Card.Content style={styles.heroContent}>
          <Text style={styles.heroEmoji}>{TODAY_WEATHER.emoji}</Text>
          <Text variant="displaySmall" style={styles.heroTemp}>
            {TODAY_WEATHER.temp}°C
          </Text>
          <Text variant="bodyLarge" style={styles.heroCondition}>
            {TODAY_WEATHER.condition}
          </Text>
          <View style={styles.heroStats}>
            <View style={styles.stat}>
              <Text style={styles.statEmoji}>💧</Text>
              <Text variant="bodyMedium">{t('weather.humidity')}</Text>
              <Text variant="titleMedium" style={styles.statValue}>{TODAY_WEATHER.humidity}%</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statEmoji}>🌧️</Text>
              <Text variant="bodyMedium">{t('weather.rainfall')}</Text>
              <Text variant="titleMedium" style={styles.statValue}>{TODAY_WEATHER.rainfall} mm</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statEmoji}>💨</Text>
              <Text variant="bodyMedium">{t('weather.wind')}</Text>
              <Text variant="titleMedium" style={styles.statValue}>{TODAY_WEATHER.wind} km/h</Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.heatCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            {t('weather.heatStress')}
          </Text>
          <Text variant="bodyMedium" style={{ marginBottom: SPACING.sm }}>
            THI: {heatStress.thi} — {t(`weather.heatLevel.${heatStress.level}`)}
          </Text>
          <ProgressBar
            progress={heatStress.thi / 100}
            color={heatStress.color}
            style={styles.progressBar}
          />
        </Card.Content>
      </Card>

      <Text variant="titleMedium" style={styles.sectionTitle}>
        {t('weather.fiveDayForecast')}
      </Text>
      <View style={styles.forecastRow}>
        {FORECAST.map((day) => (
          <Card key={day.day} style={styles.forecastCard}>
            <Card.Content style={styles.forecastContent}>
              <Text variant="labelLarge" style={styles.forecastDay}>{day.day}</Text>
              <Text style={styles.forecastEmoji}>{day.emoji}</Text>
              <Text variant="titleMedium" style={styles.forecastTemp}>{day.temp}°C</Text>
              <Text variant="bodySmall" style={styles.forecastRain}>
                🌧 {day.rain}%
              </Text>
            </Card.Content>
          </Card>
        ))}
      </View>

      <Button
        mode="outlined"
        icon="volume-high"
        onPress={() => {}}
        style={styles.voiceButton}
        contentStyle={styles.voiceContent}
      >
        {t('weather.voiceSummary')}
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
    padding: SPACING.md,
    paddingBottom: 100,
  },
  heading: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  location: {
    color: '#616161',
    marginBottom: SPACING.md,
  },
  alertBanner: {
    backgroundColor: '#FFF3E0',
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
    borderLeftWidth: 4,
    borderLeftColor: '#FF9800',
  },
  alertContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  alertEmoji: {
    fontSize: 24,
  },
  alertText: {
    color: '#E65100',
    flex: 1,
  },
  heroCard: {
    backgroundColor: '#E8F5E9',
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
  },
  heroContent: {
    alignItems: 'center',
    paddingVertical: SPACING.lg,
  },
  heroEmoji: {
    fontSize: 64,
  },
  heroTemp: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  heroCondition: {
    color: '#616161',
    marginBottom: SPACING.md,
  },
  heroStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginTop: SPACING.sm,
  },
  stat: {
    alignItems: 'center',
  },
  statEmoji: {
    fontSize: 20,
    marginBottom: 2,
  },
  statValue: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  heatCard: {
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.lg,
  },
  progressBar: {
    height: 12,
    borderRadius: 6,
  },
  sectionTitle: {
    color: '#212121',
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
    marginTop: SPACING.sm,
  },
  forecastRow: {
    flexDirection: 'row',
    gap: SPACING.sm,
    marginBottom: SPACING.lg,
  },
  forecastCard: {
    flex: 1,
    borderRadius: 12,
  },
  forecastContent: {
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.xs,
  },
  forecastDay: {
    color: '#616161',
  },
  forecastEmoji: {
    fontSize: 28,
    marginVertical: SPACING.xs,
  },
  forecastTemp: {
    color: '#212121',
    fontWeight: 'bold',
  },
  forecastRain: {
    color: '#1565C0',
  },
  voiceButton: {
    borderColor: '#2E7D32',
    borderRadius: CARD_BORDER_RADIUS,
  },
  voiceContent: {
    minHeight: TOUCH_TARGET_MIN,
  },
});
