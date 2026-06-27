export function useLiveUpdates(onUpdate: () => Promise<void>) {
  const delay = Math.random() * 60000

  function scheduleUpdate() {
    const timeout = (420000 - (Date.now() % 300000) + delay) % 300000
    setTimeout(runUpdate, timeout)
  }

  async function runUpdate() {
    if (document.visibilityState === 'visible') {
      await onUpdate()
    }
    scheduleUpdate()
  }

  function handleVisibilityChange() {
    if (document.visibilityState === 'visible') {
      const elapsed = Date.now() % 300000
      if (elapsed >= 120000 + delay) {
        onUpdate()
      }
    }
  }

  function start() {
    scheduleUpdate()
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }

  function stop() {
    document.removeEventListener('visibilitychange', handleVisibilityChange)
  }

  return { start, stop }
}
