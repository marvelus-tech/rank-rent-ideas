// components/BrowserWindow.tsx — Glassmorphism browser frame
import { useCurrentFrame, interpolate } from "remotion";
import { ReactNode } from "react";

interface BrowserWindowProps {
  children: ReactNode;
  url?: string;
  title?: string;
  color?: string;
}

export const BrowserWindow: React.FC<BrowserWindowProps> = ({
  children,
  url = "app.example.com",
  title = "Web Application",
  color = "#6366f1",
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scaleY = interpolate(
    frame,
    [0, 25],
    [0.85, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      className="w-full h-full flex flex-col rounded-2xl overflow-hidden"
      style={{
        opacity,
        transform: `scaleY(${scaleY})`,
        background: "rgba(255, 255, 255, 0.85)",
        backdropFilter: "blur(20px) saturate(180%)",
        border: "1px solid rgba(255, 255, 255, 0.3)",
        boxShadow: `
          0 1px 2px rgba(0,0,0,0.02),
          0 4px 8px rgba(0,0,0,0.03),
          0 12px 24px rgba(0,0,0,0.05),
          0 24px 48px rgba(0,0,0,0.06),
          0 0 0 1px rgba(0,0,0,0.04)
        `,
      }}
    >
      {/* Browser chrome */}
      <div
        className="h-12 flex items-center px-4 gap-3"
        style={{
          background: "rgba(255, 255, 255, 0.6)",
          borderBottom: "1px solid rgba(0,0,0,0.06)",
          backdropFilter: "blur(10px)",
        }}
      >
        {/* Traffic lights with inner glow */}
        <div className="flex gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{
              background: "#ff5f57",
              boxShadow: "inset 0 0 0 0.5px rgba(0,0,0,0.1)",
            }}
          />
          <div
            className="w-3 h-3 rounded-full"
            style={{
              background: "#febc2e",
              boxShadow: "inset 0 0 0 0.5px rgba(0,0,0,0.1)",
            }}
          />
          <div
            className="w-3 h-3 rounded-full"
            style={{
              background: "#28c840",
              boxShadow: "inset 0 0 0 0.5px rgba(0,0,0,0.1)",
            }}
          />
        </div>

        {/* URL bar — glassmorphism */}
        <div
          className="flex-1 h-8 rounded-lg flex items-center px-3 gap-2"
          style={{
            background: "rgba(0, 0, 0, 0.04)",
            border: "1px solid rgba(0,0,0,0.06)",
          }}
        >
          <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <span className="text-sm text-gray-500 font-mono">{url}</span>
        </div>

        {/* Spacer for symmetry */}
        <div className="w-16" />
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-hidden relative bg-white">
        {children}
      </div>
    </div>
  );
};
