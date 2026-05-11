<template>
  <div class="filter-config">
    <h1 class="page-title glow-text">{{ t('filters.title') || 'Filter Configuration' }}</h1>

    <div class="config-sections">
      <!-- Scale Filters -->
      <section class="config-section glow-card">
        <h2>Scale Filters</h2>
        <div class="filter-row">
          <label>Min Trade Amount (USD)</label>
          <input v-model.number="config.minTradeUsd" type="number" class="glow-input" placeholder="10000" />
        </div>
        <div class="filter-row">
          <label>Min Portfolio Size (USD)</label>
          <input v-model.number="config.minPortfolioUsd" type="number" class="glow-input" placeholder="100000" />
        </div>
        <div class="filter-row">
          <label>Min Token Holdings</label>
          <input v-model.number="config.minHoldings" type="number" class="glow-input" placeholder="5" />
        </div>
      </section>

      <!-- Profitability -->
      <section class="config-section glow-card">
        <h2>Profitability</h2>
        <div class="filter-row">
          <label>Min Win Rate (%)</label>
          <input v-model.number="config.minWinRate" type="number" class="glow-input" placeholder="60" />
        </div>
        <div class="filter-row">
          <label>Min ROI Multiplier</label>
          <input v-model.number="config.minRoi" type="number" class="glow-input" placeholder="2.0" step="0.1" />
        </div>
        <div class="filter-row">
          <label>Min Total Profit (USD)</label>
          <input v-model.number="config.minProfit" type="number" class="glow-input" placeholder="50000" />
        </div>
      </section>

      <!-- Consistency -->
      <section class="config-section glow-card">
        <h2>Consistency</h2>
        <div class="filter-row">
          <label>Min Trade Count</label>
          <input v-model.number="config.minTrades" type="number" class="glow-input" placeholder="20" />
        </div>
        <div class="filter-row">
          <label>Active Period (days)</label>
          <input v-model.number="config.activeDays" type="number" class="glow-input" placeholder="90" />
        </div>
        <div class="filter-row">
          <label>Max Drawdown (%)</label>
          <input v-model.number="config.maxDrawdown" type="number" class="glow-input" placeholder="30" />
        </div>
      </section>

      <!-- Activity -->
      <section class="config-section glow-card">
        <h2>Activity</h2>
        <div class="filter-row">
          <label>Last Active (days ago)</label>
          <input v-model.number="config.lastActiveDays" type="number" class="glow-input" placeholder="7" />
        </div>
        <div class="filter-row">
          <label>Min Trades/Week</label>
          <input v-model.number="config.tradesPerWeek" type="number" class="glow-input" placeholder="3" />
        </div>
      </section>

      <!-- Chain/Token -->
      <section class="config-section glow-card">
        <h2>Chain & Token</h2>
        <div class="filter-row">
          <label>Chains</label>
          <div class="tag-selector">
            <button v-for="chain in availableChains" :key="chain"
              :class="['tag-btn', { active: config.chains.includes(chain) }]"
              @click="toggleChain(chain)">
              {{ chain }}
            </button>
          </div>
        </div>
        <div class="filter-row">
          <label>Tokens (comma separated)</label>
          <input v-model="config.tokens" type="text" class="glow-input" placeholder="ETH, BNB, SOL" />
        </div>
      </section>

      <!-- Auto Analysis -->
      <section class="config-section glow-card">
        <h2>Auto Analysis</h2>
        <div class="filter-row toggle-row">
          <label>Enable Auto Analysis</label>
          <button :class="['toggle-btn', { active: config.autoAnalyze }]" @click="config.autoAnalyze = !config.autoAnalyze">
            {{ config.autoAnalyze ? 'ON' : 'OFF' }}
          </button>
        </div>
        <div v-if="config.autoAnalyze" class="filter-row">
          <label>Analysis Type</label>
          <select v-model="config.analysisType" class="glow-input">
            <option value="reverse">Reverse</option>
            <option value="forward">Forward</option>
            <option value="both">Both</option>
          </select>
        </div>
      </section>

      <!-- Notifications -->
      <section class="config-section glow-card">
        <h2>Notifications</h2>
        <div class="filter-row toggle-row">
          <label>Enable Notifications</label>
          <button :class="['toggle-btn', { active: config.notify }]" @click="config.notify = !config.notify">
            {{ config.notify ? 'ON' : 'OFF' }}
          </button>
        </div>
        <div v-if="config.notify" class="filter-row">
          <label>Notification Channels</label>
          <div class="tag-selector">
            <button v-for="ch in ['telegram', 'discord', 'email']" :key="ch"
              :class="['tag-btn', { active: config.notifyChannels.includes(ch) }]"
              @click="toggleChannel(ch)">
              {{ ch }}
            </button>
          </div>
        </div>
      </section>
    </div>

    <div class="config-actions">
      <GlowButton variant="primary" @click="saveConfig">Save Filter</GlowButton>
      <GlowButton variant="ghost" @click="$router.back()">Cancel</GlowButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import GlowButton from '@/components/common/GlowButton.vue'

const { t } = useI18n()

const availableChains = ['BSC', 'Ethereum', 'Solana', 'Arbitrum', 'Polygon', 'Base']

const config = reactive({
  minTradeUsd: 10000,
  minPortfolioUsd: 100000,
  minHoldings: 5,
  minWinRate: 60,
  minRoi: 2.0,
  minProfit: 50000,
  minTrades: 20,
  activeDays: 90,
  maxDrawdown: 30,
  lastActiveDays: 7,
  tradesPerWeek: 3,
  chains: ['BSC'] as string[],
  tokens: '',
  autoAnalyze: false,
  analysisType: 'reverse',
  notify: false,
  notifyChannels: [] as string[]
})

function toggleChain(chain: string) {
  const idx = config.chains.indexOf(chain)
  if (idx >= 0) config.chains.splice(idx, 1)
  else config.chains.push(chain)
}

function toggleChannel(ch: string) {
  const idx = config.notifyChannels.indexOf(ch)
  if (idx >= 0) config.notifyChannels.splice(idx, 1)
  else config.notifyChannels.push(ch)
}

function saveConfig() {
  // TODO: save to backend
  console.log('Saving config:', config)
}
</script>

<style scoped>
.filter-config { padding: 24px; max-width: 900px; margin: 0 auto; }
.page-title { font-size: 24px; font-family: var(--font-mono); margin-bottom: 24px; color: var(--accent); }
.config-sections { display: flex; flex-direction: column; gap: 16px; }
.config-section { padding: 20px; }
.config-section h2 { font-size: 15px; color: var(--text-primary); margin-bottom: 16px; font-weight: 600; }
.filter-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.filter-row label { font-size: 13px; color: var(--text-secondary); }
.glow-input { padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-family: var(--font-mono); font-size: 13px; width: 200px; }
.glow-input:focus { border-color: var(--accent); outline: none; box-shadow: 0 0 8px rgba(0,229,255,0.2); }
.tag-selector { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.tag-btn { font-size: 11px; padding: 4px 10px; border-radius: 12px; border: 1px solid var(--border); background: transparent; color: var(--text-muted); cursor: pointer; transition: all 0.2s; }
.tag-btn:hover { border-color: var(--accent); }
.tag-btn.active { background: rgba(0,229,255,0.15); border-color: var(--accent); color: var(--accent); }
.toggle-row { height: 40px; }
.toggle-btn { font-size: 12px; padding: 4px 16px; border-radius: 12px; border: 1px solid var(--border); background: transparent; color: var(--text-muted); cursor: pointer; font-family: var(--font-mono); transition: all 0.2s; }
.toggle-btn.active { background: rgba(0,255,136,0.15); border-color: #00ff88; color: #00ff88; }
.config-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; }
</style>
