// Master.tsx — Master composition with staggered scene timing
import { AbsoluteFill } from "remotion";
import { SizzleTransition } from "./components/SizzleTransition";
import { WebAppScene } from "./components/WebAppScene";

export const Master: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#0a0a0f]">
      <SizzleTransition
        transitionType="fade"
        durationInFrames={30}
        sceneDurationInFrames={180}
      >
        {/* Scene 1: Marvelus.cc */}
        <WebAppScene
          appName="Marvelus"
          appUrl="marvelus.cc"
          searchQuery="AI voice agents for small business"
          tagline="AI that answers your calls"
          color="#6366f1"
          startFrame={0}
          sceneDuration={180}
        />

        {/* Scene 2: Nolostsales.cc */}
        <WebAppScene
          appName="Nolostsales"
          appUrl="nolostsales.cc"
          searchQuery="recover lost sales with AI"
          tagline="Never lose another lead"
          color="#10b981"
          startFrame={0}
          sceneDuration={180}
        />

        {/* Scene 3: Generic SaaS */}
        <WebAppScene
          appName="Your SaaS"
          appUrl="yoursaas.io"
          searchQuery="modern web application platform"
          tagline="Build faster, ship smarter"
          color="#f59e0b"
          startFrame={0}
          sceneDuration={180}
        />
      </SizzleTransition>
    </AbsoluteFill>
  );
};
