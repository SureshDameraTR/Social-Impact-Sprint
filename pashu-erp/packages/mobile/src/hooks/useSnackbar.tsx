import React, { createContext, useCallback, useContext, useState } from 'react';
import { Snackbar } from 'react-native-paper';

type SnackType = 'error' | 'success' | 'info';

interface SnackbarContextValue {
  showError: (message: string) => void;
  showSuccess: (message: string) => void;
  showInfo: (message: string) => void;
}

const SnackbarContext = createContext<SnackbarContextValue>({
  showError: () => {},
  showSuccess: () => {},
  showInfo: () => {},
});

export function SnackbarProvider({ children }: { children: React.ReactNode }) {
  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState('');
  const [type, setType] = useState<SnackType>('info');

  const show = useCallback((msg: string, t: SnackType) => {
    setMessage(msg);
    setType(t);
    setVisible(true);
  }, []);

  const bgColor = type === 'error' ? '#d32f2f' : type === 'success' ? '#2e7d32' : '#1976d2';

  return (
    <SnackbarContext.Provider
      value={{
        showError: (m) => show(m, 'error'),
        showSuccess: (m) => show(m, 'success'),
        showInfo: (m) => show(m, 'info'),
      }}
    >
      {children}
      <Snackbar
        visible={visible}
        onDismiss={() => setVisible(false)}
        duration={4000}
        style={{ backgroundColor: bgColor }}
        action={{ label: 'OK', onPress: () => setVisible(false) }}
      >
        {message}
      </Snackbar>
    </SnackbarContext.Provider>
  );
}

export const useSnackbar = () => useContext(SnackbarContext);
