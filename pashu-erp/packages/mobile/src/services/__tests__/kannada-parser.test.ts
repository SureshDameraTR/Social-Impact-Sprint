import { parseKannadaNumber } from '../kannada-parser';

// Basic numbers
console.assert(parseKannadaNumber('\u0C90\u0CA6\u0CC1') === 5, '\u0C90\u0CA6\u0CC1 should be 5');
console.assert(parseKannadaNumber('\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1') === 10, '\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1 should be 10');
console.assert(parseKannadaNumber('\u0C92\u0C82\u0CA6\u0CC1') === 1, '\u0C92\u0C82\u0CA6\u0CC1 should be 1');
console.assert(parseKannadaNumber('\u0CA8\u0CC2\u0CB0\u0CC1') === 100, '\u0CA8\u0CC2\u0CB0\u0CC1 should be 100');

// Numbers with unit words stripped
console.assert(parseKannadaNumber('\u0CAE\u0CC2\u0CB0\u0CC1 \u0CB2\u0CC0\u0C9F\u0CB0\u0CCD') === 3, '\u0CAE\u0CC2\u0CB0\u0CC1 \u0CB2\u0CC0\u0C9F\u0CB0\u0CCD should be 3');
console.assert(parseKannadaNumber('\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1 \u0CAE\u0CCA\u0C9F\u0CCD\u0C9F\u0CC6') === 10, '\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1 \u0CAE\u0CCA\u0C9F\u0CCD\u0C9F\u0CC6 should be 10');

// Direct numeric strings
console.assert(parseKannadaNumber('5.5') === 5.5, '5.5 should be 5.5');
console.assert(parseKannadaNumber('42') === 42, '42 should be 42');

// Unknown text returns null
console.assert(parseKannadaNumber('random text') === null, 'random text should be null');
console.assert(parseKannadaNumber('') === null, 'empty string should be null');

console.log('All kannada-parser tests passed.');
