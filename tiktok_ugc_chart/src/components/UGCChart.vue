<template>
  <div class="chart-container" ref="chartContainer">
    <!-- 試しに適当なアイコン -->
    <!-- ドラッグ可能なアイコン画像 -->
    <img
      src="https://p16-sign-sg.tiktokcdn.com/tos-alisg-avt-0068/55757448d73b443f8cb49a4df55f73bd~tplv-tiktokx-cropcenter:100:100.jpeg?dr=14579&nonce=1668&refresh_token=b3c4f878035159bf2792866d78db20f0&x-expires=1740196800&x-signature=BfxydXUs9tRk3l%2Btp09rJSxdRno%3D&idc=my&ps=13740610&shcp=81f88b70&shp=a5d48078&t=4d5b0474"
      alt="アイコン"
      class="chart-icon"
      :style="{ top: iconPosition.y + 'px', left: iconPosition.x + 'px' }"
      @mousedown="startDrag"
      @touchstart="startDrag"
    />
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend } from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'

interface SongInfo {
  楽曲名: string
  楽曲URL: string
  日付: string | number
  総UGC数: number
}

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend)

const props = defineProps<{
  data: SongInfo[]
}>()

const canvas = ref<HTMLCanvasElement | null>(null)
const chartContainer = ref<HTMLElement | null>(null)
let chart: Chart | null = null

const formatData = (data: SongInfo[]) => {
  const labels = data.map((item, index) => {
    if (!item.日付) {
      console.warn(`データの項目 ${index + 1} に日付が欠けています:`, item)
      return '不明'
    }

    if (typeof item.日付 === 'string') {
      const date = new Date(item.日付)
      if (isNaN(date.getTime())) {
        console.warn(`データの項目 ${index + 1} に無効な日付形式があります:`, item.日付)
        return '無効な日付'
      }
      // 日付をフォーマット
      return `${date.getFullYear()}/${(date.getMonth()+1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')}`
    }
    return item.日付.toString()
  })
  const ugcData = data.map(item => item.総UGC数)
  return { labels, ugcData }
}

const renderChart = () => {
  if (canvas.value) {
    const { labels, ugcData } = formatData(props.data)
    const chartData: ChartData<'line'> = {
      labels,
      datasets: [{
        label: 'UGC数',
        data: ugcData,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
      }]
    }

    const options: ChartOptions<'line'> = {
      responsive: true,
      maintainAspectRatio: false, // レスポンシブ対応
      scales: {
        x: {
          title: {
            display: true,
            text: '日付'
          }
        },
        y: {
          title: {
            display: true,
            text: 'UGC数'
          },
          beginAtZero: true
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
        },
        tooltip: {
          enabled: true,
        }
      }
    }

    if (chart) {
      chart.destroy()
    }

    chart = new Chart(canvas.value, {
      type: 'line',
      data: chartData,
      options
    })
  }
}

onMounted(() => {
  renderChart()
})

watch(() => props.data, () => {
  renderChart()
}, { deep: true })

// ドラッグ機能の実装
const iconPosition = ref({ x: 10, y: 10 }) // 初期位置
const isDragging = ref(false)
const startX = ref(0)
const startY = ref(0)
const initialX = ref(0)
const initialY = ref(0)

// ドラッグ開始
const startDrag = (event: MouseEvent | TouchEvent) => {
  isDragging.value = true
  if (event instanceof MouseEvent) {
    startX.value = event.clientX
    startY.value = event.clientY
  } else if (event instanceof TouchEvent) {
    startX.value = event.touches[0].clientX
    startY.value = event.touches[0].clientY
  }
  initialX.value = iconPosition.value.x
  initialY.value = iconPosition.value.y

  // イベントリスナーを追加
  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', endDrag)
  window.addEventListener('touchmove', onDrag, { passive: false })
  window.addEventListener('touchend', endDrag)
  window.addEventListener('touchcancel', endDrag)

  event.preventDefault()
}

// ドラッグ中
const onDrag = (event: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return

  let currentX = 0
  let currentY = 0

  if (event instanceof MouseEvent) {
    currentX = event.clientX
    currentY = event.clientY
  } else if (event instanceof TouchEvent) {
    event.preventDefault()
    if (event.touches.length > 0) {
      currentX = event.touches[0].clientX
      currentY = event.touches[0].clientY
    }
  }

  const dx = currentX - startX.value
  const dy = currentY - startY.value

  let newX = initialX.value + dx
  let newY = initialY.value + dy

  if (chartContainer.value) {
    const containerRect = chartContainer.value.getBoundingClientRect()
    const iconWidth = 80 // .chart-iconのwidthと同じ
    const iconHeight = 80 // .chart-iconのheightと同じ

    // コンテナ内の相対座標を計算
    const minX = 0
    const minY = 0
    const maxX = containerRect.width - iconWidth
    const maxY = containerRect.height - iconHeight

    // 新しい位置を制限
    newX = Math.max(minX, Math.min(newX, maxX))
    newY = Math.max(minY, Math.min(newY, maxY))
  }

  iconPosition.value = {
    x: newX,
    y: newY
  }
}

// ドラッグ終了
const endDrag = () => {
  if (isDragging.value) {
    isDragging.value = false
    // イベントリスナーを削除
    window.removeEventListener('mousemove', onDrag)
    window.removeEventListener('mouseup', endDrag)
    window.removeEventListener('touchmove', onDrag)
    window.removeEventListener('touchend', endDrag)
    window.removeEventListener('touchcancel', endDrag)
  }
}

// コンポーネントが破棄される前にイベントリスナーをクリーンアップ
onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', endDrag)
  window.removeEventListener('touchmove', onDrag)
  window.removeEventListener('touchend', endDrag)
  window.removeEventListener('touchcancel', endDrag)
})
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 400px; /*  */
}

.chart-icon {
  position: absolute;
  width: 80px; /* 画像の幅を */
  height: 80px; /* 画像の高さ */
  z-index: 10; /* グラフより前面 */
  border-radius: 50%; /* 画像を丸くする */
  border: 2px solid #fff; /* 画像に白い枠線を追加 */
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.3); /* 画像に影を追加 */
  cursor: grab; /* ドラッグ可能であることを示すカーソル */
  user-select: none; /* 画像の選択を防止 */
}

.chart-icon:active {
  cursor: grabbing; /* ドラッグ中のカーソル */
}

canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>