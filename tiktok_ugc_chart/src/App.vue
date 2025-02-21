<template>
  <v-app>
    <v-main>
      <v-container>
        <!-- Excel読み込みボタンと日付フィルタ -->
        <v-row align="center" justify="start" class="my-4" spacing="4">
          <v-col cols="12" sm="6" md="3">
            <v-btn
              color="primary"
              @click="triggerFileInput"
              block
              :disabled="!isFilterValid"
            >
              Excelを読み込む
            </v-btn>
          </v-col>

          <!-- From-Toフィルタ -->
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              label="From"
              type="date"
              v-model="filterFrom"
              outlined
              dense
              :rules="fromRules"
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              label="To"
              type="date"
              v-model="filterTo"
              outlined
              dense
              :rules="toRules"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-text-field
              label="From 2"
              type="date"
              v-model="filterFrom2"
              outlined
              dense
              :rules="fromRules2"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              label="To 2"
              type="date"
              v-model="filterTo2"
              outlined
              dense
              disabled
            ></v-text-field>
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
            <UGCChart :data="filteredSongInfoData" v-if="filteredSongInfoData.length > 0" />
          </v-col>
        </v-row>
      </v-container>

      <!-- Snackbar for Errors -->
      <v-snackbar v-model="snackbar" :timeout="6000" color="error">
        {{ snackbarMessage }}
        <v-btn color="white" variant="text" @click="snackbar = false">
          閉じる
        </v-btn>
      </v-snackbar>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import * as XLSX from 'xlsx'
import UGCChart from './components/UGCChart.vue'

// 型定義
interface SongInfo {
  楽曲名: string
  楽曲URL: string
  日付: string | number
  総UGC数: number
}

const fileInput = ref<HTMLInputElement | null>(null)
const songInfoData = ref<SongInfo[]>([])

// フィルタ用のFrom-To
const filterFrom = ref<string>('')
const filterTo = ref<string>('')

// 新しいフィルタ用のFrom-To
const filterFrom2 = ref<string>('')
const filterTo2 = computed(() => filterTo.value) // To 2 は To と同じ値

// バリデーションルール
const required = (value: string) => !!value || '必須項目です。'
const isValidDate = (dateStr: string): boolean => {
  const date = new Date(dateStr)
  return !isNaN(date.getTime())
}
const validDate = (value: string) => isValidDate(value) || '有効な日付を入力してください。'

// FromがToより前または同じであることを確認するルール
const fromBeforeTo = () => {
  if (filterFrom.value && filterTo.value) {
    return new Date(filterFrom.value) <= new Date(filterTo.value) || 'Fromの日付はToより前または同じでなければなりません。'
  }
  return true
}

// FromとToのルールを配列
const fromRules = [required, validDate, fromBeforeTo]
const toRules = [required, validDate, fromBeforeTo]

// From2のバリデーションルール（非必須）
const fromRules2 = [
  (value: string) => {
    if (value && !isValidDate(value)) {
      return '有効な日付を入力してください。'
    }
    return true
  },
  () => {
    if (filterFrom2.value) {
      return new Date(filterFrom2.value) <= new Date(filterTo2.value) || 'From 2の日付はTo 2より前または同じでなければなりません。'
    }
    return true
  }
]

// Snackbar state
const snackbar = ref(false)
const snackbarMessage = ref('')

// ファイル入力をトリガー
const triggerFileInput = () => {
  fileInput.value?.click()
}

// Snackbar表示関数
const showError = (message: string) => {
  snackbarMessage.value = message
  snackbar.value = true
}

// 行が完全に空かどうかを確認
const isRowEmpty = (row: any[]): boolean => {
  return row.every(cell => cell == null || cell === '')
}

// ファイル入力をリセットする関数
const resetFileInput = () => {
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// yyyymmdd形式にフォーマットする関数
const formatDateToYYYYMMDD = (dateStr: string): string => {
  const date = new Date(dateStr)
  const yyyy = date.getFullYear()
  const mm = (date.getMonth() + 1).toString().padStart(2, '0')
  const dd = date.getDate().toString().padStart(2, '0')
  return `${yyyy}${mm}${dd}`
}

// ファイル読み込み
const handleFile = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) {
    showError('ファイルが選択されていません。')
    resetFileInput()
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })

      const mainSheetName = '楽曲情報'
      if (!workbook.SheetNames.includes(mainSheetName)) {
        showError(`シート "${mainSheetName}" が見つかりません。`)
        return
      }

      // メインシートの処理
      const worksheet = workbook.Sheets[mainSheetName]
      const rawData: any[][] = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' })

      console.log(`"${mainSheetName}" シートのExcelデータ:`, rawData)

      // データの整形
      if (rawData.length > 1) {
        const headers: string[] = rawData[0] as string[]
        const data: SongInfo[] = rawData.slice(1)
          .filter(row => !isRowEmpty(row))
          .map((row, rowIndex) => {
            const rowData: Record<string, any> = {}
            headers.forEach((header, index) => {
              rowData[header] = row[index]
            })
            return rowData as SongInfo
          })

        // 不正データの検出
        data.forEach((item, index) => {
          if (!item.日付) {
            console.warn(`楽曲情報シートの行 ${index + 2} に日付が欠けています:`, item)
            showError(`楽曲情報シートの行 ${index + 2} に日付が欠けています。`)
          } else if (isNaN(new Date(item.日付 as string).getTime())) {
            console.warn(`楽曲情報シートの行 ${index + 2} に無効な日付形式があります:`, item.日付)
            showError(`楽曲情報シートの行 ${index + 2} に無効な日付形式があります。`)
          }
        })

        // 日付が存在し、有効なデータのみをフィルタリング
        songInfoData.value = data.filter(item => item.日付 && !isNaN(new Date(item.日付 as string).getTime()))
      }

      // 「To」日付を yyyymmdd 形式に変換
      if (filterTo.value) {
        const toDateStr = formatDateToYYYYMMDD(filterTo.value)
        console.log(`フォーマットされたTo日付: ${toDateStr}`)

        if (workbook.SheetNames.includes(toDateStr)) {
          const toSheet = workbook.Sheets[toDateStr]
          const toSheetData: any[][] = XLSX.utils.sheet_to_json(toSheet, { header: 1, defval: '' })
          console.log(`"${toDateStr}" シートのデータ:`, toSheetData)
        } else {
          console.warn(`シート "${toDateStr}" が見つかりません。`)
          showError(`シート "${toDateStr}" が見つかりません。`)
        }
      }
    } catch (error) {
      console.error('ファイルの解析中にエラーが発生しました:', error)
      showError('ファイルの解析中にエラーが発生しました。')
    } finally {
      // ファイル入力をリセット
      resetFileInput()
    }
  }
  reader.readAsArrayBuffer(file)
}

// フィルタの有効な日付形式かつFromがToの日付以下
const isFilterValid = computed(() => {
  return (
    isValidDate(filterFrom.value) &&
    isValidDate(filterTo.value) &&
    new Date(filterFrom.value) <= new Date(filterTo.value)
  )
})

// フィルタリングされたデータ
const filteredSongInfoData = computed(() => {
  if (!isFilterValid.value) {
    return []
  }

  return songInfoData.value.filter(item => {
    if (typeof item.日付 !== 'string') return false
    const itemDate = new Date(item.日付)
    const fromDate = new Date(filterFrom.value)
    const toDate = new Date(filterTo.value)
    const fromDate2 = filterFrom2.value ? new Date(filterFrom2.value) : null
    const toDate2 = filterTo2.value ? new Date(filterTo2.value) : null

    let valid = itemDate >= fromDate && itemDate <= toDate
    if (fromDate2 && toDate2) {
      valid = valid && itemDate >= fromDate2 && itemDate <= toDate2
    }
    return valid
  })
})

// filteredSongInfoDataがない場合
watch(filteredSongInfoData, (newData) => {
  if (isFilterValid.value && songInfoData.value.length > 0 && newData.length === 0) {
    showError('指定した期間内にデータがありません。')
  }
})
</script>

<style>
</style>