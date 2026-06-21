// Root.tsx — Entry point with composition presets
import "./index.css";
import { Composition } from "remotion";
import { Master } from "./Master";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 1080p horizontal — YouTube, presentations */}
      <Composition
        id="WebAppShowcase"
        component={Master}
        durationInFrames={510} // 3 scenes × 180 - 2 transitions × 30 = 510
        fps={30}
        width={1920}
        height={1080}
      />

      {/* Vertical — TikTok, Reels, Shorts */}
      <Composition
        id="WebAppVertical"
        component={Master}
        durationInFrames={510}
        fps={30}
        width={1080}
        height={1920}
      />

      {/* Square — Instagram, Twitter */}
      <Composition
        id="WebAppSquare"
        component={Master}
        durationInFrames={510}
        fps={30}
        width={1080}
        height={1080}
      />
    </>
  );
};
