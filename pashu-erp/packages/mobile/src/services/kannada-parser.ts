/**
 * Kannada number word to digit parser
 * Handles: \u0C92\u0C82\u0CA6\u0CC1(1) through \u0CB9\u0CA4\u0CCD\u0CA4\u0CC1(10), teens, tens, hundreds
 * Also handles decimal numbers passed as digit strings
 */

const KANNADA_NUMBERS: Record<string, number> = {
  '\u0C92\u0C82\u0CA6\u0CC1': 1,
  '\u0C8E\u0CB0\u0CA1\u0CC1': 2,
  '\u0CAE\u0CC2\u0CB0\u0CC1': 3,
  '\u0CA8\u0CBE\u0CB2\u0CCD\u0C95\u0CC1': 4,
  '\u0C90\u0CA6\u0CC1': 5,
  '\u0C86\u0CB0\u0CC1': 6,
  '\u0C8F\u0CB3\u0CC1': 7,
  '\u0C8E\u0C82\u0C9F\u0CC1': 8,
  '\u0C92\u0C82\u0CAC\u0CA4\u0CCD\u0CA4\u0CC1': 9,
  '\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1': 10,
  '\u0CB9\u0CA8\u0CCD\u0CA8\u0CCA\u0C82\u0CA6\u0CC1': 11,
  '\u0CB9\u0CA8\u0CCD\u0CA8\u0CC6\u0CB0\u0CA1\u0CC1': 12,
  '\u0CB9\u0CA6\u0CBF\u0CAE\u0CC2\u0CB0\u0CC1': 13,
  '\u0CB9\u0CA6\u0CBF\u0CA8\u0CBE\u0CB2\u0CCD\u0C95\u0CC1': 14,
  '\u0CB9\u0CA6\u0CBF\u0CA8\u0CC8\u0CA6\u0CC1': 15,
  '\u0CB9\u0CA6\u0CBF\u0CA8\u0CBE\u0CB0\u0CC1': 16,
  '\u0CB9\u0CA6\u0CBF\u0CA8\u0CC7\u0CB3\u0CC1': 17,
  '\u0CB9\u0CA6\u0CBF\u0CA8\u0CC6\u0C82\u0C9F\u0CC1': 18,
  '\u0CB9\u0CA4\u0CCD\u0CA4\u0CCA\u0C82\u0CAC\u0CA4\u0CCD\u0CA4\u0CC1': 19,
  '\u0C87\u0CAA\u0CCD\u0CAA\u0CA4\u0CCD\u0CA4\u0CC1': 20,
  '\u0CAE\u0CC2\u0CB5\u0CA4\u0CCD\u0CA4\u0CC1': 30,
  '\u0CA8\u0CB2\u0CB5\u0CA4\u0CCD\u0CA4\u0CC1': 40,
  '\u0C90\u0CB5\u0CA4\u0CCD\u0CA4\u0CC1': 50,
  '\u0C85\u0CB0\u0CB5\u0CA4\u0CCD\u0CA4\u0CC1': 60,
  '\u0C8E\u0CAA\u0CCD\u0CAA\u0CA4\u0CCD\u0CA4\u0CC1': 70,
  '\u0C8E\u0C82\u0CAC\u0CA4\u0CCD\u0CA4\u0CC1': 80,
  '\u0CA4\u0CCA\u0C82\u0CAC\u0CA4\u0CCD\u0CA4\u0CC1': 90,
  '\u0CA8\u0CC2\u0CB0\u0CC1': 100,
};

// Unit words spoken by farmers that should be stripped before parsing
const UNIT_WORDS = [
  '\u0CB2\u0CC0\u0C9F\u0CB0\u0CCD',   // liter
  '\u0CAE\u0CCA\u0C9F\u0CCD\u0C9F\u0CC6', // motte (eggs)
  '\u0C95\u0CC6\u0C9C\u0CBF',           // keji (kg)
  'liter', 'liters', 'eggs', 'kg',
];

/**
 * Parse Kannada number words (or digit strings) into a numeric value.
 * Strips unit words like \u0CB2\u0CC0\u0C9F\u0CB0\u0CCD, \u0CAE\u0CCA\u0C9F\u0CCD\u0C9F\u0CC6, \u0C95\u0CC6\u0C9C\u0CBF before parsing.
 *
 * Examples:
 *   "\u0C90\u0CA6\u0CC1"          -> 5
 *   "\u0CAE\u0CC2\u0CB0\u0CC1 \u0CB2\u0CC0\u0C9F\u0CB0\u0CCD"  -> 3
 *   "\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1 \u0CAE\u0CCA\u0C9F\u0CCD\u0C9F\u0CC6" -> 10
 *   "5.5"           -> 5.5
 *   "random text"   -> null
 */
export function parseKannadaNumber(text: string): number | null {
  let cleaned = text.trim();

  // Strip unit words
  for (const unit of UNIT_WORDS) {
    cleaned = cleaned.replace(new RegExp(unit, 'gi'), '').trim();
  }

  // Try direct numeric parse first
  const directNum = parseFloat(cleaned);
  if (!isNaN(directNum)) return directNum;

  // Try Kannada word lookup
  const words = cleaned.split(/\s+/).filter(Boolean);
  let total = 0;
  let hasMatch = false;

  for (const word of words) {
    // Skip decimal separator words
    if (word === '\u0CAA\u0CBE\u0CAF\u0CBF\u0C82\u0C9F\u0CCD' || word === 'point') continue;

    const val = KANNADA_NUMBERS[word];
    if (val !== undefined) {
      total += val;
      hasMatch = true;
    }
  }

  return hasMatch ? total : null;
}
