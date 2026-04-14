<template>
  <div class="gn-home" ref="root">

    <!-- ═══════════ NAVIGATION ═══════════ -->
    <nav class="gn-nav" :class="{ scrolled: scrolled }">
      <div class="gn-nav-inner">
        <a href="/" class="gn-logo">
          <span class="gn-logo-leaf">🌿</span>
          <span class="gn-logo-text">Green<span class="accent">Node</span></span>
        </a>
        <div class="gn-nav-links">
          <a href="/" class="gn-nl active">Home</a>
          <a href="/research/market-research" class="gn-nl">Docs</a>
          <a href="/hardware/mechanical" class="gn-nl">Hardware</a>
          <a href="/software/setup" class="gn-nl">Software</a>
          <a href="/dashboard/index.html" class="gn-nl gn-cta" @click.prevent="goToDashboard">Dashboard →</a>
        </div>
        <button class="gn-hamburger" @click="menuOpen = !menuOpen" aria-label="Menu">
          <span :class="{ open: menuOpen }"></span>
        </button>
      </div>
      <div class="gn-mobile" :class="{ open: menuOpen }">
        <a href="/" class="gn-ml" @click="menuOpen=false">Home</a>
        <a href="/research/market-research" class="gn-ml" @click="menuOpen=false">Docs</a>
        <a href="/hardware/mechanical" class="gn-ml" @click="menuOpen=false">Hardware</a>
        <a href="/software/setup" class="gn-ml" @click="menuOpen=false">Software</a>
        <a href="/dashboard/index.html" class="gn-ml" @click.prevent="goToDashboard">Dashboard →</a>
      </div>
    </nav>

    <!-- ═══════════ HERO ═══════════ -->
    <section class="gn-hero">
      <div class="gn-hero-bg">
        <img src="/hero-bonsai.jpg" alt="Green Node sensors monitoring bonsai plants" />
        <div class="gn-hero-overlay"></div>
      </div>

      <div class="gn-hero-content">
        <div class="gn-badge">
          <span class="gn-badge-dot"></span>
          Team Robomanipal — Hardware Hackathon 3.0 - Team 6
        </div>

        <h1 class="gn-hero-title">
          <span class="gn-t1">GREEN</span>
          <span class="gn-t2">NODE</span>
        </h1>

        <p class="gn-hero-sub">AI-Optimized Growth Monitoring for Plants</p>

        <div class="gn-hero-btns">
          <a href="/dashboard/index.html" class="gn-btn-primary" @click.prevent="goToDashboard">
            <span>Open Dashboard</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </a>
          <a href="/research/market-research" class="gn-btn-secondary">Explore Docs</a>
        </div>
      </div>

      <div class="gn-scroll-hint">
        <div class="gn-scroll-line"></div>
        <span>Scroll</span>
      </div>
    </section>

    <!-- ═══════════ FEATURES ═══════════ -->
    <section class="gn-features">
      <div class="gn-container">
        <div class="gn-sec-head">
          <span class="gn-tag">What We Built</span>
          <h2 class="gn-sec-title">A Complete <span class="gn-grad">Ecosystem</span></h2>
          <p class="gn-sec-desc">Every component engineered for precision — from soil sensors to AI-powered health analysis.</p>
        </div>
        <div class="gn-feat-grid">
          <div class="gn-fcard" v-for="(f, i) in features" :key="i">
            <div class="gn-fnum">{{ String(i+1).padStart(2,'0') }}</div>
            <div class="gn-fico">{{ f.icon }}</div>
            <h3 class="gn-ftitle">{{ f.title }}</h3>
            <p class="gn-fdesc">{{ f.desc }}</p>
            <a :href="f.link" class="gn-flink" @click="handleFeatureLink($event, f.link)">Learn More <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></a>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ PIPELINE ═══════════ -->
    <section class="gn-pipeline">
      <div class="gn-container">
        <div class="gn-sec-head">
          <span class="gn-tag">The Pipeline</span>
          <h2 class="gn-sec-title">How <span class="gn-grad">Green Node</span> Works</h2>
        </div>
        <div class="gn-pipe-wrap">
          <div class="gn-pstep" v-for="(s, i) in pipeline" :key="i">

            <div class="gn-pbody"><h4>{{ s.title }}</h4><p>{{ s.desc }}</p></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ TECH STACK ═══════════ -->
    <section class="gn-tech">
      <div class="gn-container">
        <div class="gn-sec-head">
          <span class="gn-tag">Built With</span>
          <h2 class="gn-sec-title">Our <span class="gn-grad">Tech Stack</span></h2>
        </div>
        <div class="gn-tech-grid">
          <div class="gn-tpill" v-for="(t, i) in techStack" :key="i">
            <span class="gn-ticon">{{ t.icon }}</span>
            <span>{{ t.name }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ CTA ═══════════ -->
    <section class="gn-cta-section">
      <div class="gn-container">
        <div class="gn-cta-box">
          <div class="gn-cta-glow"></div>
          <h2>Ready to Monitor Smarter?</h2>
          <p>Dive into the live dashboard or explore our full documentation.</p>
          <div class="gn-cta-btns">
            <a href="/dashboard/index.html" class="gn-btn-primary lg" @click.prevent="goToDashboard">
              <span>Open Live Dashboard</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </a>
            <a href="/software/setup" class="gn-btn-secondary lg">Setup Guide</a>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ FOOTER ═══════════ -->
    <footer class="gn-footer">
      <div class="gn-footer-inner">
        <div class="gn-footer-brand"><span>🌿</span> Green<span class="accent">Node</span></div>
        <p class="gn-footer-copy">Team Robomanipal · Hardware Hackathon 3.0 · 2026</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const scrolled = ref(false)
const menuOpen = ref(false)

/* ─── Hide ALL VitePress chrome on mount, restore on unmount ─── */
function hideVPChrome() {
  document.documentElement.classList.add('gn-home-active')
}
function showVPChrome() {
  document.documentElement.classList.remove('gn-home-active')
}

function onScroll() {
  scrolled.value = window.scrollY > 50
}

onMounted(() => {
  hideVPChrome()
  window.addEventListener('scroll', onScroll)
})

onUnmounted(() => {
  showVPChrome()
  window.removeEventListener('scroll', onScroll)
})

function goToDashboard() {
  menuOpen.value = false
  window.location.href = '/dashboard/index.html'
}

function handleFeatureLink(event, link) {
  if (link.includes('.html')) {
    event.preventDefault()
    window.location.href = link
  }
}

const features = [
  { icon: '🔧', title: 'Modular Hardware', desc: 'Cleanly engineered enclosures & PCBs for ESP32-C3 sensor nodes — snap-fit, weather-resistant, and field-ready.', link: '/hardware/mechanical' },
  { icon: '📡', title: 'Real-Time Telemetry', desc: 'WiFi-enabled nodes stream temperature, moisture, humidity & light data every 30 seconds via mDNS discovery.', link: '/software/protocols' },
  { icon: '📸', title: 'Visual Diagnostics', desc: 'ESP32-CAM nodes capture leaf images on demand, enabling AI-powered disease detection and growth tracking.', link: '/hardware/electronics' },
  { icon: '🤖', title: 'AI Health Advisory', desc: 'Gemini-powered analysis generates actionable care plans with multilingual support and voice playback.', link: '/software/code' },
  { icon: '📊', title: 'Live Dashboard', desc: 'A real-time web dashboard with animated charts, sensor timelines, and AI-generated daily action plans.', link: '/dashboard/index.html' },
  { icon: '📈', title: 'Market Validated', desc: 'Backed by thorough market research, competitor analysis, and a successful real-world bonsai nursery trial.', link: '/research/market-research' },
]

const pipeline = [
  { icon: '🌱', title: 'Sense', desc: 'ESP32-C3 nodes measure temperature, soil moisture, humidity, and light intensity in real time.' },
  { icon: '📶', title: 'Transmit', desc: 'Data is pushed over WiFi to the FastAPI backend via HTTP POST with mDNS discovery.' },
  { icon: '🗄️', title: 'Store', desc: 'The server logs readings in-memory with full historical timelines per node.' },
  { icon: '🧠', title: 'Analyze', desc: 'Gemini AI processes sensor data + leaf images to produce structured health advisories.' },
  { icon: '📱', title: 'Act', desc: 'The dashboard surfaces AI care plans, alerts, and multilingual voice guidance.' },
]

const techStack = [
  { icon: '⚡', name: 'ESP32-C3' },
  { icon: '📷', name: 'ESP32-CAM' },
  { icon: '🐍', name: 'FastAPI' },
  { icon: '🤖', name: 'Gemini AI' },
  { icon: '🌐', name: 'VitePress' },
  { icon: '📊', name: 'Chart.js' },
  { icon: '🗣️', name: 'Sarvam AI' },
  { icon: '🔌', name: 'mDNS' },
]
</script>

<style>
/* ═══════════════════════════════════════════════════════
   GLOBAL: Hide ALL VitePress chrome when home is active
   This MUST be unscoped to target VitePress elements
   ═══════════════════════════════════════════════════════ */
html.gn-home-active .VPNav,
html.gn-home-active .VPLocalNav,
html.gn-home-active .VPSidebar,
html.gn-home-active .VPFooter,
html.gn-home-active .VPDocFooter {
  display: none !important;
}

html.gn-home-active .VPContent {
  padding-top: 0 !important;
  margin: 0 !important;
}

html.gn-home-active .VPContent.has-sidebar {
  padding-left: 0 !important;
  margin-left: 0 !important;
}

html.gn-home-active .VPPage {
  padding: 0 !important;
}

html.gn-home-active .VPDoc,
html.gn-home-active .VPDoc .container,
html.gn-home-active .VPDoc .content,
html.gn-home-active .VPDoc .content-container {
  max-width: none !important;
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}

html.gn-home-active body,
html.gn-home-active .Layout {
  background: #071a12 !important;
}
</style>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

/* ═══════════ CORE ═══════════ */
.gn-home {
  --em: #10b981;
  --em-light: #34d399;
  --em-dark: #059669;
  --lime: #84cc16;
  --teal: #14b8a6;
  --sky: #06b6d4;
  --dark: #071a12;
  --dark-card: #0c2419;
  --dark-surf: #103023;
  --muted: #7dae96;
  --grad: linear-gradient(135deg, #10b981, #06b6d4, #84cc16);

  font-family: 'Inter', -apple-system, sans-serif;
  background: var(--dark);
  color: #f0fdf4;
  min-height: 100vh;
  overflow-x: hidden;
}

.gn-home *, .gn-home *::before, .gn-home *::after { box-sizing: border-box; }
.gn-home a { text-decoration: none; color: inherit; }
.gn-home img { display: block; max-width: 100%; }

/* ═══════════ GLASS NAV ═══════════ */
.gn-nav {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  width: calc(100% - 32px);
  max-width: 860px;
  border-radius: 60px;
  background: rgba(255,255,255,0.07);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.10);
  transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
}

.gn-nav.scrolled {
  background: rgba(7,26,18,0.92);
  border-color: rgba(16,185,129,0.18);
  box-shadow: 0 8px 40px rgba(0,0,0,0.5);
}

.gn-nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 28px;
}

.gn-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
}

.gn-logo-leaf { font-size: 1.3rem; }
.accent { color: var(--em); }

.gn-nav-links { display: flex; align-items: center; gap: 4px; }

.gn-nl {
  color: rgba(255,255,255,0.65);
  font-size: 0.88rem;
  font-weight: 500;
  padding: 8px 18px;
  border-radius: 30px;
  transition: all 0.25s ease;
}

.gn-nl:hover, .gn-nl.active {
  color: #fff;
  background: rgba(255,255,255,0.10);
}

.gn-nl.gn-cta {
  background: var(--em);
  color: var(--dark) !important;
  font-weight: 600;
}

.gn-nl.gn-cta:hover {
  background: var(--em-light);
  transform: translateY(-1px);
}

/* Hamburger */
.gn-hamburger {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  width: 28px;
  height: 20px;
  position: relative;
}

.gn-hamburger span,
.gn-hamburger span::before,
.gn-hamburger span::after {
  display: block;
  width: 100%;
  height: 2px;
  background: #fff;
  border-radius: 2px;
  transition: all 0.3s ease;
  position: absolute;
  left: 0;
}

.gn-hamburger span { top: 50%; transform: translateY(-50%); }
.gn-hamburger span::before { content: ''; top: -7px; }
.gn-hamburger span::after  { content: ''; top: 7px; }
.gn-hamburger span.open { background: transparent; }
.gn-hamburger span.open::before { transform: rotate(45deg); top: 0; }
.gn-hamburger span.open::after  { transform: rotate(-45deg); top: 0; }

.gn-mobile { display: none; flex-direction: column; padding: 0 20px 16px; gap: 4px; }
.gn-mobile.open { display: flex; }

.gn-ml {
  display: block;
  color: rgba(255,255,255,0.75);
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.gn-ml:hover { background: rgba(16,185,129,0.12); color: var(--em); }

/* ═══════════ HERO ═══════════ */
.gn-hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: flex-end;
  padding-bottom: 72px;
}

.gn-hero-bg {
  position: absolute;
  inset: 0;
}

.gn-hero-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
}

.gn-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg,
    rgba(7,26,18,0.18) 0%,
    rgba(7,26,18,0.35) 35%,
    rgba(7,26,18,0.72) 62%,
    rgba(7,26,18,0.97) 100%
  );
}

.gn-hero-content {
  position: relative;
  z-index: 2;
  padding: 0 56px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.gn-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: rgba(16,185,129,0.10);
  border: 1px solid rgba(16,185,129,0.22);
  padding: 7px 20px;
  border-radius: 40px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--em-light);
  margin-bottom: 28px;
  opacity: 0;
  animation: gnFadeUp .7s ease .1s forwards;
}

.gn-badge-dot {
  width: 7px;
  height: 7px;
  background: var(--em);
  border-radius: 50%;
  animation: gnPulse 2s ease infinite;
}

@keyframes gnPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.5); }
  50%     { box-shadow: 0 0 0 7px rgba(16,185,129,0); }
}

.gn-hero-title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 800;
  line-height: 0.95;
  margin-bottom: 24px;
  opacity: 0;
  animation: gnFadeUp .7s ease .2s forwards;
}

.gn-t1 {
  display: block;
  font-size: clamp(3.6rem, 8vw, 7.5rem);
  color: #fff;
  letter-spacing: -3px;
}

.gn-t2 {
  display: block;
  font-size: clamp(3.6rem, 8vw, 7.5rem);
  letter-spacing: -3px;
  background: var(--grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gn-hero-sub {
  font-size: clamp(1rem, 1.8vw, 1.35rem);
  color: rgba(255,255,255,0.55);
  max-width: 460px;
  line-height: 1.65;
  margin-bottom: 36px;
  opacity: 0;
  animation: gnFadeUp .7s ease .3s forwards;
}

.gn-hero-btns {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  opacity: 0;
  animation: gnFadeUp .7s ease .4s forwards;
}

/* Buttons */
.gn-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--em);
  color: var(--dark);
  font-weight: 700;
  font-size: 0.95rem;
  padding: 15px 30px;
  border-radius: 50px;
  transition: all .3s cubic-bezier(.16,1,.3,1);
  box-shadow: 0 4px 24px rgba(16,185,129,0.28);
}

.gn-btn-primary:hover {
  background: var(--em-light);
  color: var(--dark);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(16,185,129,0.4);
}

.gn-btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.06);
  color: #f0fdf4;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 15px 30px;
  border-radius: 50px;
  border: 1px solid rgba(255,255,255,0.12);
  transition: all .3s ease;
}

.gn-btn-secondary:hover {
  background: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.28);
}

.gn-btn-primary.lg, .gn-btn-secondary.lg { padding: 18px 38px; font-size: 1.05rem; }

/* Stats */
.gn-stats {
  display: flex;
  gap: 14px;
  margin-top: 44px;
  flex-wrap: wrap;
  opacity: 0;
  animation: gnFadeUp .7s ease .55s forwards;
}

.gn-stat {
  display: flex;
  align-items: center;
  gap: 11px;
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.07);
  padding: 12px 18px;
  border-radius: 14px;
  transition: all .3s ease;
}

.gn-stat:hover {
  background: rgba(16,185,129,0.07);
  border-color: rgba(16,185,129,0.18);
  transform: translateY(-2px);
}

.gn-stat-ico { font-size: 1.5rem; }
.gn-stat-info { display: flex; flex-direction: column; }
.gn-stat-val { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.95rem; }
.gn-stat-lbl { font-size: 0.72rem; color: var(--muted); font-weight: 500; }

/* Scroll hint */
.gn-scroll-hint {
  position: absolute;
  bottom: 28px;
  right: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  z-index: 2;
  color: rgba(255,255,255,0.35);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.gn-scroll-line {
  width: 1px;
  height: 44px;
  background: linear-gradient(180deg, transparent, var(--em));
  animation: gnScrollPulse 2s ease infinite;
}

@keyframes gnScrollPulse { 0%,100% { opacity: .3; } 50% { opacity: 1; } }

@keyframes gnFadeUp {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ═══════════ SHARED SECTION ═══════════ */
.gn-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 36px;
}

.gn-sec-head {
  text-align: center;
  margin-bottom: 56px;
}

.gn-tag {
  display: inline-block;
  background: rgba(16,185,129,0.09);
  border: 1px solid rgba(16,185,129,0.18);
  color: var(--em);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 5px 16px;
  border-radius: 30px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 18px;
}

.gn-sec-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(1.9rem, 3.8vw, 3rem);
  font-weight: 800;
  color: #f0fdf4;
  letter-spacing: -1px;
  margin-bottom: 14px;
}

.gn-grad {
  background: var(--grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gn-sec-desc {
  font-size: 1.05rem;
  color: var(--muted);
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.7;
}

/* ═══════════ FEATURES ═══════════ */
.gn-features {
  padding: 110px 0;
  position: relative;
}

.gn-features::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 560px;
  height: 560px;
  background: radial-gradient(circle, rgba(16,185,129,0.05) 0%, transparent 70%);
  pointer-events: none;
}

.gn-feat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.gn-fcard {
  position: relative;
  background: var(--dark-card);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 18px;
  padding: 32px 26px;
  transition: all .35s cubic-bezier(.16,1,.3,1);
  overflow: hidden;
}

.gn-fcard::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2.5px;
  background: var(--grad);
  opacity: 0;
  transition: opacity .3s ease;
}

.gn-fcard:hover {
  transform: translateY(-5px);
  border-color: rgba(16,185,129,0.18);
  box-shadow: 0 18px 50px rgba(0,0,0,0.28);
}

.gn-fcard:hover::after { opacity: 1; }

.gn-fnum {
  position: absolute;
  top: 16px; right: 20px;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2.6rem;
  font-weight: 800;
  color: rgba(255,255,255,0.025);
}

.gn-fico { font-size: 2.2rem; margin-bottom: 16px; }
.gn-ftitle { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; }
.gn-fdesc { font-size: 0.9rem; color: var(--muted); line-height: 1.7; margin-bottom: 18px; }

.gn-flink {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--em);
  font-size: 0.85rem;
  font-weight: 600;
  transition: gap .3s ease;
}

.gn-flink:hover { gap: 11px; }

/* ═══════════ PIPELINE ═══════════ */
.gn-pipeline {
  padding: 110px 0;
  background: var(--dark-card);
}

.gn-pipe-wrap {
  max-width: 660px;
  margin: 0 auto;
}

.gn-pstep {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  position: relative;
  padding-bottom: 42px;
}

.gn-pstep:last-child { padding-bottom: 0; }



.gn-pbody h4 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  margin: 3px 0 5px;
}

.gn-pbody p { font-size: 0.92rem; color: var(--muted); line-height: 1.6; }

/* ═══════════ TECH STACK ═══════════ */
.gn-tech { padding: 100px 0; }

.gn-tech-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.gn-tpill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--dark-card);
  border: 1px solid rgba(255,255,255,0.05);
  padding: 13px 22px;
  border-radius: 50px;
  font-size: 0.92rem;
  font-weight: 600;
  transition: all .3s ease;
}

.gn-tpill:hover {
  border-color: rgba(16,185,129,0.28);
  background: rgba(16,185,129,0.07);
  transform: translateY(-3px);
  box-shadow: 0 8px 22px rgba(0,0,0,0.22);
}

.gn-ticon { font-size: 1.15rem; }

/* ═══════════ CTA ═══════════ */
.gn-cta-section { padding: 110px 0; }

.gn-cta-box {
  position: relative;
  max-width: 780px;
  margin: 0 auto;
  text-align: center;
  padding: 72px 36px;
  background: var(--dark-card);
  border: 1px solid rgba(16,185,129,0.12);
  border-radius: 28px;
  overflow: hidden;
}

.gn-cta-glow {
  position: absolute;
  top: -70px;
  left: 50%;
  transform: translateX(-50%);
  width: 380px;
  height: 180px;
  background: radial-gradient(ellipse, rgba(16,185,129,0.13), transparent);
  pointer-events: none;
}

.gn-cta-box h2 {
  position: relative;
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(1.7rem, 3.4vw, 2.5rem);
  font-weight: 800;
  margin-bottom: 14px;
}

.gn-cta-box p {
  position: relative;
  font-size: 1.05rem;
  color: var(--muted);
  margin-bottom: 36px;
}

.gn-cta-btns {
  position: relative;
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
}

/* ═══════════ FOOTER ═══════════ */
.gn-footer {
  padding: 36px 0;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.gn-footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.gn-footer-brand {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 1.05rem;
}

.gn-footer-copy { font-size: 0.82rem; color: var(--muted); }

/* ═══════════ RESPONSIVE ═══════════ */
@media (max-width: 960px) {
  .gn-feat-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .gn-nav-links { display: none; }
  .gn-hamburger { display: block; }
  .gn-hero-content { padding: 0 22px; }
  .gn-hero { padding-bottom: 56px; }
  .gn-stats { flex-direction: column; gap: 10px; }
  .gn-stat { max-width: 200px; }
  .gn-feat-grid { grid-template-columns: 1fr; }
  .gn-container { padding: 0 18px; }
  .gn-scroll-hint { display: none; }
  .gn-footer-inner { flex-direction: column; gap: 12px; text-align: center; }
  .gn-cta-box { padding: 48px 22px; margin: 0 18px; }
}
</style>
