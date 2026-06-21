import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeIn, slideIn} from '../design-system/animations';
import {palette} from '../design-system/colors';
import {interFontFamily} from '../design-system/typography';

export type ActionItemProps = {
  title: string;
  detail: string;
  urgency: 'Low' | 'Medium' | 'High';
  startFrame?: number;
};

const urgencyColor = (urgency: ActionItemProps['urgency']) => {
  if (urgency === 'High') return palette.red;
  if (urgency === 'Medium') return palette.orange;
  return palette.green;
};

export const ActionItem: React.FC<ActionItemProps> = ({title, detail, urgency, startFrame = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localFrame = Math.max(0, frame - startFrame);

  return (
    <AbsoluteFill
      style={{
        position: 'relative',
        width: 920,
        height: 132,
        borderRadius: 24,
        border: `1px solid ${palette.divider}`,
        backgroundColor: palette.white,
        padding: '22px 26px',
        justifyContent: 'center',
        gap: 8,
        transform: `translateY(${slideIn({frame: localFrame, fps, from: 16})}px)`,
        opacity: fadeIn({frame: localFrame, duration: 12}),
      }}
    >
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div style={{fontFamily: interFontFamily, fontSize: 30, fontWeight: 700, color: palette.ink}}>{title}</div>
        <div style={{fontFamily: interFontFamily, fontSize: 18, fontWeight: 700, color: palette.white, backgroundColor: urgencyColor(urgency), borderRadius: 999, padding: '8px 13px'}}>
          {urgency}
        </div>
      </div>
      <div style={{fontFamily: interFontFamily, fontSize: 24, fontWeight: 500, color: palette.mutedText}}>{detail}</div>
    </AbsoluteFill>
  );
};
