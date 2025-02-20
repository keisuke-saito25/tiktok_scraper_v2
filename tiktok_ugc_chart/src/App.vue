<template>
  <v-app>
    <v-main>
      <v-container>
        <!-- 日付選択とExcel読み込み -->
        <v-row align="center" justify="start" class="my-4" spacing="4">
          
          <!-- 日付選択 -->
          <v-col cols="12" sm="6" md="4">
            <v-text-field
              v-model="selectedDate"
              label="シートの日付を選択"
              prepend-icon="mdi-calendar"
              readonly
              @click="menu = true"
            ></v-text-field>
            <v-menu
              v-model="menu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
            >
              <v-date-picker v-model="selectedDate" @input="menu = false"></v-date-picker>
            </v-menu>
          </v-col>

          <!-- Excel読み込みボタン -->
          <v-col cols="12" sm="6" md="3">
            <v-btn color="primary" @click="triggerFileInput" :disabled="!selectedDate" block>
              Excelを読み込む
            </v-btn>
          </v-col>

        </v-row>

        <!-- 隠しファイル入力 -->
        <input
          type="file"
          ref="fileInput"
          @change="handleFile"
          accept=".xlsx, .xls"
          style="display: none"
        />

         <!-- グラフ表示 -->
         <v-row>
          <v-col cols="12">
            <UGCChart :data="songInfoData" v-if="songInfoData.length > 0" />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'
import UGCChart from './components/UGCChart.vue'

const fileInput = ref<HTMLInputElement | null>(null)
const selectedDate = ref<string | Date | null>(null)
const menu = ref(false)
const songInfoData = ref<any[]>([])

// 日付を "YYYYMMDD" にフォーマット
const formattedSheetName = computed((): string => {
  if (typeof selectedDate.value === 'string') {
    return selectedDate.value.replace(/-/g, '')
  } else if (selectedDate.value instanceof Date) {
    const pad = (num: number) => num.toString().padStart(2, '0')
    const year = selectedDate.value.getFullYear()
    const month = pad(selectedDate.value.getMonth() + 1)
    const day = pad(selectedDate.value.getDate())
    return `${year}${month}${day}`
  }
  return ''
})

// ファイル入力をトリガー
const triggerFileInput = () => {
  fileInput.value?.click()
}

// ファイル読み込み
const handleFile = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) {
    console.error('ファイルが選択されていません。')
    return
  }

  if (!formattedSheetName.value) {
    console.error('日付を選択してください。')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    const data = new Uint8Array(e.target?.result as ArrayBuffer)
    const workbook = XLSX.read(data, { type: 'array' })

    const sheetNamesToLoad = [formattedSheetName.value, '楽曲情報']
    const missingSheets = sheetNamesToLoad.filter(name => !workbook.SheetNames.includes(name))

    if (missingSheets.length > 0) {
      console.error(`以下のシートが見つかりません: ${missingSheets.join(', ')}`)
      return
    }

    const extractedData: Record<string, any[]> = {}

    sheetNamesToLoad.forEach(sheetName => {
      const worksheet = workbook.Sheets[sheetName]
      extractedData[sheetName] = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
    })

    console.log('選択された日付のシートのExcelデータ:', extractedData[formattedSheetName.value])
    console.log('楽曲情報シートのExcelデータ:', extractedData['楽曲情報'])
    
    // 楽曲情報の整形
    const rawData = extractedData['楽曲情報'] as any[][]
    if (rawData.length > 1) {
      const headers = rawData[0]
      const data = rawData.slice(1).map(row => {
        const rowData: Record<string, any> = {}
        headers.forEach((header, index) => {
          rowData[header] = row[index]
        })
        return rowData
      })
      songInfoData.value = data
    }
  }
  reader.readAsArrayBuffer(file)
}
</script>