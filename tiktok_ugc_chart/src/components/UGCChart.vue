
  <script setup lang="ts">
  import { ref, onMounted, watch } from 'vue'
  import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Legend } from 'chart.js'
  import type { ChartData, ChartOptions } from 'chart.js'
  
  interface SongInfo {
    楽曲名: string
    楽曲URL: string
    日付: string | number
    総UGC数: number
  }
  
  interface TikTokPost {
    投稿ID: string;
    投稿日: string;
    アカウント名: string;
    ニックネーム: string;
    いいね数: number;
    コメント数: number;
    保存数: number;
    シェア数: number;
    再生回数: number;
    フォロワー数: number;
    動画リンク_URL: string;
    更新日: string;
    アイコンURL: string;
  }

  Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend)
  
  const props = defineProps<{
    data: SongInfo[]
    top30FollowerPost: TikTokPost[]
  }>()
  
  const canvas = ref<HTMLCanvasElement | null>(null)
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
    console.log("props.top30FollowerPost: ", props.top30FollowerPost)
    console.log("props.data: ", props.data)

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
  </script>
  
  <template>
    <canvas ref="canvas"></canvas>
  </template>

  <style scoped>
  canvas {
    max-width: 100%;
  }
  </style>