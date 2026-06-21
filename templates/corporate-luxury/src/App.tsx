import { useEffect } from 'react';
import { siteContent } from './config/site';

const sectionIds = ['problem', 'sites', 'roi', 'testimonials', 'cta'] as const;

function App() {
  useEffect(() => {
    const targets = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2, rootMargin: '0px 0px -40px 0px' }
    );

    targets.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="page-shell">
      <header className="top-nav">
        <div className="brand">CODY / AI WORK OUTPUT</div>
        <nav>
          {siteContent.nav.map((item, i) => (
            <a key={item} href={`#${sectionIds[i]}`}>
              {item}
            </a>
          ))}
        </nav>
      </header>

      <main>
        <section className="hero section reveal is-visible">
          <p className="eyebrow">{siteContent.hero.eyebrow}</p>
          <h1>{siteContent.hero.title}</h1>
          <p className="subtitle">{siteContent.hero.subtitle}</p>

          <div className="hero-cta-row">
            <a href="#sites" className="btn btn-primary">
              {siteContent.hero.ctaPrimary}
            </a>
            <a href="#roi" className="btn btn-ghost">
              {siteContent.hero.ctaSecondary}
            </a>
          </div>

          <div className="hero-metric">
            <span>{siteContent.hero.metricLabel}</span>
            <strong>{siteContent.hero.metricValue}</strong>
          </div>
        </section>

        <section id="problem" className="section panel reveal">
          <h2>{siteContent.problem.title}</h2>
          <ul>
            {siteContent.problem.points.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>
          <p className="statement">{siteContent.problem.statement}</p>
        </section>

        <section id="sites" className="section reveal">
          <h2>10 AI-Powered Sites</h2>
          <div className="sites-grid">
            {siteContent.sites.map((site) => (
              <article key={site.number + site.title} className="site-card">
                <div className="site-meta">
                  <span>{site.number}</span>
                </div>
                <h3>{site.title}</h3>
                <p>{site.description}</p>
                <p className="value">{site.value}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="roi" className="section panel reveal">
          <h2>{siteContent.roi.title}</h2>
          <div className="roi-grid">
            {siteContent.roi.stats.map((stat) => (
              <div key={stat.label} className="roi-card">
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
              </div>
            ))}
          </div>
        </section>

        <section id="testimonials" className="section reveal">
          <h2>{siteContent.testimonials.title}</h2>
          <div className="testimonials-grid">
            {siteContent.testimonials.quotes.map((quote) => (
              <blockquote key={quote.author} className="quote-card">
                <p>“{quote.text}”</p>
                <cite>{quote.author}</cite>
              </blockquote>
            ))}
          </div>
        </section>

        <section id="cta" className="section cta-panel reveal">
          <h2>{siteContent.cta.title}</h2>
          <p>{siteContent.cta.body}</p>
          <div className="hero-cta-row">
            <button className="btn btn-primary">{siteContent.cta.primary}</button>
            <button className="btn btn-ghost">{siteContent.cta.secondary}</button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
