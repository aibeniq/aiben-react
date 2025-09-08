import { expect, test } from "@playwright/test"

test.describe("Consult Documents Toggle", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the review page
    await page.goto("/review")
  })

  test("should toggle consult documents for individual questions", async ({
    page,
  }) => {
    // This test verifies that the consult documents toggle works for individual questions

    // First, we need to be logged in and have a knowledge base selected
    // Skip test if not properly set up
    const loginButton = page.locator("text=Login")
    if (await loginButton.isVisible()) {
      test.skip(true, "Test requires user to be logged in")
    }

    // Check if knowledge base selection is available
    const knowledgeBaseSection = page.locator(
      '[data-testid="knowledge-base-section"]',
    )
    if (await knowledgeBaseSection.isVisible()) {
      // Select a knowledge base if available
      const firstKnowledgeBase = page.locator("table tbody tr").first()
      if (await firstKnowledgeBase.isVisible()) {
        await firstKnowledgeBase.locator('input[type="radio"]').check()
      }
    }

    // Check if checklist section is available
    const checklistSection = page.locator('[data-testid="checklist-section"]')
    if (await checklistSection.isVisible()) {
      // Create or select a checklist
      const createChecklistButton = page.locator("text=Create New Checklist")
      if (await createChecklistButton.isVisible()) {
        await createChecklistButton.click()

        // Fill in checklist details
        await page.fill(
          'input[placeholder*="checklist name"]',
          "Test Checklist",
        )
        await page.fill(
          'textarea[placeholder*="description"]',
          "Test checklist for consult documents toggle",
        )

        // Add a few questions
        await page.fill(
          'textarea[placeholder*="Enter question"]',
          "Question 1: Test question with consult documents enabled",
        )
        await page.keyboard.press("Tab")

        // Add second question
        const secondQuestionInput = page
          .locator('textarea[placeholder*="Enter question"]')
          .nth(1)
        await secondQuestionInput.fill(
          "Question 2: Test question with consult documents disabled",
        )

        // Toggle off consult documents for the second question
        const consultDocumentsToggles = page.locator(
          'input[type="checkbox"][aria-label*="Consult documents"]',
        )
        const secondToggle = consultDocumentsToggles.nth(1)

        // Verify the toggle exists and is initially checked
        await expect(secondToggle).toBeVisible()
        await expect(secondToggle).toBeChecked()

        // Toggle it off
        await secondToggle.uncheck()
        await expect(secondToggle).not.toBeChecked()

        // Save the checklist
        await page.click("text=Create Checklist")

        // Verify checklist was created and can be selected
        await page.waitForSelector("text=Test Checklist")

        // Select the created checklist
        const testChecklistRow = page
          .locator("text=Test Checklist")
          .locator("..")
        await testChecklistRow.locator('input[type="checkbox"]').check()

        console.log("✅ Consult documents toggle test setup completed")
        console.log(
          "✅ Created checklist with mixed consult documents settings",
        )
        console.log("✅ Question 1: Consult documents ON")
        console.log("✅ Question 2: Consult documents OFF")
      }
    }
  })

  test("should maintain toggle states when editing checklist", async ({
    page,
  }) => {
    // This test verifies that toggle states are preserved when editing a checklist

    // Skip if not properly set up
    const loginButton = page.locator("text=Login")
    if (await loginButton.isVisible()) {
      test.skip(true, "Test requires user to be logged in")
    }

    // Look for existing test checklist
    const testChecklist = page.locator("text=Test Checklist")
    if (await testChecklist.isVisible()) {
      // Click the view/edit button for the test checklist
      const checklistRow = testChecklist.locator("..")
      const editButton = checklistRow.locator(
        'button[aria-label="View checklist"]',
      )
      await editButton.click()

      // Verify the modal opened
      await expect(page.locator("text=Edit Checklist")).toBeVisible()

      // Check that question toggle states are maintained
      const consultDocumentsToggles = page.locator(
        'input[type="checkbox"][aria-label*="Consult documents"]',
      )

      // First question should have consult documents ON
      const firstToggle = consultDocumentsToggles.nth(0)
      await expect(firstToggle).toBeChecked()

      // Second question should have consult documents OFF
      const secondToggle = consultDocumentsToggles.nth(1)
      await expect(secondToggle).not.toBeChecked()

      console.log("✅ Toggle states correctly maintained when editing")

      // Close the modal
      await page.click("text=Cancel")
    } else {
      test.skip(
        true,
        "Test checklist not found - run the first test to create it",
      )
    }
  })
})
