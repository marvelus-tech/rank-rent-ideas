import React from 'react';
import {Composition, Folder} from 'remotion';
import {
  AnnouncementVideo,
  announcementDurationInFrames,
  defaultAnnouncementProps,
} from './compositions/AnnouncementVideo';
import {DataStoryVideo, dataStoryDurationInFrames, defaultDataStoryProps} from './compositions/DataStoryVideo';
import {
  defaultLeadReportProps,
  LeadReportVideo,
} from './compositions/LeadReportVideo';
import {LustreApple2d} from './compositions/LustreApple2d';
import {AppleStyleVideo, appleStyleDurationInFrames, defaultAppleStyleProps} from './compositions/AppleStyleVideo';
import {LustreAppleStyle} from './compositions/LustreAppleStyle';
import {LustrePro3dV5} from './compositions/LustrePro3dV5';
import {LustrePro3dV4} from './compositions/LustrePro3dV4';
import {LustrePro3dV3} from './compositions/LustrePro3dV3';
import {LustrePro3d} from './compositions/LustrePro3d';
import {Lustre3dViral} from './compositions/Lustre3dViral';
import {WebLustreSkinAnnouncement} from './compositions/WebLustreSkinAnnouncement';
import {WebWwwRemotionDevAnnouncement} from './compositions/WebWwwRemotionDevAnnouncement';
import {Promo3DVideo, promo3DDurationInFrames, defaultPromo3DProps} from './compositions/Promo3DVideo';
import {
  LustreAppleFinal3d,
  lustreAppleFinal3dDurationInFrames,
  defaultLustreAppleFinal3dProps,
} from './compositions/LustreAppleFinal3d';

// Platform format presets
export const FORMATS = {
  short: {width: 1080, height: 1920, name: 'TikTok / Reels / Shorts (9:16)'},
  vertical: {width: 1080, height: 1920, name: 'Vertical (9:16)'},
  square: {width: 1080, height: 1080, name: 'Instagram Feed / Twitter (1:1)'},
  landscape: {width: 1920, height: 1080, name: 'YouTube / LinkedIn (16:9)'},
  widescreen: {width: 1920, height: 1080, name: 'Widescreen (16:9)'},
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="Templates">
        <Composition
          id="lead-report"
          component={LeadReportVideo}
          durationInFrames={600}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={defaultLeadReportProps}
        />

        <Composition
          id="data-story"
          component={DataStoryVideo}
          durationInFrames={dataStoryDurationInFrames}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={defaultDataStoryProps}
        />

        <Composition
          id="announcement"
          component={AnnouncementVideo}
          durationInFrames={announcementDurationInFrames}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={defaultAnnouncementProps}
        />

        <Composition
          id="lead-report-2026-05-27"
          component={LeadReportVideo}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={defaultLeadReportProps}
        />

        <Composition
          id="web-www-remotion-dev-announcement"
          component={WebWwwRemotionDevAnnouncement}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />



        <Composition
          id="apple-style"
          component={AppleStyleVideo}
          durationInFrames={appleStyleDurationInFrames}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={defaultAppleStyleProps}
        />

        <Composition
          id="3d-promo"
          component={Promo3DVideo}
          durationInFrames={promo3DDurationInFrames}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={defaultPromo3DProps}
        />

        <Composition
          id="web-lustre-skin-announcement"
          component={WebLustreSkinAnnouncement}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />

        <Composition
          id="lustre-3d-viral"
          component={Lustre3dViral}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />

        <Composition
          id="lustre-pro-3d"
          component={LustrePro3d}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />

        <Composition
          id="lustre-pro-3d-v3"
          component={LustrePro3dV3}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />

        <Composition
          id="lustre-pro-3d-v4"
          component={LustrePro3dV4}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />

        <Composition
          id="lustre-pro-3d-v5"
          component={LustrePro3dV5}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />

        <Composition
          id="lustre-apple-style"
          component={LustreAppleStyle}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />

        <Composition
          id="lustre-apple-2d"
          component={LustreApple2d}
          durationInFrames={450}
          fps={30}
          width={1080}
          height={1920}
        />

        <Composition
          id="lustre-apple-final-3d"
          component={LustreAppleFinal3d}
          durationInFrames={lustreAppleFinal3dDurationInFrames}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={defaultLustreAppleFinal3dProps}
        />
      </Folder>
    </>
  );
};
