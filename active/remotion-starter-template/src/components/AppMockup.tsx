// components/AppMockup.tsx — Realistic product interface mockup
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

interface AppMockupProps {
  color: string;
  delay?: number;
}

export const AppMockup: React.FC<AppMockupProps> = ({ color, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = frame - delay;

  // Content reveal with spring
  const contentReveal = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 20, stiffness: 100 },
    delay: 40,
  });

  // Card staggered reveal
  const card1Reveal = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 18, stiffness: 90 },
    delay: 50,
  });

  const card2Reveal = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 18, stiffness: 90 },
    delay: 60,
  });

  const card3Reveal = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 18, stiffness: 90 },
    delay: 70,
  });

  // Subtle floating animation for cards
  const floatY1 = interpolate(
    adjustedFrame,
    [0, fps * 2],
    [0, -4],
    { extrapolateRight: "clamp" }
  );
  const floatY2 = interpolate(
    adjustedFrame,
    [0, fps * 2],
    [0, -6],
    { extrapolateRight: "clamp" }
  );
  const floatY3 = interpolate(
    adjustedFrame,
    [0, fps * 2],
    [0, -2],
    { extrapolateRight: "clamp" }
  );

  return (
    <div
      className="w-full h-full flex flex-col p-8"
      style={{
        opacity: contentReveal,
        transform: `translateY(${(1 - contentReveal) * 30}px)`,
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Navigation bar — realistic */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center shadow-sm"
            style={{
              background: `linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`,
            }}
          >
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-sm text-gray-900">Dashboard</span>
            <span className="text-xs text-gray-400">Pro Plan</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-32 h-9 rounded-full bg-gray-50 border border-gray-200 flex items-center px-3 gap-2">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span className="text-xs text-gray-400">Search...</span>
          </div>
          <div className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center">
            <div className="w-5 h-5 rounded-full bg-gradient-to-br from-gray-300 to-gray-400" />
          </div>
        </div>
      </div>

      {/* Hero section — realistic typography hierarchy */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-2 h-2 rounded-full" style={{ background: color }} />
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Overview</span>
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2 tracking-tight">
          Welcome back
        </h2>
        <p className="text-sm text-gray-500">
          Here's what's happening with your projects today.
        </p>
      </div>

      {/* Stats row — realistic cards */}
      <div className="flex gap-3 mb-6">
        {[
          { label: "Total Revenue", value: "$48,250", change: "+12.5%", positive: true },
          { label: "Active Users", value: "2,420", change: "+8.2%", positive: true },
          { label: "Conversion", value: "3.24%", change: "-2.1%", positive: false },
        ].map((stat, i) => (
          <div
            key={i}
            className="flex-1 rounded-xl p-4 border"
            style={{
              background: "rgba(255, 255, 255, 0.8)",
              borderColor: "rgba(0, 0, 0, 0.06)",
              boxShadow: "0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.02)",
            }}
          >
            <p className="text-xs text-gray-500 mb-1">{stat.label}</p>
            <div className="flex items-end gap-2">
              <span className="text-xl font-bold text-gray-900">{stat.value}</span>
              <span className={`text-xs font-medium ${stat.positive ? 'text-green-600' : 'text-red-500'}`}>
                {stat.change}
              </span>
            </div>
            {/* Mini chart bar */}
            <div className="flex gap-0.5 mt-3">
              {[40, 65, 45, 80, 55, 70, 90].map((h, j) => (
                <div
                  key={j}
                  className="flex-1 rounded-sm"
                  style={{
                    height: `${h * 0.25}px`,
                    background: j === 6 ? color : 'rgba(0,0,0,0.08)',
                    opacity: 0.6 + (j * 0.05),
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Feature cards — glassmorphism with real content */}
      <div className="flex gap-4">
        {[
          {
            title: "AI Automation",
            desc: "Smart workflows that adapt to your business",
            icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
          },
          {
            title: "Analytics",
            desc: "Real-time insights into customer behavior",
            icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
          },
          {
            title: "Integrations",
            desc: "Connect with your favorite tools instantly",
            icon: "M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z",
          },
        ].map((feature, i) => {
          const reveal = [card1Reveal, card2Reveal, card3Reveal][i];
          const floatY = [floatY1, floatY2, floatY3][i];
          return (
            <div
              key={i}
              className="flex-1 rounded-xl p-5 border relative overflow-hidden"
              style={{
                opacity: reveal,
                transform: `translateY(${(1 - reveal) * 20 + floatY}px)`,
                background: "rgba(255, 255, 255, 0.7)",
                borderColor: "rgba(0, 0, 0, 0.06)",
                boxShadow: "0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03)",
              }}
            >
              {/* Subtle gradient overlay */}
              <div
                className="absolute inset-0 opacity-30"
                style={{
                  background: `linear-gradient(135deg, ${color}08 0%, transparent 50%)`,
                }}
              />
              <div className="relative z-10">
                <div
                  className="w-10 h-10 rounded-lg mb-4 flex items-center justify-center"
                  style={{ background: `${color}15` }}
                >
                  <svg className="w-5 h-5" style={{ color }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={feature.icon} />
                  </svg>
                </div>
                <h3 className="font-semibold text-sm text-gray-900 mb-1">{feature.title}</h3>
                <p className="text-xs text-gray-500 leading-relaxed">{feature.desc}</p>
                {/* Fake button */}
                <div className="mt-4 flex items-center gap-1">
                  <span className="text-xs font-medium" style={{ color }}>Learn more</span>
                  <svg className="w-3 h-3" style={{ color }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
