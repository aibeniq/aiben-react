// Simple test file for the RTF cleaner
const { cleanRTFFormatting } = require("./src/utils/rtfCleaner.ts")

// Test cases with various RTF formatting issues
const testCases = [
  {
    name: "Double backslashes",
    input: "Text with \\\\ double backslashes",
    expected: "Text with double backslashes",
  },
  {
    name: "Hexadecimal characters",
    input: "Caf\\'e9 and na\\'efve text",
    expected: "Café and naïve text",
  },
  {
    name: "Tilde escapes",
    input: "Some \\~tilde~text and normal text",
    expected: "Some tildetext and normal text",
  },
  {
    name: "RTF formatting codes",
    input: "\\pard\\tx220\\fi-360 Document with formatting",
    expected: "Document with formatting",
  },
  {
    name: "Complex RTF document",
    input:
      "{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}}\\f0\\fs24 This is some text with \\pard\\tx220\\tx720\\fi-360\\bullet Here is a bullet point\\par Another line with \\\\ backslashes\\par Text with \\~non-breaking~space and \\'e9accented\\'e0characters.}",
    expected:
      "This is some text with • Here is a bullet point\nAnother line with backslashes\nText with non-breakingspace and éaccentedàcharacters.",
  },
  {
    name: "Normal text (should be unchanged)",
    input: "Normal text without any RTF codes",
    expected: "Normal text without any RTF codes",
  },
]

console.log("Testing RTF cleaner...\n")

testCases.forEach((testCase, index) => {
  console.log(`Test ${index + 1}: ${testCase.name}`)
  console.log(`Input:    "${testCase.input}"`)

  try {
    const result = cleanRTFFormatting(testCase.input)
    console.log(`Output:   "${result}"`)
    console.log(`Expected: "${testCase.expected}"`)

    const passed = result.trim() === testCase.expected.trim()
    console.log(`Status:   ${passed ? "✅ PASS" : "❌ FAIL"}`)

    if (!passed) {
      console.log(
        `Difference: Expected length ${testCase.expected.length}, got ${result.length}`,
      )
    }
  } catch (error) {
    console.log(`Status:   ❌ ERROR: ${error.message}`)
  }

  console.log("")
})

console.log("RTF cleaner test completed.")
