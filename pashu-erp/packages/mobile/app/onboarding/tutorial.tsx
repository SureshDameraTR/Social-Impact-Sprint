import React, { useState, useRef } from 'react';
import { View, StyleSheet, FlatList, Dimensions, ViewToken } from 'react-native';
import { Button, Text } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import { SPACING, TOUCH_TARGET_MIN, CARD_BORDER_RADIUS } from '../../src/config/theme';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface TutorialSlide {
  key: string;
  emoji: string;
  titleKey: string;
  descKey: string;
  bgColor: string;
}

const SLIDES: TutorialSlide[] = [
  {
    key: 'voice',
    emoji: '🎤',
    titleKey: 'onboarding.tutorialVoiceTitle',
    descKey: 'onboarding.tutorialVoiceDesc',
    bgColor: '#E8F5E9',
  },
  {
    key: 'health',
    emoji: '🩺',
    titleKey: 'onboarding.tutorialHealthTitle',
    descKey: 'onboarding.tutorialHealthDesc',
    bgColor: '#E3F2FD',
  },
  {
    key: 'sell',
    emoji: '₹',
    titleKey: 'onboarding.tutorialSellTitle',
    descKey: 'onboarding.tutorialSellDesc',
    bgColor: '#FFF3E0',
  },
];

export default function TutorialScreen() {
  const { t } = useTranslation();
  const [activeIndex, setActiveIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const onViewableItemsChanged = useRef(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      if (viewableItems.length > 0 && viewableItems[0].index != null) {
        setActiveIndex(viewableItems[0].index);
      }
    }
  ).current;

  const goToTabs = () => {
    router.replace('/(tabs)');
  };

  const renderSlide = ({ item }: { item: TutorialSlide }) => (
    <View style={[styles.slide, { width: SCREEN_WIDTH, backgroundColor: item.bgColor }]}>
      <Text style={styles.slideEmoji}>{item.emoji}</Text>
      <Text variant="headlineSmall" style={styles.slideTitle}>
        {t(item.titleKey)}
      </Text>
      <Text variant="bodyLarge" style={styles.slideDesc}>
        {t(item.descKey)}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Button
        mode="text"
        onPress={goToTabs}
        style={styles.skipButton}
        labelStyle={styles.skipLabel}
      >
        {t('onboarding.skip')}
      </Button>

      <FlatList
        ref={flatListRef}
        data={SLIDES}
        renderItem={renderSlide}
        keyExtractor={(item) => item.key}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={{ viewAreaCoveragePercentThreshold: 50 }}
      />

      <View style={styles.footer}>
        <View style={styles.dots}>
          {SLIDES.map((_, i) => (
            <View
              key={i}
              style={[styles.dot, i === activeIndex && styles.dotActive]}
            />
          ))}
        </View>

        {activeIndex === SLIDES.length - 1 ? (
          <Button
            mode="contained"
            onPress={goToTabs}
            style={styles.getStarted}
            contentStyle={styles.getStartedContent}
            labelStyle={styles.getStartedLabel}
          >
            {t('onboarding.getStarted')}
          </Button>
        ) : (
          <Button
            mode="outlined"
            onPress={() => {
              flatListRef.current?.scrollToIndex({ index: activeIndex + 1 });
            }}
            style={styles.nextButton}
            contentStyle={styles.nextContent}
          >
            {t('onboarding.next')}
          </Button>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  skipButton: {
    position: 'absolute',
    top: 50,
    right: SPACING.md,
    zIndex: 10,
  },
  skipLabel: {
    color: '#616161',
  },
  slide: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: SPACING.xl,
  },
  slideEmoji: {
    fontSize: 80,
    marginBottom: SPACING.lg,
  },
  slideTitle: {
    color: '#212121',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: SPACING.md,
  },
  slideDesc: {
    color: '#616161',
    textAlign: 'center',
    lineHeight: 26,
  },
  footer: {
    paddingHorizontal: SPACING.lg,
    paddingBottom: SPACING.xl + 20,
    alignItems: 'center',
  },
  dots: {
    flexDirection: 'row',
    marginBottom: SPACING.lg,
    gap: SPACING.sm,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#BDBDBD',
  },
  dotActive: {
    backgroundColor: '#2E7D32',
    width: 24,
  },
  getStarted: {
    backgroundColor: '#2E7D32',
    borderRadius: CARD_BORDER_RADIUS,
    width: '100%',
  },
  getStartedContent: {
    minHeight: TOUCH_TARGET_MIN + 8,
  },
  getStartedLabel: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  nextButton: {
    borderRadius: CARD_BORDER_RADIUS,
    borderColor: '#2E7D32',
    width: '100%',
  },
  nextContent: {
    minHeight: TOUCH_TARGET_MIN,
  },
});
