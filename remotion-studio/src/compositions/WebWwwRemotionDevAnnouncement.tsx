import React from 'react';
import {AnnouncementVideo, type AnnouncementVideoProps} from './AnnouncementVideo';

const generatedProps: AnnouncementVideoProps = {
  "kicker": "WWW REMOTION DEV",
  "title": "Make videos programmatically.",
  "benefit": "Visit www.remotion.dev",
  "cta": "Learn Remotion"
};

export const WebWwwRemotionDevAnnouncement: React.FC = () => <AnnouncementVideo {...generatedProps} />;
