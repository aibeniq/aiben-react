import { useTranslation } from "react-i18next"

// Test the getTranslation helper function
const getTranslation = (key: string, fallback: string) => {
    try {
        const translated = useTranslation().t(key)
        return translated === key ? fallback : translated
    } catch {
        return fallback
    }
}

// Test cases
console.log("Testing getTranslation function:")
console.log("common.feedback.modalTitlePositive:", getTranslation("common.feedback.modalTitlePositive", "What was helpful?"))
console.log("common.feedback.modalTitleNegative:", getTranslation("common.feedback.modalTitleNegative", "What could be improved?"))
console.log("common.feedback.submit:", getTranslation("common.feedback.submit", "Submit"))
console.log("nonexistent.key:", getTranslation("nonexistent.key", "Fallback text"))