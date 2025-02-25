<template>
    <img
      :src="src"
      :alt="alt"
      class="chart-icon"
      :style="{ top: position.y + 'px', left: position.x + 'px' }"
      @mousedown="startDrag"
      @touchstart="startDrag"
    />
  </template>
  
  <script setup lang="ts">
  import { ref, onBeforeUnmount, defineProps, defineEmits } from 'vue'
  
  // Props定義
  const props = defineProps<{
    src: string
    alt: string
    initialPosition?: { x: number, y: number }
    containerRef: HTMLElement | null
  }>()
  
  // Emitted events定義
  const emit = defineEmits<{
    (e: 'update:position', position: { x: number, y: number }): void
  }>()
  
  // アイコンの現在位置
  const position = ref<{ x: number, y: number }>(props.initialPosition || { x: 10, y: 10 })
  
  // ドラッグ状態管理
  const isDragging = ref(false)
  const startX = ref(0)
  const startY = ref(0)
  const initialX = ref(0)
  const initialY = ref(0)
  
  // ドラッグ中の処理
  const onDrag = (event: MouseEvent | TouchEvent) => {
    if (!isDragging.value) return
  
    let currentX = 0
    let currentY = 0
  
    if (event instanceof MouseEvent) {
      currentX = event.clientX
      currentY = event.clientY
    } else if (event instanceof TouchEvent) {
      event.preventDefault()
      if (event.touches.length > 0) {
        currentX = event.touches[0].clientX
        currentY = event.touches[0].clientY
      }
    }
  
    const dx = currentX - startX.value
    const dy = currentY - startY.value
  
    let newX = initialX.value + dx
    let newY = initialY.value + dy
  
    if (props.containerRef) {
      const containerRect = props.containerRef.getBoundingClientRect()
      const iconWidth = 80 // アイコンの幅
      const iconHeight = 80 // アイコンの高さ
  
      // コンテナ内の相対座標を計算
      const minX = 0
      const minY = 0
      const maxX = containerRect.width - iconWidth
      const maxY = containerRect.height - iconHeight
  
      // 新しい位置を制限
      newX = Math.max(minX, Math.min(newX, maxX))
      newY = Math.max(minY, Math.min(newY, maxY))
    }
  
    position.value = {
      x: newX,
      y: newY
    }
    
    // 親に位置更新を通知
    emit('update:position', position.value)
  }
  
  // ドラッグ終了の処理
  const endDrag = () => {
    if (isDragging.value) {
      isDragging.value = false
      window.removeEventListener('mousemove', onDrag)
      window.removeEventListener('mouseup', endDrag)
      window.removeEventListener('touchmove', onDrag)
      window.removeEventListener('touchend', endDrag)
      window.removeEventListener('touchcancel', endDrag)
    }
  }
  
  // ドラッグ開始の処理
  const startDrag = (event: MouseEvent | TouchEvent) => {
    isDragging.value = true
    if (event instanceof MouseEvent) {
      startX.value = event.clientX
      startY.value = event.clientY
    } else if (event instanceof TouchEvent) {
      startX.value = event.touches[0].clientX
      startY.value = event.touches[0].clientY
    }
    initialX.value = position.value.x
    initialY.value = position.value.y
  
    // イベントリスナーを追加
    window.addEventListener('mousemove', onDrag)
    window.addEventListener('mouseup', endDrag)
    window.addEventListener('touchmove', onDrag, { passive: false })
    window.addEventListener('touchend', endDrag)
    window.addEventListener('touchcancel', endDrag)
  
    event.preventDefault()
  }
  
  // コンポーネント破棄時にイベントリスナーを削除
  onBeforeUnmount(() => {
    window.removeEventListener('mousemove', onDrag)
    window.removeEventListener('mouseup', endDrag)
    window.removeEventListener('touchmove', onDrag)
    window.removeEventListener('touchend', endDrag)
    window.removeEventListener('touchcancel', endDrag)
  })
  </script>
  
  <style scoped>
  .chart-icon {
    position: absolute;
    width: 80px; /* アイコンの幅 */
    height: 80px; /* アイコンの高さ */
    z-index: 10; /* チャートより前面に表示 */
    border-radius: 50%; /* 丸く表示 */
    border: 2px solid #fff; /* 白枠 */
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.3); /* 影を追加 */
    cursor: grab; /* ドラッグ可能カーソル */
    user-select: none; /* テキスト選択防止 */
  }
  
  .chart-icon:active {
    cursor: grabbing; /* ドラッグ中のカーソル */
  }
  </style>