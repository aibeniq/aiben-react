import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate, useRouterState } from "@tanstack/react-router"
import { useState } from "react"

import {
  type Body_login_login_access_token as AccessToken,
  type ApiError,
  LoginService,
  type UserPublic,
  type UserRegister,
  UsersService,
} from "@/client"
import { handleError } from "@/utils"

// Check if user is logged in by checking if we can fetch current user data
// This will work with HTTP-only cookies since the API call will include them
const isLoggedIn = () => {
  // We'll determine auth state by checking if the currentUser query has data
  // This will be handled by the useAuth hook's user state
  return false // Default to false, let the useQuery determine actual state
}

const useAuth = () => {
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const routerState = useRouterState()
  const queryClient = useQueryClient()

  // Don't run the user query on authentication pages to prevent infinite loops
  const isAuthPage = ['/login', '/signup', '/reset-password', '/recover-password'].some(path =>
    routerState.location.pathname.startsWith(path)
  )

  const { data: user, isLoading, isError } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    retry: false, // Don't retry on auth errors
    staleTime: 5 * 60 * 1000, // Consider fresh for 5 minutes
    enabled: !isAuthPage, // Only run query if NOT on auth pages
    refetchOnWindowFocus: false, // Don't refetch when window gains focus
    refetchOnMount: !isAuthPage, // Don't refetch on mount if on auth pages
  })

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ requestBody: data }),

    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const login = async (data: AccessToken) => {
    const response = await LoginService.loginAccessToken({
      formData: data,
    })
    // No need to store token in localStorage - it's now an HTTP-only cookie
    // The response should contain user info instead of token
    return response
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      // Invalidate current user query to refetch user data with new auth state
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      // Navigate to home - the query will be enabled on protected routes
      navigate({ to: "/" })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const logout = async () => {
    try {
      // Call the logout endpoint to clear HTTP-only cookie
      // For now, we'll make a direct API call since the generated client may not have the logout method yet
      const response = await fetch("/api/v1/login/logout", {
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
    error,
    resetError: () => setError(null),
  }
}

export { isLoggedIn }
export default useAuth
