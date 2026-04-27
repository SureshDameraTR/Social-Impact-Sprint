import React, { useState, useEffect, useCallback, useRef } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Button, Card, Text, ProgressBar, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { EmptyState } from '../src/components/EmptyState';
import { useSnackbar } from '../src/hooks/useSnackbar';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS, colors, statusColors, accentColors } from '../src/config/theme';
import { api } from '../src/config/api';

interface WeatherCurrent {
  temp: number;
  humidity: number;
  rainfall: number;
  wind: number;
  condition: string;
  emoji: string;
  location: string;
}

interface ForecastDay {
  day: string;
  temp: number;
  emoji: string;
  rain: number;
}

interface WeatherResponse {
  current: WeatherCurrent;
  forecast: ForecastDay[];
}

interface TtsResponse {
  audio: string;
  request_id: string;
}

function getHeatStress(temp: number, humidity: number): { level: string; color: string; thi: number } {
  const thi = temp - (0.55 - 0.0055 * humidity) * (temp - 14.5);
  if (thi < 72) return { level: 'normal', color: '#4CAF50', thi: Math.round(thi) };
  if (thi < 79) return { level: 'mild', color: '#FF9800', thi: Math.round(thi) };
  return { level: 'severe', color: statusColors.urgent, thi: Math.round(thi) };
}

export default function WeatherScreen() {
  const { t } = useTranslation();
  const { showError } = useSnackbar();
  const [weather, setWeather] = useState<WeatherResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ttsLoading, setTtsLoading] = useState(false);
  const soundRef = useRef<Audio.Sound | null>(null);

  const playWeatherSummary = useCallback(async (district: string) => {
    try {
      setTtsLoading(true);
      // Unload any previous sound
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
        soundRef.current = null;
      }
      const data = await api.get<TtsResponse>(`/weather/tts/${encodeURIComponent(district)}`);
      const uri = FileSystem.cacheDirectory + 'weather_tts.wav';
      await FileSystem.writeAsStringAsync(uri, data.audio, {
        encoding: FileSystem.EncodingType.Base64,
      });
      const { sound } = await Audio.Sound.createAsync({ uri });
      soundRef.current = sound;
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          sound.unloadAsync();
          soundRef.current = null;
        }
      });
      await sound.playAsync();
    } catch (e) {
      showError(t('weather.ttsError'));
    } finally {
      setTtsLoading(false);
    }
  }, [showError, t]);

  useEffect(() => {
    return () => {
      soundRef.current?.unloadAsync();
    };
  }, []);

  const fetchWeather = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<WeatherResponse>('/weather')
      .then(res => setWeather(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchWeather();
  }, [fetchWeather]);

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
          onAction={fetchWeather}
        />
      </View>
    );
  }

  if (!weather) {
    return (
      <View style={styles.container}>
        <EmptyState
          icon={'\uD83C\uDF24\uFE0F'}
          title={t('common.noData')}
          subtitle={t('weather.title')}
        />
      </View>
    );
  }

  const current = weather.current;
  const forecast = weather.forecast;
  const heatStress = getHeatStress(current.temp, current.humidity);
  const hasRainAlert = forecast.some((d) => d.rain >= 60);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text variant="headlineMedium" style={styles.heading}>
        {t('weather.title')}
      </Text>
      <Text variant="bodyMedium" style={styles.location}>
        {'\uD83D\uDCCD'} {current.location}
      </Text>

      {hasRainAlert && (
        <Card style={styles.alertBanner}>
          <Card.Content style={styles.alertContent}>
            <Text style={styles.alertEmoji}>{'\uD83C\uDF27\uFE0F'}</Text>
            <Text variant="titleSmall" style={styles.alertText}>
              {t('weather.rainfallAlert')}
            </Text>
          </Card.Content>
        </Card>
      )}

      <Card style={styles.heroCard}>
        <Card.Content style={styles.heroContent}>
          <Text style={styles.heroEmoji}>{current.emoji}</Text>
          <Text variant="displaySmall" style={styles.heroTemp}>
            {current.temp}°C
          </Text>
          <Text variant="bodyLarge" style={styles.heroCondition}>
            {current.condition}
          </Text>
          <View style={styles.heroStats}>
            <View style={styles.stat}>
              <Text style={styles.statEmoji}>{'\uD83D\uDCA7'}</Text>
              <Text variant="bodyMedium">{t('weather.humidity')}</Text>
              <Text variant="titleMedium" style={styles.statValue}>{current.humidity}%</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statEmoji}>{'\uD83C\uDF27\uFE0F'}</Text>
              <Text variant="bodyMedium">{t('weather.rainfall')}</Text>
              <Text variant="titleMedium" style={styles.statValue}>{current.rainfall} mm</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statEmoji}>{'\uD83D\uDCA8'}</Text>
              <Text variant="bodyMedium">{t('weather.wind')}</Text>
              <Text variant="titleMedium" style={styles.statValue}>{current.wind} km/h</Text>
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

      {forecast.length > 0 && (
        <>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            {t('weather.fiveDayForecast')}
          </Text>
          <View style={styles.forecastRow}>
            {forecast.map((day) => (
              <Card key={day.day} style={styles.forecastCard}>
                <Card.Content style={styles.forecastContent}>
                  <Text variant="labelLarge" style={styles.forecastDay}>{day.day}</Text>
                  <Text style={styles.forecastEmoji}>{day.emoji}</Text>
                  <Text variant="titleMedium" style={styles.forecastTemp}>{day.temp}°C</Text>
                  <Text variant="bodySmall" style={styles.forecastRain}>
                    {'\uD83C\uDF27'} {day.rain}%
                  </Text>
                </Card.Content>
              </Card>
            ))}
          </View>
        </>
      )}

      <Button
        mode="outlined"
        icon="volume-high"
        onPress={() => playWeatherSummary(current.location)}
        loading={ttsLoading}
        disabled={ttsLoading}
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
    backgroundColor: colors.surface,
  },
  content: {
    padding: SPACING.md,
    paddingBottom: 100,
  },
  heading: {
    color: colors.primary,
    fontWeight: 'bold',
  },
  location: {
    color: colors.onSurfaceVariant,
    marginBottom: SPACING.md,
  },
  alertBanner: {
    backgroundColor: accentColors.amberLight,
    borderRadius: CARD_BORDER_RADIUS,
    marginBottom: SPACING.md,
    borderLeftWidth: 4,
    borderLeftColor: statusColors.watch,
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
    color: accentColors.amber,
    flex: 1,
  },
  heroCard: {
    backgroundColor: statusColors.healthyBg,
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
    color: statusColors.healthy,
    fontWeight: 'bold',
  },
  heroCondition: {
    color: colors.onSurfaceVariant,
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
    color: statusColors.healthy,
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
    color: colors.onSurface,
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
    color: colors.onSurfaceVariant,
  },
  forecastEmoji: {
    fontSize: 28,
    marginVertical: SPACING.xs,
  },
  forecastTemp: {
    color: colors.onSurface,
    fontWeight: 'bold',
  },
  forecastRain: {
    color: colors.tertiary,
  },
  voiceButton: {
    borderColor: colors.primary,
    borderRadius: CARD_BORDER_RADIUS,
  },
  voiceContent: {
    minHeight: TOUCH_TARGET_MIN,
  },
});
