<template>
  <div class="chart-container" ref="chartContainer">
    <canvas ref="canvas"></canvas>
    
    <!-- ロード済みのDraggableIconを表示 -->
    <DraggableIcon
      v-for="(post, index) in loadedFollowerPosts"
      :key="post.uniqueId"
      :src="post.アイコン"
      :alt="post.アカウント名"
      :initialPosition="getInitialPosition(post.uniqueId, index)"
      :containerRef="chartContainer"
      :isOrangeBorder="post.isOrangeBorder"
      @update:position="handlePositionUpdate(post.uniqueId, $event)"
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

// アイコンの位置管理をオブジェクトに変更
const iconPositions = ref<Record<string, { x: number, y: number }>>({})

// ロード済みの投稿を管理するリスト
const loadedFollowerPosts = ref<TikTokPost[]>([])

// 初期位置を設定する関数
const getInitialPosition = (uniqueId: string, index: number) => {
  if (iconPositions.value[uniqueId]) {
    return iconPositions.value[uniqueId]
  }

  const iconSize = 80 // アイコンの幅・高さ
  const padding = 10 // アイコン間のパディング
  const spacing = iconSize + padding // スペーシング

  const position = {
    x: padding + (index % 10) * spacing,
    y: padding + Math.floor(index / 10) * spacing
  }

  // 初期位置を保存
  iconPositions.value[uniqueId] = position

  return position
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

// 画像を並列でロードする関数
const loadFollowerPostsInParallel = async () => {
  const loadPromises = props.topFollowerPosts.map(async (post) => {
    await loadImage(post.アイコン)
    loadedFollowerPosts.value.push(post)
  })
  await Promise.all(loadPromises)
}

// 画像をロードする関数
const loadImage = (src: string): Promise<void> => {
  return new Promise((resolve) => {
    console.log(`画像ロード開始: ${src}`)
    const img = new Image()
    img.crossOrigin = 'anonymous' 
    img.src = src
    img.onload = () => {
      console.log(`画像ロード成功: ${src}`)
      resolve()
    }
    img.onerror = (error) => {
      console.error(`画像ロードエラー: ${src}`, error)
      resolve() // エラー時も次に進む
    }
  })
}

// アイコンをCanvasに描画するヘルパー関数（クリッピングを追加）
const drawIcon = (ctx: CanvasRenderingContext2D, src: string, x: number, y: number, isOrangeBorder: boolean): Promise<void> => {
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous' // 画像のCORS設定
    img.src = src
    img.onload = () => {
      // クリッピングパスの設定
      ctx.save() // 現在の描画状態を保存
      ctx.beginPath()
      ctx.arc(x + 40, y + 40, 40, 0, 2 * Math.PI) // アイコンの中心と半径
      ctx.clip() // クリッピングパスを適用

      // 画像を描画
      ctx.drawImage(img, x, y, 80, 80) // アイコンサイズに合わせて調整

      ctx.restore() // 描画状態を復元

      // 境界線の描画
      ctx.beginPath()
      if (isOrangeBorder) {
        ctx.strokeStyle = 'orange'
      } else {
        ctx.strokeStyle = '#90ee90' // デフォルトの緑色枠
      }
      ctx.lineWidth = 4
      ctx.arc(x + 40, y + 40, 40, 0, 2 * Math.PI)
      ctx.stroke()

      resolve()
    }
    img.onerror = (error) => {
      console.error(`画像のロードに失敗しました: ${src}`, error)
      resolve()
    }
  })
}

// **エクスポート関数の追加**
// 1. アイコンのみをエクスポートする関数は既に存在しますが、チャートのみをエクスポートする新しい関数を追加します。
const exportChartAsImage = () => {
  if (!canvas.value) {
    console.error('チャートキャンバスが見つかりません。')
    return
  }

  // チャートのデータURLを取得
  const dataURL = canvas.value.toDataURL('image/png')

  // ダウンロードリンクを作成してクリック
  const link = document.createElement('a')
  link.href = dataURL
  link.download = 'chart.png'
  link.click()
}

// 既存のアイコンをエクスポートする関数（修正不要）
const exportIconsAsImage = async () => {
  if (!chartContainer.value) {
    console.error('チャートコンテナが見つかりません。')
    return
  }

  // Canvasのサイズを取得
  const containerRect = chartContainer.value.getBoundingClientRect()
  const exportCanvas = document.createElement('canvas')
  exportCanvas.width = containerRect.width
  exportCanvas.height = containerRect.height
  const ctx = exportCanvas.getContext('2d')

  if (!ctx) {
    console.error('Canvasのコンテキストを取得できませんでした。')
    return
  }

  // 背景を透明に設定
  ctx.clearRect(0, 0, exportCanvas.width, exportCanvas.height)

  // 各アイコンを描画
  for (const post of loadedFollowerPosts.value) {
    if (!post.isVisible) continue

    const position = iconPositions.value[post.uniqueId]
    if (!position) continue

    await drawIcon(ctx, post.アイコン, position.x, position.y, post.isOrangeBorder)
  }

  // 画像としてダウンロード
  const dataURL = exportCanvas.toDataURL('image/png')
  const link = document.createElement('a')
  link.href = dataURL
  link.download = 'icons.png'
  link.click()
}

// **チャートとアイコンを一緒にエクスポートする関数（オプション）**
const exportChartAndIconsAsImage = async () => {
  if (!chartContainer.value || !canvas.value) {
    console.error('チャートコンテナかチャートキャンバスが見つかりません。')
    return
  }

  // チャートの画像を取得
  const chartDataURL = canvas.value.toDataURL('image/png')
  const chartImage = new Image()
  chartImage.src = chartDataURL

  // チャート画像の読み込みを待つ
  await new Promise<void>((resolve, reject) => {
    chartImage.onload = () => resolve()
    chartImage.onerror = () => resolve() // エラー時も続行
  })

  // オフスクリーンCanvasの作成
  const containerRect = chartContainer.value.getBoundingClientRect()
  const exportCanvas = document.createElement('canvas')
  exportCanvas.width = containerRect.width
  exportCanvas.height = containerRect.height
  const ctx = exportCanvas.getContext('2d')

  if (!ctx) {
    console.error('オフスクリーンCanvasのコンテキストを取得できませんでした。')
    return
  }

  // 背景を透明に設定
  ctx.clearRect(0, 0, exportCanvas.width, exportCanvas.height)

  // チャート画像をオフスクリーンCanvasに描画
  ctx.drawImage(chartImage, 0, 0, exportCanvas.width, exportCanvas.height)

  // 各アイコンを描画
  for (const post of loadedFollowerPosts.value) {
    if (!post.isVisible) continue

    const position = iconPositions.value[post.uniqueId]
    if (!position) continue

    await drawIcon(ctx, post.アイコン, position.x, position.y, post.isOrangeBorder)
  }

  // 画像としてダウンロード
  const dataURL = exportCanvas.toDataURL('image/png')
  const link = document.createElement('a')
  link.href = dataURL
  link.download = 'chart_with_icons.png'
  link.click()
}

// エクスポート関数を親コンポーネントからアクセス可能にする
defineExpose({
  exportChartAsImage,
  exportIconsAsImage,
  exportChartAndIconsAsImage
})

 // チャートのマウント時にレンダリングと画像ロードを開始
onMounted(() => {
  renderChart()
  loadFollowerPostsInParallel()
})

// データの変更を監視してチャートを再描画
watch(() => props.data, () => {
  renderChart()
}, { deep: true })

// topFollowerPostsが変更されたときに位置情報をリセットせずに画像をロード
watch(() => props.topFollowerPosts, async (newPosts) => {
  // ロード済みの投稿をリセット
  loadedFollowerPosts.value = []

  // 画像ロードをトリガー
  loadFollowerPostsInParallel()
})

// アイコン位置の更新ハンドラー
const handlePositionUpdate = (uniqueId: string, newPosition: { x: number, y: number }) => {
  iconPositions.value[uniqueId] = newPosition
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
  width: 80px; 
  height: 80px;
  z-index: 10;
  border-radius: 50%;
  border: 2px solid #90ee90;
  cursor: grab;
  user-select: none;
}

.chart-icon.orange-border {
  border-color: orange; /* オレンジの縁 */
}

.chart-icon:active {
  cursor: grabbing;
}

button {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 8px 16px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px; /* ボタン間のスペースを追加 */
}
button:hover {
  background-color: #1565c0;
}
</style>