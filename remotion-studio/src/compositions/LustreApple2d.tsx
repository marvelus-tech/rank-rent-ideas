import React from 'react';
import {AppleStyleVideo, type AppleStyleVideoProps} from './AppleStyleVideo';

const generatedProps: AppleStyleVideoProps = {
  "kicker": "LUSTRE · SKIN",
  "title": "Skincare that truly understands you",
  "benefit": "Personalized skin wellness powered by science",
  "cta": "Start Your Journey",
  "imageUrl": "lustre-skin-v2.png",
  "durationInSeconds": 15,
  "logoText": "LUSTRE"
};

export const LustreApple2d: React.FC = () => <AppleStyleVideo {...generatedProps} />;
