import { MD3LightTheme, configureFonts } from 'react-native-paper';
import type { MD3Theme } from 'react-native-paper';

const fontConfig = {
  displayLarge: { fontFamily: 'NotoSansKannada-Regular', fontSize: 57, lineHeight: 64 },
  displayMedium: { fontFamily: 'NotoSansKannada-Regular', fontSize: 45, lineHeight: 52 },
  displaySmall: { fontFamily: 'NotoSansKannada-Regular', fontSize: 36, lineHeight: 44 },
  headlineLarge: { fontFamily: 'NotoSansKannada-Bold', fontSize: 32, lineHeight: 40 },
  headlineMedium: { fontFamily: 'NotoSansKannada-Bold', fontSize: 28, lineHeight: 36 },
  headlineSmall: { fontFamily: 'NotoSansKannada-Bold', fontSize: 24, lineHeight: 32 },
  titleLarge: { fontFamily: 'NotoSansKannada-Bold', fontSize: 22, lineHeight: 28 },
  titleMedium: { fontFamily: 'NotoSansKannada-Medium', fontSize: 18, lineHeight: 24 },
  titleSmall: { fontFamily: 'NotoSansKannada-Medium', fontSize: 16, lineHeight: 20 },
  bodyLarge: { fontFamily: 'NotoSansKannada-Regular', fontSize: 18, lineHeight: 26 },
  bodyMedium: { fontFamily: 'NotoSansKannada-Regular', fontSize: 16, lineHeight: 24 },
  bodySmall: { fontFamily: 'NotoSansKannada-Regular', fontSize: 14, lineHeight: 20 },
  labelLarge: { fontFamily: 'NotoSansKannada-Medium', fontSize: 16, lineHeight: 22 },
  labelMedium: { fontFamily: 'NotoSansKannada-Medium', fontSize: 14, lineHeight: 18 },
  labelSmall: { fontFamily: 'NotoSansKannada-Medium', fontSize: 12, lineHeight: 16 },
};

export const theme: MD3Theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#2E7D32',
    primaryContainer: '#C8E6C9',
    secondary: '#FF8F00',
    secondaryContainer: '#FFE0B2',
    tertiary: '#1565C0',
    tertiaryContainer: '#BBDEFB',
    surface: '#FFFFFF',
    surfaceVariant: '#F5F5F5',
    background: '#FAFAFA',
    error: '#D32F2F',
    errorContainer: '#FFCDD2',
    onPrimary: '#FFFFFF',
    onPrimaryContainer: '#1B5E20',
    onSecondary: '#FFFFFF',
    onSecondaryContainer: '#E65100',
    onSurface: '#212121',
    onSurfaceVariant: '#616161',
    onBackground: '#212121',
    onError: '#FFFFFF',
    outline: '#BDBDBD',
    outlineVariant: '#E0E0E0',
    elevation: {
      level0: 'transparent',
      level1: '#FFFFFF',
      level2: '#F5F5F5',
      level3: '#EEEEEE',
      level4: '#E0E0E0',
      level5: '#BDBDBD',
    },
  },
  fonts: configureFonts({ config: fontConfig }),
};

// Design constants for accessibility
export const TOUCH_TARGET_MIN = 48;
export const ICON_SIZE_LARGE = 64;
export const ICON_SIZE_MEDIUM = 32;
export const ICON_SIZE_SMALL = 24;
export const CARD_BORDER_RADIUS = 16;
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;
