<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const LABELS = { equal_payment: '等额本息', equal_principal: '等额本金' }
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const out = ref(null)
const lastSwitch = ref(null)
onMounted(async () => {
  const items = (await getJSON('/api/settings/method/history?limit=1')).items
  lastSwitch.value = items.length ? items[0].created_at : null
})
const run = async () => {
  out.value = await postJSON('/api/schedule', { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: true })
  if (out.value.last_method_switch_at) lastSwitch.value = out.value.last_method_switch_at
}
</script>
<template><div class="page"><h1>等额本息试算</h1>
<p>最近方式切换:{{ lastSwitch || '暂无' }}<template v-if="out"> · 当前默认方式 {{ LABELS[out.default_method] || out.default_method }}</template></p>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<button @click="run">计算</button>
<p v-if="out">月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>
</div></template>
