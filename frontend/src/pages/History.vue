<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function fmt(x) {
  return Number(x ?? 0).toFixed(3)
}
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="hint">列表钉写入摘要（inner / total）；详情走开放视图字段。</p>
    <p class="lede">算纸页「写入用纸档」后的落库结果，按次钉住外层、里层与合计；改全局系数不会重算旧档。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/history/${r.id}`">
          #{{ r.id }} {{ r.box_name }}
          <span class="pill" v-if="r.result?.double_wrap">双层</span>
        </router-link>
        <span class="meta">
          外 {{ fmt(r.result?.outer_paper_m2 ?? r.result?.paper_m2) }} /
          里 {{ r.result?.double_wrap ? fmt(r.result?.inner_paper_m2) : '—' }} /
          合计 <strong>{{ fmt(r.result?.total_paper_m2 ?? r.result?.paper_m2) }}</strong> m²
        </span>
      </li>
    </ul>
  </div>
</template>
