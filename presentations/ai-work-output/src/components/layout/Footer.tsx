import { Github, Linkedin, Twitter } from "lucide-react";
import { siteConfig } from "../../config/site";

const socialIcons: Record<string, React.ElementType> = {
  Twitter,
  LinkedIn: Linkedin,
  GitHub: Github,
};

export default function Footer() {
  return (
    <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Logo */}
          <div className="font-display text-xl font-bold text-gradient">
            AI Work Output
          </div>

          {/* Links */}
          <nav className="flex flex-wrap items-center justify-center gap-6">
            {siteConfig.footer.links.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm text-navy-400 hover:text-gold-400 transition-colors duration-300"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* Social */}
          <div className="flex items-center gap-4">
            {siteConfig.footer.social.map((social) => {
              const Icon = socialIcons[social.label] || Twitter;
              return (
                <a
                  key={social.label}
                  href={social.href}
                  className="w-10 h-10 rounded-full bg-navy-800/50 flex items-center justify-center text-navy-400 hover:text-gold-400 hover:bg-navy-700/50 transition-all duration-300"
                  aria-label={social.label}
                >
                  <Icon size={18} />
                </a>
              );
            })}
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-white/5 text-center text-sm text-navy-500">
          {siteConfig.footer.copyright}
        </div>
      </div>
    </footer>
  );
}
