import { LandingNav } from "@/components/landing/LandingNav";
import { Hero } from "@/components/landing/Hero";
import { Features } from "@/components/landing/Features";
import { ArchitectureStrip } from "@/components/landing/ArchitectureStrip";
import { SecurityAndCta } from "@/components/landing/SecurityAndCta";
import { LandingFooter } from "@/components/landing/LandingFooter";

export function Landing() {
  return (
    <div className="min-h-dvh">
      <LandingNav />
      <main>
        <Hero />
        <Features />
        <ArchitectureStrip />
        <SecurityAndCta />
      </main>
      <LandingFooter />
    </div>
  );
}
