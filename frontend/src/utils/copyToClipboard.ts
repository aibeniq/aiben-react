/**
 * Robust copy to clipboard function with fallback for insecure contexts
 */
export const copyToClipboard = async (text: string): Promise<void> => {
    // Debug logging
    console.log('🔄 copyToClipboard called with text:', {
        length: text.length,
        preview: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
        isSecureContext: typeof window !== 'undefined' ? window.isSecureContext : 'unknown',
        clipboardApiAvailable: typeof navigator !== 'undefined' && navigator.clipboard && typeof navigator.clipboard.writeText === 'function'
    })

    // Try modern Clipboard API first (requires HTTPS and navigator.clipboard support)
    if (typeof navigator !== 'undefined' && navigator.clipboard && typeof navigator.clipboard.writeText === 'function' && window.isSecureContext) {
        try {
            console.log('✅ Using modern Clipboard API')
            await navigator.clipboard.writeText(text)
            console.log('✅ Modern Clipboard API succeeded')
            return
        } catch (err) {
            console.warn('❌ Clipboard API failed, falling back to legacy method:', err)
            // Continue to fallback method
        }
    } else {
        console.log('⚠️ Modern Clipboard API not available, using fallback method')
    }

    // Fallback to legacy method (works on HTTP and when Clipboard API is not available)
    console.log('🔄 Starting legacy copy method')
    return new Promise((resolve, reject) => {
        try {
            // Check if we can use execCommand at all
            if (!document.queryCommandSupported || !document.queryCommandSupported('copy')) {
                console.error('❌ Copy command not supported by browser')
                reject(new Error('Copy functionality not supported by this browser'))
                return
            }

            console.log('✅ execCommand copy is supported')
            // Create a temporary textarea element
            const textArea = document.createElement('textarea')
            textArea.value = text

            // Make the textarea properly visible for selection but visually hidden
            textArea.style.position = 'fixed'
            textArea.style.left = '-9999px'
            textArea.style.top = '0'
            textArea.style.width = '1px'
            textArea.style.height = '1px'
            textArea.style.padding = '0'
            textArea.style.border = '0'
            textArea.style.outline = 'none'
            textArea.style.boxShadow = 'none'
            textArea.style.background = 'transparent'

            // Critical: Don't set opacity to 0 or contentEditable
            // These can interfere with copy operations
            textArea.readOnly = false
            textArea.setAttribute('tabindex', '-1')
            textArea.setAttribute('aria-hidden', 'true')

            document.body.appendChild(textArea)
            console.log('✅ Textarea element created and added to DOM')

            try {
                // Focus and select all text
                textArea.focus()
                textArea.select()
                console.log('✅ Textarea focused and selected')

                // For mobile browsers - ensure full selection
                if (textArea.setSelectionRange) {
                    textArea.setSelectionRange(0, textArea.value.length)
                    console.log('✅ Selection range set for mobile compatibility')
                }

                // Verify selection before copying
                const preSelection = window.getSelection()
                const preSelectedText = preSelection ? preSelection.toString() : ''
                console.log('🔍 Pre-copy verification:', {
                    hasSelection: !!preSelection,
                    selectedLength: preSelectedText.length,
                    originalLength: text.length,
                    textareaLength: textArea.value.length,
                    selectionMatches: preSelectedText === text,
                    textareaMatches: textArea.value === text
                })

                // Check if copy command is supported
                if (!document.queryCommandSupported('copy')) {
                    console.error('❌ Copy command not supported after selection')
                    reject(new Error('Copy command not supported by browser'))
                    return
                }

                console.log('✅ About to execute copy command')
                // Attempt the copy
                const successful = document.execCommand('copy')
                console.log('📋 execCommand result:', successful)

                if (successful) {
                    console.log('✅ Copy command executed successfully')
                    resolve()
                } else {
                    console.error('❌ execCommand returned false')
                    reject(new Error('Copy command execution failed'))
                }
            } catch (copyError) {
                console.error('❌ Copy operation error:', copyError)
                reject(new Error(`Copy operation failed: ${copyError}`))
            } finally {
                // Clean up
                if (document.body.contains(textArea)) {
                    document.body.removeChild(textArea)
                    console.log('🧹 Textarea cleanup completed')
                }
            }
        } catch (outerError) {
            console.error('❌ General copy error:', outerError)
            reject(new Error(`Copy to clipboard failed: ${outerError}`))
        }
    })
}