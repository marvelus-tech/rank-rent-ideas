import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {CategoryBar} from '../components/CategoryBar';
import {TitleScene} from '../components/TitleScene';
import {palette} from '../design-system/colors';
import {interFontFamily} from '../design-system/typography';

export type DataStoryPoint = {label: string; value: number; color?: string};

export type DataStoryVideoProps = {
  title: string;
  kicker: string;
  subtitle?: string;
  points: DataStoryPoint[];
};

export const dataStoryDurationInFrames = 360;

export const DataStoryVideo: React.FC<DataStoryVideoProps> = ({title, kicker, subtitle, points}) => {
  return (
    <AbsoluteFill style={{backgroundColor: palette.cloud}}>
      <Sequence from={0} durationInFrames={110} premountFor={30}>
        <TitleScene kicker={kicker} title={title} subtitle={subtitle} />
      </Sequence>

      <Sequence from={90} durationInFrames={220} premountFor={30}>
        <AbsoluteFill style={{padding: '120px 90px', gap: 20}}>
          {points.slice(0, 5).map((point, i) => (
            <CategoryBar
              key={point.label}
              label={point.label}
              value={point.value}
              color={point.color}
              startFrame={i * 8}
            />
          ))}
        </AbsoluteFill>
      </Sequence>

      <Sequence from={300} durationInFrames={60} premountFor={30}>
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
          <div style={{fontFamily: interFontFamily, fontSize: 44, fontWeight: 700, color: palette.ink}}>
            Clarity creates momentum.
          </div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

export const defaultDataStoryProps: DataStoryVideoProps = {
  title: 'Revenue Mix Story',
  kicker: 'Quarterly Strategy',
  subtitle: 'What changed and where to double down.',
  points: [
    {label: 'Referrals', value: 42, color: palette.blue},
    {label: 'Organic Search', value: 31, color: palette.green},
    {label: 'Paid Ads', value: 18, color: palette.orange},
    {label: 'Partnerships', value: 24, color: palette.red},
  ],
};
