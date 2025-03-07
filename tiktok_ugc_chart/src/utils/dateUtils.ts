/**
 * 日付を検証する
 * @param dateStr 検証する日付文字列
 * @returns 有効な日付の場合はtrue
 */
export const isValidDate = (dateStr: string): boolean => {
    const date = new Date(dateStr)
    return !isNaN(date.getTime())
  }
  
/**
 * 日付をYYYYMMDD形式にフォーマットする
 * @param dateStr 日付文字列
 * @returns YYYYMMDD形式の文字列
 */
export const formatDateToYYYYMMDD = (dateStr: string): string => {
  const date = new Date(dateStr)
  const yyyy = date.getFullYear()
  const mm = (date.getMonth() + 1).toString().padStart(2, '0')
  const dd = date.getDate().toString().padStart(2, '0')
  return `${yyyy}${mm}${dd}`
}

/**
 * 日付をYYYY/MM/DD形式にフォーマットする
 * @param dateStr 日付文字列
 * @returns YYYY/MM/DD形式の文字列
 */
export const formatDateToYYYYMMDDWithSlash = (dateStr: string): string => {
  const date = new Date(dateStr)
  const yyyy = date.getFullYear()
  const mm = (date.getMonth() + 1).toString().padStart(2, '0')
  const dd = date.getDate().toString().padStart(2, '0')
  return `${yyyy}/${mm}/${dd}`
}

/**
 * mm/ddまたはyyyy/mm/dd形式の日付文字列を解析し、yyyy/mm/dd形式に変換する
 * @param dateStr 解析する日付文字列
 * @param toYear mm/dd形式の場合に使用する年
 * @returns yyyy/mm/dd形式の日付文字列
 */
export const parsePostDate = (dateStr: string, toYear: number): string => {
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

/**
 * 日付文字列を MM/DD 形式にフォーマットします。
 * @param dateStr - フォーマットしたい日付文字列
 * @returns フォーマットされた MMDD 文字列
 */
export const formatDateToMMDDWithSlash = (dateStr: string): string => {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) {
    console.warn(`無効な日付形式です: ${dateStr}`)
    return '無効な日付'
  }
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  return `${month}/${day}`
}