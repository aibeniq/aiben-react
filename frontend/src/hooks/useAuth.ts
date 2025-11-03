import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate, useRouterState } from "@tanstack/react-router"
import { toaster } from "@/components/ui/toaster"

import {
  type Body_login_access_token_api_v1_login_access_token_post as AccessToken,
  type ApiError,
  type UserPublic,
  type UserRegister,
} from "@/client"
import { useHandleError } from "@/utils"

// Check if user is logged in by checking if we can fetch current user data
// This will work with HTTP-only cookies since the API call will include them
const isLoggedIn = () => {
  // We'll determine auth state by checking if the currentUser query has data
  // This will be handled by the useAuth hook's user state
  return false // Default to false, let the useQuery determine actual state
}

const useAuth = () => {
  const navigate = useNavigate()
  const routerState = useRouterState()
  const queryClient = useQueryClient()
  const handleError = useHandleError()

  // Don't run the user query on authentication pages to prevent infinite loops
  const isAuthPage = routerState.location.pathname.startsWith('/login') ||
    routerState.location.pathname.startsWith('/signup') ||
    routerState.location.pathname.startsWith('/recover-password') ||
    routerState.location.pathname.startsWith('/reset-password')

  // Check if we're on a protected route (under _layout) or auth route
  const isProtectedRoute = routerState.location.pathname.startsWith('/_layout') ||
    (routerState.location.pathname === '/' && !isAuthPage)

  const isEnabled = isProtectedRoute && typeof window !== 'undefined'
  console.log('useAuth: isAuthPage:', isAuthPage, 'isProtectedRoute:', isProtectedRoute, 'isEnabled:', isEnabled, 'pathname:', routerState.location.pathname)

  const { data: user, isLoading, isError } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: async () => {
      // Double-check we're not on an auth page before making the request
      const currentPath = window.location.pathname
      const isCurrentlyAuthPage = currentPath.startsWith('/login') ||
        currentPath.startsWith('/signup') ||
        currentPath.startsWith('/recover-password') ||
        currentPath.startsWith('/reset-password')

      if (isCurrentlyAuthPage) {
        console.log('useAuth: Skipping /me request on auth page:', currentPath)
        throw new Error('Cannot fetch user on auth page')
      }

      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/users/me`, {
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Failed to fetch user')
      }

      return await response.json()
    },
    retry: false, // Don't retry on auth errors
    staleTime: 5 * 60 * 1000, // Consider fresh for 5 minutes
    enabled: isProtectedRoute && typeof window !== 'undefined', // Only run query if NOT on auth pages and in browser
    refetchOnWindowFocus: false, // Don't refetch when window gains focus
    refetchOnMount: isProtectedRoute && typeof window !== 'undefined', // Don't refetch on mount if on auth pages or not in browser
  })

  const signUpMutation = useMutation({
    mutationFn: async (data: UserRegister) => {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/users/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        credentials: 'include',
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Signup failed' }))
        throw new Error(errorData.detail || 'Signup failed')
      }

      return await response.json()
    },

    onSuccess: (response) => {
      // Show success message for pending approval
      toaster.create({
        title: "Registration Submitted",
        description: response.message || "Your account is pending admin approval. You'll receive an email when approved.",
        type: "info",
        duration: 8000,
      })
      navigate({ to: "/login" })
    },
    onError: (err: Error | ApiError) => {
      // Handle both ApiError and regular Error objects
      let errDetail: string
      let status: number

      if ('status' in err && 'body' in err) {
        // It's an ApiError
        errDetail = (err.body as any)?.detail
        status = err.status
      } else {
        // For regular Error objects, the message contains the error detail
        errDetail = err.message
        status = 400 // Default status for regular errors
      }

      if (status === 400 && errDetail?.includes?.("Registration pending approval")) {
        toaster.create({
          title: "Registration Pending",
          description: "Your registration is pending admin approval. Please check your email for updates.",
          type: "warning",
          duration: 6000,
        })
      } else if (status === 400 && errDetail?.includes?.("already exists in the system")) {
        toaster.create({
          title: "Account Already Exists",
          description: "An account with this email already exists. Please try logging in or use a different email.",
          type: "error",
          duration: 5000,
        })
      } else {
        // For ApiError objects, use the handleError function
        if ('status' in err && 'body' in err) {
          handleError(err)
        } else {
          // For regular Error objects, show a generic error
          toaster.create({
            title: "Registration Failed",
            description: errDetail || "Something went wrong. Please try again.",
            type: "error",
            duration: 5000,
          })
        }
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const login = async (data: AccessToken) => {
    // Use direct fetch for login to avoid client generation issues
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/v1/login/access-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
      credentials: 'include', // Include cookies
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Login failed' }))
      throw new Error(errorData.detail || 'Login failed')
    }

    return await response.json()
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      // Invalidate current user query to refetch user data with new auth state
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      // Navigate to home - the query will be enabled on protected routes
      navigate({ to: "/" })
    },
    onError: (err: Error | ApiError) => {
      // Handle both ApiError and regular Error objects
      let errDetail: string
      let status: number

      if ('status' in err && 'body' in err) {
        // It's an ApiError
        errDetail = (err.body as any)?.detail
        status = err.status
      } else {
        // For regular Error objects, the message contains the error detail
        errDetail = err.message
        status = 400 // Default status for regular errors
      }

      if (status === 403 && errDetail?.includes?.("pending")) {
        toaster.create({
          title: "Account Pending",
          description: "Your account is awaiting admin approval. Please check your email for updates.",
          type: "warning",
          duration: 6000,
        })
      } else if (status === 400 && errDetail?.includes?.("Incorrect email or password")) {
        // More user-friendly message for wrong credentials
        toaster.create({
          title: "Login Failed",
          description: "The email or password you entered is incorrect. Please check your credentials and try again.",
          type: "error",
          duration: 5000,
        })
      } else if (status === 429 && errDetail?.includes?.("Too many login attempts")) {
        // Rate limiting due to too many attempts
        toaster.create({
          title: "Too Many Attempts",
          description: errDetail,
          type: "error",
          duration: 8000,
        })
      } else if (status === 400 && errDetail?.includes?.("Inactive user")) {
        toaster.create({
          title: "Account Inactive",
          description: "Your account is not currently activated. Please contact support for assistance.",
          type: "error",
          duration: 6000,
        })
      } else {
        // For ApiError objects, use the handleError function
        if ('status' in err && 'body' in err) {
          handleError(err)
        } else {
          // For regular Error objects, show a generic error
          toaster.create({
            title: "Login Failed",
            description: errDetail || "Something went wrong. Please try again.",
            type: "error",
            duration: 5000,
          })
        }
      }
    },
  })

  const logout = async () => {
    try {
      // Call the logout endpoint to clear HTTP-only cookie
      // For now, we'll make a direct API call since the generated client may not have the logout method yet
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/login/logout`, {
        method: "POST",
        credentials: "include", // Include cookies
      })
      if (!response.ok) {
        console.warn("Logout API call failed:", response.status)
      }
    } catch (error) {
      // Even if logout fails, redirect to login
      console.warn("Logout API call failed:", error)
    }
    // Clear user data from cache
    queryClient.setQueryData(["currentUser"], null)
    queryClient.clear()
    navigate({ to: "/login" })
  }

  return {
    signUpMutation,
    loginMutation,
    logout,
    user,
    isLoading,
    isError,
  }
}

export { isLoggedIn }
export default useAuth
