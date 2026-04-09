import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './en.json';

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
  },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
  compatibilityJSON: 'v4',
});

const bundles: Record<string, () => Record<string, string>> = {
  kn: () => require('./kn.json'),
};

export function loadLanguage(lang: string) {
  if (lang !== 'en' && !i18n.hasResourceBundle(lang, 'translation')) {
    const loader = bundles[lang];
    if (loader) {
      i18n.addResourceBundle(lang, 'translation', loader());
    }
  }
  i18n.changeLanguage(lang);
}

export default i18n;
