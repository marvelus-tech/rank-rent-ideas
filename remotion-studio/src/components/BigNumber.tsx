import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {palette} from '../design-system/colors';
import {interFontFamily} from '../design-system/typography';

export type BigNumberProps = {
  value: string;
  label: string;
  startFrame?: number;
  durationInFrames?: number;
};

export const BigNumber: React.FC<BigNumberProps> = ({value, label, startFrame = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localFrame = Math.max(0, frame - startFrame);

  const intro = spring({
    frame: localFrame,
    fps,
    config: {
      damping: 14,
      stiffness: 90,
    },
  });

  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 18, transform: `scale(${0.9 + intro * 0.1})`, opacity: intro}}>
      <div
        style={{
          fontFamily: interFontFamily,
          fontSize: 180,
          fontWeight: 800,
          letterSpacing: -4,
          color: palette.ink,
          lineHeight: 0.9,
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontFamily: interFontFamily,
          fontSize: 36,
          fontWeight: 500,
          color: palette.mutedText,
          letterSpacing: 0.3,
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};
