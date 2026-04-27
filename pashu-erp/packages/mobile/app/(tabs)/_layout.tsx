import React from 'react';
import { Tabs } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Icon, IconButton } from 'react-native-paper';
import { View, StyleSheet, Pressable } from 'react-native';
import { router } from 'expo-router';
import { colors } from '../../src/config/theme';

const HeaderRight = React.memo(function HeaderRight() {
  return (
    <View style={styles.headerRight}>
      <IconButton
        icon="sprout"
        size={24}
        onPress={() => router.push('/smart-farm')}
        iconColor={colors.primary}
        accessibilityLabel="Smart Farm"
        accessibilityRole="button"
      />
      <IconButton
        icon="bell-outline"
        size={24}
        onPress={() => router.push('/vaccinations')}
        iconColor={colors.onSurfaceVariant}
        accessibilityLabel="Notifications"
        accessibilityRole="button"
      />
      <Pressable
        onPress={() => router.push('/profile')}
        accessibilityLabel="Profile"
        accessibilityRole="button"
        style={styles.avatar}
      >
        <Icon source="account" size={20} color={colors.onPrimary} />
      </Pressable>
    </View>
  );
});

export default function TabLayout() {
  const { t } = useTranslation();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.outline,
        tabBarLabelStyle: {
          fontSize: 13,
          fontWeight: '600',
          marginTop: -4,
        },
        tabBarStyle: {
          height: 72,
          paddingBottom: 12,
          paddingTop: 8,
          borderTopWidth: 0,
          backgroundColor: colors.onPrimary,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.08,
          shadowRadius: 8,
          elevation: 8,
        },
        tabBarItemStyle: {
          paddingVertical: 4,
        },
        headerRight: () => <HeaderRight />,
        headerStyle: {
          backgroundColor: colors.surface,
          shadowColor: 'transparent',
          elevation: 0,
        },
        headerTitleStyle: {
          color: colors.primary,
          fontWeight: '700',
          fontSize: 22,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: t('common.home'),
          tabBarIcon: ({ color, focused }) => (
            <View style={[styles.tabIconContainer, focused && styles.tabIconActive]}>
              <Icon source="home" size={26} color={color} />
            </View>
          ),
          headerTitle: 'PashuRaksha',
        }}
      />
      <Tabs.Screen
        name="milk"
        options={{
          title: t('common.milk'),
          tabBarIcon: ({ color, focused }) => (
            <View style={[styles.tabIconContainer, focused && styles.tabIconActive]}>
              <Icon source="water" size={26} color={color} />
            </View>
          ),
        }}
      />
      <Tabs.Screen
        name="sell"
        options={{
          title: t('common.sell'),
          tabBarIcon: ({ color, focused }) => (
            <View style={[styles.tabIconContainer, focused && styles.tabIconActive]}>
              <Icon source="cart" size={26} color={color} />
            </View>
          ),
        }}
      />
      <Tabs.Screen
        name="health"
        options={{
          title: t('common.health'),
          tabBarIcon: ({ color, focused }) => (
            <View style={[styles.tabIconContainer, focused && styles.tabIconActive]}>
              <Icon source="heart-pulse" size={26} color={color} />
            </View>
          ),
        }}
      />
      <Tabs.Screen
        name="income"
        options={{
          title: t('common.income'),
          tabBarIcon: ({ color, focused }) => (
            <View style={[styles.tabIconContainer, focused && styles.tabIconActive]}>
              <Icon source="currency-inr" size={26} color={color} />
            </View>
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 4,
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  tabIconContainer: {
    borderRadius: 20,
    paddingHorizontal: 8,
    paddingVertical: 4,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabIconActive: {
    backgroundColor: colors.primaryContainer,
    borderRadius: 20,
    paddingHorizontal: 16,
  },
});
