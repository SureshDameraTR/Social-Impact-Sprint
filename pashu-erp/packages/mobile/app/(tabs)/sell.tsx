import React, { useState, useEffect, useCallback } from 'react';
import { View, FlatList, StyleSheet, StatusBar, AccessibilityInfo } from 'react-native';
import { Text, TextInput, Button, Card, Snackbar, Divider, HelperText, ActivityIndicator } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { ProductCard } from '../../src/components/ProductCard';
import { MicButton } from '../../src/components/MicButton';
import { useSnackbar } from '../../src/hooks/useSnackbar';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS, colors } from '../../src/config/theme';
import { api } from '../../src/config/api';

type ProductType = 'milk' | 'eggs' | 'goat_products' | 'manure';

// UI configuration: product types available for sale (matches API ProductType enum)
const PRODUCTS: { key: ProductType; icon: string; price: string; unit: string }[] = [
  { key: 'milk', icon: '\uD83E\uDD5B', price: '\u20B945/L', unit: 'liters' },
  { key: 'eggs', icon: '\uD83E\uDD5A', price: '\u20B97/pc', unit: 'pieces' },
  { key: 'goat_products', icon: '\uD83D\uDC10', price: '\u20B9600/kg', unit: 'kg' },
  { key: 'manure', icon: '\uD83C\uDF3E', price: '\u20B96/kg', unit: 'kg' },
];

interface SaleRecord {
  id: string;
  product: string;
  productName: string;
  qty: string;
  amount: number;
  buyer: string;
  date: string;
}

const MIN_QUANTITY = 0.1;
const MAX_QUANTITY = 999;
const MAX_PRICE = 99999;

function validateNumericField(value: string, min: number, max: number, fieldName: string): string | null {
  const num = parseFloat(value);
  if (isNaN(num) || num < 0) return `Enter a valid ${fieldName}`;
  if (num < min) return `Minimum ${min}`;
  if (num > max) return `Maximum ${max}`;
  return null;
}

export default function SellScreen() {
  const { t } = useTranslation();
  const { showError } = useSnackbar();
  const [recentSales, setRecentSales] = useState<SaleRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<ProductType | ''>('');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [quantityError, setQuantityError] = useState<string | null>(null);
  const [priceError, setPriceError] = useState<string | null>(null);
  const [snackVisible, setSnackVisible] = useState(false);
  const [snackMessage, setSnackMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchSales = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<{ data: SaleRecord[] }>('/marketplace/rates')
      .then(() => {}) // preload rates
      .catch(() => {});
    api.get<SaleRecord[]>('/income/transactions?period=week')
      .then(res => {
        const data = Array.isArray(res) ? res : (res as any).data ?? [];
        setRecentSales(data);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchSales();
  }, [fetchSales]);

  const total = (parseFloat(quantity) || 0) * (parseFloat(price) || 0);

  const handleSelectProduct = useCallback((key: ProductType) => {
    setSelectedProduct(key);
  }, []);

  const handleVoiceResult = useCallback((value: number) => {
    const clamped = Math.max(MIN_QUANTITY, Math.min(MAX_QUANTITY, value));
    setQuantity(String(clamped));
    setQuantityError(null);
    setSnackMessage(`${clamped}`);
  }, []);

  const handleVoiceTranscript = useCallback((text: string) => {
    setSnackMessage((prev) => `${text} \u2014 ${prev || '...'}`);
    setSnackVisible(true);
  }, []);

  const handleRecordSale = useCallback(async () => {
    const qtyErr = validateNumericField(quantity, MIN_QUANTITY, MAX_QUANTITY, 'quantity');
    const priceErr = validateNumericField(price, MIN_QUANTITY, MAX_PRICE, 'price');
    setQuantityError(qtyErr);
    setPriceError(priceErr);
    if (qtyErr || priceErr) return;

    setIsSubmitting(true);
    try {
      const selectedConfig = PRODUCTS.find(p => p.key === selectedProduct);
      await api.post('/marketplace/sell', {
        product_type: selectedProduct,
        quantity: parseFloat(quantity),
        unit: selectedConfig?.unit ?? 'kg',
        price_per_unit: parseFloat(price),
      });
      setSnackMessage(t('sell.saleRecorded'));
      setSnackVisible(true);
      AccessibilityInfo.announceForAccessibility(t('sell.saleRecorded'));
      setSelectedProduct('');
      setQuantity('');
      setPrice('');
      // Refresh recent sales
      fetchSales();
    } catch (e) {
      console.error('Listing creation failed:', e);
      showError('Failed to create listing. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [quantity, price, selectedProduct, t, fetchSales, showError]);

  const renderSaleItem = ({ item: sale }: { item: SaleRecord }) => (
    <Card key={sale.id} style={styles.saleCard} accessibilityLabel={`${sale.qty} ${sale.productName}, ${sale.buyer}, ${sale.date}`}>
      <Card.Content style={styles.saleContent}>
        <View style={styles.saleLeft}>
          <Text style={styles.saleIcon}>{sale.product}</Text>
          <View>
            <Text variant="titleSmall" style={styles.saleName}>{sale.qty}</Text>
            <Text variant="bodySmall" style={styles.saleMeta}>
              {sale.buyer} | {sale.date}
            </Text>
          </View>
        </View>
        <Text variant="titleMedium" style={styles.saleAmount}>
          +{'\u20B9'}{sale.amount}
        </Text>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <EmptyState
          icon={'\u26A0\uFE0F'}
          title={t('common.error')}
          subtitle={error}
          actionLabel={t('common.retry')}
          onAction={fetchSales}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F5F5F0" />
      <FlatList
        data={recentSales}
        keyExtractor={(item) => item.id}
        renderItem={renderSaleItem}
        contentContainerStyle={styles.scroll}
        ListHeaderComponent={
          <>
            <Text variant="headlineSmall" style={styles.heading}>
              {t('sell.sellProducts')}
            </Text>

            {/* Product grid (2 columns) */}
            <View style={styles.grid}>
              {PRODUCTS.map((p) => (
                <ProductCard
                  key={p.key}
                  icon={p.icon}
                  label={t(`sell.${p.key}`)}
                  price={p.price}
                  selected={selectedProduct === p.key}
                  onPress={() => handleSelectProduct(p.key)}
                />
              ))}
            </View>

            {/* Quantity and price */}
            {selectedProduct !== '' && (
              <View style={styles.form}>
                <View style={styles.quantityRow}>
                  <TextInput
                    label={t('sell.quantity')}
                    value={quantity}
                    onChangeText={(text) => {
                      setQuantity(text);
                      if (quantityError) setQuantityError(validateNumericField(text, MIN_QUANTITY, MAX_QUANTITY, 'quantity'));
                    }}
                    keyboardType="decimal-pad"
                    mode="outlined"
                    style={[styles.input, styles.quantityInput]}
                    outlineColor="#C1C9BF"
                    activeOutlineColor={colors.primary}
                    error={!!quantityError}
                    accessibilityLabel={t('sell.quantity')}
                  />
                  <MicButton
                    context="sell_quantity"
                    onResult={handleVoiceResult}
                    onTranscript={handleVoiceTranscript}
                  />
                </View>
                {!!quantityError && (
                  <HelperText type="error" visible={!!quantityError}>{quantityError}</HelperText>
                )}
                <TextInput
                  label={`${t('sell.pricePerUnit')} (\u20B9)`}
                  value={price}
                  onChangeText={(text) => {
                    setPrice(text);
                    if (priceError) setPriceError(validateNumericField(text, MIN_QUANTITY, MAX_PRICE, 'price'));
                  }}
                  keyboardType="decimal-pad"
                  mode="outlined"
                  style={styles.input}
                  outlineColor="#C1C9BF"
                  activeOutlineColor={colors.primary}
                  error={!!priceError}
                  accessibilityLabel={t('sell.pricePerUnit')}
                />
                {!!priceError && (
                  <HelperText type="error" visible={!!priceError}>{priceError}</HelperText>
                )}

                {total > 0 && (
                  <Card style={styles.totalCard}>
                    <Card.Content style={styles.totalContent}>
                      <Text variant="bodyLarge" style={styles.totalLabel}>{t('sell.total')}</Text>
                      <Text variant="headlineMedium" style={styles.totalAmount}>
                        {'\u20B9'}{total.toLocaleString('en-IN')}
                      </Text>
                    </Card.Content>
                  </Card>
                )}

                <Button
                  mode="contained"
                  onPress={handleRecordSale}
                  disabled={isSubmitting || !quantity || !price}
                  loading={isSubmitting}
                  style={styles.recordButton}
                  contentStyle={styles.recordButtonContent}
                  labelStyle={styles.recordButtonLabel}
                  buttonColor={colors.primary}
                >
                  {t('sell.recordSale')}
                </Button>
              </View>
            )}

            {/* Recent sales header */}
            <Divider style={styles.divider} />
            <Text variant="titleMedium" style={styles.sectionTitle}>
              {t('sell.recentSales')}
            </Text>
            {recentSales.length === 0 && (
              <EmptyState
                icon={'\uD83D\uDED2'}
                title={t('empty.noSales')}
                subtitle={t('sell.recordSale')}
              />
            )}
          </>
        }
      />

      <Snackbar
        visible={snackVisible}
        onDismiss={() => setSnackVisible(false)}
        duration={2000}
        style={styles.snackbar}
      >
        {snackMessage || t('sell.saleRecorded')}
      </Snackbar>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F0',
  },
  scroll: {
    padding: SPACING.md,
    paddingBottom: 100,
  },
  heading: {
    fontWeight: '700',
    color: colors.primary,
    marginBottom: SPACING.md,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm + 4,
  },
  form: {
    marginTop: SPACING.lg,
    gap: SPACING.md,
  },
  input: {
    fontSize: 18,
    backgroundColor: '#FFFFFF',
  },
  quantityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  quantityInput: {
    flex: 1,
  },
  totalCard: {
    backgroundColor: '#A8F5C8',
    borderRadius: CARD_BORDER_RADIUS,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  totalContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
  },
  totalLabel: {
    color: '#002112',
  },
  totalAmount: {
    color: colors.primary,
    fontWeight: '700',
  },
  recordButton: {
    borderRadius: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  recordButtonContent: {
    height: 56,
  },
  recordButtonLabel: {
    fontSize: 18,
    fontWeight: '700',
  },
  divider: {
    marginVertical: SPACING.lg,
    backgroundColor: '#C1C9BF',
  },
  sectionTitle: {
    fontWeight: '700',
    marginBottom: SPACING.sm,
    color: '#1A1A1A',
  },
  saleCard: {
    marginBottom: SPACING.sm + 2,
    borderRadius: CARD_BORDER_RADIUS,
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  saleContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  saleLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm + 4,
  },
  saleIcon: {
    fontSize: 28,
  },
  saleName: {
    color: '#1A1A1A',
  },
  saleMeta: {
    color: '#717971',
    marginTop: 2,
  },
  saleAmount: {
    color: colors.primary,
    fontWeight: '700',
  },
  snackbar: {
    backgroundColor: colors.primary,
  },
});
