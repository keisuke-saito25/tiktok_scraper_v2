<template>
    <canvas ref="canvas"></canvas>
  </template>
  
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
  
  Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend)
  
  const props = defineProps<{
    data: SongInfo[]
  }>()
  
  const canvas = ref<HTMLCanvasElement | null>(null)
  let chart: Chart | null = null
  
  const formatData = (data: SongInfo[]) => {
    const labels = data.map(item => {
      if (typeof item.日付 === 'string') {
        const date = new Date(item.日付)
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
  
  <style scoped>
  canvas {
    max-width: 100%;
  }
  </style>