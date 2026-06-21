// components/TerminalContent.tsx - Typewriter text animation
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Cursor } from "./Cursor";

interface TerminalContentProps {
  command?: string;
  charsPerSecond?: number;
  prompt?: string;
}

export const TerminalContent: React.FC<TerminalContentProps> = ({
  command = "npx create-video@latest my-video",
  charsPerSecond = 15,
  prompt = "~",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const framesPerChar = fps / charsPerSecond;
  const visibleChars = Math.floor(frame / framesPerChar);
  const displayedText = command.slice(0, Math.min(visibleChars, command.length));
  const isTyping = visibleChars < command.length;

  return (
    <div className="flex-1 bg-white p-6 font-mono text-4xl">
      <div className="flex items-center text-[#333]">
        <span className="text-[#2ecc71] font-semibold">{prompt}</span>
        <span className="text-[#333] mx-2">$</span>
        <span>{displayedText}</span>
        <Cursor blinking={!isTyping} />
      </div>
    </div>
  );
};
