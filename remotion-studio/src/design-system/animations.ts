import {Easing, interpolate, spring} from 'remotion';

export const defaultSpringConfig = {
  damping: 18,
  stiffness: 110,
  mass: 0.9,
} as const;

export const fadeIn = ({frame, start = 0, duration = 20}: {frame: number; start?: number; duration?: number}) =>
  interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.2, 0.8, 0.2, 1),
  });

export const slideIn = ({
  frame,
  fps,
  from = 24,
  start = 0,
}: {
  frame: number;
  fps: number;
  from?: number;
  start?: number;
}) => {
  const value = spring({
    frame: Math.max(0, frame - start),
    fps,
    config: defaultSpringConfig,
  });

  return interpolate(value, [0, 1], [from, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
};

export const scaleIn = ({
  frame,
  fps,
  from = 0.9,
  start = 0,
}: {
  frame: number;
  fps: number;
  from?: number;
  start?: number;
}) => {
  const value = spring({
    frame: Math.max(0, frame - start),
    fps,
    config: {
      damping: 16,
      stiffness: 120,
      mass: 0.8,
    },
  });

  return interpolate(value, [0, 1], [from, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
};

export const stagger = (index: number, stepFrames = 6) => index * stepFrames;
