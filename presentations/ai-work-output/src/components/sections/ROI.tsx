import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";
import { TrendingUp, Clock, Shield, Users } from "lucide-react";
import { siteConfig } from "../../config/site";

const iconMap: Record<string, React.ElementType> = {
  TrendingUp,
  Clock,
  Shield,
  Users,
};

export default function ROI() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section id="roi" className="py-24 lg:py-32 px-4 sm:px-6 lg:px-8" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
            The <span className="text-gradient">ROI</span> of Living Documents
          </h2>
          <p className="text-xl text-navy-300 max-w-3xl mx-auto">
            {siteConfig.roi.subtitle}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {siteConfig.roi.metrics.map((metric, index) => {
            const Icon = iconMap[metric.label] || TrendingUp;
            const isHovered = hoveredIndex === index;

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={isInView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                className={`relative p-8 rounded-2xl border transition-all duration-500 ${
                  isHovered
                    ? "bg-navy-800/50 border-gold-500/30 scale-105"
                    : "bg-navy-900/30 border-white/5"
                }`}
              >
                <div className="text-center">
                  <div
                    className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 transition-all duration-300 ${
                      isHovered ? "bg-gold-500/20" : "bg-navy-800/50"
                    }`}
                  >
                    <Icon
                      className={`w-8 h-8 transition-colors duration-300 ${
                        isHovered ? "text-gold-400" : "text-navy-400"
                      }`}
                    />
                  </div>

                  <div className="font-display text-5xl font-bold text-gradient mb-2">
                    {metric.value}
                  </div>

                  <div className="text-lg font-semibold text-white mb-3">
                    {metric.label}
                  </div>

                  <div className="text-sm text-navy-400 leading-relaxed">
                    {metric.description}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
