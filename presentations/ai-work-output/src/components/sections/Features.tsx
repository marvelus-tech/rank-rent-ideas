import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";
import {
  Presentation,
  FileText,
  Table,
  BarChart3,
  GraduationCap,
  BookOpen,
  LayoutDashboard,
  LineChart,
  Shield,
  ChevronRight,
  Users,
} from "lucide-react";
import { siteConfig } from "../../config/site";

const iconMap: Record<string, React.ElementType> = {
  Presentation,
  FileText,
  Table,
  BarChart3,
  Users,
  GraduationCap,
  BookOpen,
  LayoutDashboard,
  LineChart,
  Shield,
};

export default function Features() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <section id="sites" className="py-24 lg:py-32 px-4 sm:px-6 lg:px-8" ref={ref}>
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
            10 Sites{" "}
            <span className="text-gradient">Knowledge Workers</span>
            <br />
            Should Build
          </h2>
          <p className="text-xl text-navy-300 max-w-3xl mx-auto">
            {siteConfig.features.subtitle}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {siteConfig.features.items.map((feature, index) => {
            const Icon = iconMap[feature.icon] || Presentation;
            const isActive = activeIndex === index;

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: index * 0.08 }}
                onMouseEnter={() => setActiveIndex(index)}
                className={`group relative p-8 rounded-2xl border transition-all duration-500 cursor-pointer ${
                  isActive
                    ? "bg-navy-800/50 border-gold-500/30"
                    : "bg-navy-900/30 border-white/5 hover:border-white/10"
                }`}
              >
                <div className="flex items-start gap-6">
                  <div
                    className={`w-14 h-14 rounded-xl flex items-center justify-center shrink-0 transition-all duration-300 ${
                      isActive
                        ? "bg-gold-500/20 scale-110"
                        : "bg-navy-800/50 group-hover:bg-navy-700/50"
                    }`}
                  >
                    <Icon
                      className={`w-7 h-7 transition-colors duration-300 ${
                        isActive ? "text-gold-400" : "text-navy-400"
                      }`}
                    />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-display text-xl font-bold text-white">
                        {feature.title}
                      </h3>
                      <ChevronRight
                        className={`w-5 h-5 transition-all duration-300 ${
                          isActive
                            ? "text-gold-400 translate-x-1"
                            : "text-navy-600"
                        }`}
                      />
                    </div>

                    <p className="text-navy-300 leading-relaxed mb-4">
                      {feature.description}
                    </p>

                    <div className="inline-flex items-center px-3 py-1 rounded-full bg-gold-500/10 text-gold-400 text-sm font-medium">
                      {feature.useCase}
                    </div>
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
