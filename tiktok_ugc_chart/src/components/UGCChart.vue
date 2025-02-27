<template>
  <div class="chart-container" ref="chartContainer">
    <canvas ref="canvas"></canvas>
    
    <!-- ロード済みのDraggableIconを表示（フォロワー数順にソート） -->
    <DraggableIcon
      v-for="(post, index) in sortedFollowerPosts"
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
import { ref, onMounted, watch, computed } from 'vue'
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend } from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'
import DraggableIcon from './DraggableIcon.vue'
import type { SongInfo } from '@/types/SongInfo'
import type { TikTokPost } from '@/types/TikTokPost'
import { formatDateToYYYYMMDDWithSlash } from '@/utils/dateUtils'

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

// フォロワー数順にソートされた投稿のリスト
const sortedFollowerPosts = computed(() => {
  // フォロワー数の多い順にソート
  return [...loadedFollowerPosts.value].sort((a, b) => b.フォロワー数 - a.フォロワー数)
})

// 初期位置を設定する関数
const getInitialPosition = (uniqueId: string, index: number) => {
  if (iconPositions.value[uniqueId]) {
    return iconPositions.value[uniqueId]
  }

  const iconSize = 80 // アイコンの幅・高さ
  const padding = 10 // アイコン間のパディング
  const spacing = iconSize + padding // スペーシング
  const iconsPerRow = 8 // 1行あたりのアイコン数

  // アイコンのグリッド位置を計算
  const position = {
    x: padding + (index % iconsPerRow) * spacing,
    y: padding + Math.floor(index / iconsPerRow) * spacing
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
      return formatDateToYYYYMMDDWithSlash(item.日付)
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

// 画像を並列でロードする関数
const loadFollowerPostsInParallel = async () => {
  const loadPromises = props.topFollowerPosts
    .filter(post => post.isVisible)
    .map(async (post) => {
      await loadImage(post.アイコン)
      return post
    })
  
  const loadedPosts = await Promise.all(loadPromises)
  loadedFollowerPosts.value = loadedPosts
}

// 画像をロードする関数
const loadImage = (src: string): Promise<void> => {
  // 既にキャッシュされている可能性があるので、処理を最適化
  return new Promise((resolve) => {
    // すでにブラウザにキャッシュされている可能性を考慮
    const img = new Image()
    img.crossOrigin = 'anonymous' 
    
    // 既にロード済みかチェック
    if (img.complete) {
      resolve()
      return
    }
    
    img.onload = () => {
      resolve()
    }
    img.onerror = () => {
      console.error(`画像ロードエラー: ${src}`)
      resolve() // エラー時も次に進む
    }
    img.src = src
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

// エクスポート関数
// チャートのみをエクスポート
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

// アイコンのみをエクスポート
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

// チャートとアイコンを一緒にエクスポート
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
  await new Promise<void>((resolve) => {
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

// アイコン位置の更新ハンドラー
const handlePositionUpdate = (uniqueId: string, newPosition: { x: number, y: number }) => {
  if (!iconPositions.value) {
    iconPositions.value = {}
  }
  iconPositions.value[uniqueId] = newPosition
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

// topFollowerPostsが変更されたときに画像をロード
// deep: trueを使うことで、配列の要素の変更も検知します
watch(() => props.topFollowerPosts, async () => {
  // ロード済みの投稿をリセット
  loadedFollowerPosts.value = []

  // 画像ロードをトリガー
  loadFollowerPostsInParallel()
}, { deep: true })
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
</style>