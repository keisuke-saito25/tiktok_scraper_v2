<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>TikTok分析ダッシュボード</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container>
        <!-- 機能切り替えタブ -->
        <v-tabs v-model="activeTab" background-color="primary" dark>
          <v-tab value="ugc-chart">UGCチャート</v-tab>
          <v-tab value="ranking">ランキング</v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="mt-5">
          <!-- UGCチャート機能 -->
          <v-window-item value="ugc-chart">
            <!-- 日付フィルタ -->
            <DateRangeFilter 
              :initial-from="filterFrom"
              :initial-to="filterTo"
              :initial-from2="filterFrom2"
              @update:filters="handleFilterUpdate"
            />

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

            <v-row v-if="currentFileName" class="my-4">
              <v-col cols="12">
                <span class="current-file-name">
                  現在読み込んでいるファイル: {{ currentFileName }}
                </span>
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

            <!-- アカウントテーブル -->
            <AccountsTable 
              :accounts="uniqueAccounts"
              @toggle-visibility="toggleVisibility"
              @toggle-orange-border="toggleOrangeBorder"
            />
          </v-window-item>

          <!-- ランキング機能 -->
          <v-window-item value="ranking">
            <TikTokRanking />
          </v-window-item>
        </v-window>
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
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'
import UGCChart from './components/UGCChart.vue'
import FileUploadButton from './components/FileUploadButton.vue'
import DateRangeFilter from './components/DateRangeFilter.vue'
import AccountsTable from './components/AccountsTable.vue'
import TikTokRanking from './components/TikTokRanking.vue'
import type { SongInfo } from './types/SongInfo'
import type { TikTokPost } from './types/TikTokPost'
import { 
  extractSongInfoData, 
  extractTikTokPostData, 
  filterPostsByDateRange, 
  getUniqueAccountsMap, 
  getTopFollowerPosts,
  extractUserIconMap
} from './utils/fileHandler'
import { formatDateToYYYYMMDD, isValidDate } from './utils/dateUtils'

// アクティブタブ
const activeTab = ref('ugc-chart')

// データモデル
const songInfoData = ref<SongInfo[]>([])
const uniqueAccounts = ref<TikTokPost[]>([])
const filteredSongInfoData = ref<SongInfo[]>([])
const userIconMap = ref<Map<string, string>>(new Map())

// フィルタ用の日付
const filterFrom = ref<string>('')
const filterTo = ref<string>('')
const filterFrom2 = ref<string>('')

// チャート参照
const ugcChartRef = ref<InstanceType<typeof UGCChart> | null>(null)

// Snackbar状態
const snackbar = ref(false)
const snackbarMessage = ref('')

// フィルタの有効性
const isFilterValid = ref(false)

// トップフォロワー
const top30Followers = ref<TikTokPost[]>([])

// フィルター更新ハンドラー
const handleFilterUpdate = (filters: { from: string, to: string, from2: string, to2: string, isValid: boolean }) => {
  filterFrom.value = filters.from
  filterTo.value = filters.to
  filterFrom2.value = filters.from2
  isFilterValid.value = filters.isValid
  
  // 日付変更時にはフィルター適用しない（データの更新は行わない）
  // applyFilters()
}

// データにフィルターを適用
const applyFilters = () => {
  if (!isFilterValid.value) {
    filteredSongInfoData.value = []
    return
  }

  try {
    filteredSongInfoData.value = songInfoData.value.filter(item => {
      if (typeof item.日付 !== 'string') return false
      const itemDate = new Date(item.日付)
      const fromDate = new Date(filterFrom.value)
      const toDate = new Date(filterTo.value)

      return itemDate >= fromDate && itemDate <= toDate
    })
  } catch (error) {
    console.error('フィルター適用中にエラーが発生しました:', error)
    filteredSongInfoData.value = []
  }
}

// エラー表示関数
const showError = (message: string) => {
  snackbarMessage.value = message
  snackbar.value = true
}

// 現在読み込んでいるファイル名を保持
const currentFileName = ref<string | null>(null)

// ファイル読み込み処理
const handleFile = (file: File) => {
  // 現在のファイル名を設定
  currentFileName.value = file.name

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })

      // ユーザーアイコンシートの処理
      console.log('Excelの読み込みが完了しました。シート一覧:', workbook.SheetNames);
      
      const userIconSheetName = 'ユーザーアイコン'
      if (workbook.SheetNames.includes(userIconSheetName)) {
        console.log(`"${userIconSheetName}"シートが見つかりました。データを読み込みます。`);
        const userIconSheet = workbook.Sheets[userIconSheetName]
        
        try {
          // シートの内容を確認用に出力
          const rawData = XLSX.utils.sheet_to_json(userIconSheet, { header: 1 });
          console.log('ユーザーアイコンシートの生データ（先頭5行）:', rawData.slice(0, 5));
          
          userIconMap.value = extractUserIconMap(userIconSheet)
          console.log(`${userIconMap.value.size}件のユーザーアイコンデータを読み込みました。`);
          
          // いくつかのアカウント名とパスをサンプル表示
          if (userIconMap.value.size > 0) {
            const sampleEntries = Array.from(userIconMap.value.entries()).slice(0, 3);
            console.log('アイコンマップのサンプル:', sampleEntries);
          }
        } catch (error) {
          console.error('ユーザーアイコンシートの処理中にエラーが発生しました:', error);
          userIconMap.value = new Map();
        }
      } else {
        console.warn(`シート "${userIconSheetName}" が見つかりません。アイコンは従来の方法で取得します。`);
        userIconMap.value = new Map();
      }

      // 楽曲情報シート処理
      const mainSheetName = '楽曲情報'
      if (!workbook.SheetNames.includes(mainSheetName)) {
        showError(`シート "${mainSheetName}" が見つかりません。`)
        return
      }

      // メインシートの処理
      const worksheet = workbook.Sheets[mainSheetName]
      songInfoData.value = extractSongInfoData(worksheet)
      
      // filterFrom2 が空の場合のみ filterFrom の値を設定
      if (!filterFrom2.value) {
        filterFrom2.value = filterFrom.value
      }
      
      // フィルタ適用
      applyFilters()
      
      // 処理が完了したらある程度の遅延を設けて次の処理を実行
      setTimeout(() => {
        processTikTokData(workbook);
      }, 100);
    } catch (error) {
      console.error('ファイルの解析中にエラーが発生しました:', error)
      showError('ファイルの解析中にエラーが発生しました。')
    }
  }
  reader.readAsArrayBuffer(file)
}

// TikTokデータ処理を分離
const processTikTokData = (workbook: XLSX.WorkBook) => {
  try {
    // 「To」日付の処理
    if (filterTo.value) {
      const toDate = new Date(filterTo.value)
      const toDateStr = formatDateToYYYYMMDD(filterTo.value)
      
      if (workbook.SheetNames.includes(toDateStr)) {
        const toSheet = workbook.Sheets[toDateStr]
        
        try {
          console.log(`"${toDateStr}"シートからTikTokポストデータを抽出します。`);
          console.log(`ユーザーアイコンマップには${userIconMap.value.size}件のデータがあります。`);
          
          // TikTokポストの抽出（ユーザーアイコンマップを渡す）
          const tikTokPosts = extractTikTokPostData(toSheet, toDate, userIconMap.value)
          console.log(`${tikTokPosts.length}件のTikTokポストデータを抽出しました。`);
          
          // 最初の数件のアイコンパスを確認
          if (tikTokPosts.length > 0) {
            const samplePosts = tikTokPosts.slice(0, 3);
            console.log('TikTokポストサンプル（アイコンパス確認用）:', samplePosts.map(post => ({
              アカウント名: post.アカウント名,
              アイコン: post.アイコン
            })));
          }
          
          // 日付範囲でフィルタリング
          if (filterFrom2.value && filterTo.value) {
            const fromDate2 = new Date(filterFrom2.value)
            const toDate2 = new Date(filterTo.value)
            
            console.log(`日付範囲でフィルタリング: ${fromDate2.toISOString()} から ${toDate2.toISOString()}`);
            const filteredPosts = filterPostsByDateRange(tikTokPosts, fromDate2, toDate2)
            console.log(`フィルタリング後: ${filteredPosts.length}件のデータが残りました。`);
            
            // ユニークなアカウントを取得
            const uniqueAccountsMap = getUniqueAccountsMap(filteredPosts)
            uniqueAccounts.value = Array.from(uniqueAccountsMap.values())
            
            // フォロワー数でトップ30取得
            top30Followers.value = getTopFollowerPosts(uniqueAccounts.value, 30)
            
            // トップ30を表示状態に設定
            uniqueAccounts.value.forEach(account => {
              account.isVisible = !!top30Followers.value.find(
                top => top.uniqueId === account.uniqueId
              )
            })
          }
        } catch (error) {
          console.error('TikTokポストの処理中にエラーが発生しました:', error)
          showError('TikTokポストの処理中にエラーが発生しました。')
        }
      } else {
        showError(`シート "${toDateStr}" が見つかりません。`)
      }
    }
  } catch (error) {
    console.error('TikTokデータ処理中にエラーが発生しました:', error)
    showError('TikTokデータ処理中にエラーが発生しました。')
  }
}

// アカウントの表示状態を切り替える
const toggleVisibility = (account: TikTokPost, value: boolean | null) => {
  const foundAccount = uniqueAccounts.value.find(a => a.uniqueId === account.uniqueId)
  if (foundAccount && value !== null) {
    // 状態が変わらない場合は更新しない（不要な再レンダリングを防止）
    if (foundAccount.isVisible === value) return;
    
    foundAccount.isVisible = value
  }
}

// オレンジ枠の状態を切り替える
const toggleOrangeBorder = (account: TikTokPost, value: boolean | null) => {
  const foundAccount = uniqueAccounts.value.find(a => a.uniqueId === account.uniqueId)
  if (foundAccount && value !== null) {
    // 状態が変わらない場合は更新しない（不要な再レンダリングを防止）
    if (foundAccount.isOrangeBorder === value) return;
    
    foundAccount.isOrangeBorder = value
  }
}

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
</script>

<style>
.ml-2 {
  margin-left: 8px;
}
</style>