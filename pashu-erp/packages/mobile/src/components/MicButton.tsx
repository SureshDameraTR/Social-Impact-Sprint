import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Animated, StyleSheet, Pressable } from 'react-native';
import { IconButton, Text } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { TOUCH_TARGET_MIN } from '../config/theme';
import { transcribeAudio, VoiceContext } from '../services/voice';

interface MicButtonProps {
  /** Called with the parsed numeric value on successful transcription */
  onResult: (value: number) => void;
  /** Context hint for mock responses and Sarvam API */
  context?: VoiceContext;
  /** Called with the raw transcribed text (for toast display) */
  onTranscript?: (text: string) => void;
}

type ButtonState = 'idle' | 'recording' | 'processing' | 'error';

export function MicButton({ onResult, context = 'generic', onTranscript }: MicButtonProps) {
  const { t } = useTranslation();
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const [state, setState] = useState<ButtonState>('idle');
  const [statusText, setStatusText] = useState('');

  // Pulse animation when recording or processing
  useEffect(() => {
    if (state === 'recording' || state === 'processing') {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.3,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      pulseAnim.stopAnimation();
      pulseAnim.setValue(1);
    }
  }, [state, pulseAnim]);

  // Clear status text after display
  useEffect(() => {
    if (statusText) {
      const timer = setTimeout(() => setStatusText(''), 2500);
      return () => clearTimeout(timer);
    }
  }, [statusText]);

  const handlePress = useCallback(async () => {
    if (state === 'recording' || state === 'processing') return;

    try {
      // Phase 1: Simulate recording (2s)
      setState('recording');
      setStatusText('\u0C95\u0CC7\u0CB3\u0CC1\u0CA4\u0CCD\u0CA4\u0CBF\u0CA6\u0CC6...'); // "Listening..." in Kannada
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Phase 2: Process / transcribe
      setState('processing');
      setStatusText('\u0C97\u0CC1\u0CB0\u0CC1\u0CA4\u0CBF\u0CB8\u0CC1\u0CA4\u0CCD\u0CA4\u0CBF\u0CA6\u0CC6...'); // "Recognizing..." in Kannada
      const result = await transcribeAudio('mock://recording.wav', context);

      if (result.parsedNumber != null) {
        setState('idle');
        setStatusText(result.text);
        onTranscript?.(result.text);
        onResult(result.parsedNumber);
      } else {
        setState('error');
        setStatusText('\u0CA6\u0CAF\u0CB5\u0CBF\u0C9F\u0CCD\u0C9F\u0CC1 \u0CAE\u0CA4\u0CCD\u0CA4\u0CC6 \u0CAA\u0CCD\u0CB0\u0CAF\u0CA4\u0CCD\u0CA8\u0CBF\u0CB8\u0CBF'); // "Please try again" in Kannada
        setTimeout(() => setState('idle'), 2000);
      }
    } catch {
      setState('error');
      setStatusText('\u0CA6\u0CCB\u0CB7\u0CB5\u0CBE\u0CAF\u0CBF\u0CA4\u0CC1'); // "Error occurred" in Kannada
      setTimeout(() => setState('idle'), 2000);
    }
  }, [state, context, onResult, onTranscript]);

  const containerColor =
    state === 'error' ? '#FF9800' :
    state === 'recording' ? '#F44336' :
    state === 'processing' ? '#1565C0' :
    '#2E7D32';

  const icon =
    state === 'recording' ? 'microphone' :
    state === 'processing' ? 'loading' :
    state === 'error' ? 'microphone-off' :
    'microphone';

  return (
    <Animated.View style={[styles.container, { transform: [{ scale: pulseAnim }] }]}>
      <Pressable
        onPress={handlePress}
        accessibilityLabel={t('milk.voiceInput')}
        accessibilityRole="button"
        disabled={state === 'recording' || state === 'processing'}
      >
        <IconButton
          icon={icon}
          mode="contained"
          size={32}
          iconColor="#FFFFFF"
          containerColor={containerColor}
          style={styles.button}
        />
      </Pressable>
      {statusText !== '' && (
        <Text variant="labelSmall" style={styles.statusText} numberOfLines={1}>
          {statusText}
        </Text>
      )}
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  button: {
    width: 64,
    height: 64,
    borderRadius: 32,
    minHeight: TOUCH_TARGET_MIN,
    minWidth: TOUCH_TARGET_MIN,
  },
  statusText: {
    marginTop: 4,
    color: '#616161',
    textAlign: 'center',
    maxWidth: 120,
  },
});
