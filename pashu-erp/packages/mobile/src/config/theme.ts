import { MD3LightTheme, configureFonts } from 'react-native-paper';
import type { MD3Theme } from 'react-native-paper';

// Agricultural MD3 palette matching the HTML prototype
export const colors = {
  primary: '#1B6B4A',
  primaryContainer: '#A8F5C8',
  onPrimary: '#FFFFFF',
  onPrimaryContainer: '#002112',
  secondary: '#4E6355',
  secondaryContainer: '#D1E8D6',
  tertiary: '#3B6470',
  tertiaryContainer: '#BFE9F7',
  surface: '#F5F5F0',
  surfaceVariant: '#DCE5DB',
  background: '#F5F5F0',
  error: '#BA1A1A',
  errorContainer: '#FFDAD6',
  onSurface: '#1A1A1A',
  onSurfaceVariant: '#414941',
  outline: '#717971',
  outlineVariant: '#C1C9BF',
  onBackground: '#1A1A1A',
  onError: '#FFFFFF',
  onSecondary: '#FFFFFF',
  onSecondaryContainer: '#0B1F13',
  onTertiary: '#FFFFFF',
  onTertiaryContainer: '#001F28',
  elevation: {
    level0: 'transparent',
    level1: '#F0F4EC',
    level2: '#EAEEE6',
    level3: '#E4E8E0',
    level4: '#DFE3DB',
    level5: '#D9DDD5',
  },
  surfaceDisabled: 'rgba(26,26,26,0.12)',
  onSurfaceDisabled: 'rgba(26,26,26,0.38)',
  backdrop: 'rgba(0,0,0,0.5)',
};

export const statusColors = {
  healthy: '#2E7D32',
  healthyBg: '#E8F5E9',
  watch: '#F57F17',
  watchBg: '#FFF8E1',
  urgent: '#C62828',
  urgentBg: '#FFEBEE',
};

export const accentColors = {
  amber: '#E65100',
  amberLight: '#FFF3E0',
};

export const speciesColors = {
  cattle: { bg: '#E8F5E9', text: '#2E7D32' },
  goat: { bg: '#FFF3E0', text: '#E65100' },
  sheep: { bg: '#F3E5F5', text: '#7B1FA2' },
  poultry: { bg: '#FFF8E1', text: '#F57F17' },
};

const fontConfig = {
  displayLarge: { fontFamily: 'System', fontSize: 57, lineHeight: 64, fontWeight: '400' as const },
  headlineLarge: { fontFamily: 'System', fontSize: 32, lineHeight: 40, fontWeight: '700' as const },
  headlineMedium: { fontFamily: 'System', fontSize: 28, lineHeight: 36, fontWeight: '700' as const },
  headlineSmall: { fontFamily: 'System', fontSize: 24, lineHeight: 32, fontWeight: '700' as const },
  titleLarge: { fontFamily: 'System', fontSize: 22, lineHeight: 28, fontWeight: '700' as const },
  titleMedium: { fontFamily: 'System', fontSize: 18, lineHeight: 24, fontWeight: '600' as const },
  titleSmall: { fontFamily: 'System', fontSize: 16, lineHeight: 20, fontWeight: '600' as const },
  bodyLarge: { fontFamily: 'System', fontSize: 18, lineHeight: 26, fontWeight: '400' as const },
  bodyMedium: { fontFamily: 'System', fontSize: 16, lineHeight: 24, fontWeight: '400' as const },
  bodySmall: { fontFamily: 'System', fontSize: 14, lineHeight: 20, fontWeight: '400' as const },
  labelLarge: { fontFamily: 'System', fontSize: 16, lineHeight: 22, fontWeight: '500' as const },
  labelMedium: { fontFamily: 'System', fontSize: 14, lineHeight: 18, fontWeight: '500' as const },
  labelSmall: { fontFamily: 'System', fontSize: 12, lineHeight: 16, fontWeight: '500' as const },
};

export const theme: MD3Theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    ...colors,
  },
  fonts: configureFonts({ config: fontConfig }),
};

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
