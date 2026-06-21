import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeIn, scaleIn, slideIn} from '../design-system/animations';
import {palette} from '../design-system/colors';
import {typeScale} from '../design-system/typography';

export type MetricCardProps = {
  value: number;
  label: string;
  suffix?: string;
  startFrame?: number;
  durationInFrames?: number;
};

export const MetricCard: React.FC<MetricCardProps> = ({
  value,
  label,
  suffix = '',
  startFrame = 0,
  durationInFrames = 90,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localFrame = Math.max(0, frame - startFrame);

  const progress = spring({
    fps,
    frame: Math.min(localFrame, durationInFrames),
    config: {
      damping: 18,
      stiffness: 90,
      mass: 0.8,
    },
  });

  const animatedValue = Math.round(interpolate(progress, [0, 1], [0, value]));
  const y = slideIn({frame: localFrame, fps, from: 26});
  const opacity = fadeIn({frame: localFrame, duration: 16});
  const scale = scaleIn({frame: localFrame, fps, from: 0.94});

  return (
    <AbsoluteFill
      style={{
        position: 'relative',
        width: 312,
        height: 220,
        backgroundColor: palette.glass,
        borderRadius: 28,
        border: `1px solid ${palette.divider}`,
        padding: 28,
        justifyContent: 'space-between',
        boxShadow: '0 24px 60px rgba(0,0,0,0.08)',
        transform: `translateY(${y}px) scale(${scale})`,
        opacity,
      }}
    >
      <div style={typeScale.metricLabel}>{label}</div>
      <div style={{...typeScale.metricValue, fontVariantNumeric: 'tabular-nums'}}>
        {animatedValue.toLocaleString()}
        {suffix}
      </div>
    </AbsoluteFill>
  );
};
