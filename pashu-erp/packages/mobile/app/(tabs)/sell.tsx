import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, TextInput, Button, Card, Snackbar, Divider } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { ProductCard } from '../../src/components/ProductCard';
import { MicButton } from '../../src/components/MicButton';
import { EmptyState } from '../../src/components/EmptyState';
import { SPACING, CARD_BORDER_RADIUS } from '../../src/config/theme';

type ProductType = 'milk' | 'eggs' | 'goatProducts' | 'manure';

const PRODUCTS: { key: ProductType; icon: string }[] = [
  { key: 'milk', icon: '\uD83E\uDD5B' },
  { key: 'eggs', icon: '\uD83E\uDD5A' },
  { key: 'goatProducts', icon: '\uD83D\uDC10' },
  { key: 'manure', icon: '\uD83C\uDF3E' },
];

const MOCK_SALES = [
  { id: '1', product: 'milk', qty: '10L', amount: 450, buyer: 'KMF', date: '2026-04-07' },
  { id: '2', product: 'eggs', qty: '30', amount: 210, buyer: 'Local Market', date: '2026-04-06' },
  { id: '3', product: 'manure', qty: '50kg', amount: 300, buyer: 'Ravi Farm', date: '2026-04-05' },
];

export default function SellScreen() {
  const { t } = useTranslation();
  const [selectedProduct, setSelectedProduct] = useState<ProductType | ''>('');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [snackVisible, setSnackVisible] = useState(false);
  const [snackMessage, setSnackMessage] = useState('');

  const total = (parseFloat(quantity) || 0) * (parseFloat(price) || 0);

  const handleVoiceResult = (value: number) => {
    setQuantity(String(value));
    setSnackMessage(`${value}`);
  };

  const handleVoiceTranscript = (text: string) => {
    setSnackMessage((prev) => `${text} \u2014 ${prev || '...'}`);
    setSnackVisible(true);
  };

  const handleRecordSale = () => {
    setSnackMessage(t('sell.saleRecorded'));
    setSnackVisible(true);
    setSelectedProduct('');
    setQuantity('');
    setPrice('');
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text variant="headlineSmall" style={styles.heading}>
          {t('sell.sellProducts')}
        </Text>

        {/* Product grid */}
        <View style={styles.grid}>
          {PRODUCTS.map((p) => (
            <ProductCard
              key={p.key}
              icon={p.icon}
              label={t(`sell.${p.key}`)}
              selected={selectedProduct === p.key}
              onPress={() => setSelectedProduct(p.key)}
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
                onChangeText={setQuantity}
                keyboardType="decimal-pad"
                mode="outlined"
                style={[styles.input, styles.quantityInput]}
              />
              <MicButton
                context="sell_quantity"
                onResult={handleVoiceResult}
                onTranscript={handleVoiceTranscript}
              />
            </View>
            <TextInput
              label={`${t('sell.pricePerUnit')} (\u20B9)`}
              value={price}
              onChangeText={setPrice}
              keyboardType="decimal-pad"
              mode="outlined"
              style={styles.input}
            />

            {total > 0 && (
              <Card style={styles.totalCard}>
                <Card.Content style={styles.totalContent}>
                  <Text variant="bodyLarge">{t('sell.total')}</Text>
                  <Text variant="headlineMedium" style={styles.totalAmount}>
                    {'\u20B9'}{total.toLocaleString('en-IN')}
                  </Text>
                </Card.Content>
              </Card>
            )}

            <Button
              mode="contained"
              onPress={handleRecordSale}
              disabled={!quantity || !price}
              style={styles.recordButton}
              contentStyle={styles.recordButtonContent}
              labelStyle={styles.recordButtonLabel}
            >
              {t('sell.recordSale')}
            </Button>
          </View>
        )}

        {/* Recent sales */}
        <Divider style={styles.divider} />
        <Text variant="titleMedium" style={styles.sectionTitle}>
          {t('sell.recentSales')}
        </Text>
        {MOCK_SALES.length === 0 ? (
          <EmptyState
            icon={'\uD83D\uDED2'}
            title={t('empty.noSales')}
            subtitle={t('sell.recordSale')}
          />
        ) : (
          MOCK_SALES.map((sale) => (
            <Card key={sale.id} style={styles.saleCard}>
              <Card.Content style={styles.saleContent}>
                <View>
                  <Text variant="titleSmall">{sale.product} - {sale.qty}</Text>
                  <Text variant="bodySmall" style={styles.saleMeta}>
                    {sale.buyer} | {sale.date}
                  </Text>
                </View>
                <Text variant="titleMedium" style={styles.saleAmount}>
                  {'\u20B9'}{sale.amount}
                </Text>
              </Card.Content>
            </Card>
          ))
        )}
      </ScrollView>

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
    backgroundColor: '#FAFAFA',
  },
  scroll: {
    padding: SPACING.md,
    paddingBottom: 100,
  },
  heading: {
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: SPACING.md,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  form: {
    marginTop: SPACING.lg,
    gap: SPACING.md,
  },
  input: {
    fontSize: 18,
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
    backgroundColor: '#E8F5E9',
    borderRadius: CARD_BORDER_RADIUS,
  },
  totalContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  totalAmount: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  recordButton: {
    borderRadius: 12,
    backgroundColor: '#2E7D32',
  },
  recordButtonContent: {
    height: 56,
  },
  recordButtonLabel: {
    fontSize: 18,
  },
  divider: {
    marginVertical: SPACING.lg,
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
  },
  saleCard: {
    marginBottom: SPACING.sm,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
  },
  saleContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  saleMeta: {
    color: '#9E9E9E',
    marginTop: 2,
  },
  saleAmount: {
    color: '#2E7D32',
    fontWeight: 'bold',
  },
  snackbar: {
    backgroundColor: '#2E7D32',
  },
});
