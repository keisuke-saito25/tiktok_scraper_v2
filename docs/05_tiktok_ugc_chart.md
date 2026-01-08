# tiktok_ugc_chart 詳細ドキュメント

## 概要

`tiktok_ugc_chart`は、TikTokデータを可視化・分析するためのWebダッシュボードです。Vue 3とVuetifyを使用したモダンなUIで、UGCチャートの表示やランキング生成が可能です。

## ファイル構成

```
tiktok_ugc_chart/
├── src/
│   ├── App.vue              # メインアプリケーション
│   ├── main.ts              # エントリポイント
│   ├── components/
│   │   ├── UGCChart.vue         # UGCチャート表示
│   │   ├── TikTokRanking.vue    # ランキング表示
│   │   ├── AccountsTable.vue    # アカウント一覧
│   │   ├── DateRangeFilter.vue  # 日付フィルタ
│   │   ├── DraggableIcon.vue    # ドラッグ可能アイコン
│   │   └── FileUploadButton.vue # ファイル読込ボタン
│   ├── types/
│   │   ├── TikTokPost.ts    # 投稿データ型定義
│   │   └── SongInfo.ts      # 楽曲情報型定義
│   ├── utils/
│   │   ├── fileHandler.ts   # Excelデータ抽出
│   │   ├── dateUtils.ts     # 日付処理
│   │   └── iconUtils.ts     # アイコン処理
│   └── assets/
│       └── styles/          # スタイルシート
├── public/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── start.bat                # Windows起動スクリプト
└── start.sh                 # Linux/Mac起動スクリプト
```

## 主要機能

### 1. UGCチャート

楽曲のUGC推移をChart.jsで可視化します。

**機能**:
- 日付範囲でのフィルタリング
- 複数楽曲の比較表示
- トップフォロワーアカウントのアイコン表示
- ドラッグ可能なアイコン配置
- 画像エクスポート

### 2. ランキング

指定条件でアカウントをランキング表示します。

**ランキングタイプ**:
- 再生数ランキング
- いいね数ランキング
- コメント数ランキング
- フォロワー数ランキング

**機能**:
- 複数タイプの同時生成
- 楽曲ごとのランキング
- 画像エクスポート（html2canvas使用）

### 3. アカウント管理

チャートに表示するアカウントを管理します。

**機能**:
- 表示/非表示の切替
- オレンジ枠（特別マーク）の切替
- フォロワー数表示の切替

## コンポーネント詳細

### App.vue

メインアプリケーションコンポーネント。

```typescript
// 主要な状態
const activeTab = ref('ugc-chart')        // アクティブタブ
const filterFrom = ref('')                 // 日付フィルタ（開始）
const filterTo = ref('')                   // 日付フィルタ（終了）
const tikTokPostData = ref<TikTokPost[]>([])      // 投稿データ
const songInfoData = ref<SongInfo[]>([])          // 楽曲情報
const filteredSongInfoData = ref<SongInfo[]>([])  // フィルタ済み楽曲情報
```

**主要メソッド**:
- `handleFile(file)`: Excelファイル読み込み
- `processTikTokData(workbook)`: データ抽出・変換
- `applyFilters()`: 日付フィルタ適用
- `handleExportChartAndIcons()`: 画像エクスポート

### UGCChart.vue

UGC推移チャートを表示するコンポーネント。

```typescript
// Props
interface Props {
  data: SongInfo[]           // チャートデータ
  topFollowerPosts: TikTokPost[]  // トップフォロワー投稿
}

// 公開メソッド
defineExpose({
  exportChartAsImage,         // チャートのみエクスポート
  exportIconsAsImage,         // アイコンのみエクスポート
  exportChartAndIconsAsImage  // 両方エクスポート
})
```

**チャート設定**:
- Chart.js LineControllerを使用
- CategoryScale（X軸：日付）
- LinearScale（Y軸：UGC数）
- 複数データセット対応

### TikTokRanking.vue

アカウントランキングを生成・表示するコンポーネント。

```typescript
// ランキングデータ構造
interface RankingData {
  rankingType: string        // ランキングタイプ
  songTitle: string          // 楽曲名
  items: TikTokPost[]        // ランキング対象
}

// 選択可能なランキングタイプ
const availableRankingTypes = [
  '再生数',
  'いいね数',
  'コメント数',
  'フォロワー数'
]
```

**主要メソッド**:
- `generateRankings()`: ランキング生成
- `exportAllRankingsAsImages()`: 全ランキング画像出力

### DateRangeFilter.vue

日付範囲を選択するフィルタコンポーネント。

```typescript
// イベント
emit('update:filters', {
  from: string,       // 開始日
  to: string,         // 終了日
  from2: string,      // 比較用開始日
  to2: string,        // 比較用終了日
  isValid: boolean    // 有効フラグ
})
```

### DraggableIcon.vue

チャート上でドラッグ可能なアイコンコンポーネント。

**機能**:
- マウスドラッグによる位置変更
- 位置の永続化
- フォロワー数バッジ表示
- オレンジ枠表示

## 型定義

### TikTokPost.ts

```typescript
export interface TikTokPost {
  動画URL: string
  投稿日: string
  再生数: number
  いいね数: number
  コメント数: number
  アカウント名: string
  フォロワー数: number
  アイコンURL: string
  
  // UI用追加フィールド
  visible?: boolean          // 表示フラグ
  hasOrangeBorder?: boolean  // オレンジ枠フラグ
  showFollowers?: boolean    // フォロワー表示フラグ
  uniqueId?: string          // 一意識別子
}
```

### SongInfo.ts

```typescript
export interface SongInfo {
  曲名: string
  日付: string
  UGC数: number
}
```

## ユーティリティ

### fileHandler.ts

```typescript
// Excelからデータを抽出
export function extractTikTokPostData(
  workbook: XLSX.WorkBook,
  sheetName: string
): TikTokPost[]

export function extractSongInfoData(
  workbook: XLSX.WorkBook
): SongInfo[]

export function extractUserIconMap(
  workbook: XLSX.WorkBook
): Map<string, string>
```

### dateUtils.ts

```typescript
// 日付フォーマット変換
export function formatDateToYYYYMMDD(date: string): string
export function formatDateToYYYYMMDDWithSlash(date: string): string
```

## 技術スタック

### フレームワーク

| 名前 | バージョン | 用途 |
|------|-----------|------|
| Vue | ^3.5.13 | UIフレームワーク |
| Vuetify | ^3.7.12 | UIコンポーネント |
| TypeScript | ~5.7.3 | 型付きJavaScript |
| Vite | ^6.1.0 | ビルドツール |

### ライブラリ

| 名前 | バージョン | 用途 |
|------|-----------|------|
| chart.js | ^4.4.8 | チャート描画 |
| vue-chartjs | ^5.3.2 | Vue用Chart.jsラッパー |
| xlsx | ^0.18.5 | Excel読み書き |
| html2canvas | ^1.4.1 | HTML→画像変換 |
| @mdi/font | ^7.4.47 | アイコンフォント |

## 開発コマンド

```bash
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# 型チェック
npm run type-check

# Lint
npm run lint

# フォーマット
npm run format
```

## 設定ファイル

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

### tsconfig.json

```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.node.json" },
    { "path": "./tsconfig.app.json" }
  ]
}
```

## 使用方法

### Excelファイルの読み込み

1. 「Excelを読み込む」ボタンをクリック
2. TikTok_UGC.xlsx または同等のExcelファイルを選択
3. データが自動的に解析され表示

### UGCチャート表示

1. 日付範囲を設定（From/To）
2. Excelファイルを読み込み
3. チャートが自動描画
4. 必要に応じてアイコンをドラッグ配置
5. 「全体を保存」で画像エクスポート

### ランキング生成

1. 「ランキング」タブを選択
2. Excelファイルを読み込み
3. 日付を選択
4. ランキングタイプを選択（複数可）
5. 「ランキング生成」ボタンをクリック
6. 「画像保存」で個別エクスポート
