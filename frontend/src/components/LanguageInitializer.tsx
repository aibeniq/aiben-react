import { useEffect } from "react"
import { useTranslation } from "react-i18next"

interface LanguageInitializerProps {
  children: React.ReactNode
}

const LanguageInitializer: React.FC<LanguageInitializerProps> = ({ children }) => {
  const { i18n } = useTranslation()

  useEffect(() => {
    // Initialize language from localStorage if available
    const savedLanguage = localStorage.getItem("preferredLanguage")
    if (savedLanguage && savedLanguage !== i18n.language) {
      console.log(`🌐 Initializing UI language from localStorage: ${savedLanguage}`)
      i18n.changeLanguage(savedLanguage)
    }
  }, [i18n])

  return <>{children}</>
}

export default LanguageInitializer
