// components/SearchField.tsx — Animated search with glassmorphism
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { useTypewriter } from "../hooks/useTypewriter";
import { ReactNode } from "react";

interface SearchFieldProps {
  query: string;
  startFrame?: number;
  charsPerSecond?: number;
  color?: string;
}

export const SearchField: React.FC<SearchFieldProps> = ({
  query,
  startFrame = 0,
  charsPerSecond = 20,
  color = "#6366f1",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = frame - startFrame;

  // Container entrance — spring pop
  const containerScale = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 15, stiffness: 150 },
  });

  const containerOpacity = interpolate(
    adjustedFrame,
    [0, 12],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Typewriter effect
  const { displayedText, isComplete } = useTypewriter({
    text: query,
    charsPerSecond,
    startFrame: startFrame + 15,
  });

  // Cursor blink
  const blinkInterval = fps / 2;
  const cursorOpacity = isComplete
    ? interpolate(
        adjustedFrame % blinkInterval,
        [0, blinkInterval / 2, blinkInterval],
        [1, 0, 1]
      )
    : 1;

  return (
    <div
      className="w-full flex items-center rounded-2xl px-6 py-4 gap-4"
      style={{
        opacity: containerOpacity,
        transform: `scale(${containerScale})`,
        background: "rgba(255, 255, 255, 0.9)",
        backdropFilter: "blur(20px) saturate(180%)",
        border: "1px solid rgba(255, 255, 255, 0.4)",
        boxShadow: `
          0 1px 2px rgba(0,0,0,0.02),
          0 4px 12px rgba(0,0,0,0.04),
          0 12px 32px rgba(0,0,0,0.06),
          inset 0 1px 0 rgba(255,255,255,0.6)
        `,
      }}
    >
      {/* Search icon */}
      <svg
        className="w-6 h-6 flex-shrink-0"
        style={{ color: "#9ca3af" }}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>

      {/* Typed text */}
      <span
        className="text-2xl flex-1 font-light"
        style={{
          color: "#374151",
          fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
          letterSpacing: "-0.01em",
        }}
      >
        {displayedText}
      </span>

      {/* Blinking cursor */}
      <span
        className="w-0.5 h-8 inline-block rounded-full"
        style={{
          opacity: cursorOpacity,
          backgroundColor: color,
        }}
      />

      {/* Command/Enter hint */}
      <div
        className="flex items-center gap-1 px-2 py-1 rounded-md"
        style={{
          background: "rgba(0,0,0,0.04)",
          border: "1px solid rgba(0,0,0,0.06)",
        }}
      >
        <span className="text-xs text-gray-400 font-medium">⌘</span>
        <span className="text-xs text-gray-400 font-medium">K</span>
      </div>
    </div>
  );
};
