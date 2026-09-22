<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const NAMES = { equal_payment: '等额本息', equal_principal: '等额本金' }
const s = ref({})
const target = ref('equal_principal')
const note = ref('')
const msg = ref('')
const items = ref([])
const load = async () => {
  s.value = await getJSON('/api/settings')
  items.value = (await getJSON('/api/settings/method/history?limit=20')).items
}
const save = async () => {
  const r = await putJSON('/api/settings/method', { method: target.value, note: note.value || null })
  msg.value = r.changed ? `已切换：${NAMES[r.from_method]} → ${NAMES[r.method]}` : '方式未变化，未追加履历'
  note.value = ''
  await load()
}
onMounted(load)
</script>
<template><div class="page"><h1>设置</h1>
<p>当前默认还款方式：<b>{{ NAMES[s.method] || s.method }}</b></p>
<label>切换为
  <select v-model="target">
    <option value="equal_payment">等额本息</option>
    <option value="equal_principal">等额本金</option>
  </select>
</label>
<label>备注 <input v-model="note" placeholder="可选" /></label>
<button @click="save">保存</button>
<p v-if="msg">{{ msg }}</p>
<h2>切换履历</h2>
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
