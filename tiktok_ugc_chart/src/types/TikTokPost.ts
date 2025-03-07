export interface TikTokPost {
    uniqueId: string; 
    投稿ID: string;
    投稿日: string;
    アカウント名: string;
    ニックネーム: string;
    いいね数: number;
    コメント数: number;
    保存数: number;
    シェア数: number;
    再生回数: number;
    フォロワー数: number;
    動画リンク_URL: string;
    更新日: string;
    アイコン: string;
    isVisible: boolean;
    isOrangeBorder: boolean
    isShowFollowers: boolean;
    楽曲名?: string; 
    [key: string]: string | number | boolean | undefined;
  }