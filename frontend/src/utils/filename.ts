/**
 * Utility functions for cleaning and processing filenames
 */

/**
 * Clean filename by removing temporary file prefixes and paths
 * Handles various prefix patterns:
 * - tmpXXXXXX_filename.ext (Python tempfile)
 * - b_dmyao_filename.ext (user-specific prefix)
 * - uuid_filename.ext (UUID prefix)
 * - any_prefix_filename.ext (generic prefix)
 */
export const getCleanFileName = (source: string): string => {
  if (!source) return "Unknown"
  
  // First get just the filename from any path
  let filename = source.split("/").pop() || source.split("\\").pop() || source
  
  // Remove various types of prefixes that might be added during file processing
  if (filename.includes("_")) {
    const parts = filename.split("_")
    if (parts.length > 1) {
      const firstPart = parts[0]
      // If first part is short and alphanumeric (likely a prefix), remove it
      // This catches patterns like:
      // - "b_dmyao_" (user prefix)
      // - "tmp123456" (temp prefix) 
      // - "uuid123" (short uuid)
      // But preserves legitimate underscores in filenames
      if (firstPart.length <= 10 && /^[a-zA-Z0-9]+$/.test(firstPart)) {
        filename = parts.slice(1).join("_")
      }
    }
  }

  return filename
}

/**
 * Get display filename for UI components
 * Alias for getCleanFileName for backward compatibility
 */
export const getDisplayFileName = getCleanFileName