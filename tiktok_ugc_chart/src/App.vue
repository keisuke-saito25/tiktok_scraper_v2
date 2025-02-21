<template>
  <v-app>
    <v-main>
      <v-container>
        <!-- 日付フィルタ -->
        <v-row align="center" justify="start" class="my-4" spacing="4">
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

        <!-- ファイルアップロードボタン -->
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <FileUploadButton
              buttonLabel="Excelを読み込む"
              :disabled="!isFilterValid"
              @file-selected="handleFile"
            />
          </v-col>
        </v-row>

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
import FileUploadButton from './components/FileUploadButton.vue'

// 型定義
interface SongInfo {
  楽曲名: string
  楽曲URL: string
  日付: string | number
  総UGC数: number
}

interface TikTokPost {
  投稿ID: string
  投稿日: string
  アカウント名: string
  ニックネーム: string
  いいね数: number
  コメント数: number
  保存数: number
  シェア数: number
  再生回数: number
  フォロワー数: number
  動画リンク_URL: string
  更新日: string
  アイコン: string
}

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

// Snackbar表示関数
const showError = (message: string) => {
  snackbarMessage.value = message
  snackbar.value = true
}

// 行が完全に空かどうかを確認
const isRowEmpty = (row: any[]): boolean => {
  return row.every(cell => cell == null || cell === '')
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
const handleFile = (file: File) => {
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

      // データの整形
      if (rawData.length > 1) {
        const headers: string[] = rawData[0] as string[]
        const data: SongInfo[] = rawData.slice(1)
          .filter(row => !isRowEmpty(row)) // 空の行を除外
          .map((row) => { // SongInfoにマッピング
            const rowData: Record<string, any> = {}
            headers.forEach((header, index) => {
              rowData[header] = row[index]
            })
            return rowData as SongInfo
          })

        // 日付が存在し、有効なデータのみをフィルタリング
        songInfoData.value = data.filter(item => item.日付 && !isNaN(new Date(item.日付 as string).getTime()))
        console.log("楽曲情報: ", songInfoData.value)
      }

      // 「To」日付を yyyymmdd 形式に変換
      if (filterTo.value) {
        const toDateStr = formatDateToYYYYMMDD(filterTo.value)
        console.log(`フォーマットされたTo日付: ${toDateStr}`)

        if (workbook.SheetNames.includes(toDateStr)) {
          const toSheet = workbook.Sheets[toDateStr]
          let toSheetData: any[][] = XLSX.utils.sheet_to_json(toSheet, { header: 1, defval: '' })
          
          // ヘッダーを取得
          const toHeaders: string[] = toSheetData[0] as string[]
          
          // 投稿IDのインデックスを取得
          const postIdIndex = toHeaders.indexOf('投稿ID')
          if (postIdIndex === -1) {
            showError(`"投稿ID" 列が "${toDateStr}" シートに存在しません。`)
          } else {
            // データ部分をフィルタリング
            const filteredToSheetData: TikTokPost[] = toSheetData.slice(1)
              .filter(row => row[postIdIndex] && row[postIdIndex].toString().trim() !== '')
              .map(row => {
                const rowData: Record<string, any> = {}
                toHeaders.forEach((header, index) => {
                  rowData[header] = row[index]
                })
                return rowData as TikTokPost
              })
            
            console.log(`"${toDateStr}" シート: `, filteredToSheetData)

            // filterFrom2とfilterTo2を使ってフィルタリング
            if (filterFrom2.value && filterTo2.value) {
              const fromDate2 = new Date(filterFrom2.value)
              const toDate2 = new Date(filterTo2.value)

              const furtherFilteredData = filteredToSheetData.filter(post => {
                const postDate = new Date(post.投稿日)
                return postDate >= fromDate2 && postDate <= toDate2
              })

              console.log(`"${toDateStr}" シートの From2-To2 範囲でフィルタリングされたデータ:`, furtherFilteredData)

              // アカウント名で重複を排除し、投稿日が最も古いものを保持
              const uniqueAccountsMap = new Map<string, TikTokPost>()

              furtherFilteredData.forEach(post => {
                const accountName = post.アカウント名
                const postDate = new Date(post.投稿日)

                if (!uniqueAccountsMap.has(accountName)) {
                  uniqueAccountsMap.set(accountName, post)
                } else {
                  const existingPost = uniqueAccountsMap.get(accountName)!
                  const existingDate = new Date(existingPost.投稿日)
                  if (postDate < existingDate) {
                    uniqueAccountsMap.set(accountName, post)
                  }
                }
              })

              const uniqueAccounts = Array.from(uniqueAccountsMap.values())
              console.log('重複排除後のデータ:', uniqueAccounts)

              // フォロワー数で降順ソートし、トップ30を取得
              const top30Followers = uniqueAccounts
                .sort((a, b) => b.フォロワー数 - a.フォロワー数)
                .slice(0, 30)

              console.log('フォロワー数 TOP 30:', top30Followers)

            } else {
              console.log('From2 と To2 のフィルタが設定されていません。')
            }
          }
        } else {
          console.warn(`シート "${toDateStr}" が見つかりません。`)
          showError(`シート "${toDateStr}" が見つかりません。`)
        }
      }
    } catch (error) {
      console.error('ファイルの解析中にエラーが発生しました:', error)
      showError('ファイルの解析中にエラーが発生しました。')
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

    return itemDate >= fromDate && itemDate <= toDate
  })
})

// filteredSongInfoDataがない場合の処理
watch(filteredSongInfoData, (newData) => {
  if (isFilterValid.value && songInfoData.value.length > 0 && newData.length === 0) {
    showError('指定した期間内にデータがありません。')
  }
})
</script>

<style>
</style>