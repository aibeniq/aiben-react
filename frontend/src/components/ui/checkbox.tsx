import { Checkbox as ChakraCheckbox } from "@chakra-ui/react"
import * as React from "react"

export interface CheckboxProps
  extends Omit<React.ComponentProps<typeof ChakraCheckbox.Root>, "onCheckedChange"> {
  icon?: React.ReactNode
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>
  rootRef?: React.Ref<HTMLLabelElement>
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  function Checkbox(props, ref) {
    const { icon, children, inputProps, rootRef, checked, onCheckedChange, ...rest } = props
    return (
      <ChakraCheckbox.Root
        ref={rootRef}
        {...rest}
        checked={checked}
        onCheckedChange={
          onCheckedChange ? (details) => onCheckedChange(!!details.checked) : undefined
        }
      >
        <ChakraCheckbox.HiddenInput ref={ref} {...inputProps} />
        <ChakraCheckbox.Control>{icon || <ChakraCheckbox.Indicator />}</ChakraCheckbox.Control>
        {children != null && <ChakraCheckbox.Label>{children}</ChakraCheckbox.Label>}
      </ChakraCheckbox.Root>
    )
  },
)
