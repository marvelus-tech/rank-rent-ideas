// hooks/useTypewriter.ts - Reusable typewriter animation hook
import { useCurrentFrame, useVideoConfig } from "remotion";

interface UseTypewriterProps {
  text: string;
  charsPerSecond?: number;
  startFrame?: number;
}

export const useTypewriter = ({
  text,
  charsPerSecond = 15,
  startFrame = 0,
}: UseTypewriterProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const framesPerChar = fps / charsPerSecond;
  const adjustedFrame = Math.max(0, frame - startFrame);

  const visibleChars = Math.floor(adjustedFrame / framesPerChar);
  const displayedText = text.slice(0, Math.min(visibleChars, text.length));
  const isTyping = visibleChars < text.length;
  const isComplete = visibleChars >= text.length;

  return { displayedText, isTyping, isComplete, visibleChars };
};
