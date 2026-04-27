import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Animated, StyleSheet, Pressable } from 'react-native';
import { IconButton, Text } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { Audio } from 'expo-av';
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
  const recordingRef = useRef<Audio.Recording | null>(null);

  // Pulse animation when recording or processing
  useEffect(() => {
    if (state === 'recording' || state === 'processing') {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      pulseAnim.stopAnimation();
      pulseAnim.setValue(1);
    }
  }, [state, pulseAnim]);

  // Cleanup recording on unmount
  useEffect(() => {
    return () => {
      if (recordingRef.current) {
        recordingRef.current.stopAndUnloadAsync().catch(() => {});
        recordingRef.current = null;
      }
    };
  }, []);

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
      // Phase 1: Start real recording
      setState('recording');
      setStatusText('\u0C95\u0CC7\u0CB3\u0CC1\u0CA4\u0CCD\u0CA4\u0CBF\u0CA6\u0CC6...'); // "Listening..." in Kannada

      // Request microphone permissions
      const permission = await Audio.requestPermissionsAsync();
      if (!permission.granted) {
        setState('error');
        setStatusText('\u0CAE\u0CC8\u0C95\u0CCD \u0C85\u0CA8\u0CC1\u0CAE\u0CA4\u0CBF \u0CAC\u0CC7\u0C95\u0CC1'); // "Mic permission needed"
        setTimeout(() => setState('idle'), 3000);
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const recording = new Audio.Recording();
      await recording.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await recording.startAsync();
      recordingRef.current = recording;

      // Record for 3 seconds (sufficient for number input)
      await new Promise(resolve => setTimeout(resolve, 3000));

      await recording.stopAndUnloadAsync();
      recordingRef.current = null;

      const uri = recording.getURI();
      if (!uri) {
        setState('error');
        setStatusText('\u0CAE\u0CA4\u0CCD\u0CA4\u0CC6 \u0CAE\u0CBE\u0CA4\u0CA8\u0CBE\u0CA1\u0CBF'); // "Speak again"
        setTimeout(() => setState('idle'), 3000);
        return;
      }

      // Phase 2: Process / transcribe
      setState('processing');
      setStatusText('\u0C97\u0CC1\u0CB0\u0CC1\u0CA4\u0CBF\u0CB8\u0CC1\u0CA4\u0CCD\u0CA4\u0CBF\u0CA6\u0CC6...'); // "Recognizing..." in Kannada
      const result = await transcribeAudio(uri, context);

      if (result.parsedNumber != null) {
        setState('idle');
        setStatusText(result.text);
        onTranscript?.(result.text);
        onResult(result.parsedNumber);
      } else {
        setState('error');
        setStatusText('\u0CAE\u0CA4\u0CCD\u0CA4\u0CC6 \u0CAE\u0CBE\u0CA4\u0CA8\u0CBE\u0CA1\u0CBF'); // "Speak again" in Kannada
        setTimeout(() => setState('idle'), 3000);
      }
    } catch {
      setState('error');
      setStatusText('\u0CAE\u0CA4\u0CCD\u0CA4\u0CC6 \u0CAE\u0CBE\u0CA4\u0CA8\u0CBE\u0CA1\u0CBF'); // "Speak again" in Kannada
      setTimeout(() => setState('idle'), 3000);
    }
  }, [state, context, onResult, onTranscript]);

  const containerColor =
    state === 'error' ? '#FF9800' :
    state === 'recording' ? '#C62828' :
    state === 'processing' ? '#3B6470' :
    '#E65100';

  const icon =
    state === 'recording' ? 'microphone' :
    state === 'processing' ? 'loading' :
    state === 'error' ? 'microphone' :   // was 'microphone-off' — keep enabled appearance
    'microphone';

  return (
    <Animated.View style={[styles.container, { transform: [{ scale: pulseAnim }] }]}>
      <Pressable
        onPress={handlePress}
        accessibilityLabel={t('milk.voiceInput')}
        accessibilityRole="button"
        accessibilityHint="Double tap to record voice input"
        disabled={state === 'recording' || state === 'processing'}
      >
        <IconButton
          icon={icon}
          mode="contained"
          size={36}
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
    width: 72,
    height: 72,
    borderRadius: 36,
    minHeight: TOUCH_TARGET_MIN,
    minWidth: TOUCH_TARGET_MIN,
    shadowColor: '#E65100',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  statusText: {
    marginTop: 6,
    color: '#414941',
    textAlign: 'center',
    maxWidth: 120,
  },
});
