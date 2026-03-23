<template>
  <Transition name="confirm">
    <div v-if="visible" class="overlay" @click.self="cancel">
      <div class="dialog" role="alertdialog" aria-modal="true" :aria-labelledby="'cd-title'" :aria-describedby="'cd-msg'">
        <div class="dialog-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <p id="cd-title" class="dialog-title">{{ title }}</p>
        <p id="cd-msg" class="dialog-message">{{ message }}</p>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="cancel">Cancelar</button>
          <button class="btn-confirm" @click="accept">Confirmar</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useConfirm } from '@/composables/useConfirm'
const { visible, title, message, accept, cancel } = useConfirm()
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 500; padding: 1rem;
}

.dialog {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); width: 100%; max-width: 360px;
  padding: 1.5rem; display: flex; flex-direction: column;
  align-items: center; gap: 0.5rem; text-align: center;
}

.dialog-icon {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--bg); border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  color: var(--ink-3); margin-bottom: 0.25rem;
}

.dialog-title {
  font-size: 0.9375rem; font-weight: 600;
  letter-spacing: -0.02em; color: var(--ink);
}

.dialog-message {
  font-size: 0.875rem; color: var(--ink-3);
  line-height: 1.5; max-width: 28ch;
}

.dialog-actions {
  display: flex; gap: 0.5rem; margin-top: 0.75rem; width: 100%;
}

.btn-cancel {
  flex: 1; padding: 0.5625rem 1rem; font-size: 0.875rem; font-weight: 500;
  color: var(--ink-2); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--r-md);
  transition: all var(--t); cursor: pointer;
}
.btn-cancel:hover { color: var(--ink); border-color: var(--border-md); }

.btn-confirm {
  flex: 1; padding: 0.5625rem 1rem; font-size: 0.875rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  border: none; border-radius: var(--r-md);
  transition: opacity var(--t); cursor: pointer;
}
.btn-confirm:hover { opacity: 0.82; }

/* Transition */
.confirm-enter-active, .confirm-leave-active { transition: opacity 0.15s ease; }
.confirm-enter-from, .confirm-leave-to { opacity: 0; }
.confirm-enter-active .dialog, .confirm-leave-active .dialog { transition: transform 0.15s ease; }
.confirm-enter-from .dialog, .confirm-leave-to .dialog { transform: scale(0.96); }

@media (max-width: 480px) {
  .dialog-actions { flex-direction: column-reverse; }
}
</style>
