import React from 'react';
import { Tabs } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { IconButton } from 'react-native-paper';
import { View, StyleSheet, Pressable } from 'react-native';
import { router } from 'expo-router';

function HeaderRight() {
  return (
    <View style={styles.headerRight}>
      <IconButton
        icon="sprout"
        size={24}
        onPress={() => router.push('/smart-farm')}
        iconColor="#2E7D32"
      />
      <IconButton
        icon="bell-outline"
        size={24}
        onPress={() => {}}
        iconColor="#616161"
      />
      <Pressable onPress={() => router.push('/profile')}>
        <View style={styles.avatar}>
          <IconButton icon="account" size={20} iconColor="#FFFFFF" />
        </View>
      </Pressable>
    </View>
  );
}

export default function TabLayout() {
  const { t } = useTranslation();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#2E7D32',
        tabBarInactiveTintColor: '#9E9E9E',
        tabBarLabelStyle: { fontSize: 13, fontWeight: '600' },
        tabBarStyle: {
          height: 72,
          paddingBottom: 12,
          paddingTop: 8,
          borderTopWidth: 1,
          borderTopColor: '#E0E0E0',
        },
        headerRight: () => <HeaderRight />,
        headerStyle: { backgroundColor: '#FFFFFF' },
        headerTitleStyle: { color: '#2E7D32', fontWeight: 'bold', fontSize: 20 },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: t('common.home'),
          tabBarIcon: ({ color, size }) => (
            <IconButton icon="home" size={size} iconColor={color} />
          ),
          headerTitle: 'PashuRaksha',
        }}
      />
      <Tabs.Screen
        name="milk"
        options={{
          title: t('common.milk'),
          tabBarIcon: ({ color, size }) => (
            <IconButton icon="water" size={size} iconColor={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="sell"
        options={{
          title: t('common.sell'),
          tabBarIcon: ({ color, size }) => (
            <IconButton icon="cart" size={size} iconColor={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="health"
        options={{
          title: t('common.health'),
          tabBarIcon: ({ color, size }) => (
            <IconButton icon="heart-pulse" size={size} iconColor={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="income"
        options={{
          title: t('common.income'),
          tabBarIcon: ({ color, size }) => (
            <IconButton icon="currency-inr" size={size} iconColor={color} />
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
    backgroundColor: '#2E7D32',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
});
