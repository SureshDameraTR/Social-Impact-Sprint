'use client';
import { Box, Typography } from '@mui/material';
import SearchOffIcon from '@mui/icons-material/SearchOff';
import { colors } from '../theme/theme';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export default function EmptyState({
  icon = <SearchOffIcon sx={{ fontSize: 48, color: colors.textLight }} />,
  title = 'No results found',
  subtitle = 'Try adjusting your search or filters.',
}: EmptyStateProps) {
  return (
    <Box sx={{ textAlign: 'center', py: 6 }}>
      {icon}
      <Typography variant="h6" sx={{ mt: 2, color: colors.textDim }}>{title}</Typography>
      <Typography variant="body2" sx={{ mt: 0.5, color: colors.textLight }}>{subtitle}</Typography>
    </Box>
  );
}
