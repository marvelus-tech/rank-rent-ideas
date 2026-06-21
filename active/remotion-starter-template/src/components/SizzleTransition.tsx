// components/SizzleTransition.tsx — Professional scene transitions
import { ReactNode } from "react";
import {
  TransitionSeries,
  linearTiming,
  springTiming,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { flip } from "@remotion/transitions/flip";
import { clockWipe } from "@remotion/transitions/clock-wipe";

type TransitionType = "fade" | "slide-left" | "slide-right" | "slide-up" | "slide-down" | "wipe" | "flip" | "clock";

interface SizzleTransitionProps {
  children: ReactNode[];
  transitionType?: TransitionType;
  durationInFrames?: number;
  sceneDurationInFrames?: number;
}

export const SizzleTransition: React.FC<SizzleTransitionProps> = ({
  children,
  transitionType = "fade",
  durationInFrames = 30,
  sceneDurationInFrames = 180,
}) => {
  const getPresentation = (type: TransitionType) => {
    switch (type) {
      case "fade": return fade();
      case "slide-left": return slide({ direction: "from-right" });
      case "slide-right": return slide({ direction: "from-left" });
      case "slide-up": return slide({ direction: "from-bottom" });
      case "slide-down": return slide({ direction: "from-top" });
      case "wipe": return wipe();
      case "flip": return flip();
      case "clock": return clockWipe();
      default: return fade();
    }
  };

  const presentation = getPresentation(transitionType);
  const timing = springTiming({
    config: { damping: 200, stiffness: 100 },
    durationInFrames,
  });

  return (
    <TransitionSeries>
      {children.map((child, index) => (
        <React.Fragment key={index}>
          <TransitionSeries.Sequence durationInFrames={sceneDurationInFrames}>
            {child}
          </TransitionSeries.Sequence>
          {index < children.length - 1 && (
            <TransitionSeries.Transition
              presentation={presentation}
              timing={timing}
            />
          )}
        </React.Fragment>
      ))}
    </TransitionSeries>
  );
};

// Pre-configured presets
export const FadeTransition: React.FC<{ children: ReactNode[]; sceneDuration?: number }> = ({
  children, sceneDuration = 180,
}) => <SizzleTransition transitionType="fade" sceneDurationInFrames={sceneDuration}>{children}</SizzleTransition>;

export const SlideLeftTransition: React.FC<{ children: ReactNode[]; sceneDuration?: number }> = ({
  children, sceneDuration = 180,
}) => <SizzleTransition transitionType="slide-left" sceneDurationInFrames={sceneDuration}>{children}</SizzleTransition>;

export const WipeTransition: React.FC<{ children: ReactNode[]; sceneDuration?: number }> = ({
  children, sceneDuration = 180,
}) => <SizzleTransition transitionType="wipe" sceneDurationInFrames={sceneDuration}>{children}</SizzleTransition>;
