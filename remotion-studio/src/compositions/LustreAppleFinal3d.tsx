import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {interFontFamily} from '../design-system/typography';

const fps = 30;

export type LustreAppleFinal3dProps = {
  kicker: string;
  title: string;
  benefit: string;
  cta: string;
  imageUrl: string;
};

export const LustreAppleFinal3d: React.FC<LustreAppleFinal3dProps> = ({
  kicker,
  title,
  benefit,
  cta,
  imageUrl,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const entry = spring({
    frame: frame - 10,
    fps,
    config: {damping: 18, stiffness: 95, mass: 1.2},
  });

  const cardY = interpolate(entry, [0, 1], [220, 0]);
  const cardScale = interpolate(entry, [0, 1], [0.88, 1]);
  const cardRotateY = interpolate(frame, [0, 450], [-7, 7]);
  const cardRotateX = interpolate(frame, [0, 450], [1.8, -1.2]);

  const scrollStart = 120;
  const scrollEnd = 280;
  const subtleScroll = interpolate(frame, [scrollStart, scrollEnd], [90, 320], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const textIn = spring({frame: frame - 26, fps, config: {damping: 14, stiffness: 140}});
  const ctaIn = spring({frame: frame - 120, fps, config: {damping: 12, stiffness: 170}});

  const pulse = 1 + (Math.sin((frame - 120) * 0.09) * 0.5 + 0.5) * 0.025;

  return (
    <AbsoluteFill style={{background: '#f5f6f8', width, height}}>
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(1200px 780px at 50% 18%, #ffffff 0%, #f1f3f6 44%, #e8ecf1 100%)',
        }}
      />

      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'linear-gradient(180deg, rgba(255,255,255,0.44) 0%, rgba(255,255,255,0) 25%, rgba(19,24,35,0.03) 100%)',
        }}
      />

      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '55%',
          width: 900,
          height: 620,
          transform: `translate(-50%, -50%) translateY(${cardY}px) perspective(1800px) rotateX(${cardRotateX}deg) rotateY(${cardRotateY}deg) scale(${cardScale})`,
          transformStyle: 'preserve-3d',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 34,
            background: 'linear-gradient(160deg, #dfe3e8 0%, #b9c0ca 46%, #a8afb8 100%)',
            boxShadow: '0 50px 90px rgba(20,27,37,0.18), 0 18px 36px rgba(20,27,37,0.13), inset 0 1px 0 rgba(255,255,255,0.6)',
            padding: 14,
          }}
        >
          <div
            style={{
              width: '100%',
              height: '100%',
              borderRadius: 24,
              background: '#040404',
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            <Img
              src={staticFile(imageUrl)}
              style={{
                width: '100%',
                height: 'auto',
                transform: `translateY(-${subtleScroll}px)`,
                transformOrigin: 'top center',
              }}
            />
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background:
                  'linear-gradient(180deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.02) 34%, rgba(255,255,255,0) 58%, rgba(255,255,255,0.06) 100%)',
              }}
            />
          </div>
        </div>

        <div
          style={{
            position: 'absolute',
            left: '8%',
            right: '8%',
            bottom: -44,
            height: 52,
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(17,24,39,0.24) 0%, rgba(17,24,39,0.02) 72%)',
            filter: 'blur(9px)',
          }}
        />
      </div>

      <div
        style={{
          position: 'absolute',
          inset: 0,
          padding: '78px 66px 90px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          pointerEvents: 'none',
        }}
      >
        <div
          style={{
            opacity: interpolate(frame, [18, 42], [0, 1], {extrapolateLeft: 'clamp'}),
            transform: `translateY(${(1 - textIn) * 24}px)`,
          }}
        >
          <div
            style={{
              fontFamily: interFontFamily,
              fontSize: 15,
              letterSpacing: '0.22em',
              fontWeight: 600,
              textTransform: 'uppercase',
              color: '#6b7280',
              marginBottom: 14,
            }}
          >
            {kicker}
          </div>

          <div
            style={{
              fontFamily: interFontFamily,
              fontSize: 58,
              fontWeight: 800,
              lineHeight: 1.08,
              letterSpacing: '-0.03em',
              color: '#17181b',
              maxWidth: '92%',
            }}
          >
            {title}
          </div>

          <div
            style={{
              marginTop: 14,
              fontFamily: interFontFamily,
              fontSize: 24,
              lineHeight: 1.35,
              color: '#5d6470',
              maxWidth: '80%',
              fontWeight: 500,
            }}
          >
            {benefit}
          </div>
        </div>

        <div style={{display: 'flex', justifyContent: 'center'}}>
          <div
            style={{
              opacity: interpolate(frame, [108, 132], [0, 1], {extrapolateLeft: 'clamp'}),
              transform: `scale(${ctaIn * pulse})`,
              background: '#0071e3',
              color: '#fff',
              padding: '18px 44px',
              borderRadius: 999,
              fontFamily: interFontFamily,
              fontSize: 24,
              fontWeight: 700,
              letterSpacing: '-0.01em',
              boxShadow: '0 14px 32px rgba(0,113,227,0.33)',
            }}
          >
            {cta}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const defaultLustreAppleFinal3dProps: LustreAppleFinal3dProps = {
  kicker: 'LUSTRE · SKIN',
  title: 'Skincare that truly understands you',
  benefit: 'Personalized skin wellness powered by science',
  cta: 'Start Your Journey',
  imageUrl: 'lustre-skin-fullpage.png',
};

export const lustreAppleFinal3dDurationInFrames = 450;
