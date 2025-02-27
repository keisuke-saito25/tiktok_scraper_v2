<template>
    <v-row align="center" justify="start" class="my-4" spacing="4">
      <v-col cols="12" sm="6" md="3">
        <v-text-field
          label="From"
          type="date"
          v-model="from"
          outlined
          dense
          :rules="fromRules"
          required
          @update:model-value="updateFilters"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-text-field
          label="To"
          type="date"
          v-model="to"
          outlined
          dense
          :rules="toRules"
          required
          @update:model-value="updateFilters"
        ></v-text-field>
      </v-col>
  
      <v-col cols="12" sm="6" md="3">
        <v-text-field
          label="From 2"
          type="date"
          v-model="from2"
          outlined
          dense
          :rules="fromRules2"
          @update:model-value="updateFilters"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-text-field
          label="To 2"
          type="date"
          :model-value="to"
          outlined
          dense
          disabled
        ></v-text-field>
      </v-col>
    </v-row>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, watch } from 'vue'
  
  // 親コンポーネントから受け取るprops
  const props = defineProps<{
    initialFrom?: string
    initialTo?: string
    initialFrom2?: string
  }>()
  
  // イベントemit
  const emit = defineEmits<{
    (e: 'update:filters', filters: { from: string, to: string, from2: string, to2: string, isValid: boolean }): void
  }>()
  
  // フィルタ用の日付
  const from = ref<string>(props.initialFrom || '')
  const to = ref<string>(props.initialTo || '')
  const from2 = ref<string>(props.initialFrom2 || '')
  const to2 = computed(() => to.value) // To 2 は To と同じ値
  
  // バリデーションヘルパー関数
  const isValidDate = (dateStr: string): boolean => {
    const date = new Date(dateStr)
    return !isNaN(date.getTime())
  }
  
  // バリデーションルール
  const required = (value: string) => !!value || '必須項目です。'
  const validDate = (value: string) => isValidDate(value) || '有効な日付を入力してください。'
  
  // FromがToより前または同じであることを確認するルール
  const fromBeforeTo = () => {
    if (from.value && to.value) {
      return new Date(from.value) <= new Date(to.value) || 'Fromの日付はToより前または同じでなければなりません。'
    }
    return true
  }
  
  // From2のバリデーションルール（非必須）
  const fromRules2 = [
    (value: string) => {
      if (value && !isValidDate(value)) {
        return '有効な日付を入力してください。'
      }
      return true
    },
    () => {
      if (from2.value) {
        return new Date(from2.value) <= new Date(to2.value) || 'From 2の日付はTo 2より前または同じでなければなりません。'
      }
      return true
    }
  ]
  
  // フィルタの有効性を検証
  const isFilterValid = computed(() => {
    return (
      isValidDate(from.value) &&
      isValidDate(to.value) &&
      new Date(from.value) <= new Date(to.value)
    )
  })
  
  // フィルタールールセット
  const fromRules = [required, validDate, fromBeforeTo]
  const toRules = [required, validDate, fromBeforeTo]
  
  // フィルターの更新を親コンポーネントに通知
  const updateFilters = () => {
    emit('update:filters', {
      from: from.value,
      to: to.value,
      from2: from2.value,
      to2: to2.value,
      isValid: isFilterValid.value
    })
  }
  
  // 初期値が変更された場合、内部のrefを更新
  watch(() => props.initialFrom, (newValue) => {
    if (newValue) from.value = newValue
  }, { immediate: true })
  
  watch(() => props.initialTo, (newValue) => {
    if (newValue) to.value = newValue
  }, { immediate: true })
  
  watch(() => props.initialFrom2, (newValue) => {
    if (newValue) from2.value = newValue
  }, { immediate: true })
  </script>