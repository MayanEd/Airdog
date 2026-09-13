"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { assetUrl } from "@/lib/paths";

type Slide = { src: string; href: string; titleKey: string; bodyKey?: string; cta?: boolean };

const SLIDES: Slide[] = [
  { src: "/assets/img/usr/slider/slider_medical.jpg", href: "/pages/medical", titleKey: "slideMedicalTitle", bodyKey: "slideMedicalBody", cta: true },
  { src: "/assets/img/usr/slider/slider_lineup.jpg", href: "/categories/x-series", titleKey: "slideTvcTitle", bodyKey: "slideTvcBody" },
  { src: "/assets/img/usr/slider/slider_x5d.jpg", href: "/products/airdog-x5d-white", titleKey: "slideFlagship" },
  { src: "/assets/img/usr/slider/slider_x1d.jpg", href: "/products/airdog-x1d-white", titleKey: "slideX1" },
  { src: "/assets/img/usr/slider/slider_x3d.jpg", href: "/products/airdog-x3d-white", titleKey: "slideX3" },
  { src: "/assets/img/usr/slider/slider_x8dpro.jpg", href: "/products/airdog-x8d-pro-white", titleKey: "slideX8" },
  { src: "/assets/img/usr/slider/slider_airdogcare-plus.jpg", href: "/pages/care-plus", titleKey: "slideCare" },
  { src: "/assets/img/usr/slider/slider_mini.jpg", href: "/categories/mini", titleKey: "slideMini" },
  { src: "/assets/img/usr/slider/slider_moi.jpg", href: "/categories/moi", titleKey: "slideMoi" },
  { src: "/assets/img/usr/slider/slider_topplate.jpg", href: "/products/airdog-top-plate-black", titleKey: "slideTop" },
  { src: "/assets/img/usr/slider/slider_cleaner.jpg", href: "/categories/options", titleKey: "slideCleaner" },
];

export default function HeroSlider() {
  const t = useTranslations("home");
  const [i, setI] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setI((n) => (n + 1) % SLIDES.length), 5000);
    return () => clearInterval(id);
  }, []);
  return (
    <section className="hero" aria-roledescription="carousel">
      <div className="hero-track" style={{ transform: `translateX(-${i * 100}%)` }}>
        {SLIDES.map((s) => (
          <Link key={s.src} href={s.href} className="hero-slide">
            <img src={assetUrl(s.src)} alt="" />
            <div className="hero-overlay">
              <h2>{t(s.titleKey)}</h2>
              {s.bodyKey ? <p>{t(s.bodyKey)}</p> : null}
              {s.cta ? <span className="btn">{t("slideMedicalCta")} →</span> : null}
            </div>
          </Link>
        ))}
      </div>
      <div className="hero-dots">
        {SLIDES.map((s, idx) => (
          <button key={s.src} type="button" className={idx === i ? "active" : ""} aria-label={`${idx + 1}`} onClick={() => setI(idx)} />
        ))}
      </div>
    </section>
  );
}
