// components/WebAppScene.tsx — World-class webapp showcase
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { SearchField } from "./SearchField";
import { BrowserWindow } from "./BrowserWindow";
import { AppMockup } from "./AppMockup";

interface WebAppSceneProps {
  appName: string;
  appUrl: string;
  searchQuery: string;
  tagline?: string;
  color?: string;
  startFrame?: number;
  sceneDuration?: number;
}

export const WebAppScene: React.FC<WebAppSceneProps> = ({
  appName,
  appUrl,
  searchQuery,
  tagline = "The future of work",
  color = "#6366f1",
  startFrame = 0,
  sceneDuration = 180,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const adjustedFrame = frame - startFrame;
  const progress = adjustedFrame / sceneDuration;

  // === SPRING ANIMATIONS (organic, not linear) ===

  // Search field entrance — spring pop
  const searchScale = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 15, stiffness: 150 },
    delay: 0,
  });

  const searchOpacity = interpolate(
    adjustedFrame,
    [0, 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // App name — delayed reveal with spring
  const nameScale = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 12, stiffness: 100 },
    delay: 45, // 1.5s delay
  });

  const nameOpacity = interpolate(
    adjustedFrame,
    [30, 50],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Tagline — fade in after name
  const taglineY = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 20, stiffness: 120 },
    delay: 60,
  });

  const taglineOpacity = interpolate(
    adjustedFrame,
    [55, 75],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Browser window — dramatic slide up with spring
  const browserY = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 14, stiffness: 80 },
    delay: 80,
  });

  const browserOpacity = interpolate(
    adjustedFrame,
    [75, 95],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Background gradient shift
  const bgShift = interpolate(
    adjustedFrame,
    [0, sceneDuration],
    [0, 30],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Ambient glow pulse
  const glowOpacity = interpolate(
    adjustedFrame % (fps * 2),
    [0, fps, fps * 2],
    [0.3, 0.6, 0.3],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      className="flex flex-col items-center justify-center"
      style={{
        background: `linear-gradient(${135 + bgShift}deg, ${color}08 0%, #0a0a0f 50%, ${color}12 100%)`,
        overflow: "hidden",
      }}
    >
      {/* Ambient glow orbs */}
      <div
        className="absolute rounded-full blur-3xl"
        style={{
          width: 600,
          height: 600,
          background: `radial-gradient(circle, ${color}30 0%, transparent 70%)`,
          top: -200,
          left: -100,
          opacity: glowOpacity,
        }}
      />
      <div
        className="absolute rounded-full blur-3xl"
        style={{
          width: 500,
          height: 500,
          background: `radial-gradient(circle, ${color}20 0%, transparent 70%)`,
          bottom: -150,
          right: -100,
          opacity: glowOpacity,
        }}
      />

      {/* Floating particles */}
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="absolute rounded-full"
          style={{
            width: 2 + i * 1.5,
            height: 2 + i * 1.5,
            background: `${color}${40 + i * 10}`,
            left: `${15 + i * 15}%`,
            top: `${20 + (i % 3) * 25}%`,
            opacity: interpolate(
              (adjustedFrame + i * 30) % (fps * 3),
              [0, fps * 1.5, fps * 3],
              [0.1, 0.5, 0.1]
            ),
            transform: `translateY(${interpolate(
              adjustedFrame,
              [0, sceneDuration],
              [0, -30 + i * 10]
            )}px)`,
          }}
        />
      ))}

      {/* Content container */}
      <div className="relative z-10 flex flex-col items-center w-full max-w-6xl px-12">
        {/* App name + tagline */}
        <div
          className="text-center mb-10"
          style={{
            opacity: nameOpacity,
            transform: `scale(${nameScale})`,
          }}
        >
          <h1
            className="text-7xl font-bold tracking-tight mb-4"
            style={{
              color: "#ffffff",
              textShadow: `0 0 80px ${color}40`,
              fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
              letterSpacing: "-0.02em",
            }}
          >
            {appName}
          </h1>
          <p
            className="text-2xl font-light"
            style={{
              opacity: taglineOpacity,
              transform: `translateY(${(1 - taglineY) * 20}px)`,
              color: "#a0a0b0",
              fontFamily: "'Inter', system-ui, sans-serif",
            }}
          >
            {tagline}
          </p>
        </div>

        {/* Search field */}
        <div
          className="w-full max-w-2xl mb-8"
          style={{
            opacity: searchOpacity,
            transform: `scale(${searchScale})`,
          }}
        >
          <SearchField
            query={searchQuery}
            startFrame={startFrame}
            charsPerSecond={25}
            color={color}
          />
        </div>

        {/* Browser window */}
        <div
          className="w-full max-w-5xl"
          style={{
            opacity: browserOpacity,
            transform: `translateY(${(1 - browserY) * 100}px)`,
          }}
        >
          <BrowserWindow url={appUrl} color={color}>
            <AppMockup color={color} delay={startFrame} />
          </BrowserWindow>
        </div>
      </div>
    </AbsoluteFill>
  );
};


