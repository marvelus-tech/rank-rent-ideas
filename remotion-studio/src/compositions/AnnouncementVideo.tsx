import React from 'react';
import {
  AbsoluteFill,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from 'remotion';
import {palette} from '../design-system/colors';
import {interFontFamily} from '../design-system/typography';

export type AnnouncementVideoProps = {
  kicker: string;
  title: string;
  benefit: string;
  cta: string;
  imageUrl?: string;
  durationInSeconds?: number;
};

const fps = 30;

// ------------------------------------------------------------------
// Utility: Ken Burns Effect — slow zoom + pan on still image
// ------------------------------------------------------------------
const KenBurnsImage: React.FC<{
  src: string;
  startScale?: number;
  endScale?: number;
  startX?: number;
  startY?: number;
  endX?: number;
  endY?: number;
  style?: React.CSSProperties;
}> = ({
  src,
  startScale = 1.0,
  endScale = 1.15,
  startX = 0,
  startY = 0,
  endX = -20,
  endY = -10,
  style,
}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const scale = interpolate(frame, [0, durationInFrames], [startScale, endScale], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const x = interpolate(frame, [0, durationInFrames], [startX, endX], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const y = interpolate(frame, [0, durationInFrames], [startY, endY], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        top: -50,
        left: -50,
        width: 'calc(100% + 100px)',
        height: 'calc(100% + 100px)',
        transform: `scale(${scale}) translate(${x}px, ${y}px)`,
        transformOrigin: 'center center',
        ...style,
      }}
    >
      <Img
        src={src}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'top center',
        }}
      />
    </div>
  );
};

// ------------------------------------------------------------------
// Utility: Spring Text Reveal — bounces in from direction
// ------------------------------------------------------------------
const SpringText: React.FC<{
  children: React.ReactNode;
  fromY?: number;
  delay?: number;
  style?: React.CSSProperties;
  className?: string;
}> = ({children, fromY = 60, delay = 0, style, className}) => {
  const frame = useCurrentFrame();

  const spr = spring({
    frame: frame - delay,
    fps,
    config: {
      damping: 12,
      stiffness: 180,
      mass: 0.8,
    },
  });

  const opacity = interpolate(frame, [delay, delay + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      className={className}
      style={{
        transform: `translateY(${fromY * (1 - spr)}px)`,
        opacity,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// ------------------------------------------------------------------
// Utility: Glow Button with animated halo
// ------------------------------------------------------------------
const GlowButton: React.FC<{
  text: string;
  delay?: number;
}> = ({text, delay = 0}) => {
  const frame = useCurrentFrame();

  const spr = spring({
    frame: frame - delay,
    fps,
    config: {damping: 10, stiffness: 200, mass: 0.9},
  });

  const scale = interpolate(spr, [0, 1], [0.7, 1]);
  const opacity = interpolate(frame, [delay, delay + 6], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const pulse = interpolate(
    frame,
    [delay + 20, delay + 30, delay + 40],
    [1, 1.08, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 70,
        left: '50%',
        transform: `translateX(-50%) scale(${scale * pulse})`,
        opacity,
        zIndex: 10,
      }}
    >
      <div
        style={{
          background: `linear-gradient(135deg, ${palette.blue} 0%, #00C6FF 100%)`,
          color: '#FFFFFF',
          padding: '20px 56px',
          borderRadius: 100,
          fontFamily: interFontFamily,
          fontSize: 26,
          fontWeight: 700,
          letterSpacing: '0.02em',
          textAlign: 'center',
          whiteSpace: 'nowrap',
          boxShadow: `0 0 40px ${palette.blue}66, 0 8px 32px rgba(0,0,0,0.3)`,
          textShadow: '0 2px 8px rgba(0,0,0,0.2)',
        }}
      >
        {text}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------
// Utility: Gradient Vignette — draws eye to center
// ------------------------------------------------------------------
const Vignette: React.FC<{opacity?: number}> = ({opacity = 0.6}) => (
  <div
    style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      background: `radial-gradient(ellipse at center, transparent 30%, ${palette.ink}${Math.round(opacity * 255).toString(16).padStart(2, '0')} 100%)`,
      pointerEvents: 'none',
      zIndex: 2,
    }}
  />
);

// ------------------------------------------------------------------
// Utility: Particle Overlay (subtle floating dots)
// ------------------------------------------------------------------
const Particles: React.FC<{count?: number}> = ({count = 12}) => {
  const frame = useCurrentFrame();

  const particles = Array.from({length: count}).map((_, i) => {
    const x = ((i * 137.5) % 100); // golden angle distribution
    const y = ((i * 73.3) % 100);
    const size = 2 + (i % 4);
    const speed = 0.3 + (i % 3) * 0.2;
    const offsetY = ((frame * speed) % 100);
    const opacity = 0.15 + (i % 5) * 0.05;

    return (
      <div
        key={i}
        style={{
          position: 'absolute',
          left: `${x}%`,
          top: `${(y + offsetY) % 100}%`,
          width: size,
          height: size,
          borderRadius: '50%',
          background: palette.blue,
          opacity,
          boxShadow: `0 0 ${size * 3}px ${palette.blue}`,
        }}
      />
    );
  });

  return (
    <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', overflow: 'hidden', zIndex: 3, pointerEvents: 'none'}}>
      {particles}
    </div>
  );
};

// ------------------------------------------------------------------
// Utility: Zoom Blur Flash — quick zoom into scene
// ------------------------------------------------------------------
const ZoomBlurIn: React.FC<{
  children: React.ReactNode;
  duration?: number;
}> = ({children, duration = 15}) => {
  const frame = useCurrentFrame();

  const scale = interpolate(frame, [0, duration], [1.4, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const blur = interpolate(frame, [0, duration], [8, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const opacity = interpolate(frame, [0, duration * 0.6], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        filter: `blur(${blur}px)`,
        opacity,
        width: '100%',
        height: '100%',
      }}
    >
      {children}
    </div>
  );
};

// ------------------------------------------------------------------
// Main Announcement Video with Viral Motion
// ------------------------------------------------------------------
export const AnnouncementVideo: React.FC<AnnouncementVideoProps> = ({
  kicker,
  title,
  benefit,
  cta,
  imageUrl,
  durationInSeconds = 15,
}) => {
  const {width, height} = useVideoConfig();
  const totalFrames = durationInSeconds * fps;

  // Scene timing (aggressive cuts for viral feel)
  const scene1 = Math.round(totalFrames * 0.25);  // Hook with image
  const scene2 = Math.round(totalFrames * 0.30);  // Feature reveal
  const scene3 = Math.round(totalFrames * 0.25);  // CTA momentum
  const scene4 = totalFrames - scene1 - scene2 - scene3; // Final punch

  // Resolve image
  const resolvedImage = imageUrl
    ? imageUrl.startsWith('http')
      ? imageUrl
      : staticFile(imageUrl)
    : null;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: palette.ink,
        width,
        height,
        overflow: 'hidden',
      }}
    >
      {/* ═══════════════════════════════════════════
          SCENE 1: ZOOM BLUR HOOK (0-25%)
          Hard cut with zoom blur — instant attention
         ═══════════════════════════════════════════ */}
      <Sequence from={0} durationInFrames={scene1}>
        <ZoomBlurIn duration={12}>
          <AbsoluteFill>
            {/* Screenshot with Ken Burns zoom */}
            {resolvedImage && (
              <KenBurnsImage
                src={resolvedImage}
                startScale={1.0}
                endScale={1.2}
                startX={0}
                endX={-30}
                startY={0}
                endY={-15}
              />
            )}

            {/* Dark overlay for text */}
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                width: '100%',
                height: '65%',
                background: `linear-gradient(to top, ${palette.ink} 0%, ${palette.ink}dd 40%, transparent 100%)`,
                zIndex: 4,
              }}
            />

            <Vignette opacity={0.4} />
            <Particles count={8} />

            {/* Text content */}
            <div
              style={{
                position: 'absolute',
                bottom: 140,
                left: 0,
                width: '100%',
                padding: '0 50px',
                display: 'flex',
                flexDirection: 'column',
                gap: 12,
                zIndex: 5,
              }}
            >
              <SpringText fromY={30} delay={5}>
                <div
                  style={{
                    fontFamily: interFontFamily,
                    fontSize: 16,
                    fontWeight: 600,
                    letterSpacing: '0.2em',
                    textTransform: 'uppercase',
                    color: palette.blue,
                  }}
                >
                  {kicker}
                </div>
              </SpringText>

              <SpringText fromY={50} delay={8}>
                <div
                  style={{
                    fontFamily: interFontFamily,
                    fontSize: 54,
                    fontWeight: 800,
                    lineHeight: 1.08,
                    color: '#FFFFFF',
                    letterSpacing: '-0.03em',
                    textShadow: '0 4px 20px rgba(0,0,0,0.4)',
                  }}
                >
                  {title}
                </div>
              </SpringText>
            </div>
          </AbsoluteFill>
        </ZoomBlurIn>
      </Sequence>

      {/* ═══════════════════════════════════════════
          SCENE 2: PERSPECTIVE TILT (25-55%)
          3D rotate reveal — "this is different"
         ═══════════════════════════════════════════ */}
      <Sequence from={scene1} durationInFrames={scene2}>
        <AbsoluteFill>
          {resolvedImage && (
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                perspective: 1200,
              }}
            >
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  transform: `rotateY(${interpolate(useCurrentFrame(), [scene1, scene1 + 20], [15, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}deg) rotateX(${interpolate(useCurrentFrame(), [scene1, scene1 + 20], [-5, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}deg) scale(${interpolate(useCurrentFrame(), [scene1, scene1 + 30], [0.9, 1.05], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})})`,
                  transformOrigin: 'center center',
                  transition: 'none',
                }}
              >
                <Img
                  src={resolvedImage}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    objectPosition: 'center top',
                  }}
                />
              </div>
            </div>
          )}

          {/* Radial glow behind text */}
          <div
            style={{
              position: 'absolute',
              bottom: 100,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 600,
              height: 300,
              background: `radial-gradient(ellipse, ${palette.blue}33 0%, transparent 70%)`,
              zIndex: 3,
            }}
          />

          <div
            style={{
              position: 'absolute',
              bottom: 120,
              left: 0,
              width: '100%',
              padding: '0 50px',
              display: 'flex',
              flexDirection: 'column',
              gap: 16,
              zIndex: 5,
              alignItems: 'center',
              textAlign: 'center',
            }}
          >
            <SpringText fromY={40} delay={scene1 + 3}>
              <div
                style={{
                  fontFamily: interFontFamily,
                  fontSize: 32,
                  fontWeight: 500,
                  lineHeight: 1.3,
                  color: '#FFFFFFdd',
                  maxWidth: '80%',
                }}
              >
                {benefit}
              </div>
            </SpringText>
          </div>

          <Vignette opacity={0.5} />
        </AbsoluteFill>
      </Sequence>

      {/* ═══════════════════════════════════════════
          SCENE 3: FAST ZOOM CTA (55-80%)
          Momentum build — quick zoom into action
         ═══════════════════════════════════════════ */}
      <Sequence from={scene1 + scene2} durationInFrames={scene3}>
        <AbsoluteFill>
          {/* Fast zoom background */}
          {resolvedImage && (
            <div
              style={{
                position: 'absolute',
                top: -100,
                left: -100,
                width: 'calc(100% + 200px)',
                height: 'calc(100% + 200px)',
                transform: `scale(${interpolate(useCurrentFrame(), [scene1 + scene2, scene1 + scene2 + 15], [1.3, 1.0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})})`,
                opacity: interpolate(useCurrentFrame(), [scene1 + scene2, scene1 + scene2 + 10], [0.3, 0.6], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
              }}
            >
              <Img
                src={resolvedImage}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  filter: 'blur(2px)',
                }}
              />
            </div>
          )}

          {/* Dark overlay */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              background: `linear-gradient(180deg, transparent 0%, ${palette.ink}aa 50%, ${palette.ink} 100%)`,
              zIndex: 2,
            }}
          />

          <Vignette opacity={0.6} />
          <Particles count={6} />

          {/* CTA */}
          <GlowButton text={cta} delay={scene1 + scene2 + 5} />
        </AbsoluteFill>
      </Sequence>

      {/* ═══════════════════════════════════════════
          SCENE 4: FINAL PUNCH (80-100%)
          Black screen with bold text — brand imprint
         ═══════════════════════════════════════════ */}
      <Sequence from={scene1 + scene2 + scene3} durationInFrames={scene4}>
        <AbsoluteFill
          style={{
            background: palette.ink,
            justifyContent: 'center',
            alignItems: 'center',
            gap: 20,
          }}
        >
          <SpringText fromY={30} delay={scene1 + scene2 + scene3 + 2}>
            <div
              style={{
                fontFamily: interFontFamily,
                fontSize: 22,
                fontWeight: 600,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: palette.blue,
              }}
            >
              {kicker}
            </div>
          </SpringText>

          <SpringText fromY={60} delay={scene1 + scene2 + scene3 + 5}>
            <div
              style={{
                fontFamily: interFontFamily,
                fontSize: 64,
                fontWeight: 800,
                lineHeight: 1.05,
                color: '#FFFFFF',
                letterSpacing: '-0.03em',
                textAlign: 'center',
                maxWidth: '85%',
              }}
            >
              {title}
            </div>
          </SpringText>

          <div
            style={{
              width: 80,
              height: 4,
              background: `linear-gradient(90deg, ${palette.blue}, transparent)`,
              marginTop: 10,
            }}
          />

          <Particles count={10} />
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

export const defaultAnnouncementProps: AnnouncementVideoProps = {
  kicker: 'Product Update',
  title: 'AI Follow-Ups, Now in Real Time',
  benefit: 'Never lose high-intent leads between inquiry and call.',
  cta: 'Turn it on today.',
  imageUrl: undefined,
  durationInSeconds: 15,
};

export const announcementDurationInFrames = 450;
