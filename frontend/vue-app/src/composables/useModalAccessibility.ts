import { nextTick, onBeforeUnmount, watch, type Ref } from 'vue';

interface ModalEntry {
  element: HTMLElement;
  close: () => void;
  canClose: () => boolean;
}

const activeModals: ModalEntry[] = [];
const previousInert = new Map<HTMLElement, boolean>();
let previousOverflow = '';
const focusableSelector = 'button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])';

/** One focus/keyboard/background lifecycle for all existing modal layouts. */
export function useModalAccessibility(options: {
  panel: Ref<HTMLElement | null>;
  isOpen: () => boolean;
  close: () => void;
  canClose?: () => boolean;
  initialFocus?: Ref<HTMLElement | null>;
  fallbackFocus?: Ref<HTMLElement | null>;
}) {
  let entry: ModalEntry | null = null;
  let trigger: HTMLElement | null = null;
  let revision = 0;

  function release() {
    if (!entry) return;
    const wasTop = activeModals[activeModals.length - 1] === entry;
    activeModals.splice(activeModals.indexOf(entry), 1);
    entry = null;
    updateBackground();
    const returnTarget = trigger;
    if (wasTop) void nextTick(() => {
      if (returnTarget?.isConnected && !returnTarget.closest('[inert]')) returnTarget.focus();
      else if (options.fallbackFocus?.value && !options.fallbackFocus.value.closest('[inert]')) options.fallbackFocus.value.focus();
    });
    trigger = null;
  }

  watch(options.isOpen, async (open) => {
    const currentRevision = ++revision;
    if (!open) {
      release();
      return;
    }
    trigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    await nextTick();
    if (currentRevision !== revision || !options.isOpen() || !options.panel.value) return;
    entry = { element: options.panel.value, close: options.close, canClose: options.canClose ?? (() => true) };
    if (!activeModals.length) {
      previousOverflow = document.body.style.overflow;
      document.addEventListener('keydown', handleModalKeydown, true);
    }
    activeModals.push(entry);
    updateBackground();
    (options.initialFocus?.value ?? entry.element).focus();
  }, { immediate: true });

  onBeforeUnmount(() => {
    revision += 1;
    release();
  });
}

function updateBackground() {
  for (const [element, inert] of previousInert) element.inert = inert;
  const top = activeModals[activeModals.length - 1];
  if (!top) {
    previousInert.clear();
    document.body.style.overflow = previousOverflow;
    document.removeEventListener('keydown', handleModalKeydown, true);
    return;
  }
  document.body.style.overflow = 'hidden';
  for (const child of document.body.children) {
    if (!(child instanceof HTMLElement) || child.contains(top.element)) continue;
    if (!previousInert.has(child)) previousInert.set(child, child.inert);
    child.inert = true;
  }
}

function handleModalKeydown(event: KeyboardEvent) {
  const top = activeModals[activeModals.length - 1];
  if (!top) return;
  if (event.key === 'Escape') {
    event.preventDefault();
    event.stopImmediatePropagation();
    if (top.canClose()) top.close();
    return;
  }
  if (event.key !== 'Tab') return;
  const controls = Array.from(top.element.querySelectorAll<HTMLElement>(focusableSelector))
    .filter((element) => element.getClientRects().length && !element.closest('[inert], [hidden]'));
  const first = controls[0];
  const last = controls[controls.length - 1];
  const focused = document.activeElement;
  if (!first || !last) {
    event.preventDefault();
    top.element.focus();
  } else if (!top.element.contains(focused) || focused === top.element) {
    event.preventDefault();
    (event.shiftKey ? last : first).focus();
  } else if (event.shiftKey && focused === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && focused === last) {
    event.preventDefault();
    first.focus();
  }
}
