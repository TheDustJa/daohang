<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Quote } from 'lucide-vue-next'

const quotes = [
  { text: '最好的方式就是动手去做。', author: '阿兰·图灵' },
  { text: '人工智能是新的电力。', author: 'Andrew Ng' },
  { text: '未来已来，只是尚未均匀分布。', author: 'William Gibson' },
  { text: '简单是终极的复杂。', author: '达芬奇' },
  { text: '不要温和地走入那个良夜。', author: 'Dylan Thomas' },
  { text: '任何足够先进的技术，都与魔法无异。', author: 'Arthur C. Clarke' },
  { text: '创造力就是把旧元素做新组合。', author: 'Steve Jobs' },
  { text: '好的设计是尽可能少的设计。', author: 'Dieter Rams' },
  { text: '学而不思则罔，思而不学则殆。', author: '孔子' },
  { text: '代码是写给人看的，顺便让机器执行。', author: 'Harold Abelson' },
]

const quote = ref(quotes[0])

onMounted(() => {
  const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000)
  quote.value = quotes[dayOfYear % quotes.length]
})
</script>

<template>
  <div class="flex items-start gap-2 py-3 px-4 opacity-60 hover:opacity-100 transition-opacity">
    <Quote class="w-4 h-4 mt-0.5 shrink-0 rotate-180" :stroke-width="2" />
    <div>
      <p class="text-xs md:text-sm font-bold italic leading-relaxed">{{ quote.text }}</p>
      <span class="text-[10px] font-bold uppercase tracking-widest opacity-50">— {{ quote.author }}</span>
    </div>
  </div>
</template>
