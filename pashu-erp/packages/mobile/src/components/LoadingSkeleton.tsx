import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';
import { SPACING, CARD_BORDER_RADIUS } from '../config/theme';

interface LoadingSkeletonProps {
  count?: number;
}

export function LoadingSkeleton({ count = 3 }: LoadingSkeletonProps) {
  const opacity = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 1.0,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    );
    animation.start();
    return () => animation.stop();
  }, [opacity]);

  return (
    <View style={styles.container}>
      {Array.from({ length: count }).map((_, i) => (
        <Animated.View key={i} style={[styles.card, { opacity }]}>
          <View style={styles.iconPlaceholder} />
          <View style={styles.textBlock}>
            <View style={styles.titleBar} />
            <View style={styles.subtitleBar} />
            <View style={styles.tagBar} />
          </View>
        </Animated.View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingTop: SPACING.sm,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E0E0E0',
    marginHorizontal: SPACING.md,
    marginVertical: SPACING.sm,
    borderRadius: CARD_BORDER_RADIUS,
    padding: SPACING.md,
    gap: SPACING.md,
  },
  iconPlaceholder: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#BDBDBD',
  },
  textBlock: {
    flex: 1,
    gap: SPACING.sm,
  },
  titleBar: {
    height: 16,
    width: '60%',
    borderRadius: 4,
    backgroundColor: '#BDBDBD',
  },
  subtitleBar: {
    height: 12,
    width: '80%',
    borderRadius: 4,
    backgroundColor: '#BDBDBD',
  },
  tagBar: {
    height: 10,
    width: '40%',
    borderRadius: 4,
    backgroundColor: '#BDBDBD',
  },
});
