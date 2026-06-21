import {loadFont} from '@remotion/google-fonts/Inter';
import {palette} from './colors';

export const {fontFamily: interFontFamily} = loadFont('normal', {
  weights: ['400', '500', '600', '700', '800'],
  subsets: ['latin'],
});

export const typeScale = {
  kicker: {
    fontFamily: interFontFamily,
    fontSize: 22,
    fontWeight: 600,
    letterSpacing: 1.5,
    textTransform: 'uppercase' as const,
    color: palette.blue,
  },
  title: {
    fontFamily: interFontFamily,
    fontSize: 78,
    lineHeight: 1.05,
    fontWeight: 700,
    color: palette.ink,
  },
  h2: {
    fontFamily: interFontFamily,
    fontSize: 48,
    lineHeight: 1.12,
    fontWeight: 700,
    color: palette.ink,
  },
  body: {
    fontFamily: interFontFamily,
    fontSize: 28,
    lineHeight: 1.3,
    fontWeight: 500,
    color: palette.mutedText,
  },
  metricLabel: {
    fontFamily: interFontFamily,
    fontSize: 24,
    fontWeight: 500,
    color: palette.mutedText,
  },
  metricValue: {
    fontFamily: interFontFamily,
    fontSize: 56,
    fontWeight: 700,
    color: palette.ink,
  },
};
