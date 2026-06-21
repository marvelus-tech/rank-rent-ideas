export type SiteCard = {
  number: string;
  title: string;
  description: string;
  value: string;
};

export const siteContent = {
  nav: ['Problem', '10 Sites', 'ROI', 'Testimonials', 'CTA'],
  hero: {
    eyebrow: 'AI-Native Knowledge Work',
    title: '10 Sites Knowledge Workers Should Build with AI',
    subtitle:
      'Replace static artifacts with living systems: interactive, collaborative, and always current.',
    ctaPrimary: 'Explore the 10 Sites',
    ctaSecondary: 'Calculate Impact',
    metricLabel: 'Potential productivity lift',
    metricValue: '3.4×',
  },
  problem: {
    title: 'The Problem with Static Deliverables',
    points: [
      'PDF decks are dead on arrival the moment context changes.',
      'Memos and spreadsheets fragment across versions and channels.',
      'Reports and proposals fail to capture real-time business state.',
    ],
    statement:
      'Knowledge workers lose momentum when insight is trapped in static files. AI turns documents into adaptive products.',
  },
  sites: [
    {
      number: '01',
      title: 'The Living Deck',
      description: 'Interactive presentations that personalize flow, depth, and storytelling in real time.',
      value: 'Close decisions faster than static PDF decks.',
    },
    {
      number: '02',
      title: 'The Dynamic Memo',
      description: 'Living narratives with connected data, linked references, and instant update propagation.',
      value: 'Keep strategy docs permanently current.',
    },
    {
      number: '03',
      title: 'The Interactive Spreadsheet',
      description: 'Decision models with embedded logic, scenarios, and guided AI interpretation.',
      value: 'Move from raw cells to executable intelligence.',
    },
    {
      number: '04',
      title: 'The Living Report',
      description: 'Executive reporting surfaces fed by live pipelines and narrative AI summaries.',
      value: 'Turn monthly snapshots into always-on clarity.',
    },
    {
      number: '05',
      title: 'The Collaborative Proposal',
      description: 'Client-facing proposals that adapt to stakeholder inputs and pricing assumptions.',
      value: 'Increase win rate with interactive buying journeys.',
    },
    {
      number: '06',
      title: 'The Training Portal',
      description: 'Interactive onboarding and upskilling environments with AI tutors and role paths.',
      value: 'Scale capability without scaling facilitation cost.',
    },
    {
      number: '07',
      title: 'The Knowledge Base',
      description: 'Searchable, maintained wikis with semantic retrieval and auto-refreshing guidance.',
      value: 'Eliminate tribal knowledge bottlenecks.',
    },
    {
      number: '08',
      title: 'The Project Hub',
      description: 'Single-pane project command centers with status, blockers, and delivery velocity.',
      value: 'Restore alignment across teams and timelines.',
    },
    {
      number: '09',
      title: 'The Analytics Dashboard',
      description: 'Real-time KPI experiences with anomaly detection and contextual recommendations.',
      value: 'Respond to trends before they become problems.',
    },
    {
      number: '10',
      title: 'The Client Portal',
      description: 'Branded, secure client environments that centralize value, communication, and outcomes.',
      value: 'Elevate retention through premium digital experience.',
    },
  ] as SiteCard[],
  roi: {
    title: 'Estimated Return from AI-Native Site Transformation',
    stats: [
      { label: 'Time saved per manager / week', value: '6.8h' },
      { label: 'Cycle-time reduction', value: '41%' },
      { label: 'Decision quality improvement', value: '+29%' },
      { label: 'Annual operating leverage', value: '$1.2M' },
    ],
  },
  testimonials: {
    title: 'What Teams Report After Switching',
    quotes: [
      {
        text: 'Our board deck became a decision platform. We now answer objections in-session, not two weeks later.',
        author: 'Chief of Staff, Global Manufacturing Group',
      },
      {
        text: 'The proposal portal changed the conversation from price to value. Our close rate jumped in one quarter.',
        author: 'Managing Partner, Strategy Consultancy',
      },
      {
        text: 'Replacing static SOP docs with a living knowledge base cut onboarding time by nearly half.',
        author: 'VP Operations, Technology Services Firm',
      },
    ],
  },
  cta: {
    title: 'Build Your First AI Site in 14 Days',
    body: 'Start with one high-friction workflow. Convert it into a living system. Expand from there.',
    primary: 'Book an AI Work Design Sprint',
    secondary: 'Download Executive Brief',
  },
};
