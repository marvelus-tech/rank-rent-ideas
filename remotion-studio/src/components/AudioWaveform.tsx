import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {palette} from '../design-system/colors';

export type AudioWaveformProps = {
  bars?: number;
  amplitude?: number;
  startFrame?: number;
};

export const AudioWaveform: React.FC<AudioWaveformProps> = ({bars = 36, amplitude = 46, startFrame = 0}) => {
  const frame = useCurrentFrame();
  const localFrame = Math.max(0, frame - startFrame);

  return (
    <AbsoluteFill style={{position: 'relative', width: 920, height: 120, flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between'}}>
      {Array.from({length: bars}).map((_, i) => {
        const wave = Math.abs(Math.sin((localFrame + i * 2.4) * 0.08));
        const height = interpolate(wave, [0, 1], [8, amplitude]);

        return (
          <div
            key={i}
            style={{
              width: 14,
              height,
              borderRadius: 999,
              backgroundColor: i % 3 === 0 ? palette.blue : palette.ink,
              opacity: 0.75,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
