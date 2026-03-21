import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const title = ref('')
let resolveFn = null

export function useConfirm() {
  function showConfirm(msg, ttl = '¿Estás seguro?') {
    message.value = msg
    title.value = ttl
    visible.value = true
    return new Promise((resolve) => {
      resolveFn = resolve
    })
  }

  function accept() {
    visible.value = false
    resolveFn?.(true)
  }

  function cancel() {
    visible.value = false
    resolveFn?.(false)
  }

  return { visible, message, title, showConfirm, accept, cancel }
}
