import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Img,
  staticFile,
} from 'remotion';
import {interFontFamily} from '../design-system/typography';

const fps = 30;

// Apple-style smooth easing
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

export type AppleStyleVideoProps = {
  kicker: string;
  title: string;
  benefit: string;
  cta: string;
  imageUrl?: string;
  durationInSeconds?: number;
  logoText?: string;
};

export const AppleStyleVideo: React.FC<AppleStyleVideoProps> = ({
  kicker, title, cta, imageUrl, logoText,
}) => {
  const {width, height} = useVideoConfig();
  const frame = useCurrentFrame();

  const resolvedImage = imageUrl
    ? imageUrl.startsWith('http')
      ? imageUrl
      : staticFile(imageUrl)
    : undefined;

  // Device frame animation
  const deviceEntry = spring({
    frame: frame - 10,
    fps,
    config: {damping: 20, stiffness: 100, mass: 1.5},
  });

  const deviceY = interpolate(deviceEntry, [0, 1], [200, 0]);
  const deviceScale = interpolate(deviceEntry, [0, 1], [0.85, 1]);
  const deviceOpacity = interpolate(frame, [10, 25], [0, 1], {extrapolateLeft: 'clamp'});

  // Screenshot scroll
  const scrollProgress = (frame % 450) / 450;
  const scrollAmount = (Math.sin(scrollProgress * Math.PI * 2) + 1) / 2;
  const screenshotY = scrollAmount * 80; // pixels

  // Text animations
  const kickerSpring = spring({frame: frame - 30, fps, config: {damping: 15, stiffness: 150}});
  const titleSpring = spring({frame: frame - 40, fps, config: {damping: 12, stiffness: 120, mass: 1.2}});
  const ctaSpring = spring({frame: frame - 120, fps, config: {damping: 10, stiffness: 180}});

  const kickerOp = interpolate(frame, [30, 45], [0, 1], {extrapolateLeft: 'clamp'});
  const titleOp = interpolate(frame, [40, 55], [0, 1], {extrapolateLeft: 'clamp'});
  const ctaOp = interpolate(frame, [120, 135], [0, 1], {extrapolateLeft: 'clamp'});

  // CTA pulse
  const pulse = Math.sin((frame - 120) * 0.08) * 0.5 + 0.5;

  return (
    <AbsoluteFill style={{background: '#f5f7fa', width, height}}>
      {/* Subtle gradient background */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'radial-gradient(ellipse at 50% 30%, #ffffff 0%, #e8ecf0 50%, #d4dbe3 100%)',
        }}
      />

      {/* Floating particles */}
      {Array.from({length: 6}).map((_, i) => {
        const x = 20 + (i * 15) + Math.sin(frame * 0.02 + i) * 5;
        const y = 30 + (i * 10) + Math.cos(frame * 0.015 + i * 2) * 3;
        const opacity = 0.3 + Math.sin(frame * 0.01 + i) * 0.15;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${x}%`,
              top: `${y}%`,
              width: 4,
              height: 4,
              borderRadius: '50%',
              background: '#aabbcc',
              opacity,
              filter: 'blur(1px)',
            }}
          />
        );
      })}

      {/* Device Frame */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `translate(-50%, -50%) translateY(${deviceY}px) scale(${deviceScale})`,
          opacity: deviceOpacity,
          width: 700,
          height: 440,
        }}
      >
        {/* Device body — silver */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'linear-gradient(135deg, #d1d5db 0%, #b8bcc4 50%, #9ca3af 100%)',
            borderRadius: 24,
            boxShadow: `
              0 20px 60px rgba(0,0,0,0.15),
              0 8px 24px rgba(0,0,0,0.1),
              inset 0 1px 0 rgba(255,255,255,0.5)
            `,
            padding: 12,
          }}
        >
          {/* Screen bezel */}
          <div
            style={{
              width: '100%',
              height: '100%',
              background: '#000000',
              borderRadius: 16,
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            {/* Screenshot with scroll */}
            {resolvedImage && (
              <Img
                src={resolvedImage}
                style={{
                  width: '100%',
                  height: 'auto',
                  transform: `translateY(-${screenshotY}px)`,
                  objectFit: 'cover',
                }}
              />
            )}
            {/* Screen reflection */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                background: 'linear-gradient(180deg, rgba(255,255,255,0.08) 0%, transparent 30%, transparent 70%, rgba(255,255,255,0.04) 100%)',
                pointerEvents: 'none',
              }}
            />
          </div>
        </div>

        {/* Device shadow */}
        <div
          style={{
            position: 'absolute',
            bottom: -30,
            left: '10%',
            width: '80%',
            height: 30,
            background: 'radial-gradient(ellipse, rgba(0,0,0,0.15) 0%, transparent 70%)',
            filter: 'blur(8px)',
          }}
        />
      </div>

      {/* Text overlay */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '80px 60px',
          pointerEvents: 'none',
          zIndex: 10,
        }}
      >
        {/* Top: Kicker + Title */}
        <div style={{display: 'flex', flexDirection: 'column', gap: 16}}>
          <div
            style={{
              transform: `translateY(${(1 - kickerSpring) * 15}px)`,
              opacity: kickerOp,
            }}
          >
            <div
              style={{
                fontFamily: interFontFamily,
                fontSize: 16,
                fontWeight: 600,
                letterSpacing: '0.2em',
                textTransform: 'uppercase',
                color: '#86868b',
              }}
            >
              {kicker}
            </div>
          </div>
          <div
            style={{
              transform: `translateY(${(1 - titleSpring) * 30}px)`,
              opacity: titleOp,
            }}
          >
            <div
              style={{
                fontFamily: interFontFamily,
                fontSize: 52,
                fontWeight: 800,
                lineHeight: 1.1,
                color: '#1d1d1f',
                letterSpacing: '-0.025em',
                maxWidth: '80%',
              }}
            >
              {title}
            </div>
          </div>
        </div>

        {/* Bottom: CTA */}
        <div style={{display: 'flex', justifyContent: 'center'}}>
          <div
            style={{
              transform: `scale(${ctaSpring})`,
              opacity: ctaOp,
            }}
          >
            <div
              style={{
                background: '#0071e3',
                color: '#ffffff',
                padding: '18px 40px',
                borderRadius: 100,
                fontFamily: interFontFamily,
                fontSize: 20,
                fontWeight: 600,
                boxShadow: `0 0 ${20 + pulse * 25}px rgba(0,113,227,${0.3 + pulse * 0.3})`,
                transform: `scale(${1 + pulse * 0.02})`,
              }}
            >
              {cta}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const defaultAppleStyleProps: AppleStyleVideoProps = {
  kicker: 'Product Update',
  title: 'AI Follow-Ups, Now in Real Time',
  benefit: 'Never lose high-intent leads between inquiry and call.',
  cta: 'Turn it on today.',
  imageUrl: undefined,
  durationInSeconds: 15,
  logoText: 'LUSTRE',
};

export const appleStyleDurationInFrames = 450;
