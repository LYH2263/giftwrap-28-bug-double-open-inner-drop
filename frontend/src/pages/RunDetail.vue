<script setup>
// 详情只认落库快照：double_wrap 开启时里层面积、合计按写入瞬间原样回显

import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getJSON } from '../api'

const props = defineProps({ id: String })
const router = useRouter()
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function fmt(x) {
  return Number(x ?? 0).toFixed(4)
}

// 带落库时同一组参数回算纸台干算，与落库快照互证。
function recheck() {
  const r = run.value.result
  const q = new URLSearchParams({
    box_id: String(run.value.box_id),
    overlap: String(r.overlap),
    double_wrap: r.double_wrap ? '1' : '0',
  })
  if (r.double_wrap && r.lining != null) q.set('lining', String(r.lining))
  router.push({ path: '/bench', query: Object.fromEntries(q) })
}
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }} · {{ run.box_name }}</h1>
      <p class="lede">以下为写入瞬间的落库快照，是唯一真相；不会随全局默认系数变化而重算。</p>
      <div class="result-board">
        <div class="paper-cols">
          <div class="paper-col">
            <p class="col-tag">外层</p>
            <div class="figure">{{ fmt(run.result.outer_paper_m2) }}<span>m²</span></div>
          </div>
          <div class="paper-col" :class="{ off: !run.result.double_wrap }">
            <p class="col-tag">里层</p>
            <div class="figure">
              {{ run.result.double_wrap ? fmt(run.result.inner_paper_m2) : '—'
            }}<span v-if="run.result.double_wrap">m²</span>
            </div>
          </div>
          <div class="paper-col total">
            <p class="col-tag">合计</p>
            <div class="figure">{{ fmt(run.result.total_paper_m2) }}<span>m²</span></div>
          </div>
        </div>
        <ul class="item-list" style="margin-top:1rem">
          <li><span>双层内外用纸</span><span class="meta">{{ run.result.double_wrap ? '是' : '否' }}</span></li>
          <li><span>折边系数</span><span class="meta">{{ run.result.overlap }}</span></li>
          <li v-if="run.result.double_wrap"><span>里衬系数</span><span class="meta">{{ run.result.lining }}</span></li>
          <li v-if="run.result.ribbon">
            <span>丝带（只跟外层三边）</span><span class="meta">{{ run.result.ribbon.ribbon_m }} m</span>
          </li>
        </ul>
      </div>
      <div class="row" style="margin-top: 1.25rem">
        <button @click="recheck">同参回算纸台互证</button>
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
    </template>
  </div>
</template>
