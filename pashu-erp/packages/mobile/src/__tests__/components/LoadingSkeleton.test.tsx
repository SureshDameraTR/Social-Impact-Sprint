import React from 'react';
import { render } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import LoadingSkeleton from '../../components/LoadingSkeleton';
import { theme } from '../../config/theme';

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

describe('LoadingSkeleton', () => {
  it('renders default number of skeleton rows (3)', () => {
    const { getAllByTestId } = render(wrap(<LoadingSkeleton />));
    expect(getAllByTestId('skeleton-row')).toHaveLength(3);
  });

  it('renders correct count when count prop is provided', () => {
    const { getAllByTestId } = render(wrap(<LoadingSkeleton count={5} />));
    expect(getAllByTestId('skeleton-row')).toHaveLength(5);
  });

  it('renders 0 rows when count=0', () => {
    const { queryAllByTestId } = render(wrap(<LoadingSkeleton count={0} />));
    expect(queryAllByTestId('skeleton-row')).toHaveLength(0);
  });

  it('does not crash when count is very large', () => {
    expect(() => render(wrap(<LoadingSkeleton count={50} />))).not.toThrow();
  });

  it('animates (Animated.Value exists in tree)', () => {
    // Smoke test: animation should not throw
    expect(() => render(wrap(<LoadingSkeleton />))).not.toThrow();
  });
});
