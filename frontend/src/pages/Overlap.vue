<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const s = ref({})
const err = ref('')

onMounted(async () => {
  try {
    s.value = await getJSON('/api/settings')
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>折边系数</h1>
    <p class="lede">盒体外表面近似面积乘以该系数，得到含重叠余量的用纸面积。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-else class="result-board">
      <div class="paper-cols">
        <div class="paper-col">
          <p class="col-tag">折边系数（外层）</p>
          <div class="figure">× {{ s.overlap ?? '—' }}</div>
        </div>
        <div class="paper-col">
          <p class="col-tag">默认里衬系数（里层）</p>
          <div class="figure">× {{ s.lining_coef ?? '—' }}</div>
        </div>
      </div>
      <p class="stat-line">外层用纸 = 六面展开表面积 × 折边系数；双层开启时里层 = 同一有效表面积 × 里衬系数。</p>
      <p class="stat-line">全局默认可在「设置」页修改；已落库用纸档按写入时快照保留。</p>
    </div>
  </div>
</template>
