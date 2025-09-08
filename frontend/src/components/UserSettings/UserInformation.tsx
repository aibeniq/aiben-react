import { Box, Button, Flex, Heading, Input, Text, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { type ApiError, type UserPublic, type UserUpdateMe, UsersService } from "@/client"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { emailPattern, handleError } from "@/utils"
import { Field } from "../ui/field"

const UserInformation = () => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const [editMode, setEditMode] = useState(false)
  const { user: currentUser } = useAuth()
  const { t } = useTranslation()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<UserPublic>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      full_name: currentUser?.full_name,
      email: currentUser?.email,
    },
  })

  const toggleEditMode = () => {
    setEditMode(!editMode)
  }

  const mutation = useMutation({
    mutationFn: (data: UserUpdateMe) => UsersService.updateUserMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast(t("common.success"))
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries()
    },
  })

  const onSubmit: SubmitHandler<UserUpdateMe> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    toggleEditMode()
  }

  return (
    <VStack gap={6} align="stretch" py={4}>
      <Heading size="sm">{t("settings.userInformation")}</Heading>
      <Box w={{ sm: "full", md: "md" }} as="form" onSubmit={handleSubmit(onSubmit)}>
        <VStack gap={4} align="stretch">
          <Field label={t("forms.fullName")}>
            {editMode ? (
              <Input {...register("full_name", { maxLength: 30 })} type="text" size="md" />
            ) : (
              <Text
                fontSize="md"
                py={2}
                color={!currentUser?.full_name ? "gray" : "inherit"}
                truncate
                maxW="sm"
              >
                {currentUser?.full_name || t("common.notAvailable")}
              </Text>
            )}
          </Field>
          <Field
            label={t("forms.email")}
            invalid={!!errors.email}
            errorText={errors.email?.message}
          >
            {editMode ? (
              <Input
                {...register("email", {
                  required: t("forms.emailRequired"),
                  pattern: emailPattern,
                })}
                type="email"
                size="md"
              />
            ) : (
              <Text fontSize="md" py={2} truncate maxW="sm">
                {currentUser?.email}
              </Text>
            )}
          </Field>
          <Flex gap={3}>
            <Button
              variant="solid"
              onClick={toggleEditMode}
              type={editMode ? "button" : "submit"}
              loading={editMode ? isSubmitting : false}
              disabled={editMode ? !isDirty || !getValues("email") : false}
              bg="rgba(0, 65, 72, 0.9)"
              color="white"
              _hover={{
                bg: "rgba(0, 65, 72, 0.85)",
              }}
            >
              {editMode ? t("buttons.save") : t("buttons.edit")}
            </Button>
            {editMode && (
              <Button
                variant="subtle"
                colorPalette="gray"
                onClick={onCancel}
                disabled={isSubmitting}
              >
                {t("buttons.cancel")}
              </Button>
            )}
          </Flex>
        </VStack>
      </Box>
    </VStack>
  )
}

export default UserInformation
