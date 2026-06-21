import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {palette} from '../design-system/colors';
import {interFontFamily} from '../design-system/typography';

export type CategoryBarProps = {
  label: string;
  value: number;
  max?: number;
  color?: string;
  startFrame?: number;
};

export const CategoryBar: React.FC<CategoryBarProps> = ({
  label,
  value,
  max = 100,
  color = palette.blue,
  startFrame = 0,
}) => {
  const frame = useCurrentFrame();
  const localFrame = Math.max(0, frame - startFrame);
  const widthProgress = interpolate(localFrame, [0, 22], [0, Math.min(1, value / max)], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{position: 'relative', width: 900, height: 70, gap: 10}}>
      <div style={{display: 'flex', justifyContent: 'space-between', fontFamily: interFontFamily, fontWeight: 600, fontSize: 26, color: palette.ink}}>
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div style={{height: 14, backgroundColor: 'rgba(29,29,31,0.08)', borderRadius: 999}}>
        <div style={{height: '100%', width: `${widthProgress * 100}%`, borderRadius: 999, backgroundColor: color}} />
      </div>
    </AbsoluteFill>
  );
};
