import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PublicNavbar from "../components/PublicNavbar";
import MarketingFooter from "../components/MarketingFooter";

function Landing() {
  const navigate = useNavigate();

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal-visible");
          }
        });
      },
      { threshold: 0.1 }
    );
    const els = document.querySelectorAll(".reveal");
    els.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="h-screen w-screen overflow-y-scroll snap-y snap-mandatory scroll-smooth bg-slate-50">
      <PublicNavbar />
      {/* Hero */}
      <section id="home" className="relative h-screen snap-start pt-28 md:pt-32">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url('${process.env.PUBLIC_URL}/meal-planner.svg')`, filter: "blur(1px)" }}
          aria-hidden="true"
        />
        <div className="absolute inset-0 bg-black/30" aria-hidden="true" />
        <div className="relative max-w-6xl mx-auto px-4 h-full grid md:grid-cols-2 gap-8 items-center">
          <div className="reveal">
            <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-green-600">
              Your Personal AI Recipe Planner
            </h1>
            <p className="mt-4 text-white/90 md:text-lg">
              Plan your meals, manage ingredients, and receive personalized daily recipes on WhatsApp — powered by RP-Agentic AI.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={() => navigate("/signup")}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-white bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 shadow-md transition-all duration-200 hover:scale-[1.02]"
              >
                <span>Get Started</span>
              </button>
              <a
                href="#demo"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/80 text-slate-900 backdrop-blur hover:bg-white shadow-md transition-all duration-200"
              >
                Watch Demo
              </a>
            </div>
          </div>
          <div className="reveal">
            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 to-green-600/20 blur-2xl rounded-3xl" aria-hidden="true" />
              <img src={process.env.PUBLIC_URL + "/meal-planner.svg"} alt="AI cooking assistant" className="relative w-full rounded-2xl ring-1 ring-white/30 shadow-2xl" />
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="bg-white h-screen snap-start pt-24">
        <div className="max-w-6xl mx-auto px-4 h-full flex flex-col justify-center">
          <h2 className="reveal text-3xl md:text-4xl font-bold text-center text-slate-900">Features</h2>
          <p className="reveal mt-2 text-center text-slate-600">Everything you need to plan meals effortlessly.</p>
          <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: "🧠", title: "AI Recipe Suggestions", desc: "Get smart meal ideas based on your ingredients." },
              { icon: "📦", title: "Ingredient Tracker", desc: "Track what's in stock and what's running low." },
              { icon: "📱", title: "WhatsApp Notifications", desc: "Receive your meal plan directly on WhatsApp." },
              { icon: "🕒", title: "Smart Scheduling", desc: "Choose your meal time and get daily reminders." },
            ].map((f) => (
              <div key={f.title} className="reveal group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-0.5">
                <div className="text-2xl">{f.icon}</div>
                <h3 className="mt-3 font-semibold text-slate-900">{f.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how" className="h-screen snap-start pt-24">
        <div className="max-w-6xl mx-auto px-4 h-full flex flex-col justify-center">
          <h2 className="reveal text-3xl md:text-4xl font-bold text-center text-slate-900">How It Works</h2>
          <div className="mt-10 reveal flex flex-col md:flex-row items-center md:items-start md:justify-between gap-8">
            {[
              { step: "1️⃣", title: "Add your ingredients", desc: "Tell us what you have — we'll plan around it." },
              { step: "2️⃣", title: "Set meal time", desc: "Choose when you'd like to get your daily plan." },
              { step: "3️⃣", title: "Get WhatsApp recipes", desc: "Receive curated recipes every day on WhatsApp." },
            ].map((s, idx) => (
              <div key={s.title} className="flex-1">
                <div className="rounded-2xl bg-white/80 border border-slate-200 p-6 shadow-sm">
                  <div className="text-2xl">{s.step}</div>
                  <h3 className="mt-2 font-semibold text-slate-900">{s.title}</h3>
                  <p className="mt-1 text-sm text-slate-600">{s.desc}</p>
                </div>
                {idx < 2 && (
                  <div className="hidden md:block h-0.5 w-full my-6 bg-gradient-to-r from-emerald-500 to-green-600" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Call To Action */}
      <section id="cta" className="bg-gradient-to-r from-emerald-500 to-green-600 h-screen snap-start pt-24">
        <div className="max-w-6xl mx-auto px-4 h-full flex flex-col items-center justify-center text-center">
          <h3 className="reveal text-2xl md:text-3xl font-bold text-white">Ready to make meal planning effortless?</h3>
          <button
            onClick={() => navigate("/signup")}
            className="reveal mt-6 inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-emerald-700 hover:bg-emerald-50 shadow-md transition-all duration-200"
          >
            Sign Up Now
          </button>
        </div>
      </section>

      {/* Demo placeholder */}
      <section id="demo" className="h-screen snap-start pt-24">
        <div className="max-w-3xl mx-auto px-4 h-full flex items-center">
          <div className="reveal rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h4 className="font-semibold text-slate-900">Watch Demo</h4>
            <p className="mt-2 text-sm text-slate-600">Demo video coming soon. Meanwhile, explore features above.</p>
          </div>
        </div>
      </section>

      {/* Footer section (auto height, snap to bottom) */}
      <section className="snap-end pt-12">
        <MarketingFooter />
      </section>
    </div>
  );
}

export default Landing;