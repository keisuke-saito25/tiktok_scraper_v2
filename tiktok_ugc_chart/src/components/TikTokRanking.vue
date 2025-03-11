<template>
  <div>
    <v-row class="justify-center align-center">
      <v-col cols="12" sm="6" md="3">
        <FileUploadButton
          buttonLabel="Excelを読み込む"
          @file-selected="handleFile"
        />
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-text-field
          label="日付を選択"
          type="date"
          v-model="selectedDate"
          outlined
          dense
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" sm="6" md="6">
        <!-- 複数選択に変更 -->
        <div class="ranking-type-checkboxes">
          <h3 class="subtitle-1 mb-2">ランキング種類（複数選択可）</h3>
          <v-checkbox
            v-for="type in rankingTypes"
            :key="type"
            v-model="selectedRankingTypes"
            :label="type"
            :value="type"
            dense
            hide-details
            class="ranking-checkbox"
          ></v-checkbox>
        </div>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <v-col cols="12" class="d-flex justify-center">
        <v-btn
          color="primary"
          :disabled="!selectedDate || selectedRankingTypes.length === 0 || !excelLoaded"
          @click="generateRankings"
          class="mr-2"
        >
          選択したランキングを生成
        </v-btn>
        
        <v-btn
          color="success"
          :disabled="!rankingGenerated"
          @click="exportAllRankings"
        >
          選択した画像を保存
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
    
    <!-- ランキング表示エリア（横スクロール可能な横並び） -->
    <div v-if="generatedRankings.length > 0" class="mt-6">
      <div class="ranking-scroll-container">
        <div
          v-for="(ranking, index) in generatedRankings"
          :key="index"
          class="ranking-scroll-item"
        >
          <div :ref="`rankingContainer_${index}`" class="ranking-container">
            <div class="ranking-title">
              <div class="title-badge">TikTok Ranking</div>
              <h1>{{ getRankingType(ranking.rankingType) }} <span>TOP 10</span></h1>
              <div class="song-title-container" v-if="ranking.songTitle">
                <div class="song-title-badge">曲名</div>
                <div class="song-title-text">{{ ranking.songTitle }}</div>
              </div>
              <p>{{ formatDate(selectedDate) }}</p>
            </div>
            
            <div class="ranking-list">
              <div v-for="(item, idx) in ranking.items" :key="item.uniqueId" class="ranking-item">
                <div class="ranking-position">
                  <span class="position-number">{{ idx + 1 }}</span>
                </div>
                
                <div class="ranking-icon">
                  <img :src="item.アイコン" :alt="item.アカウント名" referrerpolicy="no-referrer" />
                </div>
                
                <div class="ranking-details">
                  <div class="account-name" :title="item.ニックネーム || item.アカウント名">
                    {{ truncateNickname(item.ニックネーム || item.アカウント名) }}
                  </div>
                  <div class="account-id" :title="'@' + item.アカウント名">
                    @{{ truncateAccountName(item.アカウント名) }}
                  </div>

                  <div class="ranking-stats">
                    <div class="ranking-value">
                      <span class="value-label">{{ getRankingLabel(ranking.rankingType) }}</span> 
                      <span class="value-number">{{ formatRankingValue(getRankingValue(item, ranking.rankingType)) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="ranking-footer">
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Snackbar for Errors/Messages -->
    <v-snackbar v-model="snackbar" :timeout="6000" :color="snackbarColor">
      {{ snackbarMessage }}
      <v-btn color="white" variant="text" @click="snackbar = false">
        閉じる
      </v-btn>
    </v-snackbar>
    
    <!-- プログレスダイアログ -->
    <v-dialog v-model="processingDialog" persistent max-width="300">
      <v-card>
        <v-card-title class="headline">処理中</v-card-title>
        <v-card-text>
          <p>{{ processingMessage }}</p>
          <v-progress-linear
            indeterminate
            color="primary"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import * as XLSX from 'xlsx'
import FileUploadButton from './FileUploadButton.vue'
import { formatDateToYYYYMMDD, formatDateToYYYYMMDDWithSlash } from '../utils/dateUtils'
import type { TikTokPost } from '../types/TikTokPost'
import type { SongInfo } from '../types/SongInfo'
import { extractTikTokPostData, extractSongInfoData, extractUserIconMap } from '../utils/fileHandler'
import html2canvas from 'html2canvas'

// ランキングデータの構造
interface RankingData {
  items: TikTokPost[];
  rankingType: string;
  songTitle?: string;
}

// データと状態
const selectedDate = ref('')
const selectedRankingTypes = ref<string[]>([]) // 複数選択用の配列
const tikTokPosts = ref<TikTokPost[]>([])
const songInfoData = ref<SongInfo[]>([])
const excelLoaded = ref(false)
const rankingGenerated = ref(false)
const workbook = ref<XLSX.WorkBook | null>(null)
const generatedRankings = ref<RankingData[]>([]) // 複数のランキングを保持
const userIconMap = ref<Map<string, string>>(new Map())

// プログレス表示用
const processingDialog = ref(false)
const processingMessage = ref('')

// ランキング種類のオプション
const rankingTypes = [
  'いいね数',
  'コメント数',
  'シェア数',
  '保存数',
  '再生回数',
  'フォロワー数'
]

// Snackbar状態
const snackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('error')

// 現在読み込んでいるファイル名を保持する変数
const currentFileName = ref<string | null>(null)

// エラー表示関数
const showError = (message: string) => {
  snackbarMessage.value = message
  snackbarColor.value = 'error'
  snackbar.value = true
}

// 成功メッセージ表示関数
const showSuccess = (message: string) => {
  snackbarMessage.value = message
  snackbarColor.value = 'success'
  snackbar.value = true
}

// ファイル読み込み処理
const handleFile = (file: File) => {
  // 現在のファイル名を設定
  currentFileName.value = file.name
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      workbook.value = XLSX.read(data, { type: 'array' })
      
      // ユーザーアイコンシートからアイコンパスのマップを取得
      console.log('TikTokRanking: Excelの読み込みが完了しました。シート一覧:', workbook.value.SheetNames);
      
      const userIconSheetName = 'ユーザーアイコン'
      if (workbook.value.SheetNames.includes(userIconSheetName)) {
        console.log(`TikTokRanking: "${userIconSheetName}"シートが見つかりました。データを読み込みます。`);
        const userIconSheet = workbook.value.Sheets[userIconSheetName]
        
        try {
          // シートの内容を確認用に出力
          const rawData = XLSX.utils.sheet_to_json(userIconSheet, { header: 1 });
          console.log('TikTokRanking: ユーザーアイコンシートの生データ（先頭5行）:', rawData.slice(0, 5));
          
          userIconMap.value = extractUserIconMap(userIconSheet)
          console.log(`TikTokRanking: ${userIconMap.value.size}件のユーザーアイコンデータを読み込みました。`);
          
          // いくつかのアカウント名とパスをサンプル表示
          if (userIconMap.value.size > 0) {
            const sampleEntries = Array.from(userIconMap.value.entries()).slice(0, 3);
            console.log('TikTokRanking: アイコンマップのサンプル:', sampleEntries);
          }
        } catch (error) {
          console.error('TikTokRanking: ユーザーアイコンシートの処理中にエラーが発生しました:', error);
          userIconMap.value = new Map();
        }
      } else {
        console.warn(`TikTokRanking: シート "${userIconSheetName}" が見つかりません。アイコンは従来の方法で取得します。`);
        userIconMap.value = new Map();
      }
      
      // 楽曲情報シートのデータを読み込む
      const mainSheetName = '楽曲情報'
      if (workbook.value.SheetNames.includes(mainSheetName)) {
        const worksheet = workbook.value.Sheets[mainSheetName]
        songInfoData.value = extractSongInfoData(worksheet)
      } else {
        console.warn(`シート "${mainSheetName}" が見つかりません。曲名情報なしで続行します。`)
      }
      
      excelLoaded.value = true
    } catch (error) {
      console.error('ファイルの解析中にエラーが発生しました:', error)
      showError('ファイルの解析中にエラーが発生しました。')
      excelLoaded.value = false
    }
  }
  reader.readAsArrayBuffer(file)
}

// 指定された日付の楽曲を取得する関数
const getSongForDate = (dateStr: string): string => {
  if (!songInfoData.value || songInfoData.value.length === 0) {
    return ''
  }
  
  const targetDate = new Date(dateStr)
  
  // 日付が一致する楽曲情報を検索
  const matchingSong = songInfoData.value.find(song => {
    const songDate = new Date(song.日付)
    return songDate.toDateString() === targetDate.toDateString()
  })
  
  return matchingSong ? matchingSong.楽曲名 : ''
}

// 選択されたすべてのランキングを生成する関数
const generateRankings = async () => {
  if (!workbook.value || !selectedDate.value || selectedRankingTypes.value.length === 0) {
    showError('Excelファイル、日付、およびランキング種類を選択してください。')
    return
  }

  // プログレス表示を開始
  processingDialog.value = true
  processingMessage.value = 'ランキングデータを生成中...'
  
  try {
    const dateStr = formatDateToYYYYMMDD(selectedDate.value)
    
    if (!workbook.value.SheetNames.includes(dateStr)) {
      processingDialog.value = false
      showError(`シート "${dateStr}" が見つかりません。`)
      return
    }

    const sheet = workbook.value.Sheets[dateStr]
    const date = new Date(selectedDate.value)
    
    // TikTokポストの抽出（再利用するためにここで一度だけ実行）
    tikTokPosts.value = extractTikTokPostData(sheet, date, userIconMap.value)
    
    // 該当日付の楽曲名を取得
    const songTitle = getSongForDate(selectedDate.value)
    
    // 生成済みのランキングをリセット
    generatedRankings.value = []
    
    // 選択されたすべてのランキング種類について処理
    for (const rankingType of selectedRankingTypes.value) {
      processingMessage.value = `${rankingType}のランキングを生成中...`
      
      // ランキング種類によるソート
      const rankingProperty = rankingType as keyof TikTokPost
      
      // 重複ユーザーを除外して上位10件を取得
      const uniqueUserPosts = removeDuplicateUsers([...tikTokPosts.value])
      
      const sortedItems = uniqueUserPosts
        .sort((a, b) => {
          const aValue = a[rankingProperty] as number
          const bValue = b[rankingProperty] as number
          return bValue - aValue
        })
        .slice(0, 10)
      
      if (sortedItems.length > 0) {
        // 生成されたランキングを追加
        generatedRankings.value.push({
          items: sortedItems,
          rankingType: rankingType,
          songTitle: songTitle
        })
      }
    }
    
    if (generatedRankings.value.length === 0) {
      processingDialog.value = false
      showError('ランキングデータが見つかりませんでした。')
      return
    }
    
    rankingGenerated.value = true
    processingDialog.value = false
    showSuccess(`${generatedRankings.value.length}種類のランキングを生成しました。`)
  } catch (error) {
    console.error('ランキング生成中にエラーが発生しました:', error)
    processingDialog.value = false
    showError('ランキング生成中にエラーが発生しました。')
  }
}

// ランキングタイプの英語表記を取得する関数
const getRankingType = (rankingType: string) => {
  const labels: Record<string, string> = {
    'いいね数': 'LIKES',
    'コメント数': 'COMMENTS',
    'シェア数': 'SHARES',
    '保存数': 'SAVES',
    '再生回数': 'VIEWS',
    'フォロワー数': 'FOLLOWERS'
  }
  
  return labels[rankingType] || rankingType
}

// ランキングのラベルを取得
const getRankingLabel = (rankingType: string) => {
  const labels: Record<string, string> = {
    'いいね数': 'いいね',
    'コメント数': 'コメント',
    'シェア数': 'シェア',
    '保存数': '保存',
    '再生回数': '再生数',
    'フォロワー数': 'フォロワー'
  }
  
  return labels[rankingType] || rankingType
}

// 日付のフォーマット
const formatDate = (dateStr: string) => {
  return formatDateToYYYYMMDDWithSlash(dateStr)
}

// ランキング値のフォーマット
const formatRankingValue = (value: number) => {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1)}万`
  }
  return value.toLocaleString()
}

// 指定されたランキング種類で値を取得
const getRankingValue = (item: TikTokPost, rankingType: string): number => {
  return item[rankingType as keyof TikTokPost] as number;
}

// 重複ユーザーを除外する関数（アカウント名をキーとして最初の投稿のみ残す）
const removeDuplicateUsers = (posts: TikTokPost[]): TikTokPost[] => {
  const uniqueUsers = new Map<string, TikTokPost>()
  
  posts.forEach(post => {
    if (!uniqueUsers.has(post.アカウント名)) {
      uniqueUsers.set(post.アカウント名, post)
    }
  })
  
  return Array.from(uniqueUsers.values())
}

// 単一ランキングの画像をエクスポートする関数
const exportSingleRanking = async (index: number) => {
  const containerRef = document.querySelector(`.ranking-container:nth-child(${index + 1})`) as HTMLElement;
  
  if (!containerRef) {
    showError('ランキングコンテナが見つかりません。')
    return
  }
  
  try {
    processingDialog.value = true
    processingMessage.value = `${generatedRankings.value[index].rankingType}のランキング画像を保存中...`
    
    await exportRankingImage(containerRef, generatedRankings.value[index].rankingType)
    
    processingDialog.value = false
    showSuccess(`${generatedRankings.value[index].rankingType}のランキング画像を保存しました。`)
  } catch (error) {
    console.error('ランキング画像のエクスポート中にエラーが発生しました:', error)
    processingDialog.value = false
    showError('ランキング画像のエクスポート中にエラーが発生しました。')
  }
}

// すべてのランキング画像をエクスポートする関数
const exportAllRankings = async () => {
  if (generatedRankings.value.length === 0) {
    showError('保存するランキングがありません。')
    return
  }
  
  processingDialog.value = true
  processingMessage.value = 'すべてのランキング画像を保存中...'
  
  try {
    // 各ランキングを順番に処理
    for (let i = 0; i < generatedRankings.value.length; i++) {
      const rankingType = generatedRankings.value[i].rankingType
      processingMessage.value = `${rankingType}のランキング画像を保存中... (${i + 1}/${generatedRankings.value.length})`
      
      const containerRef = document.querySelectorAll('.ranking-container')[i] as HTMLElement
      if (containerRef) {
        await exportRankingImage(containerRef, rankingType)
        // 少し待機して連続ダウンロードによるブラウザの制限を回避
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }
    
    processingDialog.value = false
    showSuccess(`${generatedRankings.value.length}種類のランキング画像を保存しました。`)
  } catch (error) {
    console.error('ランキング画像のエクスポート中にエラーが発生しました:', error)
    processingDialog.value = false
    showError('ランキング画像のエクスポート中にエラーが発生しました。')
  }
}

// ランキング画像のエクスポート処理（共通関数）
const exportRankingImage = async (containerElement: HTMLElement, rankingType: string) => {
  // 既存のスタイルをキャプチャ
  const originalStyles = window.getComputedStyle(containerElement);
  
  // html2canvasのオプションを詳細に設定
  const canvas = await html2canvas(containerElement, {
    useCORS: true,
    allowTaint: true,
    backgroundColor: '#ffffff',
    scale: 2, // 高解像度化
    logging: false,
    removeContainer: false,
    foreignObjectRendering: false
  })
  
  // 画像としてダウンロード
  const link = document.createElement('a')
  link.download = `ranking_${rankingType}_${formatDateToYYYYMMDD(selectedDate.value)}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
}

// ニックネームを適切な長さに省略する関数（日本語と英数字の幅の違いを考慮）
const truncateNickname = (text: string, maxLength = 20): string => {
  if (!text) return '';
  
  // 文字列の表示幅を概算する (日本語は2、英数字は1と仮定)
  let displayWidth = 0;
  let truncatedText = '';
  
  for (let i = 0; i < text.length; i++) {
    // 日本語やその他の全角文字は幅が広い
    const charCode = text.charCodeAt(i);
    const charWidth = (charCode >= 0x3000 && charCode <= 0x9FFF) ||
                     (charCode >= 0xFF00 && charCode <= 0xFFEF) ? 2 : 1;
                     
    displayWidth += charWidth;
    
    if (displayWidth > maxLength) {
      truncatedText += '…';
      break;
    }
    
    truncatedText += text.charAt(i);
  }
  
  return truncatedText;
}

// アカウント名も同様に省略する関数
const truncateAccountName = (text: string, maxLength = 16): string => {
  if (!text) return '';
  // 省略
  if (text.length > maxLength) {
    return text.substring(0, maxLength - 1) + '…';
  }
  return text;
}
</script>

<style scoped>
.ranking-type-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
}

.ranking-checkbox {
  width: auto;
  margin-right: 12px;
}

.ranking-scroll-container {
  display: flex;
  overflow-x: auto;
  padding: 20px 10px;
  gap: 20px;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}

.ranking-scroll-item {
  flex: 0 0 auto;
  scroll-snap-align: start;
  margin-bottom: 20px;
}

.ranking-container {
  background-color: #f5f7fc;
  color: #111;
  border-radius: 0; /* 0に変更して四角形にする */
  padding: 40px; 
  width: 600px;
  margin: 0 auto;
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.03),
    0 15px 30px rgba(106, 90, 255, 0.04);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  position: relative;
  overflow: hidden;
}

.ranking-title {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.title-badge {
  background: #4361EE;
  color: white;
  font-size: 14px;
  font-weight: 800;
  padding: 9px 20px;
  border-radius: 100px;
  display: inline-block;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 14px;
  box-shadow: 0 10px 25px rgba(106, 90, 255, 0.25);
}

.ranking-title h1 {
  font-size: 48px;
  font-weight: 900;
  margin-bottom: 16px;
  color: #000;
  text-transform: uppercase;
  letter-spacing: -0.03em;
  line-height: 1.1;
}

.ranking-title h1 span {
  color: #4361EE;
  font-weight: 900;
}

.ranking-title p {
  font-size: 16px;
  color: #5c5c7c;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.ranking-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.ranking-item {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-radius: 24px;
  padding: 24px 28px;
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 
    0 10px 25px rgba(0, 0, 0, 0.03),
    0 6px 12px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.ranking-position {
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 56px;
  height: 56px;
  background: #4361EE;
  color: white;
  border-radius: 18px;
  font-weight: 800;
  font-size: 24px;
  margin-right: 24px;
  box-shadow: 0 8px 16px rgba(106, 90, 255, 0.2);
  position: relative;
  overflow: hidden;
}

/* 上位3位のカスタムスタイル */
.ranking-item:nth-child(1) .ranking-position {
  background: #FF2D55;
  box-shadow: 0 8px 16px rgba(255, 45, 85, 0.2);
}

.ranking-item:nth-child(2) .ranking-position {
  background: #5E5CE6;
  box-shadow: 0 8px 16px rgba(94, 92, 230, 0.2);
}

.ranking-item:nth-child(3) .ranking-position {
  background: #FF9500;
  box-shadow: 0 8px 16px rgba(255, 108, 0, 0.2);
}

.ranking-icon {
  width: 72px;
  height: 72px;
  min-width: 72px; /* 固定サイズを確保 */
  margin-right: 24px;
  overflow: hidden;
  border-radius: 22px;
  position: relative;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  background-color: #e0e0e0; /* プレースホルダー背景色 */
}

.ranking-icon img {
  width: 72px;
  height: 72px;
  object-fit: cover;
}

.ranking-details {
  flex: 1;
  min-width: 0; /* flexアイテム内での省略を有効にする */
}

.account-name {
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 6px;
  color: #000;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  letter-spacing: -0.01em;
}

.account-id {
  font-size: 15px;
  color: #5c5c7c;
  margin-bottom: 6px;
  font-weight: 500;
  letter-spacing: 0.02em;
  opacity: 0.8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-title-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 16px;
  margin-bottom: 8px;
  gap: 10px;
}

.song-title-badge {
  background: #FF2D55;
  color: white;
  font-size: 13px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 100px;
  display: inline-block;
  box-shadow: 0 6px 15px rgba(255, 45, 85, 0.2);
}

.song-title-text {
  font-size: 20px;
  color: #333;
  font-weight: 700;
  letter-spacing: 0.01em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.ranking-stats {
  display: flex;
  align-items: center;
}

.ranking-value {
  background: rgba(106, 90, 255, 0.08);
  padding: 8px 18px;
  border-radius: 100px;
  display: inline-flex;
  align-items: center;
  position: relative;
  border: 1px solid rgba(106, 90, 255, 0.15);
  box-shadow: 0 4px 8px rgba(106, 90, 255, 0.05);
}

.value-label {
  color: #5c5c7c;
  font-weight: 600;
  font-size: 14px;
}

.value-number {
  font-weight: 800;
  color: #4361EE;
  margin-left: 8px;
  font-size: 20px;
  letter-spacing: -0.02em;
}

/* 上位3位のハイライト */
.ranking-item:nth-child(1) {
  background: rgba(255, 247, 247, 0.85);
  border-left: 3px solid #FF2D55;
}

.ranking-item:nth-child(2) {
  background: rgba(245, 247, 255, 0.85);
  border-left: 3px solid #5E5CE6;
}

.ranking-item:nth-child(3) {
  background: rgba(255, 247, 232, 0.85);
  border-left: 3px solid #FF9500;
}

/* フッター部分 */
.ranking-footer {
  margin-top: 40px;
  text-align: center;
  font-size: 14px;
  color: #8e8e93;
  font-weight: 500;
}
</style>