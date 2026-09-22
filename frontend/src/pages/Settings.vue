<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const LABELS = { equal_payment: '等额本息', equal_principal: '等额本金' }
const s = ref({})
const items = ref([])
const target = ref('equal_principal')
const note = ref('')
const msg = ref('')
const load = async () => {
  s.value = await getJSON('/api/settings')
  items.value = (await getJSON('/api/settings/method/history?limit=20')).items
}
const switchMethod = async () => {
  const r = await postJSON('/api/settings/method', { method: target.value, note: note.value || null })
  msg.value = r.changed ? '已切换并记入履历' : '方式未变化,未新增履历'
  note.value = ''
  await load()
}
onMounted(load)
</script>
<template><div class="page"><h1>设置</h1>
<p>当前默认还款方式:<b>{{ LABELS[s.method] || s.method }}</b></p>
<label>切换为
  <select v-model="target">
    <option value="equal_payment">等额本息</option>
    <option value="equal_principal">等额本金</option>
  </select>
</label>
<label>备注 <input v-model="note" placeholder="可选" /></label>
<button @click="switchMethod">切换</button>
<span>{{ msg }}</span>
<h2>方式切换履历</h2>
<table v-if="items.length">
  <tr><th>时间</th><th>原方式</th><th>新方式</th><th>备注</th></tr>
  <tr v-for="h in items" :key="h.id">
    <td>{{ h.created_at }}</td>
    <td>{{ LABELS[h.from_method] || h.from_method || '—' }}</td>
    <td>{{ LABELS[h.to_method] || h.to_method }}</td>
    <td>{{ h.note || '—' }}</td>
  </tr>
</table>
<p v-else>暂无切换履历</p>
</div></template>
