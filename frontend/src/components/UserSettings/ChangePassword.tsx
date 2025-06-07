import { Box, Button, Heading, VStack } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiLock } from "react-icons/fi"

import { type ApiError, type UpdatePassword, UsersService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { confirmPasswordRules, handleError, passwordRules } from "@/utils"
import { PasswordInput } from "../ui/password-input"

interface UpdatePasswordForm extends UpdatePassword {
  confirm_password: string
}

const ChangePassword = () => {
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { errors, isValid, isSubmitting },
  } = useForm<UpdatePasswordForm>({
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: UpdatePassword) => UsersService.updatePasswordMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Password updated successfully.")
      reset()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onSubmit: SubmitHandler<UpdatePasswordForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <VStack gap={6} align="stretch" py={4}>
      <Heading size="sm">Change Password</Heading>
      <Box as="form" onSubmit={handleSubmit(onSubmit)}>
        <VStack gap={4} w={{ base: "100%", md: "md" }}>
          <PasswordInput
            type="current_password"
            startElement={<FiLock />}
            {...register("current_password", passwordRules())}
            placeholder="Current Password"
            errors={errors}
          />
          <PasswordInput
            type="new_password"
            startElement={<FiLock />}
            {...register("new_password", passwordRules())}
            placeholder="New Password"
            errors={errors}
          />
          <PasswordInput
            type="confirm_password"
            startElement={<FiLock />}
            {...register("confirm_password", confirmPasswordRules(getValues))}
            placeholder="Confirm Password"
            errors={errors}
          />
          <Button
            variant="solid"
            type="submit"
            loading={isSubmitting}
            disabled={!isValid}
            bg="rgba(0, 65, 72, 0.9)"
            color="white"
            _hover={{
              bg: "rgba(0, 65, 72, 0.85)",
            }}
            alignSelf="flex-start"
          >
            Save
          </Button>
        </VStack>
      </Box>
    </VStack>
  )
}
export default ChangePassword
