import { Box, Container, HStack, Image, Input, Text } from "@chakra-ui/react"
import {
  Link as RouterLink,
  createFileRoute,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiLock, FiMail } from "react-icons/fi"

import type { Body_login_login_access_token as AccessToken } from "@/client"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { InputGroup } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import useAuth from "@/hooks/useAuth"
import { UsersService } from "@/client"
import Logo from "/assets/images/aibeniq-logo-center.png"
import { emailPattern, passwordRules } from "../utils"

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    // Check if user is already authenticated
    try {
      await UsersService.readUserMe()
      // If successful, user is already logged in, redirect to home
      throw redirect({
        to: "/",
      })
    } catch (error) {
      // User is not authenticated, allow access to login page
    }
  },
})

function Login() {
  const { loginMutation, error, resetError } = useAuth()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AccessToken>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const onSubmit: SubmitHandler<AccessToken> = async (data) => {
    if (isSubmitting) return

    resetError()

    try {
      console.log(data)
      await loginMutation.mutateAsync(data)
    } catch {
      // error is handled by useAuth hook
    }
  }

  return (
    <>
      <Container
        as="form"
        onSubmit={handleSubmit(onSubmit)}
        h="100vh"
        maxW="sm"
        alignItems="stretch"
        justifyContent="center"
        gap={4}
        centerContent
      >
        <Image
          src={Logo}
          alt="FastAPI logo"
          height="auto"
          maxW="2xs"
          alignSelf="center"
        />
        <Field
          invalid={!!errors.username}
          errorText={errors.username?.message || !!error}
        >
          <InputGroup w="100%" startElement={<FiMail />}>
            <Input
              id="username"
              {...register("username", {
                required: "Username is required",
                pattern: emailPattern,
              })}
              placeholder="Email"
              type="email"
            />
          </InputGroup>
        </Field>
        <PasswordInput
          type="password"
          startElement={<FiLock />}
          {...register("password", passwordRules())}
          placeholder="Password"
          errors={errors}
        />
        <RouterLink
          to="/recover-password"
          className="main-link"
          style={{ width: "fit-content" }}
        >
          <Text
            color="rgba(0, 65, 72, 0.8)"
            fontSize="sm"
            _hover={{ textDecoration: "underline" }}
            width="fit-content"
            alignSelf="flex-end"
          >
            Forgot Password?
          </Text>
        </RouterLink>
        <Button
          variant="solid"
          type="submit"
          loading={isSubmitting}
          size="md"
          bg="rgba(0, 65, 72, 0.9)"
          _hover={{ bg: "rgba(0, 65, 72, 0.8)" }}
        >
          Log In
        </Button>
        <HStack gap={1}>
          <Text>Don't have an account? </Text>
          <Box>
            <RouterLink
              to="/signup"
              className="main-link"
              style={{ width: "fit-content" }}
            >
              <Text
                color="rgba(0, 65, 72, 0.8)"
                fontSize="sm"
                _hover={{ textDecoration: "underline" }}
              >
                Sign Up
              </Text>
            </RouterLink>
          </Box>
        </HStack>
      </Container>
    </>
  )
}
