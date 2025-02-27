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

        <!-- ファイルアップロードボタンとエクスポートボタン -->
        <v-row class="my-4">
          <v-col cols="12" sm="6" md="3" class="d-flex">
            <FileUploadButton
              buttonLabel="Excelを読み込む"
              :disabled="!isFilterValid"
              @file-selected="handleFile"
            />
            <!-- エクスポートボタンを追加 -->
            <v-btn
              class="ml-2"
              color="primary"
              :disabled="!filteredSongInfoData.length"
              @click="handleExportChart"
            >
              チャートを保存
            </v-btn>
            <v-btn
              class="ml-2"
              color="primary"
              :disabled="!filteredSongInfoData.length"
              @click="handleExportIcons"
            >
              アイコンを保存
            </v-btn>
            <v-btn
              class="ml-2"
              color="primary"
              :disabled="!filteredSongInfoData.length"
              @click="handleExportChartAndIcons"
            >
              全体を保存
            </v-btn>
          </v-col>
        </v-row>

        <!-- グラフ表示 -->
        <v-row>
          <v-col cols="12">
            <UGCChart 
              ref="ugcChartRef"
              :data="filteredSongInfoData" 
              :top-follower-posts="uniqueAccounts.filter(account => account.isVisible)" 
              v-if="filteredSongInfoData.length > 0" 
            />  
          </v-col>
        </v-row>

        <v-row>
        <V-col cols="12" sm="6" md="4">
          <v-text-field
            v-model="searchAccountName"
            label="アカウント名で検索"
            append-icon="mdi-magnify"
            clearable
          ></v-text-field>
        </V-col>
      </v-row>

      <!-- ユニークアカウントのテーブル表示 -->
      <v-row>
        <v-col cols="12">
          <v-data-table
            :headers="tableHeaders"
            :items="filteredAccounts"
            class="elevation-1"
            :items-per-page="10"
          >
            <template v-slot:item.isVisible="{ item }">
              <v-checkbox
                v-model="item.isVisible"
                @change="toggleVisibility(item)"
              ></v-checkbox>
            </template>

            <template v-slot:item.isOrangeBorder="{ item }">
              <v-checkbox
                v-model="item.isOrangeBorder"
                @change="toggleOrangeBorder(item)"
              ></v-checkbox>
            </template>
          </v-data-table>
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
import type { SongInfo } from './types/SongInfo'
import type { TikTokPost } from './types/TikTokPost'
import { generateUniqueId } from './utils/generateUniqueId'

const songInfoData = ref<SongInfo[]>([])
const uniqueAccounts = ref<TikTokPost[]>([])
const searchAccountName = ref<string>('')

const filteredAccounts = computed(() => {
  if(!searchAccountName.value) return uniqueAccounts.value
  return uniqueAccounts.value.filter(account =>
    account.アカウント名.toLowerCase().includes(searchAccountName.value.toLowerCase())
  )
})

// フィルタ用のFrom-To
const filterFrom = ref<string>('')
const filterTo = ref<string>('')

// 新しいフィルタ用のFrom-To
const filterFrom2 = ref<string>('')
const filterTo2 = computed(() => filterTo.value) // To 2 は To と同じ値
const toggleVisibility = (item: TikTokPost) => {
}
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

const top30Followers = ref<TikTokPost[]>([])

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

const parsePostDate = (dateStr: string, toYear: number): string => {
  // 正規表現でmm/ddまたはyyyy/mm/ddを判定
  const mmddRegex = /^(\d{2})\/(\d{2})$/
  const yyyymmddRegex = /^(\d{4})\/(\d{2})\/(\d{2})$/

  if (yyyymmddRegex.test(dateStr)) {
    // 既にyyyy/mm/dd形式の場合はそのまま返す
    return dateStr
  }

  const mmddMatch = dateStr.match(mmddRegex)
  if (mmddMatch) {
    const month = mmddMatch[1]
    const day = mmddMatch[2]
    return `${toYear}/${month}/${day}`
  }

  // デフォルトで元の文字列を返す
  return dateStr
}

const applyFilters = () => {
  if (!isFilterValid.value) {
    filteredSongInfoData.value = []
    return
  }

  filteredSongInfoData.value = songInfoData.value.filter(item => {
    if (typeof item.日付 !== 'string') return false
    const itemDate = new Date(item.日付)
    const fromDate = new Date(filterFrom.value)
    const toDate = new Date(filterTo.value)

    return itemDate >= fromDate && itemDate <= toDate
  })
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

        // SongInfoマッピング（アイコンを除外）
        const data: SongInfo[] = rawData.slice(1)
          .filter(row => !isRowEmpty(row)) // 空の行を除外
          .map((row, rowIndex) => { // SongInfoにマッピング
            const rowData: Record<string, any> = {}

            headers.forEach((header, index) => {
              const key = header.trim() !== '' ? header : undefined
              if (key) rowData[key] = row[index]
            })

            rowData.isOrangeBorder = false

            return rowData as SongInfo
          })

        // 日付が存在し、有効なデータのみをフィルタリング
        songInfoData.value = data.filter(item => item.日付 && !isNaN(new Date(item.日付 as string).getTime())
        )

        // フィルタ適用
        applyFilters()
        console.log("楽曲情報: ", filteredSongInfoData.value)
      }

      // 「To」日付の処理
      if (filterTo.value) {
        const toDate = new Date(filterTo.value)
        const toYear = toDate.getFullYear()
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
            // アイコン列のインデックスを固定で指定
            const ICON_COLUMN_INDEX = 12 // M列

            // データ部分をフィルタリング
            const filteredToSheetData: TikTokPost[] = toSheetData.slice(1)
              .filter(row => row[postIdIndex] && row[postIdIndex].toString().trim() !== '')
              .map(row => {
                const rowData: Record<string, any> = {}

                toHeaders.forEach((header, index) => {
                  if (index === ICON_COLUMN_INDEX) {
                    rowData['アイコン'] = row[index] // M列を 'アイコン' としてマッピング
                  } else {
                    const key = header.trim() !== '' ? header : undefined
                    if (key) rowData[key] = row[index]
                  }
                })

                // 投稿日のパースを追加
                if (rowData['投稿日']) {
                  rowData['投稿日'] = parsePostDate(rowData['投稿日'], toYear)
                }

                return {
                  ...rowData,
                  uniqueId: generateUniqueId(),
                  isVisible: false, // 初期状態は非表示
                  isOrangeBorder: false,
                } as TikTokPost
              })
            
            console.log(`"${toDateStr}" シート: `, filteredToSheetData)

            // フィルタリング（From2とTo2）
            if (filterFrom2.value && filterTo2.value) {
              const fromDate2 = new Date(filterFrom2.value)
              const toDate2 = new Date(filterTo2.value)

              const furtherFilteredData = filteredToSheetData.filter(post => {
                if (!post.投稿日) return false
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

              uniqueAccounts.value = Array.from(uniqueAccountsMap.values())
              console.log('重複排除後のデータ:', uniqueAccounts)

              // フォロワー数で降順ソートし、トップ30を取得
              top30Followers.value = uniqueAccounts.value
                .sort((a, b) => b.フォロワー数 - a.フォロワー数)
                .slice(0, 30)
              
              uniqueAccounts.value.forEach(account => {
                if (top30Followers.value.find(top => top.uniqueId === account.uniqueId)) {
                  account.isVisible = true
                } else {
                  account.isVisible = false
                }
              })

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

// エクスポートボタン用のref
const ugcChartRef = ref<InstanceType<typeof UGCChart> | null>(null)

// エクスポートハンドラー
const handleExportChart = () => {
  if (ugcChartRef.value) {
    ugcChartRef.value.exportChartAsImage()
  }
}

const handleExportIcons = () => {
  if (ugcChartRef.value) {
    ugcChartRef.value.exportIconsAsImage()
  }
}

const handleExportChartAndIcons = () => {
  if (ugcChartRef.value) {
    ugcChartRef.value.exportChartAndIconsAsImage()
  }
}

const filteredSongInfoData = ref<SongInfo[]>([])

const tableHeaders = [
  { title: '表示', key: 'isVisible' },  
  { title: 'オレンジ', key: 'isOrangeBorder' },
  { title: 'アカウント名', key: 'アカウント名' },
  { title: 'ニックネーム', key: 'ニックネーム' },
  { title: 'いいね数', key: 'いいね数' },
  { title: 'コメント数', key: 'コメント数' },
  { title: '保存数', key: '保存数' },
  { title: 'シェア数', key: 'シェア数' },
  { title: '再生回数', key: '再生回数' },
  { title: 'フォロワー数', key: 'フォロワー数' },
]

const toggleOrangeBorder = (item: TikTokPost) => {
}
</script>

<style>
.ml-2 {
  margin-left: 8px;
}
</style>