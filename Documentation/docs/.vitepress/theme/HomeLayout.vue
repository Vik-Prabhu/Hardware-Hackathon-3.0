<template>
  <Layout>
    <template #home-features-after>
      <div class="custom-home" v-if="frontmatter.layout === 'home'">

        <!-- Quick Start Terminal -->
        <section class="quickstart-section">
          <h2 class="section-heading">Quick Start</h2>
          <p class="section-subtitle">Get up and running in seconds.</p>
          <div class="terminal">
            <div class="terminal-header">
              <span class="terminal-dot red"></span>
              <span class="terminal-dot yellow"></span>
              <span class="terminal-dot green"></span>
              <span class="terminal-title">terminal</span>
            </div>
            <div class="terminal-body">
              <div v-for="(cmd, i) in commands" :key="i" class="terminal-line"
                   :style="{ animationDelay: i * 0.2 + 's' }">
                <span class="terminal-prompt">$</span>
                <span class="terminal-cmd">{{ cmd.text }}</span>
                <span v-if="cmd.comment" class="terminal-comment"> # {{ cmd.comment }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Interactive Section Cards -->
        <section class="explore-section">
          <h2 class="section-heading">Explore Documentation</h2>
          <p class="section-subtitle">Dive into the details of our project across every layer.</p>
          <div class="explore-grid">
            <a v-for="(card, i) in cards" :key="i"
               :href="card.link"
               class="explore-card"
               :style="{ animationDelay: i * 0.1 + 's' }">
              <div class="card-icon-wrap" :style="{ background: card.gradient }">
                <span class="card-icon">{{ card.icon }}</span>
              </div>
              <h3>{{ card.title }}</h3>
              <p>{{ card.description }}</p>
              <span class="card-arrow">→</span>
            </a>
          </div>
        </section>



      </div>
    </template>
  </Layout>
</template>

<script setup>
import { useData } from 'vitepress'
import Theme from 'vitepress/theme'

const { Layout } = Theme
const { frontmatter } = useData()

const commands = [
  { text: 'git clone https://github.com/team-robomanipal/project-name.git', comment: 'Clone the repo' },
  { text: 'cd project-name && pip install -r requirements.txt', comment: 'Install dependencies' },
  { text: 'python main.py', comment: 'Run the project' },
]

const cards = [
  {
    icon: '📖',
    title: 'Introduction',
    description: 'Project overview and team behind the build.',
    link: '/introduction/overview',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    icon: '🔧',
    title: 'Hardware',
    description: 'Mechanical design, electronics, and BOM breakdown.',
    link: '/hardware/mechanical',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  },
  {
    icon: '💻',
    title: 'Software',
    description: 'Setup, code structure, and communication protocols.',
    link: '/software/setup',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  },
  {
    icon: '📊',
    title: 'Market Research',
    description: 'Industry analysis, competitors, and market opportunity.',
    link: '/research/market-research',
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  },
  {
    icon: '🔬',
    title: 'Case Study',
    description: 'Problem, solution, implementation, and impact.',
    link: '/research/case-study',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  },
  {
    icon: '🧪',
    title: 'Testing & Results',
    description: 'Methodology and discussion of outcomes.',
    link: '/results/methodology',
    gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
  },
]
</script>

<style scoped>
/* ---- Custom Home Sections ---- */
.custom-home {
  max-width: 1152px;
  margin: 0 auto;
  padding: 0 24px;
}

.section-heading {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-subtitle {
  text-align: center;
  color: var(--vp-c-text-2);
  margin-bottom: 40px;
  font-size: 1.1rem;
}

/* ---- Quick Start Terminal ---- */
.quickstart-section {
  margin: 48px 0 64px;
}

.terminal {
  max-width: 720px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  background: #1e1e2e;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
  animation: fadeSlideUp 0.5s ease both;
}

.terminal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #181825;
}

.terminal-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.terminal-dot.red { background: #f38ba8; }
.terminal-dot.yellow { background: #f9e2af; }
.terminal-dot.green { background: #a6e3a1; }

.terminal-title {
  margin-left: 8px;
  font-size: 0.78rem;
  color: #6c7086;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.terminal-body {
  padding: 20px 24px;
}

.terminal-line {
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-size: 0.88rem;
  line-height: 2;
  color: #cdd6f4;
  animation: fadeSlideUp 0.5s ease both;
  white-space: nowrap;
  overflow-x: auto;
}

.terminal-prompt {
  color: #a6e3a1;
  margin-right: 10px;
  font-weight: 700;
  user-select: none;
}

.terminal-cmd {
  color: #cdd6f4;
}

.terminal-comment {
  color: #585b70;
  font-style: italic;
}

/* ---- Explore Cards Section ---- */
.explore-section {
  margin: 64px 0;
}

.explore-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.explore-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 28px 24px;
  border-radius: 16px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  text-decoration: none;
  color: inherit;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  animation: fadeSlideUp 0.6s ease both;
  overflow: hidden;
}

.explore-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.4s ease;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(102,126,234,0.05), rgba(118,75,162,0.05));
}

.explore-card:hover::before {
  opacity: 1;
}

.explore-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(0,0,0,0.1);
  border-color: var(--vp-c-brand-1);
}

.card-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.card-icon {
  font-size: 1.5rem;
}

.explore-card h3 {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.explore-card p {
  font-size: 0.92rem;
  color: var(--vp-c-text-2);
  line-height: 1.5;
  flex: 1;
}

.card-arrow {
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-size: 1.2rem;
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.3s ease;
  color: var(--vp-c-brand-1);
}

.explore-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(0);
}


/* ---- Animations ---- */
@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
