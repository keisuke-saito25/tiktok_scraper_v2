<template>
  <div>
    <v-row>
      <v-col cols="12" sm="6" md="4">
        <v-text-field
          v-model="searchAccountName"
          label="アカウント名で検索"
          append-icon="mdi-magnify"
          clearable
        ></v-text-field>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-data-table
          :headers="tableHeaders"
          :items="filteredAccounts"
          class="elevation-1"
          :items-per-page="10"
          :sort-by="[{ key: 'フォロワー数', order: 'desc' }]"
        >
          <template v-slot:item.isVisible="{ item }">
            <v-checkbox
              :model-value="item.isVisible"
              @update:model-value="(value) => toggleVisibility(item, value)"
            ></v-checkbox>
          </template>

          <template v-slot:item.isOrangeBorder="{ item }">
            <v-checkbox
              :model-value="item.isOrangeBorder"
              @update:model-value="(value) => toggleOrangeBorder(item, value)"
            ></v-checkbox>
          </template>

          <template v-slot:item.isShowFollowers="{ item }">
            <v-checkbox
              :model-value="item.isShowFollowers"
              @update:model-value="(value) => toggleShowFollowers(item, value)"
            ></v-checkbox>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TikTokPost } from '../types/TikTokPost'

// Props定義
const props = defineProps<{
  accounts: TikTokPost[]
}>()

// Emits定義
const emit = defineEmits<{
  (e: 'toggle-visibility', account: TikTokPost, value: boolean | null): void
  (e: 'toggle-orange-border', account: TikTokPost, value: boolean | null): void
  (e: 'toggle-show-followers', account: TikTokPost, value: boolean | null): void
}>()

// 検索フィルター
const searchAccountName = ref<string>('')

// フィルタリングされたアカウント
const filteredAccounts = computed(() => {
  if (!searchAccountName.value) return props.accounts
  return props.accounts.filter(account =>
    account.アカウント名.toLowerCase().includes(searchAccountName.value.toLowerCase())
  )
})

// テーブルヘッダー
const tableHeaders = [
  { title: '表示', key: 'isVisible' },  
  { title: 'オレンジ', key: 'isOrangeBorder' },
  { title: 'フォロワー表示', key: 'isShowFollowers' },
  { title: 'アカウント名', key: 'アカウント名' },
  { title: 'ニックネーム', key: 'ニックネーム' },
  { title: 'いいね数', key: 'いいね数' },
  { title: 'コメント数', key: 'コメント数' },
  { title: '保存数', key: '保存数' },
  { title: 'シェア数', key: 'シェア数' },
  { title: '再生回数', key: '再生回数' },
  { title: 'フォロワー数', key: 'フォロワー数', sortable: true }
]

// アカウントの表示状態を切り替える
const toggleVisibility = (item: TikTokPost, value: boolean | null) => {
  emit('toggle-visibility', item, value)
}

// オレンジ枠の状態を切り替える
const toggleOrangeBorder = (item: TikTokPost, value: boolean | null) => {
  emit('toggle-orange-border', item, value)
}

// フォロワー数表示の状態を切り替える
const toggleShowFollowers = (item: TikTokPost, value: boolean | null) => {
  emit('toggle-show-followers', item, value)
}
</script>