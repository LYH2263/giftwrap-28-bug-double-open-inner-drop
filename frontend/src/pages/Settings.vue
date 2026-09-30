<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const s = ref({})
const overlap = ref(null)
const lining = ref(null)
const err = ref('')
const saved = ref(false)
const busy = ref(false)

async function load() {
  s.value = await getJSON('/api/settings')
  overlap.value = Number(s.value.overlap)
  lining.value = Number(s.value.lining_coef)
}

onMounted(load)

async function save() {
  err.value = ''
  saved.value = false
  busy.value = true
  try {
    await putJSON('/api/settings', { overlap: overlap.value, lining_coef: lining.value })
    await load()
    saved.value = true
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>设置</h1>
    <p class="lede">全局默认系数用于算纸台未显式填值时的干算；已写入用纸档的单子按落库快照保留，不受影响。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="saved" class="pill">已保存</p>
    <div class="row coef-row" style="margin-top:1rem">
      <label>折边系数 overlap <input v-model.number="overlap" type="number" step="0.01" min="0.01" /></label>
      <label>默认里衬系数 lining_coef <input v-model.number="lining" type="number" step="0.01" min="0.01" /></label>
    </div>
    <div class="row">
      <button :disabled="busy" @click="save">保存全局系数</button>
    </div>
    <p class="hint">系数须为正；双层单子的里衬系数 ≤ 0 时整单失败，不会写档。</p>
  </div>
</template>
