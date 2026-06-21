export type Feature = {
  title: string;
  description: string;
  accent: string;
};

export type Stat = {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
};

export const site = {
  meta: {
    name: 'Tech Modern',
    tagline: 'Future-ready template for ambitious product teams',
  },
  nav: ['Problem', 'Features', 'Stats', 'Proof', 'CTA'],
  hero: {
    eyebrow: 'Template System — Tech Modern',
    titleTop: 'Build The Future',
    titleBottom: 'Before It Arrives',
    subtitle:
      'A futuristic landing template for SaaS, AI products, and startup launches with asymmetric composition and cinematic motion.',
    primaryCta: 'Launch The Prototype',
    secondaryCta: 'See The Blueprint',
    badges: ['SaaS', 'AI Products', 'Startup Launches'],
  },
  problem: {
    title: 'Why Legacy Tools Are Killing Your Velocity',
    bullets: [
      'Static decks break the moment strategy shifts.',
      'Disconnected tools force teams to rebuild context every week.',
      'Conventional templates flatten differentiation before launch.',
    ],
    statement:
      'Modern teams need adaptive interfaces, not static artifacts. This template is built for speed, narrative clarity, and momentum.',
  },
  features: {
    title: 'Core System Features',
    items: [
      {
        title: 'Asymmetric Hero Grid',
        description: 'Off-axis composition with layered depth for immediate visual memorability.',
        accent: '01',
      },
      {
        title: 'Section Rhythm Engine',
        description: 'Diagonal transitions and staggered spacing to guide scanning flow.',
        accent: '02',
      },
      {
        title: 'Frictionless Content Config',
        description: 'Everything editable from one site config file for fast adaptation.',
        accent: '03',
      },
      {
        title: 'Performance-First Motion',
        description: 'GPU-safe transforms and orchestrated reveals with Framer Motion.',
        accent: '04',
      },
      {
        title: 'Signal-Heavy Proof Blocks',
        description: 'Structured social proof with logos and testimonial cards.',
        accent: '05',
      },
      {
        title: 'Conversion-Ready CTA',
        description: 'High-contrast final section with clear action hierarchy.',
        accent: '06',
      },
    ] as Feature[],
  },
  stats: {
    title: 'Template Performance Signals',
    items: [
      { label: 'Faster narrative assembly', value: 3.2, suffix: 'x' },
      { label: 'Mobile engagement uplift', value: 67, suffix: '%' },
      { label: 'Design handoff friction reduction', value: 42, suffix: '%' },
      { label: 'Avg. launch prep time saved', value: 18, suffix: ' hrs' },
    ] as Stat[],
  },
  socialProof: {
    title: 'Designed For Modern Product Teams',
    logos: ['NEXUS AI', 'QUANTIX', 'FLOWSTATE', 'NEUROLAB', 'ITERA', 'SKYFORGE'],
    testimonials: [
      {
        quote:
          'This template made our launch page look custom-built in a day. The asymmetry instantly felt premium.',
        author: 'Head of Marketing, Seed-stage AI SaaS',
      },
      {
        quote:
          'We replaced our old landing framework and cut iteration cycles in half without losing visual quality.',
        author: 'Product Design Lead, B2B Platform Startup',
      },
    ],
  },
  cta: {
    title: 'Start Building Tomorrow',
    body: 'Clone the structure, swap the narrative, and ship a launch-ready experience in your own brand voice.',
    primary: 'Use This Template',
    secondary: 'Download Structure Guide',
  },
};
