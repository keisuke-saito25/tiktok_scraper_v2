<template>
  <div class="chart-container" ref="chartContainer">
    <DraggableIcon
      :src="iconSrc"
      :alt="iconAlt"
      :initialPosition="iconPosition"
      :containerRef="chartContainer"
      @update:position="handlePositionUpdate"
    />
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend } from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'
import DraggableIcon from './DraggableIcon.vue'
import type { SongInfo } from '@/types/SongInfo'

// Chart.jsのコンポーネント登録
Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend)

// Props定義
const props = defineProps<{
  data: SongInfo[]
}>()

// アイコンのソースとalt属性
const iconSrc = "https://p16-sign-sg.tiktokcdn.com/tos-alisg-avt-0068/55757448d73b443f8cb49a4df55f73bd~tplv-tiktokx-cropcenter:100:100.jpeg?dr=14579&nonce=1668&refresh_token=b3c4f878035159bf2792866d78db20f0&x-expires=1740196800&x-signature=BfxydXUs9tRk3l%2Btp09rJSxdRno%3D&idc=my&ps=13740610&shcp=81f88b70&shp=a5d48078&t=4d5b0474"
const iconAlt = "アイコン"

// Canvasとコンテナの参照
const canvas = ref<HTMLCanvasElement | null>(null)
const chartContainer = ref<HTMLElement | null>(null)
let chartInstance: Chart | null = null

// アイコンの位置管理
const iconPosition = ref<{ x: number, y: number }>({ x: 10, y: 10 }) // 初期位置

// データのフォーマット関数
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

// チャートのレンダリング関数
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

    if (chartInstance) {
      chartInstance.destroy()
    }

    chartInstance = new Chart(canvas.value, {
      type: 'line',
      data: chartData,
      options
    })
  }
}

// マウント時にチャートを描画
onMounted(() => {
  renderChart()
})

// データの変更を監視してチャートを再描画
watch(() => props.data, () => {
  renderChart()
}, { deep: true })

// アイコンの位置が更新されたときのハンドラー
const handlePositionUpdate = (newPosition: { x: number, y: number }) => {
  iconPosition.value = newPosition
}
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 400px; /*  */
}

canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>