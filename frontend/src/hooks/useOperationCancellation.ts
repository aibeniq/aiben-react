import type { CancelablePromise } from "@/client/core/CancelablePromise"
import { useEffect, useRef } from "react"

/**
 * Hook for managing cancellation of long-running operations when user navigates to different parts of the app.
 *
 * This hook tracks active cancelable operations and automatically cancels them when the user navigates
 * to a different route. This prevents operations like Veradoc/Review, Reportgenie/Generate,
 * Compare/Twincheck, and Match/Formconnect from continuing to run in the background.
 *
 * @returns Object with methods to register and manually cancel operations
 */
export function useOperationCancellation() {
  const activeOperations = useRef<Set<CancelablePromise<any>>>(new Set())
  const currentPath = useRef<string>(window.location.pathname)

  // Cancel all active operations
  const cancelAllOperations = () => {
    console.log(
      `🚫 Cancelling ${activeOperations.current.size} active operations`,
    )

    activeOperations.current.forEach((operation) => {
      try {
        if (!operation.isCancelled) {
          operation.cancel()
          console.log("✅ Operation cancelled successfully")
        }
      } catch (error) {
        console.warn("⚠️ Error cancelling operation:", error)
      }
    })

    activeOperations.current.clear()
  }

  // Register a new cancelable operation
  const registerOperation = <T>(
    operation: CancelablePromise<T>,
  ): CancelablePromise<T> => {
    console.log("📝 Registering new cancelable operation")
    activeOperations.current.add(operation)

    // Auto-remove from set when operation completes or is cancelled
    operation.finally(() => {
      activeOperations.current.delete(operation)
      console.log(
        `🧹 Operation removed from tracking (${activeOperations.current.size} remaining)`,
      )
    })

    return operation
  }

  // Monitor for route changes and cancel operations
  useEffect(() => {
    const handleLocationChange = () => {
      const newPath = window.location.pathname
      const previousPath = currentPath.current

      // If the path has changed and we have active operations, cancel them
      if (newPath !== previousPath && activeOperations.current.size > 0) {
        console.log(`🛤️ Route changed from ${previousPath} to ${newPath}`)
        console.log(
          `📊 Found ${activeOperations.current.size} active operations to cancel`,
        )
        cancelAllOperations()
      }

      currentPath.current = newPath
    }

    // Listen for browser navigation events
    const originalPushState = window.history.pushState
    const originalReplaceState = window.history.replaceState

    // Override pushState to detect programmatic navigation
    window.history.pushState = (...args) => {
      originalPushState.apply(window.history, args)
      handleLocationChange()
    }

    // Override replaceState to detect programmatic navigation
    window.history.replaceState = (...args) => {
      originalReplaceState.apply(window.history, args)
      handleLocationChange()
    }

    // Listen for browser back/forward buttons
    window.addEventListener("popstate", handleLocationChange)

    return () => {
      // Restore original methods
      window.history.pushState = originalPushState
      window.history.replaceState = originalReplaceState
      window.removeEventListener("popstate", handleLocationChange)
    }
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (activeOperations.current.size > 0) {
        console.log("🧹 Component unmounting, cancelling remaining operations")
        cancelAllOperations()
      }
    }
  }, [])

  return {
    registerOperation,
    cancelAllOperations,
    activeOperationsCount: activeOperations.current.size,
  }
}
