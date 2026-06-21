import { animate, motion, useInView, useMotionValue, useTransform } from 'framer-motion'
import { useEffect, useRef } from 'react'
import { site, type Stat } from './config/site'

type CounterProps = {
  stat: Stat
}

function Counter({ stat }: CounterProps) {
  const ref = useRef<HTMLDivElement | null>(null)
  const value = useMotionValue(0)
  const rounded = useTransform(value, (latest) => latest.toFixed(stat.value % 1 ? 1 : 0))
  const visible = useInView(ref, { once: true, margin: '-120px' })

  useEffect(() => {
    if (!visible) return
    const controls = animate(value, stat.value, {
      duration: 1.6,
      ease: [0.16, 1, 0.3, 1],
    })
    return () => controls.stop()
  }, [visible, stat.value, value])

  return (
    <div ref={ref} className="rounded-2xl border border-cyan/30 bg-midnight/60 p-5 shadow-cyan backdrop-blur">
      <p className="text-xs uppercase tracking-[0.2em] text-cyan/70">{stat.label}</p>
      <p className="mt-4 font-display text-4xl text-ink md:text-5xl">
        {stat.prefix}
        <motion.span>{rounded}</motion.span>
        {stat.suffix}
      </p>
    </div>
  )
}

function App() {
  return (
    <div className="relative overflow-hidden bg-transparent">
      <div className="pointer-events-none absolute inset-0 bg-grid bg-[length:56px_56px] opacity-30" />

      <main className="relative mx-auto max-w-7xl px-5 pb-24 pt-6 text-ink sm:px-8 lg:px-12">
        <header className="mb-14 flex items-center justify-between">
          <span className="font-body text-xs uppercase tracking-[0.22em] text-cyan/80">{site.meta.name}</span>
          <nav className="hidden gap-8 text-sm text-ink/70 md:flex">
            {site.nav.map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} className="transition hover:text-cyan">
                {item}
              </a>
            ))}
          </nav>
        </header>

        <section id="hero" className="relative grid gap-10 pb-16 md:grid-cols-[1.15fr_0.85fr] md:items-end">
          <div className="relative z-10">
            <motion.p
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45 }}
              className="font-body text-xs uppercase tracking-[0.22em] text-cyan"
            >
              {site.hero.eyebrow}
            </motion.p>

            <motion.h1
              initial={{ opacity: 0, y: 28 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.1 }}
              className="mt-4 font-display text-[2.65rem] uppercase leading-[0.9] text-ink sm:text-6xl lg:text-7xl"
            >
              <span className="block">{site.hero.titleTop}</span>
              <span className="block text-cyan">{site.hero.titleBottom}</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-6 max-w-xl text-base text-ink/78"
            >
              {site.hero.subtitle}
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.3 }}
              className="mt-8 flex flex-wrap gap-4"
            >
              <button className="rounded-full bg-cyan px-6 py-3 font-body text-sm font-semibold text-[#041019] transition hover:scale-[1.02]">
                {site.hero.primaryCta}
              </button>
              <button className="rounded-full border border-cyan/40 px-6 py-3 font-body text-sm text-cyan transition hover:border-cyan hover:bg-cyan/10">
                {site.hero.secondaryCta}
              </button>
            </motion.div>
          </div>

          <div className="relative min-h-[320px]">
            <div className="absolute right-0 top-2 h-52 w-52 rotate-[12deg] rounded-[2.5rem] border border-cyan/50 bg-cyan/10 blur-[0.3px]" />
            <div className="absolute left-8 top-24 h-44 w-44 -rotate-12 rounded-[2rem] border border-cyan/40 bg-gradient-to-br from-cyan/20 to-transparent" />
            <div className="absolute bottom-0 right-10 h-48 w-48 rounded-full border border-cyan/40 bg-cyan/10 shadow-cyan" />
            <div className="absolute left-0 top-8 max-w-[280px] rounded-3xl border border-cyan/30 bg-midnight/75 p-5 backdrop-blur-lg">
              <p className="font-body text-xs uppercase tracking-[0.2em] text-cyan/75">Template Tags</p>
              <ul className="mt-4 space-y-2 text-sm text-ink/85">
                {site.hero.badges.map((badge) => (
                  <li key={badge}>▸ {badge}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <div className="my-10 h-14 -skew-y-2 bg-gradient-to-r from-cyan/20 to-transparent" />

        <section id="problem" className="grid gap-8 py-4 md:grid-cols-[1.1fr_0.9fr]">
          <h2 className="font-display text-3xl uppercase leading-tight text-ink sm:text-4xl">{site.problem.title}</h2>
          <div>
            <ul className="space-y-3 text-ink/80">
              {site.problem.bullets.map((item) => (
                <li key={item} className="rounded-xl border border-cyan/20 bg-midnight/40 px-4 py-3">
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-5 text-sm text-cyan/90">{site.problem.statement}</p>
          </div>
        </section>

        <section id="features" className="py-16">
          <h2 className="font-display text-3xl uppercase text-ink sm:text-4xl">{site.features.title}</h2>
          <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {site.features.items.map((feature) => (
              <article
                key={feature.title}
                className="group rounded-2xl border border-cyan/20 bg-midnight/45 p-5 transition hover:-translate-y-1 hover:border-cyan/55"
              >
                <p className="font-display text-xl text-cyan">{feature.accent}</p>
                <h3 className="mt-2 font-display text-xl uppercase text-ink">{feature.title}</h3>
                <p className="mt-3 text-sm text-ink/75">{feature.description}</p>
              </article>
            ))}
          </div>
        </section>

        <div className="my-8 h-14 skew-y-2 bg-gradient-to-l from-cyan/25 to-transparent" />

        <section id="stats" className="py-12">
          <h2 className="font-display text-3xl uppercase text-ink sm:text-4xl">{site.stats.title}</h2>
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            {site.stats.items.map((stat) => (
              <Counter key={stat.label} stat={stat} />
            ))}
          </div>
        </section>

        <section id="proof" className="py-16">
          <h2 className="font-display text-3xl uppercase text-ink sm:text-4xl">{site.socialProof.title}</h2>
          <div className="mt-8 grid grid-cols-2 gap-4 text-center sm:grid-cols-3">
            {site.socialProof.logos.map((logo) => (
              <div key={logo} className="rounded-xl border border-cyan/20 bg-midnight/45 px-3 py-6 font-display text-sm tracking-[0.2em] text-cyan/90">
                {logo}
              </div>
            ))}
          </div>
          <div className="mt-8 grid gap-4 lg:grid-cols-2">
            {site.socialProof.testimonials.map((item) => (
              <blockquote key={item.quote} className="rounded-2xl border border-cyan/25 bg-midnight/55 p-6">
                <p className="text-ink/85">“{item.quote}”</p>
                <footer className="mt-4 text-sm text-cyan">— {item.author}</footer>
              </blockquote>
            ))}
          </div>
        </section>

        <section id="cta" className="rounded-3xl border border-cyan/35 bg-gradient-to-r from-midnight to-[#111a30] p-7 sm:p-10">
          <h2 className="font-display text-3xl uppercase text-ink sm:text-5xl">{site.cta.title}</h2>
          <p className="mt-4 max-w-2xl text-ink/75">{site.cta.body}</p>
          <div className="mt-7 flex flex-wrap gap-4">
            <button className="rounded-full bg-cyan px-7 py-3 font-semibold text-[#03111b]">{site.cta.primary}</button>
            <button className="rounded-full border border-cyan/40 px-7 py-3 text-cyan">{site.cta.secondary}</button>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
