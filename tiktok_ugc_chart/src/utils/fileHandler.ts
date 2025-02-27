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
 * 指定された日付のシートからTikTokポストデータを抽出
 * @param worksheet ワークシート
 * @param toDate 日付
 * @returns 抽出したTikTokポストの配列
 */
export const extractTikTokPostData = (worksheet: XLSX.WorkSheet, toDate: Date): TikTokPost[] => {
  const toSheetData: any[][] = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' })
  
  // ヘッダーを取得
  const toHeaders: string[] = toSheetData[0] as string[]
  
  // 投稿IDのインデックスを取得
  const postIdIndex = toHeaders.indexOf('投稿ID')
  if (postIdIndex === -1) {
    throw new Error('投稿ID列が見つかりません。')
  }
  
  // アイコン列のインデックスを固定で指定
  const ICON_COLUMN_INDEX = 12 // M列
  const toYear = toDate.getFullYear()
  
  // データ部分をフィルタリング
  const tikTokPosts: TikTokPost[] = toSheetData.slice(1)
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
  
  return tikTokPosts
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