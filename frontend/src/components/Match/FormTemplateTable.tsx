import { Button, Checkbox, HStack, IconButton, Table } from "@chakra-ui/react"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { FiCopy, FiEye, FiPlus, FiTrash2 } from "react-icons/fi"
import { type FormConnectForm, FormconnectService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import FormTemplateModal from "./FormTemplateModal"

interface FormTemplateTableProps {
  forms: FormConnectForm[]
  selectedForm: FormConnectForm | null
  onFormChange: (form: FormConnectForm | null) => void
  onFieldsChange: (fields: string) => void
  onFormsUpdate: () => void
  fields: string
  formName: string
  setFormName: (name: string) => void
  formDescription: string
  setFormDescription: (description: string) => void
  isDisabled?: boolean
  searchMode?: "vector" | "full_scan"
}

interface FormTemplateTableHeaderProps {
  onCreateNew: () => void
}

interface FormTemplateTableBodyProps {
  forms: FormConnectForm[]
  selectedForm: FormConnectForm | null
  onFormChange: (form: FormConnectForm | null) => void
  onFieldsChange: (fields: string) => void
  onViewForm: (form: FormConnectForm) => void
  onCopyForm: (form: FormConnectForm) => void
  onDeleteForm: (form: FormConnectForm) => void
}

const FormTemplateTableHeader = ({
  onCreateNew,
}: FormTemplateTableHeaderProps) => {
  const { t } = useTranslation()

  return (
    <Table.Header position="sticky" top="0" bg="transparent" zIndex="1">
      <Table.Row>
        <Table.ColumnHeader w="6" />
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold" }}
        >
          {t("modelSelection.tableHeaders.name")}
        </Table.ColumnHeader>
        <Table.ColumnHeader
          style={{ fontSize: "0.875rem", fontWeight: "bold" }}
        >
          {t("modelSelection.tableHeaders.description")}
        </Table.ColumnHeader>
        <Table.ColumnHeader
          w="32"
          style={{ fontSize: "0.875rem", fontWeight: "bold" }}
        >
          <Button size="sm" onClick={onCreateNew} ml="auto" variant="ghost">
            <FiPlus size={14} />
          </Button>
        </Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
  )
}

const FormTemplateTableBody = ({
  forms,
  selectedForm,
  onFormChange,
  onFieldsChange,
  onViewForm,
  onCopyForm,
  onDeleteForm,
}: FormTemplateTableBodyProps) => {
  // Sort forms: selected first, then alphabetically
  const sortedForms = [...forms].sort((a, b) => {
    const aSelected = selectedForm?.id === a.id
    const bSelected = selectedForm?.id === b.id

    if (aSelected !== bSelected) {
      return aSelected ? -1 : 1
    }

    return (a.name || "").localeCompare(b.name || "")
  })

  return (
    <Table.Body>
      {sortedForms.map((form) => (
        <Table.Row
          key={form.id}
          data-selected={selectedForm?.id === form.id ? "" : undefined}
        >
          <Table.Cell>
            <Checkbox.Root
              size="sm"
              top="0.5"
              aria-label="Select row"
              checked={selectedForm?.id === form.id}
              onCheckedChange={(details) => {
                if (details.checked) {
                  onFormChange(form)
                  onFieldsChange(form.fields)
                } else {
                  onFormChange(null)
                  onFieldsChange("")
                }
              }}
            >
              <Checkbox.HiddenInput />
              <Checkbox.Control />
            </Checkbox.Root>
          </Table.Cell>
          <Table.Cell>{form.name}</Table.Cell>
          <Table.Cell>{form.description || ""}</Table.Cell>
          <Table.Cell>
            <HStack gap={1} justify="center">
              <IconButton
                size="xs"
                variant="ghost"
                aria-label="View form template"
                onClick={() => onViewForm(form)}
              >
                <FiEye size={14} />
              </IconButton>
              <IconButton
                size="xs"
                variant="ghost"
                aria-label="Copy form template"
                onClick={() => onCopyForm(form)}
              >
                <FiCopy size={14} />
              </IconButton>
              <IconButton
                size="xs"
                variant="ghost"
                colorPalette="red"
                aria-label="Delete form template"
                onClick={() => onDeleteForm(form)}
              >
                <FiTrash2 size={14} />
              </IconButton>
            </HStack>
          </Table.Cell>
        </Table.Row>
      ))}
      {forms.length === 0 && (
        <Table.Row>
          <Table.Cell colSpan={4} textAlign="center" py={8} color="gray.500">
            No form templates available. Create your first form template to get
            started.
          </Table.Cell>
        </Table.Row>
      )}
    </Table.Body>
  )
}

const FormTemplateTable = ({
  forms,
  selectedForm,
  onFormChange,
  onFieldsChange,
  onFormsUpdate,
  fields,
  formName,
  setFormName,
  formDescription,
  setFormDescription,
  isDisabled = false,
}: FormTemplateTableProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [editingForm, setEditingForm] = useState<FormConnectForm | null>(null)
  const [showFormModal, setShowFormModal] = useState(false)

  const handleViewForm = (form: FormConnectForm) => {
    setEditingForm(form)
    setFormName(form.name)
    setFormDescription(form.description || "")
    onFieldsChange(form.fields)
    setShowFormModal(true)
  }

  const handleCopyForm = async (form: FormConnectForm) => {
    try {
      await FormconnectService.createForm({
        requestBody: {
          name: `${form.name} (Copy)`,
          description: form.description,
          fields: form.fields,
          owner_id: "", // Backend will set this automatically
        },
      })
      showSuccessToast("Form template copied successfully.")
      onFormsUpdate()
    } catch (error: any) {
      console.error("Error copying form template:", error)
      showErrorToast("Failed to copy form template. Please try again.")
    }
  }

  const handleDeleteForm = async (form: FormConnectForm) => {
    if (!form.id) {
      showErrorToast("Cannot delete form: missing ID")
      return
    }

    try {
      await FormconnectService.deleteForm({ formId: form.id })
      showSuccessToast("Form template deleted successfully.")

      // Clear selection if deleted form was selected
      if (selectedForm?.id === form.id) {
        onFormChange(null)
        onFieldsChange("")
        setFormName("")
        setFormDescription("")
      }

      onFormsUpdate()
    } catch (error: any) {
      console.error("Error deleting form template:", error)
      showErrorToast("Failed to delete form template. Please try again.")
    }
  }

  const handleSave = async () => {
    try {
      if (editingForm?.id) {
        await FormconnectService.updateForm({
          formId: editingForm.id,
          requestBody: {
            name: formName,
            description: formDescription,
            fields,
            owner_id: editingForm.owner_id || "",
          },
        })
        showSuccessToast("Form template updated successfully.")
      } else {
        await FormconnectService.createForm({
          requestBody: {
            name: formName,
            description: formDescription,
            fields,
            owner_id: "", // Backend will set this automatically
          },
        })
        showSuccessToast("Form template created successfully.")
      }

      // Reset form and refresh
      setEditingForm(null)
      setFormName("")
      setFormDescription("")
      onFieldsChange("")
      setShowFormModal(false)
      onFormsUpdate()
    } catch (error: any) {
      console.error("Error saving form template:", error)
      showErrorToast("Failed to save form template. Please try again.")
    }
  }

  const handleCreateNew = () => {
    setEditingForm(null)
    setFormName("")
    setFormDescription("")
    onFieldsChange("")
    setShowFormModal(true)
  }

  const handleModalClose = () => {
    setShowFormModal(false)
    setEditingForm(null)
    setFormName("")
    setFormDescription("")
    onFieldsChange("")
  }

  return (
    <div
      style={{
        opacity: isDisabled ? 0.3 : 1,
        pointerEvents: isDisabled ? "none" : "auto",
      }}
    >
      {/* Form Template Table */}
      <div
        style={{
          maxHeight: "300px",
          overflowY: "auto",
          border: "1px solid #E2E8F0",
          borderRadius: "8px",
          width: "100%",
        }}
      >
        <Table.Root variant="line">
          <FormTemplateTableHeader onCreateNew={handleCreateNew} />
          <FormTemplateTableBody
            forms={forms}
            selectedForm={selectedForm}
            onFormChange={onFormChange}
            onFieldsChange={onFieldsChange}
            onViewForm={handleViewForm}
            onCopyForm={handleCopyForm}
            onDeleteForm={handleDeleteForm}
          />
        </Table.Root>
      </div>

      {/* Form Template Modal */}
      <FormTemplateModal
        isOpen={showFormModal}
        onClose={handleModalClose}
        editingForm={editingForm}
        onSave={handleSave}
        formName={formName}
        setFormName={setFormName}
        formDescription={formDescription}
        setFormDescription={setFormDescription}
        fields={fields}
        onFieldsChange={onFieldsChange}
      />
    </div>
  )
}

export default FormTemplateTable
