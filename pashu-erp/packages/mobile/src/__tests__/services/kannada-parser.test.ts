/**
 * Kannada number parser tests (Jest format).
 *
 * Verifies: basic number words, unit word stripping, numeric strings,
 * edge cases (empty, unknown text).
 */
import { parseKannadaNumber } from '../../services/kannada-parser';

describe('parseKannadaNumber', () => {
  // ---- Basic Kannada number words ----

  it.each([
    ['\u0C92\u0C82\u0CA6\u0CC1', 1],
    ['\u0C8E\u0CB0\u0CA1\u0CC1', 2],
    ['\u0CAE\u0CC2\u0CB0\u0CC1', 3],
    ['\u0CA8\u0CBE\u0CB2\u0CCD\u0C95\u0CC1', 4],
    ['\u0C90\u0CA6\u0CC1', 5],
    ['\u0C86\u0CB0\u0CC1', 6],
    ['\u0C8F\u0CB3\u0CC1', 7],
    ['\u0C8E\u0C82\u0C9F\u0CC1', 8],
    ['\u0C92\u0C82\u0CAC\u0CA4\u0CCD\u0CA4\u0CC1', 9],
    ['\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1', 10],
  ])('parses "%s" as %d', (input, expected) => {
    expect(parseKannadaNumber(input)).toBe(expected);
  });

  // ---- Larger numbers ----

  it('parses 20 (ippattu)', () => {
    expect(parseKannadaNumber('\u0C87\u0CAA\u0CCD\u0CAA\u0CA4\u0CCD\u0CA4\u0CC1')).toBe(20);
  });

  it('parses 100 (nooru)', () => {
    expect(parseKannadaNumber('\u0CA8\u0CC2\u0CB0\u0CC1')).toBe(100);
  });

  // ---- Unit word stripping ----

  it('strips liter unit word', () => {
    expect(parseKannadaNumber('\u0CAE\u0CC2\u0CB0\u0CC1 \u0CB2\u0CC0\u0C9F\u0CB0\u0CCD')).toBe(3);
  });

  it('strips motte (eggs) unit word', () => {
    expect(parseKannadaNumber('\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1 \u0CAE\u0CCA\u0C9F\u0CCD\u0C9F\u0CC6')).toBe(10);
  });

  it('strips English unit words', () => {
    expect(parseKannadaNumber('5 liters')).toBe(5);
    expect(parseKannadaNumber('10 kg')).toBe(10);
  });

  // ---- Numeric strings (direct parse) ----

  it('parses integer string', () => {
    expect(parseKannadaNumber('42')).toBe(42);
  });

  it('parses decimal string', () => {
    expect(parseKannadaNumber('5.5')).toBe(5.5);
  });

  it('parses zero', () => {
    expect(parseKannadaNumber('0')).toBe(0);
  });

  // ---- Edge cases ----

  it('returns null for empty string', () => {
    expect(parseKannadaNumber('')).toBeNull();
  });

  it('returns null for unrecognized text', () => {
    expect(parseKannadaNumber('random text')).toBeNull();
  });

  it('handles whitespace-only input', () => {
    expect(parseKannadaNumber('   ')).toBeNull();
  });

  it('handles leading and trailing whitespace', () => {
    expect(parseKannadaNumber('  \u0C90\u0CA6\u0CC1  ')).toBe(5);
  });
});
