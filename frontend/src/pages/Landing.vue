<template>
  <div class="landing">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-bg">
        <div class="star-field" />
        <div class="nebula" />
      </div>
      <div class="hero-content">
        <h1 class="hero-title glow-text">Wind Motion</h1>
        <p class="hero-subtitle">AI-Powered Whale Intelligence. Decode the movements that shape markets.</p>
        <div class="hero-cta">
          <GlowButton variant="primary" @click="$router.push('/dashboard')">Enter Dashboard</GlowButton>
          <GlowButton variant="ghost" @click="scrollToDemo">Watch Demo</GlowButton>
        </div>
        <div class="hero-metrics">
          <div class="metric">
            <span class="metric-value mono-number">12,847</span>
            <span class="metric-label">Whales Tracked</span>
          </div>
          <div class="metric">
            <span class="metric-value mono-number">$2.4B</span>
            <span class="metric-label">Volume Monitored</span>
          </div>
          <div class="metric">
            <span class="metric-value mono-number">73%</span>
            <span class="metric-label">Prediction Accuracy</span>
          </div>
          <div class="metric">
            <span class="metric-value mono-number">5</span>
            <span class="metric-label">Chains Supported</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 5-Step Visualization -->
    <section class="steps-section" ref="demoSection">
      <h2 class="section-title">How It Works</h2>
      <p class="section-desc">Five-stage AI analysis pipeline that turns raw blockchain data into actionable intelligence.</p>

      <div class="steps-pipeline">
        <div v-for="(step, i) in pipelineSteps" :key="i" class="pipeline-step" :class="{ active: activeStep === i }" @click="activeStep = i">
          <div class="step-number">{{ i + 1 }}</div>
          <div class="step-icon">{{ step.icon }}</div>
          <h3 class="step-title">{{ step.title }}</h3>
          <p class="step-desc">{{ step.desc }}</p>
        </div>
      </div>

      <div class="step-detail glow-card">
        <div class="detail-visual">
          <div class="visual-placeholder" :style="{ background: pipelineSteps[activeStep].color }">
            <span class="visual-icon">{{ pipelineSteps[activeStep].icon }}</span>
          </div>
        </div>
        <div class="detail-content">
          <h3>{{ pipelineSteps[activeStep].title }}</h3>
          <p>{{ pipelineSteps[activeStep].detail }}</p>
          <div class="detail-stats">
            <div v-for="stat in pipelineSteps[activeStep].stats" :key="stat.label" class="detail-stat">
              <span class="stat-value mono-number">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Data Metrics -->
    <section class="data-section">
      <h2 class="section-title">Platform Metrics</h2>
      <div class="data-grid">
        <div v-for="metric in platformMetrics" :key="metric.label" class="data-card glow-card">
          <span class="data-icon">{{ metric.icon }}</span>
          <span class="data-value mono-number glow-text">{{ metric.value }}</span>
          <span class="data-label">{{ metric.label }}</span>
          <span class="data-trend" :class="metric.trend">{{ metric.trendValue }}</span>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title glow-text">Start Tracking Whales Today</h2>
        <p class="cta-desc">Join thousands of traders using AI-powered whale intelligence to gain an edge.</p>
        <GlowButton variant="primary" @click="$router.push('/dashboard')">Get Started Free</GlowButton>
      </div>
    </section>

    <footer class="landing-footer">
      <span class="footer-text">Wind Motion © 2026 — Powered by AI</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import GlowButton from '@/components/common/GlowButton.vue'

const activeStep = ref(0)
const demoSection = ref<HTMLElement>()

function scrollToDemo() {
  demoSection.value?.scrollIntoView({ behavior: 'smooth' })
}

const pipelineSteps = [
  {
    icon: '🕸️',
    title: 'Causal Graph Construction',
    desc: 'Build a causal graph from on-chain data using multi-agent review.',
    detail: 'Our AI agents analyze blockchain transactions, smart contract interactions, and token flows to construct a comprehensive causal graph. Multiple reviewer agents cross-validate the graph structure, ensuring accuracy through adversarial review.',
    color: 'rgba(0,229,255,0.1)',
    stats: [
      { value: '32', label: 'Avg Nodes' },
      { value: '39', label: 'Avg Edges' },
      { value: '70s', label: 'Build Time' }
    ]
  },
  {
    icon: '🔗',
    title: 'Event Chain Analysis',
    desc: 'Trace the sequence of events that led to whale decisions.',
    detail: 'Map the temporal sequence of on-chain events, social signals, and market conditions. Each event is analyzed by specialized agents that provide probability estimates based on historical patterns and current context.',
    color: 'rgba(124,58,237,0.1)',
    stats: [
      { value: '6-12', label: 'Events/Chain' },
      { value: '4', label: 'Agent Types' },
      { value: '72%', label: 'Avg Confidence' }
    ]
  },
  {
    icon: '📊',
    title: 'Probability Pricing',
    desc: 'Aggregate agent estimates into a calibrated probability.',
    detail: 'Multiple agents provide independent probability estimates. These are aggregated using a calibrated ensemble method that accounts for agent expertise, historical accuracy, and current market regime. Standard deviation captures uncertainty.',
    color: 'rgba(0,255,136,0.1)',
    stats: [
      { value: '72.8%', label: 'Avg Probability' },
      { value: '±15%', label: 'Avg Std Dev' },
      { value: '<5%', label: 'Calibration Error' }
    ]
  },
  {
    icon: '⚖️',
    title: 'Deliberation',
    desc: 'Agents debate when estimates diverge beyond threshold.',
    detail: 'When agent estimates diverge by more than 30%, a structured deliberation process is triggered. Agents challenge each other\'s reasoning, leading to refined estimates. The referee agent mediates and produces a final ruling.',
    color: 'rgba(255,170,0,0.1)',
    stats: [
      { value: '35%', label: 'Trigger Rate' },
      { value: '2', label: 'Avg Rounds' },
      { value: '12%', label: 'Avg Adjustment' }
    ]
  },
  {
    icon: '📄',
    title: 'Report Generation',
    desc: 'Synthesize all findings into an actionable intelligence report.',
    detail: 'The final report combines causal analysis, probability estimates, and deliberation outcomes into a clear, actionable summary. Includes key factors, risk assessment, and recommended actions with confidence levels.',
    color: 'rgba(255,51,102,0.1)',
    stats: [
      { value: '423s', label: 'Total Time' },
      { value: '¥3.2', label: 'Avg Cost' },
      { value: '5', label: 'Key Factors' }
    ]
  }
]

const platformMetrics = [
  { icon: '🐋', value: '12,847', label: 'Whales Tracked', trend: 'up', trendValue: '+234 this week' },
  { icon: '📊', value: '89,241', label: 'Analyses Completed', trend: 'up', trendValue: '+1,247 this week' },
  { icon: '🎯', value: '73.2%', label: 'Prediction Accuracy', trend: 'up', trendValue: '+2.1% vs last month' },
  { icon: '⚡', value: '423s', label: 'Avg Analysis Time', trend: 'down', trendValue: '-15s vs last month' },
  { icon: '💰', value: '$2.4B', label: 'Volume Monitored', trend: 'up', trendValue: '+$180M this week' },
  { icon: '🔗', value: '5', label: 'Chains Supported', trend: 'neutral', trendValue: 'BSC, ETH, SOL, ARB, MATIC' }
]
</script>

<style scoped>
.landing { min-height: 100vh; background: #050a14; overflow-x: hidden; }

/* Hero */
.hero { position: relative; min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; }
.hero-bg { position: absolute; inset: 0; overflow: hidden; }
.star-field { position: absolute; inset: 0; background: radial-gradient(2px 2px at 20px 30px, rgba(0,229,255,0.3), transparent),
  radial-gradient(2px 2px at 40px 70px, rgba(0,229,255,0.2), transparent),
  radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.3), transparent),
  radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.2), transparent),
  radial-gradient(2px 2px at 160px 30px, rgba(0,229,255,0.15), transparent);
  background-size: 200px 100px; animation: drift 60s linear infinite; }
.nebula { position: absolute; top: 20%; left: 30%; width: 400px; height: 400px; background: radial-gradient(ellipse, rgba(0,229,255,0.05), transparent 70%); filter: blur(60px); }
@keyframes drift { to { background-position: 200px 100px; } }

.hero-content { position: relative; z-index: 1; max-width: 800px; padding: 0 24px; }
.hero-title { font-size: 64px; font-family: var(--font-mono); font-weight: 700; color: #00e5ff; text-shadow: 0 0 40px rgba(0,229,255,0.4), 0 0 80px rgba(0,229,255,0.2); margin-bottom: 16px; }
.hero-subtitle { font-size: 20px; color: rgba(255,255,255,0.7); line-height: 1.6; margin-bottom: 32px; }
.hero-cta { display: flex; gap: 16px; justify-content: center; margin-bottom: 48px; }
.hero-metrics { display: flex; gap: 40px; justify-content: center; flex-wrap: wrap; }
.metric { text-align: center; }
.metric-value { display: block; font-size: 28px; font-weight: 700; color: #00e5ff; }
.metric-label { font-size: 12px; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 1px; }

/* Steps */
.steps-section { padding: 80px 24px; max-width: 1100px; margin: 0 auto; }
.section-title { font-size: 32px; font-family: var(--font-mono); color: #00e5ff; text-align: center; margin-bottom: 8px; }
.section-desc { font-size: 16px; color: rgba(255,255,255,0.6); text-align: center; margin-bottom: 48px; }
.steps-pipeline { display: flex; gap: 12px; margin-bottom: 32px; overflow-x: auto; padding-bottom: 8px; }
.pipeline-step { flex: 1; min-width: 160px; padding: 20px 16px; background: rgba(0,229,255,0.03); border: 1px solid rgba(0,229,255,0.1); border-radius: 8px; text-align: center; cursor: pointer; transition: all 0.3s; }
.pipeline-step:hover { border-color: rgba(0,229,255,0.3); }
.pipeline-step.active { border-color: #00e5ff; background: rgba(0,229,255,0.08); box-shadow: 0 0 20px rgba(0,229,255,0.15); }
.step-number { font-size: 10px; color: rgba(255,255,255,0.3); font-family: var(--font-mono); margin-bottom: 8px; }
.step-icon { font-size: 28px; margin-bottom: 8px; }
.step-title { font-size: 13px; color: #e0e0e0; font-weight: 600; margin-bottom: 4px; }
.step-desc { font-size: 11px; color: rgba(255,255,255,0.5); line-height: 1.4; }
.step-detail { display: grid; grid-template-columns: 200px 1fr; gap: 24px; padding: 24px; }
.detail-visual { display: flex; align-items: center; justify-content: center; }
.visual-placeholder { width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.visual-icon { font-size: 48px; }
.detail-content h3 { font-size: 20px; color: #e0e0e0; margin-bottom: 8px; }
.detail-content p { font-size: 14px; color: rgba(255,255,255,0.6); line-height: 1.6; margin-bottom: 16px; }
.detail-stats { display: flex; gap: 24px; }
.detail-stat { text-align: center; }
.detail-stat .stat-value { display: block; font-size: 22px; font-weight: 700; color: #00e5ff; }
.detail-stat .stat-label { font-size: 11px; color: rgba(255,255,255,0.5); text-transform: uppercase; }

/* Data */
.data-section { padding: 80px 24px; max-width: 1100px; margin: 0 auto; }
.data-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.data-card { text-align: center; padding: 24px; background: rgba(0,229,255,0.03); border: 1px solid rgba(0,229,255,0.1); }
.data-icon { font-size: 28px; display: block; margin-bottom: 8px; }
.data-value { font-size: 28px; font-weight: 700; color: #00e5ff; display: block; margin-bottom: 4px; }
.data-label { font-size: 12px; color: rgba(255,255,255,0.5); display: block; margin-bottom: 8px; text-transform: uppercase; }
.data-trend { font-size: 11px; font-family: var(--font-mono); }
.data-trend.up { color: #00ff88; }
.data-trend.down { color: #00e5ff; }
.data-trend.neutral { color: rgba(255,255,255,0.4); }

/* CTA */
.cta-section { padding: 80px 24px; text-align: center; }
.cta-title { font-size: 36px; font-family: var(--font-mono); color: #00e5ff; margin-bottom: 12px; }
.cta-desc { font-size: 16px; color: rgba(255,255,255,0.6); margin-bottom: 24px; }

/* Footer */
.landing-footer { text-align: center; padding: 24px; border-top: 1px solid rgba(0,229,255,0.1); }
.footer-text { font-size: 12px; color: rgba(255,255,255,0.3); }
</style>
