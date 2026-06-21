import React from 'react';
import {Promo3DVideo, type Promo3DVideoProps} from './Promo3DVideo';

const generatedProps: Promo3DVideoProps = {
  "kicker": "LUSTRE · SKIN",
  "title": "Skincare that truly understands you",
  "benefit": "Personalized skin wellness powered by science",
  "cta": "Start Your Journey",
  "imageUrl": "lustre-skin.png",
  "durationInSeconds": 15
};

export const Lustre3dViral: React.FC = () => <Promo3DVideo {...generatedProps} />;
