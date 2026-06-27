<template lang="pug">
dialog(ref="dialogEl")
  h2 {{ title }}
  form(method="dialog")
    button(@click="close")
      svg(viewBox="0 0 30 30")
        path(d="M6,6 24,24")
        path(d="M6,24 24,6")
  div(v-html="content")
</template>

<script setup lang="ts">
const dialogEl = ref<HTMLDialogElement | null>(null)
const title = ref('')
const content = ref('')

function open(helpContent: string, helpTitle: string) {
  title.value = helpTitle
  content.value = helpContent
  dialogEl.value?.showModal()
}

function close() {
  dialogEl.value?.close()
}

defineExpose({ open })
</script>
