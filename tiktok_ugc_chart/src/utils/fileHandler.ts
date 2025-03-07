import * as XLSX from 'xlsx'
import type { SongInfo } from '../types/SongInfo'
import type { TikTokPost } from '../types/TikTokPost'
import { formatDateToYYYYMMDD, parsePostDate } from './dateUtils'
import { generateUniqueId } from './generateUniqueId'

/**
 * 行が完全に空かどうかを確認
 * @param row 検証する行データ
 * @returns 行が空の場合はtrue
 */
export const isRowEmpty = (row: any[]): boolean => {
  return row.every(cell => cell == null || cell === '')
}

/**
 * メインシート（楽曲情報）からデータを抽出
 * @param worksheet ワークシート
 * @returns 抽出した楽曲情報の配列
 */
export const extractSongInfoData = (worksheet: XLSX.WorkSheet): SongInfo[] => {
  const rawData: any[][] = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' })
  
  if (rawData.length <= 1) {
    return []
  }
  
  const headers: string[] = rawData[0] as string[]
  
  // データの整形
  const songInfoData: SongInfo[] = rawData.slice(1)
    .filter(row => !isRowEmpty(row)) // 空の行を除外
    .map(row => {
      const rowData: Record<string, any> = {}
      
      headers.forEach((header, index) => {
        const key = header.trim() !== '' ? header : undefined
        if (key) rowData[key] = row[index]
      })
      
      return rowData as SongInfo
    })
  
  // 日付が存在し、有効なデータのみをフィルタリング
  return songInfoData.filter(item => 
    item.日付 && !isNaN(new Date(item.日付 as string).getTime())
  )
}

/**
 * ユーザーアイコンシートからアイコンパスのマップを作成
 * @param worksheet ユーザーアイコンシート
 * @returns アカウント名をキー、アイコンパスを値とするマップ
 */
export const extractUserIconMap = (worksheet: XLSX.WorkSheet): Map<string, string> => {
  console.log('extractUserIconMap: ユーザーアイコンマップの抽出を開始します。');
  const rawData: any[][] = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' })
  
  console.log(`extractUserIconMap: 読み込んだデータ行数: ${rawData.length}`);
  
  if (rawData.length <= 1) {
    console.warn('extractUserIconMap: ユーザーアイコンシートにデータがありません。');
    return new Map()
  }
  
  const headers: string[] = rawData[0] as string[]
  console.log('extractUserIconMap: ヘッダー行:', headers);
  
  const accountNameIndex = headers.findIndex(h => h === 'アカウント名')
  const iconPathIndex = headers.findIndex(h => h === 'アイコンパス')
  
  console.log(`extractUserIconMap: アカウント名の列インデックス: ${accountNameIndex}, アイコンパスの列インデックス: ${iconPathIndex}`);
  
  if (accountNameIndex === -1 || iconPathIndex === -1) {
    console.error('extractUserIconMap: 必要なヘッダーが見つかりません。ヘッダー行を確認してください。');
    throw new Error('ユーザーアイコンシートに必要なヘッダー（アカウント名、アイコンパス）が見つかりません。')
  }
  
  const iconMap = new Map<string, string>()
  
  rawData.slice(1)
    .filter(row => !isRowEmpty(row) && row[accountNameIndex] && row[iconPathIndex])
    .forEach((row, index) => {
      const accountName = row[accountNameIndex].toString().trim()
      const iconPath = row[iconPathIndex].toString().trim()
      if (accountName && iconPath) {
        iconMap.set(accountName, iconPath)
        if (index < 5) { // 最初の5行だけログに表示
          console.log(`extractUserIconMap: マッピング追加 - ${accountName} => ${iconPath}`);
        }
      }
    })
  
  console.log(`extractUserIconMap: 合計${iconMap.size}件のアイコンマッピングを作成しました。`);
  return iconMap
}

/**
 * 指定された日付のシートからTikTokポストデータを抽出し、ユーザーアイコンマップを適用
 * @param worksheet 日付シート
 * @param toDate 日付
 * @param userIconMap ユーザーアイコンマップ（省略可能）
 * @returns 抽出したTikTokポストの配列
 */
export const extractTikTokPostData = (
  worksheet: XLSX.WorkSheet, 
  toDate: Date,
  userIconMap?: Map<string, string>
): TikTokPost[] => {
  const toSheetData: any[][] = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' })
  
  // ヘッダーを取得
  const toHeaders: string[] = toSheetData[0] as string[]
  
  // 投稿IDとアカウント名のインデックスを取得
  const postIdIndex = toHeaders.indexOf('投稿ID')
  const accountNameIndex = toHeaders.indexOf('アカウント名')
  
  if (postIdIndex === -1) {
    throw new Error('投稿ID列が見つかりません。')
  }
  
  if (accountNameIndex === -1) {
    throw new Error('アカウント名列が見つかりません。')
  }
  
  const toYear = toDate.getFullYear()
  
  // データ部分をフィルタリング
  const posts: TikTokPost[] = [];
  
  toSheetData.slice(1)
    .filter(row => row[postIdIndex] && row[postIdIndex].toString().trim() !== '')
    .forEach(row => {
      const rowData: Record<string, any> = {}
      
      toHeaders.forEach((header, index) => {
        const key = header.trim() !== '' ? header : undefined
        if (key) rowData[key] = row[index]
      })
      
      // 投稿日のパースを追加
      if (rowData['投稿日']) {
        rowData['投稿日'] = parsePostDate(rowData['投稿日'], toYear)
      }
      
      // アカウント名からアイコンパスを取得
      const accountName = rowData['アカウント名']
      if (userIconMap && accountName) {
        if (userIconMap.has(accountName)) {
          const iconPath = userIconMap.get(accountName);
          rowData['アイコン'] = iconPath;
          // 最初の数件だけログに表示
          if (posts.length < 3) {
            console.log(`アイコンパスを設定しました: ${accountName} => ${iconPath}`);
          }
        } else {
          // 最初の数件だけログに表示
          if (posts.length < 3) {
            console.log(`警告: アカウント "${accountName}" のアイコンパスが見つかりません。`);
          }
        }
      }
      
      const post = {
        ...rowData,
        uniqueId: generateUniqueId(),
        isVisible: false, // 初期状態は非表示
        isOrangeBorder: false,
        isShowFollowers: true, 
      } as TikTokPost;
      
      posts.push(post);
    })
  
  return posts
}

/**
 * 日付範囲でTikTokポストをフィルタリング
 * @param posts TikTokポストの配列
 * @param fromDate 開始日
 * @param toDate 終了日
 * @returns フィルタリングされたTikTokポストの配列
 */
export const filterPostsByDateRange = (
  posts: TikTokPost[],
  fromDate: Date,
  toDate: Date
): TikTokPost[] => {
  return posts.filter(post => {
    if (!post.投稿日) return false
    const postDate = new Date(post.投稿日)
    return postDate >= fromDate && postDate <= toDate
  })
}

/**
 * アカウント名ごとに最も古い投稿を取得
 * @param posts TikTokポストの配列
 * @returns ユニークなアカウントのマップ
 */
export const getUniqueAccountsMap = (posts: TikTokPost[]): Map<string, TikTokPost> => {
  const uniqueAccountsMap = new Map<string, TikTokPost>()
  
  posts.forEach(post => {
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
  
  return uniqueAccountsMap
}

/**
 * フォロワー数でソートして上位N件を取得
 * @param posts TikTokポストの配列
 * @param limit 上限数
 * @returns フォロワー数順にソートした上位N件のTikTokポスト
 */
export const getTopFollowerPosts = (posts: TikTokPost[], limit: number = 30): TikTokPost[] => {
  return [...posts].sort((a, b) => b.フォロワー数 - a.フォロワー数).slice(0, limit)
}