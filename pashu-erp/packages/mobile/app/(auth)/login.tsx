import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { Text, TextInput, Button } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { SPACING } from '../../src/config/theme';

export default function LoginScreen() {
  const { t } = useTranslation();
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSendOtp = async () => {
    setLoading(true);
    // Mock OTP send - in production, call API
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setOtpSent(true);
    setLoading(false);
  };

  const handleVerifyOtp = async () => {
    setLoading(true);
    // Mock OTP verification - in production, call API and get JWT
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await SecureStore.setItemAsync('auth_token', 'mock-jwt-token');
    setLoading(false);
    router.replace('/(tabs)');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        <Text style={styles.logo}>{'\uD83D\uDC04'}</Text>
        <Text variant="headlineLarge" style={styles.title}>
          {t('auth.welcome')}
        </Text>
        <Text variant="titleMedium" style={styles.subtitle}>
          PashuRaksha
        </Text>

        <View style={styles.form}>
          <TextInput
            label={t('auth.phoneLabel')}
            placeholder={t('auth.enterPhone')}
            value={phone}
            onChangeText={setPhone}
            keyboardType="phone-pad"
            mode="outlined"
            style={styles.input}
            left={<TextInput.Affix text="+91 " />}
            maxLength={10}
            disabled={otpSent}
          />

          {otpSent && (
            <TextInput
              label="OTP"
              placeholder={t('auth.enterOtp')}
              value={otp}
              onChangeText={setOtp}
              keyboardType="number-pad"
              mode="outlined"
              style={styles.input}
              maxLength={6}
            />
          )}

          <Button
            mode="contained"
            onPress={otpSent ? handleVerifyOtp : handleSendOtp}
            loading={loading}
            disabled={loading || (otpSent ? otp.length < 6 : phone.length < 10)}
            style={styles.button}
            contentStyle={styles.buttonContent}
            labelStyle={styles.buttonLabel}
          >
            {otpSent ? t('auth.verifyOtp') : t('auth.sendOtp')}
          </Button>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: SPACING.xl,
  },
  logo: {
    fontSize: 80,
    textAlign: 'center',
    marginBottom: SPACING.md,
  },
  title: {
    textAlign: 'center',
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  subtitle: {
    textAlign: 'center',
    color: '#616161',
    marginBottom: SPACING.xl,
  },
  form: {
    gap: SPACING.md,
  },
  input: {
    fontSize: 18,
  },
  button: {
    marginTop: SPACING.sm,
    borderRadius: 12,
  },
  buttonContent: {
    height: 56,
  },
  buttonLabel: {
    fontSize: 18,
  },
});
