# tiktok_ugc_chart - Vue.js TikTokデータ可視化ダッシュボード

![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)
![Vuetify](https://img.shields.io/badge/Vuetify-3.x-1867C0.svg)
![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384.svg)

Vue 3 + TypeScriptで構築された高性能TikTokデータ可視化ダッシュボードです。Material DesignベースのモダンなUIと、Chart.jsによるインタラクティブな分析機能を提供します。

## 🎯 主要機能

### 📊 データ可視化
- **インタラクティブチャート**: Chart.js powered 動的グラフ
- **リアルタイム更新**: ライブデータフィードのサポート
- **カスタマイズ可能な表示**: 多様なチャートタイプ（棒グラフ、線グラフ、円グラフ）
- **ドリルダウン分析**: 詳細レベルまでのデータ探索

### 🎨 ユーザーインターフェース
- **Material Design 3**: Vuetifyによる最新UIコンポーネント
- **レスポンシブデザイン**: PC、タブレット、スマートフォン対応
- **ダークモード**: ライト/ダークテーマの切り替え
- **アクセシビリティ**: WCAG準拠のアクセシブルなUI

### 📋 データ管理機能
- **Excelインポート**: .xlsx/.csv ファイルの読み込み
- **データ変換**: 柔軟なデータ形式変換
- **フィルタリング**: 日付範囲、カテゴリ、キーワード検索
- **エクスポート**: CSV、Excel、PDFでの結果出力

### ⚡ パフォーマンス機能
- **仮想スクローリング**: 大量データの効率的表示
- **レイジーローディング**: コンポーネントの必要時読み込み
- **キャッシュシステム**: データとコンポーネントの高速化
- **PWA対応**: オフライン使用可能な Progressive Web App

## 🏗️ アーキテクチャ概要

```
┌─────────────────────────────────────┐
│         tiktok_ugc_chart            │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Vue 3 App   │  │ TypeScript  │   │
│  │             │  │   Types     │   │
│  │ • Components│  │ • Interfaces│   │
│  │ • Routing   │  │ • Validation│   │
│  │ • State     │  │ • Type Safe │   │
│  └─────────────┘  └─────────────┘   │
│           │               │         │
│  ┌─────────────────────────────────┐ │
│  │         Vuetify 3               │ │
│  │                                │ │
│  │ • Material Design Components   │ │
│  │ • Theme System                 │ │
│  │ • Grid & Layout                │ │
│  └─────────────────────────────────┘ │
│           │                         │
│  ┌─────────────────────────────────┐ │
│  │         Chart.js                │ │
│  │                                │ │
│  │ • Interactive Charts           │ │
│  │ • Real-time Updates            │ │
│  │ • Multiple Chart Types         │ │
│  │ • Export Functionality         │ │
│  └─────────────────────────────────┘ │
│           │                         │
│  ┌─────────────────────────────────┐ │
│  │       Vite Build System         │ │
│  │                                │ │
│  │ • Hot Module Replacement       │ │
│  │ • TypeScript Integration       │ │
│  │ • Production Optimization      │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 📁 プロジェクト構造

```
tiktok_ugc_chart/
├── public/                    # 静的アセット
│   └── images/
│       └── favicon.ico        # アプリケーションアイコン
├── src/
│   ├── App.vue               # メインアプリケーションコンポーネント
│   ├── main.ts               # アプリケーションエントリーポイント
│   ├── components/           # Vueコンポーネント
│   │   ├── AccountsTable.vue      # アカウント情報テーブル
│   │   ├── DateRangeFilter.vue    # 日付範囲フィルター
│   │   ├── DraggableIcon.vue      # ドラッグ可能アイコン
│   │   ├── FileUploadButton.vue   # ファイルアップロードボタン
│   │   ├── TikTokRanking.vue      # TikTokランキング表示
│   │   └── UGCChart.vue           # UGCデータチャート
│   ├── types/                # TypeScript型定義
│   │   ├── SongInfo.ts            # 楽曲情報型
│   │   └── TikTokPost.ts          # TikTok投稿型
│   ├── utils/                # ユーティリティ関数
│   │   ├── dateUtils.ts           # 日付操作関数
│   │   ├── fileHandler.ts         # ファイル処理関数
│   │   └── generateUniqueId.ts    # ユニークID生成
│   └── assets/               # スタイルとアセット
│       ├── base.css               # ベーススタイル
│       ├── logo.svg               # アプリケーションロゴ
│       └── main.css               # メインスタイル
├── package.json              # Node.js 依存関係とスクリプト
├── package-lock.json         # 依存関係ロックファイル
├── vite.config.ts           # Vite 設定
├── tsconfig.json            # TypeScript 設定
├── tsconfig.app.json        # アプリケーション用TS設定
├── tsconfig.node.json       # Node.js用TS設定
├── eslint.config.ts         # ESLint設定
├── env.d.ts                 # 環境変数型定義
├── index.html               # HTML テンプレート
├── start.bat                # Windows 実行用バッチファイル
├── start.sh                 # Linux/Mac 実行用シェルスクリプト
└── README.md                # このファイル
```

### コンポーネント詳細

#### 📊 チャート・可視化コンポーネント
- **`UGCChart.vue`**: メインのUGCデータチャートコンポーネント
- **`TikTokRanking.vue`**: TikTokコンテンツランキング表示
- **`AccountsTable.vue`**: アカウント情報の表形式表示

#### 🔧 ユーティリティコンポーネント
- **`FileUploadButton.vue`**: ドラッグ&ドロップ対応ファイルアップロード
- **`DateRangeFilter.vue`**: 日付範囲選択フィルター
- **`DraggableIcon.vue`**: ドラッグ可能なUI要素

#### 🎯 型定義
- **`SongInfo.ts`**: 楽曲情報のTypeScript interface
- **`TikTokPost.ts`**: TikTok投稿データの型定義

## ⚙️ システム要件

### 🔧 必須環境
- **Node.js**: 16.x以上 (推奨: 18.x LTS)
- **npm**: 8.x以上 (または yarn 3.x以上)
- **ブラウザ**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)

### 📦 主要依存関係

#### コア技術スタック
```json
{
  "vue": "^3.4.0",
  "typescript": "^5.3.0",
  "vuetify": "^3.5.0",
  "chart.js": "^4.4.0",
  "vue-chartjs": "^5.3.0"
}
```

#### 開発・ビルドツール
```json
{
  "vite": "^5.0.0",
  "@vitejs/plugin-vue": "^5.0.0",
  "@vue/tsconfig": "^0.5.0",
  "eslint": "^8.0.0",
  "prettier": "^3.0.0"
}
```

## 🚀 インストール・セットアップ

### 1️⃣ プロジェクトの準備
```bash
# リポジトリクローン
git clone <リポジトリのURL>
cd tiktok_scraper/tiktok_ugc_chart
```

### 2️⃣ 依存関係のインストール
```bash
# npm を使用する場合
npm install

# yarn を使用する場合
yarn install
```

### 3️⃣ 開発環境の起動
```bash
# 開発サーバー起動
npm run dev

# または
yarn dev
```

開発サーバーが起動したら、ブラウザで `http://localhost:5173` にアクセスしてください。

### 4️⃣ 環境設定（オプション）
プロジェクトルートに `.env.local` ファイルを作成して環境変数を設定：

```bash
# .env.local
VITE_API_BASE_URL=http://localhost:3000
VITE_APP_TITLE=TikTok UGC Chart
VITE_DEBUG_MODE=true
```

## 🎮 使用方法

### 基本的な操作フロー

#### 1. アプリケーション起動
```bash
npm run dev
# ブラウザで http://localhost:5173 を開く
```

#### 2. データファイルのアップロード
1. **ファイルアップロードエリア**をクリックまたはドラッグ&ドロップ
2. **Excel (.xlsx) または CSV ファイル**を選択
3. データの**自動パース・バリデーション**を確認

#### 3. データ可視化・分析
1. **チャートタイプ選択**: 棒グラフ、線グラフ、円グラフから選択
2. **フィルター適用**: 日付範囲、カテゴリ、キーワードで絞り込み
3. **インタラクティブ操作**: ホバー、クリック、ズームで詳細確認

#### 4. 結果エクスポート
1. **エクスポート形式選択**: CSV、Excel、PDFから選択
2. **データ範囲指定**: 表示中または全データから選択
3. **ファイルダウンロード**: 処理結果をローカルに保存

### 📊 サポートするデータ形式

#### Excel形式 (.xlsx)
```
| date       | account_name | song_title    | ugc_count | engagement |
|------------|--------------|---------------|-----------|------------|
| 2024-01-01 | user123      | Sample Song   | 1500      | 3.2        |
| 2024-01-02 | user456      | Another Song  | 2300      | 4.1        |
```

#### CSV形式 (.csv)
```csv
date,account_name,song_title,ugc_count,engagement
2024-01-01,user123,Sample Song,1500,3.2
2024-01-02,user456,Another Song,2300,4.1
```

### 🎛️ カスタマイズ設定

#### チャート表示設定
- **チャートタイプ**: 棒グラフ、線グラフ、円グラフ、散布図
- **色テーマ**: プライマリ、セカンダリ、カスタムカラーパレット
- **アニメーション**: 表示アニメーションのオン/オフ
- **データポイント表示**: 値の表示/非表示

#### UI・UX設定
- **テーマ**: ライトテーマ / ダークテーマ
- **言語**: 日本語 / English（将来実装予定）
- **表示密度**: コンパクト / 標準 / 快適
- **アニメーション**: 減らされた動き / 標準

## 🔧 開発・カスタマイズ

### 🛠️ 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# 型チェック
npm run type-check

# ESLint によるコードチェック
npm run lint

# 本番ビルド
npm run build

# ビルドプレビュー
npm run preview
```

### 🎨 スタイルカスタマイズ

#### Vuetify テーマ設定
```typescript
// src/plugins/vuetify.ts
import { createVuetify } from 'vuetify'

export default createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
        },
      },
      dark: {
        colors: {
          primary: '#2196F3',
          secondary: '#616161',
          accent: '#FF4081',
        },
      },
    },
  },
})
```

#### CSS変数によるカスタマイズ
```css
/* src/assets/main.css */
:root {
  --chart-primary-color: #1976d2;
  --chart-secondary-color: #424242;
  --background-color: #fafafa;
  --text-color: #212121;
}

[data-theme="dark"] {
  --background-color: #121212;
  --text-color: #ffffff;
}
```

### 📊 新しいチャートタイプの追加

#### カスタムChart.jsプラグイン作成
```typescript
// src/plugins/chartPlugins.ts
import { Plugin } from 'chart.js'

export const customTooltipPlugin: Plugin = {
  id: 'customTooltip',
  afterTooltipDraw(chart, args, options) {
    // カスタムツールチップロジック
  }
}
```

#### Vueコンポーネントでの使用
```vue
<!-- src/components/CustomChart.vue -->
<template>
  <Bar
    :data="chartData"
    :options="chartOptions"
    :plugins="[customTooltipPlugin]"
  />
</template>

<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { customTooltipPlugin } from '@/plugins/chartPlugins'
</script>
```

## 🏗️ ビルド・デプロイ

### 📦 本番ビルド

```bash
# 本番用ビルド実行
npm run build

# ビルド結果の確認
npm run preview
```

### 🌐 デプロイメント

#### 静的ホスティング（Netlify、Vercel）
```bash
# ビルドコマンド
npm run build

# 出力ディレクトリ
dist/
```

#### Docker コンテナ化
```dockerfile
# Dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### GitHub Pages
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

## 📊 パフォーマンス最適化

### ⚡ ビルド最適化

#### Vite 設定の最適化
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import { splitVendorChunkPlugin } from 'vite'

export default defineConfig({
  plugins: [splitVendorChunkPlugin()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router'],
          'ui-vendor': ['vuetify'],
          'chart-vendor': ['chart.js', 'vue-chartjs'],
        },
      },
    },
  },
})
```

### 🧠 ランタイム最適化

#### コンポーネント遅延読み込み
```typescript
// src/router/index.ts
import { defineAsyncComponent } from 'vue'

const routes = [
  {
    path: '/dashboard',
    component: defineAsyncComponent(() => import('@/views/Dashboard.vue'))
  },
]
```

#### 大量データの仮想化
```vue
<!-- 大きなリスト用仮想スクロール -->
<template>
  <VirtualList
    :items="largeDateSet"
    :item-height="50"
    :container-height="400"
    v-slot="{ item, index }"
  >
    <div class="list-item">
      {{ item.name }}
    </div>
  </VirtualList>
</template>
```

## 🛡️ セキュリティ・品質保証

### 🔒 セキュリティ対策

#### CSP (Content Security Policy) 設定
```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  style-src 'self' 'unsafe-inline';
  script-src 'self';
  img-src 'self' data: https:;
">
```

#### 入力データの検証
```typescript
// src/utils/dataValidation.ts
export function validateExcelData(data: any[]): boolean {
  return data.every(row => {
    return (
      typeof row.date === 'string' &&
      typeof row.ugc_count === 'number' &&
      row.ugc_count >= 0
    )
  })
}
```

### 🧪 品質管理

#### ESLint 設定
```typescript
// eslint.config.ts
export default [
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': 'error',
      'vue/no-mutating-props': 'error',
      'vue/require-default-prop': 'warn',
    },
  },
]
```

#### TypeScript 厳密設定
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. 依存関係インストールエラー
**症状**: `npm install` でエラーが発生
```bash
# 解決方法
# 1. Node.js バージョンを確認
node --version  # 16.x以上であることを確認

# 2. npm キャッシュクリア
npm cache clean --force

# 3. node_modules 削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

#### 2. TypeScript型エラー
**症状**: 型チェックでエラーが発生
```bash
# 解決方法
# 1. 型チェック実行
npm run type-check

# 2. VSCode のTypeScript再起動
# Command Palette > "TypeScript: Restart TS Server"

# 3. 型定義の更新
npm install --save-dev @types/node
```

#### 3. Chart.js レンダリング問題
**症状**: チャートが正しく表示されない
```typescript
// 解決方法
// 1. Chart.js 登録の確認
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)
```

#### 4. Vuetify コンポーネントエラー
**症状**: Vuetifyコンポーネントが表示されない
```typescript
// src/main.ts
import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
})

app.use(vuetify)
```

#### 5. ビルドエラー
**症状**: `npm run build` でビルドが失敗
```bash
# 解決方法
# 1. TypeScript エラーの修正
npm run type-check

# 2. ESLint エラーの修正
npm run lint

# 3. メモリ不足の場合
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

### 🔧 デバッグツール

#### Vue DevTools の活用
```bash
# Vue DevToolsブラウザ拡張機能をインストール
# Chrome: https://chrome.google.com/webstore/detail/vuejs-devtools/
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/
```

#### パフォーマンス分析
```bash
# バンドルサイズ分析
npm run build -- --analyze

# パフォーマンス測定
npm run build && npm run preview
# ブラウザ Developer Tools > Lighthouse でパフォーマンス測定
```

## 📈 将来の機能拡張

### 🔮 計画中の機能

#### 高度な分析機能
- **機械学習統合**: データトレンド予測
- **AIアシスタント**: 自動インサイト生成
- **異常検知**: データの異常値自動検出
- **パフォーマンス予測**: 楽曲人気度予測モデル

#### エンタープライズ機能
- **マルチテナント**: 組織・ユーザー管理
- **API統合**: REST/GraphQL APIサポート
- **データベース連携**: PostgreSQL、MongoDB接続
- **リアルタイム同期**: WebSocket によるライブデータ

#### ユーザビリティ向上
- **多言語対応**: 国際化 (i18n) サポート
- **アクセシビリティ**: WCAG 2.1 AA準拠
- **PWA機能**: オフライン対応・プッシュ通知
- **モバイルアプリ**: Capacitor によるネイティブアプリ

### 🤝 コントリビューション

プロジェクトへの貢献方法：

1. **Issue報告**: バグ報告・機能要望の投稿
2. **Pull Request**: コード改善・新機能の提案
3. **ドキュメント貢献**: README・コメント改善
4. **テスト追加**: ユニットテスト・E2Eテストの充実
5. **UI/UXデザイン**: デザイン改善・アイコン作成

### 📄 ライセンス・クレジット

このプロジェクトは適切なライセンスの下で提供されています。

#### 使用ライブラリのクレジット
- **Vue.js**: MIT License
- **TypeScript**: Apache License 2.0
- **Vuetify**: MIT License
- **Chart.js**: MIT License
- **Vite**: MIT License

---

**📊 データ可視化の世界へようこそ！**

TikTok UGC Chartで、あなたのデータ分析を次のレベルに引き上げましょう。質問やサポートが必要な場合は、お気軽にお問い合わせください。