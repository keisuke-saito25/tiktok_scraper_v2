<template>
  <div>
    <v-btn
      color="primary"
      @click="triggerFileInput"
      block
      :disabled="disabled"
    >
      {{ buttonLabel }}
    </v-btn>
    <input
      type="file"
      ref="fileInput"
      @change="onFileChange"
      :accept="accept"
      style="display: none"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'

// Propsの定義
const props = defineProps({
  buttonLabel: {
    type: String,
    default: 'ファイルをアップロード'
  },
  accept: {
    type: String,
    default: '.xlsx, .xls'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

// Emitsの定義
const emit = defineEmits(['file-selected'])

const fileInput = ref<HTMLInputElement | null>(null)

// ファイル入力をトリガー
const triggerFileInput = () => {
  fileInput.value?.click()
}

// ファイルが選択されたときのハンドラ
const onFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files[0]) {
    emit('file-selected', files[0])
  }
  // ファイル入力をリセット（次回同じファイルを選択できるように）
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
</style>