const colors = {
  background: '#F5F7F8',
  primary: '#164E75',
  primaryDark: '#123F60',
  secondary: '#BDD0DE',
  surface: '#FFFFFF',
  surfaceMuted: '#E8F3F5',
  textPrimary: '#263746',
  textSecondary: '#46576A',
  textMuted: '#64748B',
  onPrimary: '#FFFFFF',
  border: '#AEBCC8',
  borderSubtle: '#D5DEE4',
  error: '#b91c1c',
  errorSurface: '#FEF2F2',
};

const fontSizes = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 20,
  xl: 24,
};

export const theme = {
  colors: {
    ...colors,
    secundary: colors.secondary,
  },
  fontSizes,
  typography: {
    title: {
      fontSize: 22,
      fontWeight: '600' as const,
      lineHeight: 32,
      marginTop: 6,
      marginBottom: 6,
      color: colors.primary,
    },
    subtitle: {
      fontSize: 18,
      fontWeight: '500' as const,
      lineHeight: 24,
      color: colors.textPrimary,
    },
    body: {
      fontSize: 16,
      fontWeight: '400' as const,
      lineHeight: 22,
      color: colors.textPrimary,
    },
    caption: {
      fontSize: 12,
      fontWeight: '400' as const,
      lineHeight: 16,
      color: colors.textSecondary,
    },
    button: {
      fontSize: 14,
      fontWeight: '600' as const,
      lineHeight: 20,
      color: colors.onPrimary,
    },
  },
};
