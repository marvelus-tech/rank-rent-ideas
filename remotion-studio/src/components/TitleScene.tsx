import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeIn, slideIn} from '../design-system/animations';
import {palette} from '../design-system/colors';
import {typeScale} from '../design-system/typography';

export type TitleSceneProps = {
  kicker: string;
  title: string;
  subtitle?: string;
  startFrame?: number;
};

export const TitleScene: React.FC<TitleSceneProps> = ({kicker, title, subtitle, startFrame = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localFrame = Math.max(0, frame - startFrame);

  const kickerY = slideIn({frame: localFrame, fps, from: 18});
  const titleY = slideIn({frame: localFrame, fps, from: 24, start: 5});

  return (
    <AbsoluteFill
      style={{
        backgroundColor: palette.cloud,
        justifyContent: 'center',
        padding: '120px 96px',
        gap: 26,
      }}
    >
      <div style={{...typeScale.kicker, opacity: fadeIn({frame: localFrame, duration: 12}), transform: `translateY(${kickerY}px)`}}>{kicker}</div>
      <div style={{...typeScale.title, opacity: fadeIn({frame: localFrame, start: 4, duration: 16}), transform: `translateY(${titleY}px)`}}>{title}</div>
      {subtitle ? (
        <div style={{...typeScale.body, opacity: fadeIn({frame: localFrame, start: 10, duration: 18})}}>{subtitle}</div>
      ) : null}
    </AbsoluteFill>
  );
};
