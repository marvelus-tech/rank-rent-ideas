// components/MacTerminal.tsx - macOS terminal window with traffic lights
import { AbsoluteFill } from "remotion";
import { TerminalContent } from "./TerminalContent";

export const MacTerminal: React.FC = () => {
  return (
    <AbsoluteFill className="p-8">
      <div className="w-full h-full flex flex-col rounded-xl overflow-hidden shadow-2xl">
        {/* Title bar */}
        <div className="h-14 bg-[#f6f6f6] flex items-center px-5 border-b border-[#e0e0e0]">
          {/* Traffic lights */}
          <div className="flex gap-2.5">
            <div className="w-4 h-4 rounded-full bg-[#ff5f57]" />
            <div className="w-4 h-4 rounded-full bg-[#febc2e]" />
            <div className="w-4 h-4 rounded-full bg-[#28c840]" />
          </div>
          {/* Title */}
          <div className="flex-1 text-center">
            <span className="text-[#4d4d4d] text-base font-medium">Terminal</span>
          </div>
          {/* Spacer for symmetry */}
          <div className="w-16" />
        </div>

        {/* Content area */}
        <TerminalContent />
      </div>
    </AbsoluteFill>
  );
};
