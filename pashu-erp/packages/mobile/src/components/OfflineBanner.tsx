import React, { useEffect, useState, useCallback } from 'react';
import { View, StyleSheet, Animated } from 'react-native';
import { Text, IconButton, TouchableRipple } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import NetInfo from '@react-native-community/netinfo';
import { statusColors, colors, SPACING } from '../config/theme';
import { getPendingCount } from '../services/offline-queue';

type BannerState = 'offline' | 'syncing' | 'synced' | 'hidden';

interface OfflineBannerProps {
  /** Number of mutations currently being synced (set by QueryProvider) */
  syncingCount?: number;
  /** Whether sync just completed successfully */
  syncComplete?: boolean;
}

export function OfflineBanner({ syncingCount = 0, syncComplete = false }: OfflineBannerProps) {
  const { t } = useTranslation();
  const [isConnected, setIsConnected] = useState<boolean | null>(true);
  const [dismissed, setDismissed] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [bannerState, setBannerState] = useState<BannerState>('hidden');
  const [fadeAnim] = useState(() => new Animated.Value(0));

  // Subscribe to network state changes
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      setIsConnected(state.isConnected);
      // Reset dismissed state when connectivity changes
      if (state.isConnected === false) {
        setDismissed(false);
      }
    });
    return () => unsubscribe();
  }, []);

  // Poll pending count when offline
  useEffect(() => {
    if (isConnected === false) {
      getPendingCount().then(setPendingCount);
      const interval = setInterval(() => {
        getPendingCount().then(setPendingCount);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  // Determine banner state
  useEffect(() => {
    if (isConnected === false && !dismissed) {
      setBannerState('offline');
    } else if (syncingCount > 0) {
      setBannerState('syncing');
      setDismissed(false);
    } else if (syncComplete) {
      setBannerState('synced');
      // Auto-hide after 3 seconds
      const timer = setTimeout(() => {
        setBannerState('hidden');
      }, 3000);
      return () => clearTimeout(timer);
    } else {
      setBannerState('hidden');
    }
  }, [isConnected, dismissed, syncingCount, syncComplete]);

  // Animate in/out
  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: bannerState === 'hidden' ? 0 : 1,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [bannerState, fadeAnim]);

  const handleDismiss = useCallback(() => {
    setDismissed(true);
  }, []);

  if (bannerState === 'hidden') return null;

  const isOffline = bannerState === 'offline';
  const isSyncing = bannerState === 'syncing';
  const isSynced = bannerState === 'synced';

  const backgroundColor = isOffline
    ? statusColors.watchBg
    : isSyncing
      ? '#E3F2FD'
      : '#E8F5E9';

  const borderColor = isOffline
    ? statusColors.watch
    : isSyncing
      ? '#1976D2'
      : statusColors.healthy;

  const textColor = isOffline
    ? '#E65100'
    : isSyncing
      ? '#1565C0'
      : statusColors.healthy;

  const icon = isOffline
    ? 'wifi-off'
    : isSyncing
      ? 'sync'
      : 'check-circle-outline';

  let message: string;
  if (isOffline) {
    const suffix = pendingCount > 0
      ? ` (${pendingCount} ${t('common.pendingChanges', { defaultValue: 'pending' })})`
      : '';
    message = t('common.offlineBanner') + suffix;
  } else if (isSyncing) {
    message = t('common.syncingBanner', { count: syncingCount });
  } else {
    message = t('common.syncComplete');
  }

  return (
    <Animated.View
      style={[
        styles.container,
        { backgroundColor, borderBottomColor: borderColor, opacity: fadeAnim },
      ]}
      accessibilityRole="alert"
      accessibilityLiveRegion="polite"
    >
      <View style={styles.content}>
        <IconButton
          icon={icon}
          size={20}
          iconColor={textColor}
          style={styles.icon}
        />
        <Text
          variant="bodySmall"
          style={[styles.text, { color: textColor }]}
          numberOfLines={2}
        >
          {message}
        </Text>
        {isOffline && (
          <TouchableRipple
            onPress={handleDismiss}
            style={styles.dismissButton}
            accessibilityLabel={t('common.cancel')}
            accessibilityRole="button"
          >
            <IconButton
              icon="close"
              size={18}
              iconColor={textColor}
              style={styles.dismissIcon}
            />
          </TouchableRipple>
        )}
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderBottomWidth: 2,
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    zIndex: 100,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    margin: 0,
    marginRight: SPACING.xs,
  },
  text: {
    flex: 1,
    fontWeight: '600',
  },
  dismissButton: {
    borderRadius: 16,
    marginLeft: SPACING.xs,
  },
  dismissIcon: {
    margin: 0,
  },
});
