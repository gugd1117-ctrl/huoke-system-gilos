<template>
  <div>
    <div class="breadcrumb">
      <a @click="$emit('back')">← 返回首页</a>
      <span style="margin:0 8px;">/</span>
      <span>任务详情 #{{ taskId }}</span>
    </div>

    <div v-if="!task" class="card">加载中...</div>

    <template v-else>
      <div class="card mb-6">
        <div class="flex-between flex-wrap">
          <div>
            <div class="flex flex-wrap" style="gap:8px; margin-bottom:6px;">
              <span :class="['tag', statusClass(task.task.status)]">
                {{ statusLabel(task.task.status) }}
              </span>
              <span class="tag gray">{{ modeLabel(task.task.search_mode) }}</span>
              <span v-if="task.task.progress < 100" class="tag blue">
                {{ task.task.progress.toFixed(1) }}% · {{ task.task.current_step }}
              </span>
              <span v-if="cost.total_usd > 0" class="tag purple">
                成本 ${{ cost.total_usd.toFixed(3) }} / ¥{{ cost.total_cny.toFixed(2) }}
              </span>
            </div>
            <h2 style="margin:0; font-size:26px; font-weight:800;">{{ task.task.query }}</h2>
            <div style="color:#9ca3af; font-size:13px; margin-top:4px;">
              创建: {{ formatDate(task.task.created_at) }} ·
              开始: {{ formatDate(task.task.started_at) }} ·
              完成: {{ formatDate(task.task.completed_at) }}
            </div>
          </div>
          <div class="flex flex-wrap" style="gap:8px;">
            <button class="btn small ghost" @click="pollOnce">🔄 刷新</button>
            <button v-if="task.task.status === 'failed' || task.task.status === 'pending'"
              class="btn small" @click="retry">▶ 重新执行</button>
            <a class="btn small secondary" :href="reportMd" target="_blank">📄 Markdown 报告</a>
            <a class="btn small secondary" :href="reportHtml" target="_blank">🌐 HTML 报告</a>
            <a class="btn small" :href="xlsxUrl" target="_blank">📥 导出 Excel</a>
          </div>
        </div>

        <div class="progress-wrap mt-4">
          <div class="progress-bar" :style="{ width: task.task.progress + '%' }"></div>
        </div>

        <div class="grid cols-4 mt-6">
          <div>
            <div class="stat-num">{{ t('total_contents') }}</div>
            <div class="stat-label">发现内容</div>
          </div>
          <div>
            <div class="stat-num score hi">{{ t('total_high_intent_leads') }}</div>
            <div class="stat-label">🔥 高意向线索</div>
          </div>
          <div>
            <div class="stat-num">{{ t('total_companies') }}</div>
            <div class="stat-label">企业线索</div>
          </div>
          <div>
            <div class="stat-num">{{ t('total_demands') }}</div>
            <div class="stat-label">识别需求</div>
          </div>
          <div>
            <div class="stat-num">{{ t('total_company_opportunities') }}</div>
            <div class="stat-label">企业机会</div>
          </div>
          <div>
            <div class="stat-num">{{ t('total_trends') }}</div>
            <div class="stat-label">热门趋势</div>
          </div>
          <div>
            <div class="stat-num">{{ t('total_competitions') }}</div>
            <div class="stat-label">竞争机会</div>
          </div>
          <div>
            <div class="stat-num">{{ task.platforms.length }}</div>
            <div class="stat-label">平台接入</div>
          </div>
        </div>

        <hr class="divider" />

        <div style="font-weight:600; margin-bottom:10px;">📡 各平台执行状态</div>
        <div class="grid cols-3">
          <div v-for="p in task.platforms" :key="p.id"
            style="border:1px solid #374151; border-radius:12px; padding:14px; background:rgba(17,24,39,.5);">
            <div class="flex-between mb-1">
              <div style="font-weight:700;">{{ platformDisplayName(p.platform_name) }}</div>
              <span :class="['tag', pStatusClass(p.status)]">{{ pStatusLabel(p.status) }}</span>
            </div>
            <div style="font-size:12px; color:#9ca3af; margin-bottom:8px;">
              Tier: {{ p.platform_tier }} · 原始 {{ p.raw_items_count }} · 线索 {{ p.leads_extracted }}
            </div>
            <div class="progress-wrap" style="height:6px;">
              <div class="progress-bar" :style="{ width: (p.progress || 0) + '%' }"></div>
            </div>
            <div v-if="p.error_message" style="font-size:12px; color:#fca5a5; margin-top:6px;">
              {{ p.error_code }}: {{ (p.error_message || '').slice(0, 120) }}
            </div>
          </div>
        </div>

        <div v-if="task.expanded_keywords && task.expanded_keywords.length" class="mt-6">
          <div style="font-weight:600; margin-bottom:10px;">🔑 扩展关键词（{{ task.expanded_keywords.length }}）</div>
          <div class="flex flex-wrap" style="gap:6px;">
            <span v-for="(k, i) in task.expanded_keywords.slice(0, 50)" :key="i" class="tag blue">{{ k }}</span>
          </div>
        </div>
      </div>

      <div class="card mb-6">
        <div class="flex-between flex-wrap mb-4">
          <div style="font-weight:700; font-size:18px;">
            🎯 线索池（{{ leads.total }} / 🔥 {{ leads.high_intent_total }}）
          </div>
          <div class="flex flex-wrap" style="gap:8px;">
            <select v-model="filter.category" @change="loadLeads">
              <option value="">全部类别</option>
              <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
            </select>
            <select v-model="filter.high_only" @change="loadLeads">
              <option value="false">全部线索</option>
              <option value="true">仅高意向</option>
            </select>
            <select v-model="filter.min_score" @change="loadLeads">
              <option value="0">任意分数</option>
              <option value="50">≥ 50</option>
              <option value="65">≥ 65</option>
              <option value="80">≥ 80</option>
            </select>
            <input type="text" v-model="filter.keyword" style="max-width:200px; padding:8px 12px; font-size:13px;"
              placeholder="关键词过滤标题/摘要" @keydown.enter="loadLeads" />
          </div>
        </div>
        <div style="max-height: 70vh; overflow:auto; border:1px solid #1f2937; border-radius:10px;">
          <table>
            <thead>
              <tr>
                <th style="width:40px;">#</th>
                <th>类别</th>
                <th style="width:30%;">标题 / 摘要</th>
                <th>公司</th>
                <th>平台</th>
                <th>意向</th>
                <th>机会</th>
                <th>综合</th>
                <th>高意向</th>
                <th style="width:60px;"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="leads.items.length === 0">
                <td colspan="10" style="text-align:center; padding:40px; color:#6b7280;">
                  暂无线索数据。如果任务仍在运行，请耐心等待或点击刷新。
                </td>
              </tr>
              <tr v-for="(l, i) in leads.items" :key="l.id">
                <td>{{ i + 1 }}</td>
                <td><span :class="['tag', catTagClass(l.category)]">{{ catLabel(l.category) }}</span></td>
                <td>
                  <div style="font-weight:600;">{{ l.title || '(无标题)' }}</div>
                  <div style="font-size:12px; color:#9ca3af; margin-top:3px;">{{ (l.summary || '').slice(0, 120) }}</div>
                  <div v-if="l.tags && l.tags.length" class="mt-1 flex flex-wrap" style="gap:3px;">
                    <span v-for="(tg, ti) in l.tags.slice(0,5)" :key="ti" class="tag gray" style="font-size:10px; padding:1px 6px;">{{ tg }}</span>
                  </div>
                </td>
                <td>
                  <div v-if="l.company_name" style="font-weight:600;">{{ l.company_name }}</div>
                  <div style="font-size:12px; color:#9ca3af;">{{ l.location || '' }}</div>
                </td>
                <td>{{ l.source_platform }}</td>
                <td class="score" :class="scoreClass(l.intent_score)">{{ (l.intent_score || 0).toFixed(0) }}</td>
                <td class="score" :class="scoreClass(l.opportunity_score)">{{ (l.opportunity_score || 0).toFixed(0) }}</td>
                <td class="score" :class="scoreClass(l.overall_score)"><b>{{ (l.overall_score || 0).toFixed(1) }}</b></td>
                <td>
                  <span v-if="l.is_high_intent" class="tag green">🔥</span>
                  <span v-else class="tag gray">—</span>
                </td>
                <td>
                  <a v-if="l.url" :href="l.url" target="_blank" class="btn small ghost">查看</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { getTask, startTask, listLeads, reportMdUrl, reportHtmlUrl, exportXlsxUrl, listPlatforms } from '../api'

const props = defineProps({ taskId: { type: [Number, String], required: true } })
defineEmits(['back'])

const task = ref(null)
const leads = reactive({ total: 0, high_intent_total: 0, items: [] })
const platformsMap = ref({})
const filter = reactive({ category: '', high_only: 'false', min_score: '0', keyword: '' })
const categories = [
  { value: 'customer', label: '客户' }, { value: 'company', label: '企业' },
  { value: 'demand', label: '需求' }, { value: 'pain_point', label: '痛点' },
  { value: 'opportunity', label: '机会' }, { value: 'trend', label: '趋势' },
  { value: 'competition', label: '竞争' },
]

const reportMd = computed(() => reportMdUrl(props.taskId))
const reportHtml = computed(() => reportHtmlUrl(props.taskId))
const xlsxUrl = computed(() => exportXlsxUrl(props.taskId, filter.high_only === 'true'))
const cost = computed(() => task.value?.cost_summary || { total_usd: 0, total_cny: 0 })
const t = (k) => task.value?.task?.[k] || 0

let pollTimer = null
onMounted(async () => {
  try {
    const ps = await listPlatforms()
    const m = {}
    ps.forEach(p => m[p.name] = p)
    platformsMap.value = m
  } catch (e) { /* ignore */ }
  await pollOnce()
  pollTimer = setInterval(() => {
    if (task.value && task.value.task && !['completed', 'failed', 'partial'].includes(task.value.task.status)) {
      pollOnce()
    }
  }, 4000)
})
onBeforeUnmount(() => { if (pollTimer) clearInterval(pollTimer) })

const pollOnce = async () => {
  try {
    task.value = await getTask(props.taskId)
  } catch (e) { /* ignore */ }
  await loadLeads()
}
const loadLeads = async () => {
  try {
    const params = {
      category: filter.category || undefined,
      high_intent_only: filter.high_only === 'true',
      min_score: parseFloat(filter.min_score) || 0,
      keyword: filter.keyword || undefined,
      limit: 200,
    }
    Object.assign(leads, await listLeads(props.taskId, params))
  } catch (e) { /* ignore */ }
}

const retry = async () => {
  try {
    await startTask(props.taskId)
    await pollOnce()
  } catch (e) { /* ignore */ }
}

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '—'
const statusLabel = (s) => ({ pending: '等待', running: '执行中', paused: '暂停', completed: '完成', failed: '失败', partial: '部分完成' }[s] || s)
const statusClass = (s) => ({ pending: 'gray', running: 'blue', paused: 'yellow', completed: 'green', failed: 'red', partial: 'yellow' }[s] || 'gray')
const pStatusLabel = (s) => statusLabel(s)
const pStatusClass = (s) => statusClass(s)
const modeLabel = (m) => ({
  customers: '找客户', companies: '找企业', demands: '找需求', suppliers: '找供应商',
  partners: '找合作', opportunities: '找市场机会', family_bucket: '全家桶'
}[m] || m)
const platformDisplayName = (n) => platformsMap.value[n]?.display_name || n
const scoreClass = (v) => v >= 70 ? 'hi' : (v >= 40 ? 'md' : 'lo')
const catLabel = (c) => ({
  customer: '客户', company: '企业', demand: '需求', pain_point: '痛点',
  opportunity: '机会', trend: '趋势', competition: '竞争'
}[c] || c)
const catTagClass = (c) => ({
  customer: 'blue', company: 'purple', demand: 'green', pain_point: 'red',
  opportunity: 'yellow', trend: 'gray', competition: 'red'
}[c] || 'gray')
</script>
