import type { SiteConfig } from "../types";

export const siteConfig: SiteConfig = {
  name: "AI Work Output",
  tagline: "The Future of Knowledge Work",
  description: "Transform static documents into living, interactive experiences with AI-powered sites.",
  url: "https://ai-work-output.com",
  ogImage: "/og-image.jpg",
  
  nav: {
    links: [
      { label: "The Problem", href: "#problem" },
      { label: "10 Sites", href: "#sites" },
      { label: "ROI", href: "#roi" },
      { label: "Testimonials", href: "#testimonials" },
    ],
    cta: { label: "Get Started", href: "#contact" },
  },
  
  hero: {
    badge: "AI-Powered Work Output",
    title: "The Future of Knowledge Work",
    subtitle: "Transform static documents into living, interactive experiences. 10 sites every knowledge worker should build with AI.",
    cta: { label: "Explore the 10 Sites", href: "#sites" },
    stats: [
      { value: "10", label: "Site Types" },
      { value: "73%", label: "Time Saved" },
      { value: "0", label: "Version Conflicts" },
    ],
  },
  
  problem: {
    title: "Why Your Documents Are Costing You Money",
    points: [
      "Version control chaos: plan_v2, plan_final, plan_final_FINAL",
      "Static snapshots go stale the moment you hit send",
      "No feedback loop — send and pray",
      "Lost context in email threads and shared folders",
      "Rebuilding the same deck for every client",
      "No analytics on who read what, when",
    ],
  },
  
  features: {
    title: "10 Sites Knowledge Workers Should Build",
    subtitle: "Replace static documents with living, interactive experiences",
    items: [
      {
        icon: "Presentation",
        title: "The Living Deck",
        description: "Interactive presentations that update in real-time. No more sending PDFs that are outdated before they arrive.",
        useCase: "Client pitches, board decks, product demos",
      },
      {
        icon: "FileText",
        title: "The Dynamic Memo",
        description: "Living documents with embedded data, charts, and real-time collaboration. Always current, always correct.",
        useCase: "Strategy memos, project briefs, research reports",
      },
      {
        icon: "Table",
        title: "The Interactive Spreadsheet",
        description: "Data tools with embedded logic, live connections, and visual outputs. Share insights, not just numbers.",
        useCase: "Financial models, capacity planning, scenario analysis",
      },
      {
        icon: "BarChart3",
        title: "The Living Report",
        description: "Dashboards with live data feeds, automated updates, and drill-down capabilities. Set it and forget it.",
        useCase: "Monthly reports, KPI dashboards, performance reviews",
      },
      {
        icon: "Handshake",
        title: "The Collaborative Proposal",
        description: "Client-facing interactive proposals with embedded pricing calculators, timelines, and e-signatures.",
        useCase: "Sales proposals, SOWs, contract negotiations",
      },
      {
        icon: "GraduationCap",
        title: "The Training Portal",
        description: "Interactive learning experiences with progress tracking, quizzes, and certifications. Scale your knowledge.",
        useCase: "Employee onboarding, compliance training, skill development",
      },
      {
        icon: "BookOpen",
        title: "The Knowledge Base",
        description: "Searchable, updateable wiki sites with AI-powered search and automatic content suggestions.",
        useCase: "Internal wikis, client portals, documentation hubs",
      },
      {
        icon: "LayoutDashboard",
        title: "The Project Hub",
        description: "Central project dashboards with status updates, task lists, and team collaboration. One source of truth.",
        useCase: "Project management, client updates, team coordination",
      },
      {
        icon: "LineChart",
        title: "The Analytics Dashboard",
        description: "Real-time metrics visualization with custom alerts, trend analysis, and automated insights.",
        useCase: "Marketing analytics, sales pipelines, operational metrics",
      },
      {
        icon: "Shield",
        title: "The Client Portal",
        description: "Branded client-facing experience with secure access, document sharing, and communication tools.",
        useCase: "Client management, vendor portals, partner extranets",
      },
    ],
  },
  
  roi: {
    title: "The ROI of Living Documents",
    subtitle: "Quantifiable benefits of replacing static files with interactive sites",
    metrics: [
      { label: "Time Saved", value: "73%", description: "Less time rebuilding decks and chasing versions" },
      { label: "Faster Decisions", value: "2.5x", description: "Interactive data leads to quicker insights" },
      { label: "Error Reduction", value: "94%", description: "Single source of truth eliminates copy-paste errors" },
      { label: "Client Satisfaction", value: "+40%", description: "Interactive proposals win more business" },
    ],
  },
  
  testimonials: {
    title: "What Teams Are Saying",
    items: [
      {
        quote: "We replaced our monthly board deck with a living dashboard. The board loves it, and we save 20 hours every month.",
        author: "Sarah Chen",
        role: "VP of Strategy",
        company: "TechCorp Inc.",
      },
      {
        quote: "Our client proposals went from 48-hour turnaround to instant interactive experiences. Win rate increased 35%.",
        author: "Marcus Johnson",
        role: "Sales Director",
        company: "Consulting Partners",
      },
      {
        quote: "The training portal we built in a weekend replaced our $50k LMS. Employees actually complete the courses now.",
        author: "Elena Rodriguez",
        role: "Head of L&D",
        company: "Global Enterprises",
      },
    ],
  },
  
  cta: {
    title: "Transform Your Work Output",
    subtitle: "Join the teams replacing static documents with living experiences. Start building your first AI-powered site today.",
    button: { label: "Get Started Free", href: "#contact" },
  },
  
  footer: {
    links: [
      { label: "The Problem", href: "#problem" },
      { label: "10 Sites", href: "#sites" },
      { label: "ROI", href: "#roi" },
      { label: "Testimonials", href: "#testimonials" },
    ],
    social: [
      { label: "Twitter", href: "#" },
      { label: "LinkedIn", href: "#" },
      { label: "GitHub", href: "#" },
    ],
    copyright: "© 2026 AI Work Output. All rights reserved.",
  },
};
