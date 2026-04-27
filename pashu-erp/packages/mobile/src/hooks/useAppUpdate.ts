import { useEffect, useState } from 'react';
import { Alert, Platform } from 'react-native';
import { useTranslation } from 'react-i18next';

/**
 * Checks for OTA updates on app launch (production only).
 * Uses expo-updates to fetch and apply JS bundle updates without
 * requiring an app store review cycle.
 *
 * Behaviour:
 *  - Skipped entirely in __DEV__ mode
 *  - Runs a background check on mount — never blocks app startup
 *  - If an update is found, downloads it and prompts the user to restart
 *  - All errors are caught silently — a failed update check must never crash the app
 */
export function useAppUpdate() {
  const { t } = useTranslation();
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    if (__DEV__) return;
    // expo-updates is not available on web
    if (Platform.OS === 'web') return;

    let cancelled = false;

    async function checkForUpdate() {
      try {
        // Dynamic import so the module is only resolved at runtime.
        // This avoids build errors in environments where expo-updates
        // is not configured (e.g. Expo Go, web export).
        const Updates = await import('expo-updates');

        setIsChecking(true);
        const check = await Updates.checkForUpdateAsync();

        if (cancelled) return;

        if (check.isAvailable) {
          const fetchResult = await Updates.fetchUpdateAsync();

          if (cancelled) return;

          if (fetchResult.isNew) {
            Alert.alert(
              t('common.updateAvailable'),
              t('common.updateRestart'),
              [
                { text: t('common.cancel'), style: 'cancel' },
                {
                  text: t('common.restart'),
                  onPress: () => {
                    Updates.reloadAsync();
                  },
                },
              ],
              { cancelable: true },
            );
          }
        }
      } catch (err) {
        // Update checks must never crash the app.
        // In production this may fire if there is no network,
        // or if EAS project ID is not yet configured.
        console.warn('OTA update check failed:', err);
      } finally {
        if (!cancelled) {
          setIsChecking(false);
        }
      }
    }

    checkForUpdate();

    return () => {
      cancelled = true;
    };
  }, [t]);

  return { isChecking };
}
