import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeIn, slideIn} from '../design-system/animations';
import {palette} from '../design-system/colors';
import {interFontFamily} from '../design-system/typography';

export type LeadCardProps = {
  name: string;
  company: string;
  score: number;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  startFrame?: number;
  durationInFrames?: number;
};

const priorityColor = (priority: LeadCardProps['priority']) => {
  if (priority === 'Critical') return palette.red;
  if (priority === 'High') return palette.orange;
  if (priority === 'Medium') return palette.blue;
  return palette.green;
};

export const LeadCard: React.FC<LeadCardProps> = ({
  name,
  company,
  score,
  priority,
  startFrame = 0,
  durationInFrames = 90,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localFrame = Math.max(0, frame - startFrame);
  const y = slideIn({frame: localFrame, fps, from: 18});
  const opacity = fadeIn({frame: localFrame, duration: 14});

  const scoreOpacity = interpolate(localFrame, [10, 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        position: 'relative',
        width: 920,
        height: 128,
        backgroundColor: palette.white,
        borderRadius: 22,
        border: `1px solid ${palette.divider}`,
        padding: '22px 28px',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        transform: `translateY(${y}px)`,
        opacity: opacity * (localFrame <= durationInFrames ? 1 : 0),
      }}
    >
      <div style={{display: 'flex', flexDirection: 'column', gap: 6}}>
        <div style={{fontFamily: interFontFamily, fontSize: 36, fontWeight: 700, color: palette.ink}}>{name}</div>
        <div style={{fontFamily: interFontFamily, fontSize: 24, fontWeight: 500, color: palette.mutedText}}>{company}</div>
      </div>

      <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
        <div
          style={{
            fontFamily: interFontFamily,
            fontSize: 28,
            fontWeight: 700,
            color: palette.ink,
            opacity: scoreOpacity,
          }}
        >
          {score}
        </div>
        <div
          style={{
            fontFamily: interFontFamily,
            fontSize: 20,
            fontWeight: 700,
            color: palette.white,
            backgroundColor: priorityColor(priority),
            padding: '9px 14px',
            borderRadius: 999,
          }}
        >
          {priority}
        </div>
      </div>
    </AbsoluteFill>
  );
};
