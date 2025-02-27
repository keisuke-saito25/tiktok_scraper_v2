/**
 * ランダムなユニークIDを生成する
 * @returns ユニークID
 */
export const generateUniqueId = (): string => {
  return Math.random().toString(36).substring(2, 9) + Date.now().toString(36);
}