import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

export const FadeTransition: React.FC<React.PropsWithChildren<{durationInFrames?: number}>> = ({
  children,
  durationInFrames = 18,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

export const SlideTransition: React.FC<
  React.PropsWithChildren<{durationInFrames?: number; from?: 'left' | 'right' | 'top' | 'bottom'}>
> = ({children, durationInFrames = 20, from = 'bottom'}) => {
  const frame = useCurrentFrame();
  const distance = interpolate(frame, [0, durationInFrames], [100, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const transform =
    from === 'left'
      ? `translateX(${-distance}px)`
      : from === 'right'
        ? `translateX(${distance}px)`
        : from === 'top'
          ? `translateY(${-distance}px)`
          : `translateY(${distance}px)`;

  return <AbsoluteFill style={{transform}}>{children}</AbsoluteFill>;
};

export const WipeTransition: React.FC<React.PropsWithChildren<{durationInFrames?: number}>> = ({
  children,
  durationInFrames = 20,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{clipPath: `inset(0 ${100 - progress}% 0 0)`}}>
      {children}
    </AbsoluteFill>
  );
};
