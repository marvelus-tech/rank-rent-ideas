// components/Cursor.tsx - Blinking cursor with smooth opacity
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";

interface CursorProps {
  blinking: boolean;
  color?: string;
}

export const Cursor: React.FC<CursorProps> = ({ blinking, color = "#3b82f6" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const blinkInterval = fps / 2; // Blink every 0.5 seconds

  const opacity = blinking
    ? interpolate(
        frame % blinkInterval,
        [0, blinkInterval / 2, blinkInterval],
        [1, 0, 1],
        { extrapolateRight: "clamp" }
      )
    : 1;

  return (
    <span
      className="w-0.5 h-8 inline-block ml-0.5"
      style={{ opacity, backgroundColor: color }}
    />
  );
};
