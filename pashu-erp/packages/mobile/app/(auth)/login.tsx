import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform, StatusBar, TextInput as RNTextInput } from 'react-native';
import { Text, TextInput, Button, HelperText } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { router } from 'expo-router';
import * as Storage from '../../src/config/storage';
import { SPACING, CARD_BORDER_RADIUS, colors } from '../../src/config/theme';

const API_URL = process.env.EXPO_PUBLIC_API_URL;
const PHONE_REGEX = /^[6-9]\d{9}$/;

export default function LoginScreen() {
  const { t } = useTranslation();
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [phoneError, setPhoneError] = useState('');
  const [error, setError] = useState('');
  const [resendCooldown, setResendCooldown] = useState(0);
  const otpRefs = useRef<(RNTextInput | null)[]>([]);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const validatePhone = (value: string): boolean => {
    if (!PHONE_REGEX.test(value)) {
      setPhoneError(t('login.invalidPhone') ?? 'Enter a valid 10-digit Indian mobile number');
      return false;
    }
    setPhoneError('');
    return true;
  };

  const handleSendOtp = async () => {
    if (!validatePhone(phone)) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/auth/request-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: `+91${phone}` }),
      });
      if (!response.ok) {
        const err = await response.json();
        setError(err.detail || (t('login.otpFailed') ?? 'Failed to send OTP'));
        return;
      }
      setOtpSent(true);
      setResendCooldown(60);
    } catch {
      setError(t('common.networkError') ?? 'Network error. Check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: `+91${phone}`,
          otp: otp.join(''),
          client_type: 'mobile',
        }),
      });
      if (!response.ok) {
        const err = await response.json();
        setError(err.detail || (t('login.verificationFailed') ?? 'Verification failed'));
        if (err.code === 'OTP_MAX_ATTEMPTS' || err.code === 'OTP_EXPIRED') {
          setOtpSent(false);
          setOtp(['', '', '', '', '', '']);
        }
        return;
      }
      const data = await response.json();
      await Storage.setItemAsync('auth_token', data.access_token);
      router.replace('/(tabs)');
    } catch {
      setError(t('common.networkError') ?? 'Network error. Check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleOtpChange = (text: string, index: number) => {
    // Handle paste: if text has multiple digits, distribute across boxes
    if (text.length > 1) {
      const digits = text.replace(/\D/g, '').slice(0, 6).split('');
      const newOtp = [...otp];
      digits.forEach((d, i) => {
        if (index + i < 6) newOtp[index + i] = d;
      });
      setOtp(newOtp);
      const focusIdx = Math.min(index + digits.length, 5);
      otpRefs.current[focusIdx]?.focus();
      return;
    }

    const newOtp = [...otp];
    newOtp[index] = text;
    setOtp(newOtp);
    // Auto-focus next
    if (text && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyPress = (key: string, index: number) => {
    if (key === 'Backspace' && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const otpString = otp.join('');

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <StatusBar barStyle="light-content" backgroundColor={colors.primary} />

      {/* Green gradient hero */}
      <View style={styles.hero}>
        <Text style={styles.heroEmoji}>{'\uD83D\uDC04'}</Text>
        <Text variant="headlineLarge" style={styles.heroTitle}>
          PashuRaksha
        </Text>
        <Text variant="titleMedium" style={styles.heroSubtitle}>
          {t('onboarding.welcomeSubtitle')}
        </Text>
      </View>

      {/* Form */}
      <View style={styles.formContainer}>
        {!!error && (
          <HelperText type="error" visible={!!error} style={{ marginBottom: 8, textAlign: 'center' }}>
            {error}
          </HelperText>
        )}
        <Text variant="headlineSmall" style={styles.welcomeText}>
          {t('auth.welcome')}
        </Text>

        <View style={styles.form}>
          {/* Phone input */}
          <View style={styles.phoneRow}>
            <View style={styles.prefixBox}>
              <Text style={styles.prefixText}>+91</Text>
            </View>
            <TextInput
              placeholder={t('auth.enterPhone')}
              value={phone}
              onChangeText={(text) => {
                setPhone(text);
                if (phoneError) validatePhone(text);
              }}
              keyboardType="phone-pad"
              mode="outlined"
              style={styles.phoneInput}
              outlineColor="#C1C9BF"
              activeOutlineColor={colors.primary}
              maxLength={10}
              disabled={otpSent}
              error={!!phoneError}
            />
          </View>
          {!!phoneError && (
            <HelperText type="error" visible={!!phoneError}>
              {phoneError}
            </HelperText>
          )}

          {/* OTP boxes */}
          {otpSent && (
            <View>
              <Text variant="bodyMedium" style={styles.otpLabel}>
                {t('auth.enterOtp')}
              </Text>
              <View style={styles.otpRow}>
                {otp.map((digit, i) => (
                  <RNTextInput
                    key={i}
                    ref={(ref) => { otpRefs.current[i] = ref; }}
                    value={digit}
                    onChangeText={(text) => handleOtpChange(text, i)}
                    onKeyPress={({ nativeEvent }) => handleOtpKeyPress(nativeEvent.key, i)}
                    keyboardType="number-pad"
                    maxLength={1}
                    style={[
                      styles.otpBox,
                      digit ? styles.otpBoxFilled : {},
                    ]}
                    textAlign="center"
                    accessibilityLabel={`OTP digit ${i + 1} of 6`}
                    accessibilityHint="Enter one digit"
                  />
                ))}
              </View>
            </View>
          )}

          <Button
            mode="contained"
            onPress={otpSent ? handleVerifyOtp : handleSendOtp}
            loading={loading}
            disabled={loading || (otpSent ? otpString.length < 6 : phone.length < 10)}
            style={styles.button}
            contentStyle={styles.buttonContent}
            labelStyle={styles.buttonLabel}
            buttonColor={colors.primary}
          >
            {otpSent ? t('auth.verifyOtp') : t('auth.sendOtp')}
          </Button>

          {otpSent && (
            <View style={{ alignItems: 'center', marginTop: 12 }}>
              {resendCooldown > 0 ? (
                <Text variant="bodySmall" style={{ color: '#414941' }}>
                  {t('login.resendOtpIn', { seconds: resendCooldown }) ?? `Resend OTP in ${resendCooldown}s`}
                </Text>
              ) : (
                <Button
                  mode="text"
                  onPress={() => {
                    setOtp(['', '', '', '', '', '']);
                    setError('');
                    handleSendOtp();
                  }}
                  textColor={colors.primary}
                >
                  {t('login.resendOtp') ?? 'Resend OTP'}
                </Button>
              )}
            </View>
          )}
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F0',
  },
  hero: {
    backgroundColor: colors.primary,
    paddingTop: 60,
    paddingBottom: 40,
    paddingHorizontal: SPACING.xl,
    alignItems: 'center',
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 32,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  heroEmoji: {
    fontSize: 72,
    marginBottom: SPACING.sm,
  },
  heroTitle: {
    color: '#FFFFFF',
    fontWeight: '700',
    textAlign: 'center',
  },
  heroSubtitle: {
    color: '#A8F5C8',
    textAlign: 'center',
    marginTop: SPACING.xs,
  },
  formContainer: {
    flex: 1,
    paddingHorizontal: SPACING.xl,
    paddingTop: SPACING.xl,
  },
  welcomeText: {
    color: '#1A1A1A',
    fontWeight: '700',
    marginBottom: SPACING.lg,
  },
  form: {
    gap: SPACING.md,
  },
  phoneRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  prefixBox: {
    backgroundColor: '#DCE5DB',
    paddingHorizontal: SPACING.md,
    paddingVertical: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#C1C9BF',
  },
  prefixText: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.primary,
  },
  phoneInput: {
    flex: 1,
    fontSize: 18,
    backgroundColor: '#FFFFFF',
  },
  otpLabel: {
    color: '#414941',
    marginBottom: SPACING.sm,
  },
  otpRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: SPACING.sm,
  },
  otpBox: {
    width: 48,
    height: 56,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#C1C9BF',
    backgroundColor: '#FFFFFF',
    fontSize: 24,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  otpBoxFilled: {
    borderColor: colors.primary,
    backgroundColor: '#A8F5C8',
  },
  button: {
    marginTop: SPACING.md,
    borderRadius: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  buttonContent: {
    height: 56,
  },
  buttonLabel: {
    fontSize: 18,
    fontWeight: '700',
  },
});
