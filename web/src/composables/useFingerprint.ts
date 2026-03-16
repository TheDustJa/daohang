const KEY = 'nav_fingerprint'

function generateId(): string {
  const arr = new Uint8Array(16)
  crypto.getRandomValues(arr)
  return Array.from(arr, b => b.toString(16).padStart(2, '0')).join('')
}

let cached: string | null = null

export function useFingerprint(): string {
  if (cached) return cached
  let fp = localStorage.getItem(KEY)
  if (!fp) {
    fp = generateId()
    localStorage.setItem(KEY, fp)
  }
  cached = fp
  return fp
}
