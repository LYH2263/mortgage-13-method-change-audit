<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const NAMES = { equal_payment: '等额本息', equal_principal: '等额本金' }
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const out = ref(null)
const lastChange = ref(null)
const run = async () => {
  out.value = await postJSON('/api/schedule', { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: true })
  if (out.value.last_method_change_at) lastChange.value = out.value.last_method_change_at
}
onMounted(async () => {
  const items = (await getJSON('/api/settings/method/history?limit=1')).items
  if (items.length) lastChange.value = items[0].created_at
})
</script>
<template><div class="page"><h1>等额本息试算</h1>
<p v-if="lastChange">最近还款方式切换：{{ lastChange }}</p>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<button @click="run">计算</button>
<p v-if="out">月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }} · 默认方式 {{ NAMES[out.default_method] || out.default_method }}</p>
</div></template>
