<template>
  <div class="chart-container" ref="chartContainer">
    <canvas ref="canvas"></canvas>
    
    <!-- ロード済みのDraggableIconを表示 -->
    <DraggableIcon
      v-for="(post, index) in loadedFollowerPosts"
      :key="post.投稿ID"
      :src="post.アイコン"
      :alt="post.アカウント名"
      :initialPosition="getInitialPosition(index)"
      :containerRef="chartContainer"
      @update:position="handlePositionUpdate(index, $event)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend } from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'
import DraggableIcon from './DraggableIcon.vue'
import type { SongInfo } from '@/types/SongInfo'
import type { TikTokPost } from '@/types/TikTokPost'

// Chart.jsのコンポーネント登録
Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend)

// Props定義
const props = defineProps<{
  data: SongInfo[],
  topFollowerPosts: TikTokPost[]
}>()

// Canvasとコンテナの参照
const canvas = ref<HTMLCanvasElement | null>(null)
const chartContainer = ref<HTMLElement | null>(null)
let chartInstance: Chart | null = null

// アイコンの位置管理
const iconPositions = ref<{ x: number, y: number }[]>([])

// ロード済みの投稿を管理するリスト
const loadedFollowerPosts = ref<TikTokPost[]>([])

// 初期位置を設定する関数
const getInitialPosition = (index: number) => {
  return {
    x: 10 + (index % 5) * 50,
    y: 10 + Math.floor(index / 5) * 50
  }
}

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
      maintainAspectRatio: false,
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

const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 画像を順次ロードする関数
const loadFollowerPostsSequentially = async () => {
  for (const post of props.topFollowerPosts) {
    await wait(1000)
    await loadImage(post.アイコン)
    loadedFollowerPosts.value.push(post)
  }
}

const loadImage = (src: string): Promise<void> => {
  return new Promise((resolve) => {
    const img = new Image()
    img.src = src
    img.onload = () => resolve()
    img.onerror = () => resolve() // エラー時も次に進む
  })
}

// チャートのマウント時にレンダリングと画像ロードを開始
onMounted(() => {
  renderChart()
  loadFollowerPostsSequentially()
})

// データの変更を監視してチャートを再描画
watch(() => props.data, () => {
  renderChart()
}, { deep: true })

// topFollowerPostsが変更されたときに初期位置を設定
watch(() => props.topFollowerPosts, (newPosts) => {
  iconPositions.value = newPosts.map((_, index) => getInitialPosition(index))
})

// アイコン位置の更新ハンドラー
const handlePositionUpdate = (index: number, newPosition: { x: number, y: number }) => {
  iconPositions.value[index] = newPosition
}
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 600px; 
}

canvas {
  width: 100% !important;
  height: 100% !important;
}

.chart-icon {
  position: absolute;
  width: 40px; /* アイコンのサイズ調整 */
  height: 40px;
  z-index: 10;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
  cursor: grab;
  user-select: none;
}

.chart-icon:active {
  cursor: grabbing;
}
</style>