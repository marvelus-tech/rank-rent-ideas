import type { ReactNode } from "react";

export interface NavLink {
  label: string;
  href: string;
}

export interface Stat {
  value: string;
  label: string;
}

export interface Feature {
  icon: string;
  title: string;
  description: string;
  useCase: string;
}

export interface Testimonial {
  quote: string;
  author: string;
  role: string;
  company: string;
}

export interface SiteConfig {
  name: string;
  tagline: string;
  description: string;
  url: string;
  ogImage: string;
  nav: {
    links: NavLink[];
    cta: { label: string; href: string };
  };
  hero: {
    badge: string;
    title: string;
    subtitle: string;
    cta: { label: string; href: string };
    stats: Stat[];
  };
  problem: {
    title: string;
    points: string[];
  };
  features: {
    title: string;
    subtitle: string;
    items: Feature[];
  };
  roi: {
    title: string;
    subtitle: string;
    metrics: { label: string; value: string; description: string }[];
  };
  testimonials: {
    title: string;
    items: Testimonial[];
  };
  cta: {
    title: string;
    subtitle: string;
    button: { label: string; href: string };
  };
  footer: {
    links: NavLink[];
    social: { label: string; href: string }[];
    copyright: string;
  };
}
