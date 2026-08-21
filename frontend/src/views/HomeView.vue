<template>
  <div>
    <div class="text-center mt-8 mb-10">
      <div class="tag purple mb-4">GLOBAL INTELLIGENCE · v0.1 MVP</div>
      <div class="hero-title">全球智能获客 OS</div>
      <div class="hero-sub">Find Demand · Find Opportunity · Find Customers · 找需求 → 找机会 → 找客户</div>
    </div>

    <div class="card mb-8">
      <div class="mb-3" style="color:#9ca3af; font-weight:600; font-size:15px;">你想寻找什么？</div>
      <input type="text" v-model="query" @keydown.enter="startSearch"
        :placeholder="placeholderExamples[exampleIdx]" />
      <div class="mt-3 flex flex-wrap">
        <span class="tag gray mr-2" style="margin-right:8px;">示例：</span>
        <button v-for="(e, i) in placeholderExamples" :key="i" class="chip-option small"
          style="margin-right:8px; margin-bottom:8px; padding:4px 10px; font-size:12px;"
          @click="query = e">{{ e }}</button>
      </div>

      <hr class="divider" />

      <div class="mb-2" style="color:#9ca3af; font-weight:600;">搜索模式</div>
      <div class="grid cols-7 mb-4" style="row-gap:10px;">
        <button v-for="m in modes" :key="m.value"
          :class="['chip-option', mode === m.value ? 'active' : '']"
          @click="mode = m.value">
          <span class="t">{{ m.label }}</span>
          <span class="d">{{ m.description }}</span>
        </button>
      </div>

      <div class="mb-2" style="color:#9ca3af; font-weight:600;">
        平台 (已选 {{ selectedPlatforms.length }} / {{ platforms.length }})
      </div>
      <div class="flex flex-wrap mb-4" style="gap:6px;">
        <button class="chip-option small" style="padding:4px 10px; font-size:12px;"
          @click="selectAllTier1">选择 Tier 1</button>
        <button class="chip-option small ghost" style="padding:4px 10px; font-size:12px;"
          @click="selectedPlatforms = []">清空</button>
      </div>
      <div class="flex flex-wrap" style="gap:8px;">
        <label v-for="p in platforms" :key="p.name"
          :class="['chip-option', selectedPlatforms.includes(p.name) ? 'active' : '']"
          style="padding:6px 12px; font-size:13px;">
          <input type="checkbox" :checked="selectedPlatforms.includes(p.name)"
            @change="togglePlatform(p.name)" style="display:none;" />
          <span class="t">{{ p.display_name }}</span>
          <span class="d">{{ tierLabel(p.tier) }}</span>
        </label>
      </div>

      <hr class="divider" />

      <div class="flex-between">
        <div class="flex flex-wrap" style="gap:8px;">
          <button class="btn secondary small" :disabled="!query || loadingExpand"
            @click="previewKeywords">🧠 预览扩展关键词 ({{ expandedKeywords.length }})</button>
        </div>
        <button class="btn" @click="startSearch" :disabled="!query.trim() || creating">
          <span v-if="creating">正在创建任务...</span>
          <span v-else>🚀 开始智能研究</span>
        </button>
      </div>

      <div v-if="expandedKeywords.length" class="mt-4">
        <div class="mb-2" style="color:#9ca3af; font-size:13px;">扩展关键词 Top 30：</div>
        <div class="flex flex-wrap" style="gap:6px;">
          <span v-for="(k, i) in expandedKeywords.slice(0, 30)" :key="i" class="tag blue">{{ k }}</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="flex-between mb-4">
        <div style="font-weight:700; font-size:18px;">📋 最近任务</div>
        <button class="btn ghost small" @click="refreshHistory">🔄 刷新</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>搜索主题</th>
            <th>模式</th>
            <th>状态</th>
            <th>进度</th>
            <th>高意向</th>
            <th>时间</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="tasks.length === 0">
            <td colspan="8" style="text-align:center; padding:30px; color:#6b7280;">暂无任务，请在上方创建。</td>
          </tr>
          <tr v-for="t in tasks" :key="t.id">
            <td class="mono">#{{ t.id }}</td>
            <td style="max-width:300px;">{{ t.query }}</td>
            <td><span class="tag gray">{{ modeLabel(t.search_mode) }}</span></td>
            <td><span :class="['tag', statusClass(t.status)]">{{ statusLabel(t.status) }}</span></td>
            <td style="min-width:140px;">
              <div class="progress-wrap">
                <div class="progress-bar" :style="{ width: (t.progress || 0) + '%' }"></div>
              </div>
              <div style="font-size:11px; color:#6b7280; margin-top:2px;">
                {{ (t.progress || 0).toFixed(1) }}% · {{ t.current_step }}
              </div>
            </td>
            <td class="score" :class="t.total_high_intent_leads > 0 ? 'hi' : 'lo'">{{ t.total_high_intent_leads }}</td>
            <td style="font-size:12px; color:#9ca3af;">
              {{ formatDate(t.created_at) }}
            </td>
            <td>
              <button class="btn small secondary" @click="openTask(t.id)">查看</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  listSearchModes, listPlatforms, expandKeywords, createTask, listTasks,
} from '../api'

const emit = defineEmits(['run-task', 'open-task'])

const query = ref('日本跨境电商卖家')
const mode = ref('family_bucket')
const modes = ref([])
const platforms = ref([])
const selectedPlatforms = ref([])
const expandedKeywords = ref([])
const loadingExpand = ref(false)
const creating = ref(false)
const tasks = ref([])
const exampleIdx = ref(0)
const placeholderExamples = [
  '日本跨境电商卖家',
  'AI 客服 SaaS 客户',
  '正在招聘营销的出海公司',
  'Shopify 独立站 DTC 品牌',
  '欧洲市场新能源储能机会',
]

let exT = null
onMounted(() => {
  listSearchModes().then(d => modes.value = d)
  listPlatforms().then(d => {
    platforms.value = d
    selectedPlatforms.value = d.filter(p => p.tier === 'tier_1').map(p => p.name)
  })
  refreshHistory()
  exT = setInterval(() => exampleIdx.value = (exampleIdx.value + 1) % placeholderExamples.length, 4000)
})

watch(() => query.value, () => { expandedKeywords.value = [] })

const selectAllTier1 = () => {
  selectedPlatforms.value = platforms.value.filter(p => p.tier === 'tier_1').map(p => p.name)
}
const togglePlatform = (n) => {
  const i = selectedPlatforms.value.indexOf(n)
  if (i >= 0) selectedPlatforms.value.splice(i, 1)
  else selectedPlatforms.value.push(n)
}
const tierLabel = (t) => ({ tier_1: 'Tier 1 · 核心', tier_2: 'Tier 2 · 重要', tier_3: 'Tier 3 · 补充' }[t] || t)
const modeLabel = (m) => {
  const found = modes.value.find(x => x.value === m)
  return found ? found.label : m
}
const statusLabel = (s) => ({ pending: '等待', running: '执行中', paused: '暂停', completed: '完成', failed: '失败', partial: '部分完成' }[s] || s)
const statusClass = (s) => ({ pending: 'gray', running: 'blue', paused: 'yellow', completed: 'green', failed: 'red', partial: 'yellow' }[s] || 'gray')
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'

const previewKeywords = async () => {
  if (!query.value.trim()) return
  loadingExpand.value = true
  try {
    const r = await expandKeywords(query.value.trim(), mode.value)
    expandedKeywords.value = r.keywords || []
  } finally { loadingExpand.value = false }
}

const startSearch = async () => {
  if (!query.value.trim()) return
  creating.value = true
  try {
    const task = await createTask(query.value.trim(), mode.value, selectedPlatforms.value)
    emit('run-task', task)
    await refreshHistory()
  } finally { creating.value = false }
}
const refreshHistory = async () => {
  try { tasks.value = await listTasks(50) } catch (e) { /* ignore */ }
}
const openTask = (id) => emit('open-task', id)
</script>
