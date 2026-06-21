import React from 'react';
import {AbsoluteFill, Sequence, useVideoConfig} from 'remotion';
import {ActionItem} from '../components/ActionItem';
import {BigNumber} from '../components/BigNumber';
import {LeadCard, type LeadCardProps} from '../components/LeadCard';
import {MetricCard} from '../components/MetricCard';
import {TitleScene} from '../components/TitleScene';
import {palette} from '../design-system/colors';
import {interFontFamily} from '../design-system/typography';

export type LeadReportMetric = {label: string; value: number; suffix?: string};
export type LeadReportAction = {title: string; detail: string; urgency: 'Low' | 'Medium' | 'High'};

export type LeadReportVideoProps = {
  title: string;
  kicker: string;
  date: string;
  metrics: LeadReportMetric[];
  leads: Array<Omit<LeadCardProps, 'startFrame' | 'durationInFrames'>>;
  bigNumber: {
    value: string;
    label: string;
  };
  actions: LeadReportAction[];
  durationInSeconds?: number;
};

const fps = 30;

// Scene ratios as fractions of total duration (must sum to 1.0)
const sceneRatios = {
  intro: 0.18,
  metrics: 0.18,
  leads: 0.20,
  bigNumber: 0.13,
  actions: 0.18,
  outro: 0.13,
};

function getSceneFrames(totalSeconds: number) {
  const totalFrames = Math.max(150, totalSeconds * fps); // minimum 5s
  return {
    intro: Math.round(totalFrames * sceneRatios.intro),
    metrics: Math.round(totalFrames * sceneRatios.metrics),
    leads: Math.round(totalFrames * sceneRatios.leads),
    bigNumber: Math.round(totalFrames * sceneRatios.bigNumber),
    actions: Math.round(totalFrames * sceneRatios.actions),
    outro: Math.round(totalFrames * sceneRatios.outro),
  };
}

export const LeadReportVideo: React.FC<LeadReportVideoProps> = ({
  title, kicker, date, metrics, leads, bigNumber, actions, durationInSeconds = 20
}) => {
  const {width, height} = useVideoConfig();
  const s = getSceneFrames(durationInSeconds);
  const totalFrames = s.intro + s.metrics + s.leads + s.bigNumber + s.actions + s.outro;

  return (
    <AbsoluteFill style={{backgroundColor: palette.cloud, width, height}}>
      <Sequence from={0} durationInFrames={s.intro} premountFor={fps}>
        <TitleScene kicker={kicker} title={title} subtitle={date} />
      </Sequence>

      <Sequence from={s.intro} durationInFrames={s.metrics} premountFor={fps}>
        <AbsoluteFill style={{padding: '92px 84px', gap: 34}}>
          <div style={{fontFamily: interFontFamily, fontSize: 48, fontWeight: 700, color: palette.ink}}>Performance at a glance</div>
          <div style={{display: 'flex', gap: 22}}>
            {metrics.slice(0, 3).map((metric, i) => (
              <MetricCard
                key={metric.label}
                label={metric.label}
                value={metric.value}
                suffix={metric.suffix}
                startFrame={i * 6}
                durationInFrames={s.metrics - i * 6}
              />
            ))}
          </div>
        </AbsoluteFill>
      </Sequence>

      <Sequence from={s.intro + s.metrics} durationInFrames={s.leads} premountFor={fps}>
        <AbsoluteFill style={{padding: '92px 84px', gap: 18}}>
          <div style={{fontFamily: interFontFamily, fontSize: 48, fontWeight: 700, color: palette.ink}}>Top opportunities</div>
          {leads.slice(0, 3).map((lead, i) => (
            <LeadCard
              key={`${lead.name}-${lead.company}`}
              {...lead}
              startFrame={i * 9}
              durationInFrames={s.leads - i * 9}
            />
          ))}
        </AbsoluteFill>
      </Sequence>

      <Sequence
        from={s.intro + s.metrics + s.leads}
        durationInFrames={s.bigNumber}
        premountFor={fps}
      >
        <BigNumber value={bigNumber.value} label={bigNumber.label} />
      </Sequence>

      <Sequence
        from={s.intro + s.metrics + s.leads + s.bigNumber}
        durationInFrames={s.actions}
        premountFor={fps}
      >
        <AbsoluteFill style={{padding: '92px 84px', gap: 20}}>
          <div style={{fontFamily: interFontFamily, fontSize: 48, fontWeight: 700, color: palette.ink}}>Action plan</div>
          {actions.slice(0, 3).map((action, i) => (
            <ActionItem key={action.title} {...action} startFrame={i * 8} />
          ))}
        </AbsoluteFill>
      </Sequence>

      <Sequence
        from={s.intro + s.metrics + s.leads + s.bigNumber + s.actions}
        durationInFrames={s.outro}
        premountFor={fps}
      >
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 14}}>
          <div style={{fontFamily: interFontFamily, fontSize: 30, fontWeight: 600, color: palette.blue}}>Next update in 24 hours</div>
          <div style={{fontFamily: interFontFamily, fontSize: 62, fontWeight: 700, color: palette.ink}}>Focus. Follow-up. Close.</div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

export const defaultLeadReportProps: LeadReportVideoProps = {
  title: 'Lead Generation Report',
  kicker: 'Marvelus Intelligence',
  date: 'May 27, 2026',
  metrics: [
    {label: 'Qualified Leads', value: 48},
    {label: 'Booked Calls', value: 17},
    {label: 'Pipeline Value', value: 124000, suffix: '$'},
  ],
  leads: [
    {name: 'Alyssa Reed', company: 'Ridge Dental Group', score: 93, priority: 'Critical'},
    {name: 'Devon Patel', company: 'Harbor Auto Imports', score: 88, priority: 'High'},
    {name: 'Mina Choi', company: 'Northpoint Law', score: 84, priority: 'Medium'},
  ],
  bigNumber: {
    value: '37%',
    label: 'Higher close rate than last week',
  },
  actions: [
    {title: 'Call hot leads by noon', detail: 'Prioritize scores above 90 and no-shows from yesterday.', urgency: 'High'},
    {title: 'Launch retargeting ad', detail: 'Use testimonial creative + booking incentive.', urgency: 'Medium'},
    {title: 'Update CRM notes', detail: 'Tag objections and next-step commitments by team.', urgency: 'Low'},
  ],
  durationInSeconds: 20,
};
