/**
 * Generate a UUID that works in all environments
 * Falls back to a Math.random() implementation when crypto.randomUUID is not available
 */
export function generateUUID(): string {
    // Check if crypto.randomUUID is available (secure context + modern browser)
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID()
    }

    // Fallback implementation for HTTP environments or older browsers
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
    })
}
