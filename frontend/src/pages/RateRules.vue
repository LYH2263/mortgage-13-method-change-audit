<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const NAMES = { equal_payment: '等额本息', equal_principal: '等额本金' }
const s = ref({})
const items = ref([])
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  items.value = (await getJSON('/api/settings/method/history?limit=5')).items
})
</script>
<template><div class="page"><h1>利率说明</h1>
<p>默认等额本息：月利率 = 年利率 / 12 / 100。</p>
<p>当前默认还款方式：<b>{{ NAMES[s.method] || s.method }}</b></p>
<h2>还款方式切换履历</h2>
<p v-if="!items.length">暂无切换记录</p>
<table v-else>
  <tr><th>时间</th><th>切换前</th><th>切换后</th><th>备注</th></tr>
  <tr v-for="h in items" :key="h.id">
    <td>{{ h.created_at }}</td>
    <td>{{ NAMES[h.from_method] || h.from_method || '—' }}</td>
    <td>{{ NAMES[h.to_method] || h.to_method }}</td>
    <td>{{ h.note || '—' }}</td>
  </tr>
</table>
</div></template>
