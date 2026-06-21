import React from 'react';
import {AnnouncementVideo, type AnnouncementVideoProps} from './AnnouncementVideo';

const generatedProps: AnnouncementVideoProps = {
  "kicker": "LUSTRE · SKIN",
  "title": "Skincare that truly understands you",
  "benefit": "Skincare that truly understands you · From questions to clarity",
  "cta": "Start Assessment",
  "imageUrl": "lustre-skin.png",
  "durationInSeconds": 15
};

export const WebLustreSkinAnnouncement: React.FC = () => <AnnouncementVideo {...generatedProps} />;
