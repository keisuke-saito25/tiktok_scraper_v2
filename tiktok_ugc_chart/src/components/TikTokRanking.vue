<template>
  <div>
    <v-row>
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
      
      <v-col cols="12" sm="6" md="3">
        <v-select
          v-model="selectedRankingType"
          :items="rankingTypes"
          label="ランキング種類"
          outlined
          dense
        ></v-select>
      </v-col>
      
      <v-col cols="12" sm="6" md="3" class="d-flex align-center">
        <v-btn
          color="primary"
          :disabled="!selectedDate || !selectedRankingType || !excelLoaded"
          @click="generateRanking"
        >
          ランキングを生成
        </v-btn>
        
        <v-btn
          class="ml-2"
          color="success"
          :disabled="!rankingGenerated"
          @click="exportRanking"
        >
          画像保存
        </v-btn>
      </v-col>
    </v-row>
    
    <v-row v-if="rankingGenerated" class="mt-6">
      <v-col cols="12">
        <div ref="rankingContainer" class="ranking-container">
          <div class="ranking-title">
            <div class="title-badge">TikTok Ranking</div>
            <h1>{{ getRankingType() }} <span>TOP 10</span></h1>
            <div class="song-title-container" v-if="currentSongTitle">
              <div class="song-title-badge">曲名</div>
              <div class="song-title-text">{{ currentSongTitle }}</div>
            </div>
            <p>{{ formatDate(selectedDate) }}</p>
          </div>
          
          <div class="ranking-list">
            <div v-for="(item, index) in topTenItems" :key="item.uniqueId" class="ranking-item">
              <div class="ranking-position">
                <span class="position-number">{{ index + 1 }}</span>
              </div>
              
              <div class="ranking-icon">
                <img :src="item.アイコン" :alt="item.アカウント名" referrerpolicy="no-referrer" />
              </div>
              
              <div class="ranking-details">
                <div class="account-name">{{ item.ニックネーム || item.アカウント名 }}</div>
                <div class="account-id">@{{ item.アカウント名 }}</div>

                <div class="ranking-stats">
                  <div class="ranking-value">
                    <span class="value-label">{{ getRankingLabel() }}</span> 
                    <span class="value-number">{{ formatRankingValue(getRankingValue(item)) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="ranking-footer">
            <p>Generated on {{ new Date().toLocaleDateString() }}</p>
          </div>
        </div>
      </v-col>
    </v-row>
    
    <!-- Snackbar for Errors -->
    <v-snackbar v-model="snackbar" :timeout="6000" color="error">
      {{ snackbarMessage }}
      <v-btn color="white" variant="text" @click="snackbar = false">
        閉じる
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import * as XLSX from 'xlsx'
import FileUploadButton from './FileUploadButton.vue'
import { formatDateToYYYYMMDD, formatDateToYYYYMMDDWithSlash } from '../utils/dateUtils'
import type { TikTokPost } from '../types/TikTokPost'
import type { SongInfo } from '../types/SongInfo'
import { extractTikTokPostData, extractSongInfoData } from '../utils/fileHandler'
import html2canvas from 'html2canvas'

// ランキングデータの構造
interface RankingData {
  items: TikTokPost[];
  rankingType: string;
  songTitle?: string;
}

// データと状態
const selectedDate = ref('')
const selectedRankingType = ref('いいね数')
const tikTokPosts = ref<TikTokPost[]>([])
const songInfoData = ref<SongInfo[]>([])
const excelLoaded = ref(false)
const rankingGenerated = ref(false)
const workbook = ref<XLSX.WorkBook | null>(null)
const currentRanking = ref<RankingData | null>(null)
const currentSongTitle = ref<string>('')

// ランキング種類のオプション
const rankingTypes = [
  'いいね数',
  'コメント数',
  'シェア数',
  '保存数',
  '再生回数',
  'フォロワー数'
]

// ランキングコンテナの参照
const rankingContainer = ref<HTMLElement | null>(null)

// Snackbar状態
const snackbar = ref(false)
const snackbarMessage = ref('')

// 上位10件のデータ - 生成されたランキングから取得
const topTenItems = computed(() => {
  return currentRanking.value?.items || []
})

// エラー表示関数
const showError = (message: string) => {
  snackbarMessage.value = message
  snackbar.value = true
}

// ファイル読み込み処理
const handleFile = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      workbook.value = XLSX.read(data, { type: 'array' })
      
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

// ランキング生成処理
const generateRanking = () => {
  if (!workbook.value || !selectedDate.value) {
    showError('Excelファイルと日付を選択してください。')
    return
  }

  const dateStr = formatDateToYYYYMMDD(selectedDate.value)
  
  if (!workbook.value.SheetNames.includes(dateStr)) {
    showError(`シート "${dateStr}" が見つかりません。`)
    return
  }

  try {
    const sheet = workbook.value.Sheets[dateStr]
    const date = new Date(selectedDate.value)
    
    // TikTokポストの抽出
    tikTokPosts.value = extractTikTokPostData(sheet, date)
    
    // 該当日付の楽曲名を取得
    const songTitle = getSongForDate(selectedDate.value)
    
    // ランキング種類によるソート
    const rankingProperty = selectedRankingType.value as keyof TikTokPost
    
    // 重複ユーザーを除外して上位10件を取得
    const uniqueUserPosts = removeDuplicateUsers([...tikTokPosts.value])
    
    const sortedItems = uniqueUserPosts
      .sort((a, b) => {
        const aValue = a[rankingProperty] as number
        const bValue = b[rankingProperty] as number
        return bValue - aValue
      })
      .slice(0, 10)
    
    if (sortedItems.length === 0) {
      showError('ランキングデータが見つかりませんでした。')
      return
    }
    
    // 現在のランキングとして保存（rankingTypeと曲名も一緒に保存）
    currentRanking.value = {
      items: sortedItems,
      rankingType: selectedRankingType.value,
      songTitle: songTitle
    }
    
    // 現在の曲名を設定
    currentSongTitle.value = songTitle
    
    rankingGenerated.value = true
  } catch (error) {
    console.error('ランキング生成中にエラーが発生しました:', error)
    showError('ランキング生成中にエラーが発生しました。')
  }
}

// ランキングのタイトルを取得
const getRankingTitle = () => {
  return `TikTok ${getRankingLabel()} ランキング TOP10`
}

// ランキングタイプを取得する関数（新しいタイトル表示用）
const getRankingType = () => {
  const labels: Record<string, string> = {
    'いいね数': 'LIKES',
    'コメント数': 'COMMENTS',
    'シェア数': 'SHARES',
    '保存数': 'SAVES',
    '再生回数': 'VIEWS',
    'フォロワー数': 'FOLLOWERS'
  }
  
  // 現在表示中のランキング種類の英語表示を使用
  return labels[currentRanking.value?.rankingType || ''] || currentRanking.value?.rankingType || ''
}

// ランキングのラベルを取得
const getRankingLabel = () => {
  const labels: Record<string, string> = {
    'いいね数': 'いいね',
    'コメント数': 'コメント',
    'シェア数': 'シェア',
    '保存数': '保存',
    '再生回数': '再生数',
    'フォロワー数': 'フォロワー'
  }
  
  // 現在表示中のランキング種類を使用
  return labels[currentRanking.value?.rankingType || ''] || currentRanking.value?.rankingType || ''
}

// 日付のフォーマット
const formatDate = (dateStr: string) => {
  return formatDateToYYYYMMDDWithSlash(dateStr)
}

// ランキング値のフォーマット
const formatRankingValue = (value: number) => {
  // 1000単位でカンマ区切り、または万単位で表示
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1)}万`
  }
  return value.toLocaleString()
}

// 現在のランキング種類で値を取得
const getRankingValue = (item: TikTokPost): number => {
  if (!currentRanking.value) return 0;
  return item[currentRanking.value.rankingType as keyof TikTokPost] as number;
}

// 重複ユーザーを除外する関数（アカウント名をキーとして最初の投稿のみ残す）
const removeDuplicateUsers = (posts: TikTokPost[]): TikTokPost[] => {
  const uniqueUsers = new Map<string, TikTokPost>()
  
  posts.forEach(post => {
    // アカウント名がまだMapに存在しない場合のみ追加
    if (!uniqueUsers.has(post.アカウント名)) {
      uniqueUsers.set(post.アカウント名, post)
    }
  })
  
  return Array.from(uniqueUsers.values())
}

// ランキング画像のエクスポート処理を修正
const exportRanking = async () => {
  if (!rankingContainer.value || !currentRanking.value) {
    showError('ランキングコンテナが見つかりません。')
    return
  }
  
  try {
    // html2canvasのオプションを詳細に設定
    const canvas = await html2canvas(rankingContainer.value, {
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      scale: 2, // 高解像度化
      logging: false,
      removeContainer: false,
      foreignObjectRendering: false, // 外部オブジェクトレンダリングを無効化
      onclone: (clonedDoc) => {
        // クローンされたDOMでスタイルを上書き - より確実にレンダリングするため
        const clonedContainer = clonedDoc.querySelector('.ranking-container')
        if (clonedContainer && clonedContainer instanceof HTMLElement) {
          clonedContainer.style.boxShadow = 'none' // 影を削除
        }
        
        // グラデーションなどの問題のある要素を修正
        const valueNumbers = clonedDoc.querySelectorAll('.value-number')
        valueNumbers.forEach(el => {
          if (el instanceof HTMLElement) {
            el.style.color = '#4361EE'
            el.style.background = 'none'
          }
        })
        
        // タイトルのスパン要素も修正
        const titleSpans = clonedDoc.querySelectorAll('.ranking-title h1 span')
        titleSpans.forEach(el => {
          if (el instanceof HTMLElement) {
            el.style.color = '#4361EE'
            el.style.background = 'none'
          }
        })
      }
    })
    
    // 画像としてダウンロード
    const link = document.createElement('a')
    link.download = `ranking_${currentRanking.value.rankingType}_${formatDateToYYYYMMDD(selectedDate.value)}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (error) {
    console.error('ランキング画像のエクスポート中にエラーが発生しました:', error)
    showError('ランキング画像のエクスポート中にエラーが発生しました。')
  }
}
</script>

<style scoped>
.ranking-container {
  background-color: #f5f7fc;
  color: #111;
  border-radius: 32px;
  padding: 50px;
  max-width: 1200px;
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
  background: linear-gradient(90deg, #00C2FF, #6A5AFF);
  color: white;
  font-size: 14px;
  font-weight: 800;
  padding: 9px 20px;
  border-radius: 100px;
  display: inline-block;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 14px;
  box-shadow: 
    0 10px 25px rgba(106, 90, 255, 0.25),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1),
    inset 0 2px 0 rgba(255, 255, 255, 0.2);
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
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  /* 要素間の距離を広げる */
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
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 
    0 10px 25px rgba(0, 0, 0, 0.03),
    0 6px 12px rgba(0, 0, 0, 0.05),
    inset 0 -1px 1px rgba(255, 255, 255, 0.4);
}

.ranking-position {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #6A5AFF, #00C2FF);
  color: white;
  border-radius: 18px;
  font-weight: 800;
  font-size: 24px;
  margin-right: 24px;
  box-shadow: 
    0 8px 16px rgba(106, 90, 255, 0.2),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1),
    inset 0 2px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.ranking-position::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 50%;
  background: rgba(255, 255, 255, 0.15);
  border-bottom-right-radius: 50%;
  border-bottom-left-radius: 50%;
}

/* 上位3位のカスタムスタイル */
.ranking-item:nth-child(1) .ranking-position {
  background: linear-gradient(135deg, #FF9500, #FF2D55);
  box-shadow: 0 8px 16px rgba(255, 45, 85, 0.2);
}

.ranking-item:nth-child(2) .ranking-position {
  background: linear-gradient(135deg, #747EF2, #5E5CE6);
  box-shadow: 0 8px 16px rgba(94, 92, 230, 0.2);
}

.ranking-item:nth-child(3) .ranking-position {
  background: linear-gradient(135deg, #FF9500, #FF6C00);
  box-shadow: 0 8px 16px rgba(255, 108, 0, 0.2);
}

.ranking-icon {
  width: 72px;
  height: 72px;
  margin-right: 24px;
  overflow: hidden;
  border-radius: 22px;
  position: relative;
  box-shadow: 
    0 8px 20px rgba(0, 0, 0, 0.1),
    inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

.ranking-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    45deg,
    rgba(106, 90, 255, 0.2),
    rgba(0, 194, 255, 0.1)
  );
  z-index: 1;
}

.ranking-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: relative;
  z-index: 0;
}

.ranking-details {
  flex: 1;
}

.account-name {
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 6px;
  color: #000;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.01em;
}

.account-id {
  font-size: 15px;
  color: #5c5c7c;
  margin-bottom: 6px;
  font-weight: 500;
  letter-spacing: 0.02em;
  opacity: 0.8;
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
  background: linear-gradient(90deg, #FF9500, #FF2D55);
  color: white;
  font-size: 13px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 100px;
  display: inline-block;
  box-shadow: 
    0 6px 15px rgba(255, 45, 85, 0.2),
    inset 0 -1px 0 rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.song-title-text {
  font-size: 20px;
  color: #333;
  font-weight: 700;
  letter-spacing: 0.01em;
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
  backdrop-filter: blur(10px);
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

/* 上位3位のアイコン装飾 */
.ranking-item:nth-child(1) .ranking-icon::before {
  background: linear-gradient(45deg, rgba(255, 45, 85, 0.15), rgba(255, 149, 0, 0.1));
}

.ranking-item:nth-child(2) .ranking-icon::before {
  background: linear-gradient(45deg, rgba(94, 92, 230, 0.15), rgba(0, 194, 255, 0.1));
}

.ranking-item:nth-child(3) .ranking-icon::before {
  background: linear-gradient(45deg, rgba(255, 149, 0, 0.15), rgba(255, 204, 0, 0.1));
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