<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const route = useRoute()
const boxes = ref([])
const bid = ref(Number(route.query.box_id) || 1)
const doubleWrap = ref(route.query.double_wrap === '1')
const overlap = ref(null)
const lining = ref(null)
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
    const s = await getJSON('/api/settings')
    overlap.value = Number(route.query.overlap ?? s.overlap)
    lining.value = Number(route.query.lining ?? s.lining_coef)
    if (!route.query.box_id && boxes.value.length) bid.value = boxes.value[0].id
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function buildQuery(save) {
  const q = new URLSearchParams({ box_id: bid.value, save: save ? 'true' : 'false' })
  // 系数留空时走后端全局默认；填了就按本台参数干算。
  if (overlap.value !== null && !Number.isNaN(overlap.value)) q.set('overlap', overlap.value)
  if (doubleWrap.value) {
    q.set('double_wrap', 'true')
    if (lining.value !== null && !Number.isNaN(lining.value)) q.set('lining', lining.value)
  }
  return q
}

async function go(save) {
  err.value = ''
  out.value = null
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', {
          box_id: bid.value,
          save: true,
          overlap: overlap.value === null || Number.isNaN(overlap.value) ? null : overlap.value,
          double_wrap: doubleWrap.value,
          lining: doubleWrap.value && lining.value !== null && !Number.isNaN(lining.value)
            ? lining.value
            : null,
        })
      : await getJSON(`/api/estimate?${buildQuery(false).toString()}`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

function fmt(x) {
  return Number(x ?? 0).toFixed(4)
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看两路面积与展开，确认后再写入用纸档。写入后以落库快照为准，改全局默认不影响旧档。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <label class="switch">
        <input type="checkbox" v-model="doubleWrap" />
        <span>双层内外用纸</span>
      </label>
    </div>
    <div class="row coef-row">
      <label>折边系数 <input v-model.number="overlap" type="number" step="0.01" min="0.01" /></label>
      <label v-if="doubleWrap">里衬系数 <input v-model.number="lining" type="number" step="0.01" min="0.01" /></label>
      <span v-if="doubleWrap" class="hint">里层 = 六面有效表面积 × 里衬系数；系数须 &gt; 0，否则整单失败不写档。</span>
    </div>
    <div class="row">
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="paper-cols">
        <div class="paper-col">
          <p class="col-tag">外层（六面×折边）</p>
          <div class="figure">{{ fmt(out.outer_paper_m2) }}<span>m²</span></div>
        </div>
        <div class="paper-col" :class="{ off: !out.double_wrap }">
          <p class="col-tag">里层（有效面积×里衬系数）</p>
          <div class="figure">{{ out.double_wrap ? fmt(out.inner_paper_m2) : '—' }}<span v-if="out.double_wrap">m²</span></div>
        </div>
        <div class="paper-col total">
          <p class="col-tag">合计</p>
          <div class="figure">{{ fmt(out.total_paper_m2) }}<span>m²</span></div>
        </div>
      </div>
      <p class="stat-line" v-if="out.ribbon">
        丝带只跟外层三边：{{ out.ribbon.wrap_style === 'band' ? '单圈' : '十字' }}约
        {{ out.ribbon.ribbon_m }} m
      </p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :paper-m2="out.total_paper_m2"
      />
      <p v-if="out.run_id" class="stat-line ok-line">
        已落库为用纸档 #{{ out.run_id }}，可在
        <router-link :to="`/history/${out.run_id}`">用纸档详情</router-link> 回看。
      </p>
    </div>
  </div>
</template>
