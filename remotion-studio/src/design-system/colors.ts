export const AppleColors = {
  ink: '#1D1D1F',
  cloud: '#F5F5F7',
  blue: '#0071E3',
  green: '#34C759',
  orange: '#FF9500',
  red: '#FF3B30',
} as const;

export const palette = {
  ...AppleColors,
  white: '#FFFFFF',
  black: '#000000',
  glass: 'rgba(255,255,255,0.72)',
  mutedText: 'rgba(29,29,31,0.72)',
  divider: 'rgba(29,29,31,0.1)',
} as const;
