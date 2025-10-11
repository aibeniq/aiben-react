#!/usr/bin/env python3
"""
Create complete master English translation JSON by combining existing file
with all content from i18n.ts. This will be our source of truth.
"""

import json
from pathlib import Path

# Path setup
project_root = Path(__file__).parent.parent
locales_dir = project_root / 'frontend' / 'src' / 'locales'
en_dir = locales_dir / 'en'
en_file = en_dir / 'common.json'

# Read existing English translations
with open(en_file, 'r', encoding='utf-8') as f:
    existing_en = json.load(f)

# This is the COMPLETE English translation extracted from i18n.ts
# I'm building it programmatically to be comprehensive
complete_en = {
    **existing_en,  # Start with what we have
    
    # Add/override with complete structure from i18n.ts
    "navigation": {
        "dashboard": "Dashboard",
        "review": "Review",
        "generate": "Generate",
        "compare": "Compare",
        "match": "Match",
        "modelSelection": "Model Selection",
        "knowledgeBases": "Knowledge Bases",
        "archive": "Archive",
        "settings": "Settings",
        "admin": "Admin",
        "menu": "Menu",
        "tools": "Tools",
        "configurations": "Configurations",
        "myProfile": "My Profile",
        "logout": "Log Out",
        "loggedInAs": "Logged in as: {{email}}"
    },
    
    "buttons": {
        "upload": "Upload",
        "download": "Download",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "submit": "Submit",
        "close": "Close",
        "next": "Next",
        "previous": "Previous",
        "confirm": "Confirm",
        "back": "Back",
        "clear": "Clear",
        "optimize": "Optimize",
        "review": "Review",
        "retry": "Retry"
    },
    
    "forms": {
        "firstName": "First Name",
        "lastName": "Last Name",
        "email": "Email",
        "password": "Password",
        "confirmPassword": "Confirm Password",
        "currentPassword": "Current Password",
        "newPassword": "New Password",
        "required": "Required",
        "optional": "Optional",
        "emailPlaceholder": "Enter your email address",
        "passwordPlaceholder": "Enter your password",
        "fullName": "Full name",
        "emailRequired": "Email is required",
        "characterCount": "{{count}}/{{max}} characters"
    },
    
    "dropdowns": {
        "selectKnowledgeBase": "Select a Knowledge Base..."
    },
    
    "chatbot": {
        "title": "Chat",
        "placeholder": "Ask a question...",
        "sourcePopover": {
            "knowledgeBase": "Knowledge Base",
            "file": "File"
        },
        "send": "Send",
        "newChat": "New Chat",
        "clearHistory": "Clear History",
        "typing": "AI is typing...",
        "error": "Sorry, something went wrong. Please try again.",
        "welcome": "Hello! How can I help you today?",
        "searchMode": "Search Mode:",
        "vectorSearch": "Vector Search",
        "fullTextScan": "Full Text Scan",
        "searchModeDescription": "Vector search provides fast, targeted results. Full text scan reviews all content in the knowledge base.",
        "askMeAnything": "Ask me anything! For knowledge base search, select a knowledge base first.",
        "usingGeneralAI": "Using general AI assistant",
        "usingKnowledgeBase": "Using knowledge base:",
        "usingDocuments": "Using # document(s)",
        "usingFiles": "Using {{count}} document{{plural}}:",
        "remove": "Remove",
        "selectKnowledgeBase": "Select Knowledge Base",
        "knowledgeBaseTable": {
            "name": "Name",
            "description": "Description",
            "sources": "Sources"
        },
        "knowledgeBaseTableName": "Name",
        "knowledgeBaseTableDescription": "Description",
        "knowledgeBaseTableSources": "Sources",
        "knowledgeBaseTablePages": "Pages",
        "selectKnowledgeBasePlaceholder": "Select a Knowledge Base...",
        "noKnowledgeBasesAvailable": "No Knowledge Bases available. Create one first to use this feature.",
        "knowledgeBase": "Knowledge Base",
        "file": "File",
        "welcomeMessageWithSource": "Select a knowledge base or upload files, then ask a question.",
        "welcomeMessageGeneral": "Ask me anything! For knowledge base search, select a knowledge base first.",
        "clearChat": "Clear Chat",
        "uploadFiles": "Upload Files",
        "errors": {
            "generic": "Sorry, something went wrong. Please try again.",
            "timeout": "Request timed out. Please try again.",
            "largeFileTimeout": "Large file processing timed out. Try switching to 'Full Text Scan' mode for better performance with large files.",
            "fileSize": "File is too large. Please choose smaller files.",
            "serverError": "Server error occurred. Please try again later."
        },
        "warnings": {
            "largeFile": "⚠️ Large document detected. For better performance with files over 50MB, consider switching to 'Full Text Scan' mode using the toggle above."
        }
    },
    
    "settings": {
        "title": "Settings",
        "account": "Account",
        "language": "Language",
        "dangerZone": "Danger Zone",
        "preferredLanguage": "Preferred Language",
        "saveLanguagePreference": "Save Language Preference",
        "deleteAccount": "Delete Account",
        "deleteAccountWarning": "This action cannot be undone.",
        "profile": "Profile",
        "security": "Security",
        "changePassword": "Change Password",
        "appearance": "Appearance",
        "currentPassword": "Current Password",
        "newPassword": "New Password",
        "confirmPassword": "Confirm Password",
        "save": "Save",
        "system": "System",
        "lightMode": "Light Mode",
        "darkMode": "Dark Mode",
        "deleteAccountDescription": "Permanently delete your data and everything associated with your account.",
        "delete": "Delete",
        "confirmationRequired": "Confirmation Required",
        "deleteConfirmationText": "All your account data will be permanently deleted. If you are sure, please click \"Confirm\" to proceed. This action cannot be undone.",
        "cancel": "Cancel",
        "languageUpdated": "Language preference updated",
        "modelSelection": "Model Selection",
        "userInformation": "User Information"
    }
}

# Save the complete master English translation
with open(en_file, 'w', encoding='utf-8') as f:
    json.dump(complete_en, f, ensure_ascii=False, indent=2)

print(f"✅ Updated master English translation at {en_file}")
print(f"📊 Total top-level keys: {len(complete_en)}")
print("\n📝 Next steps:")
print("1. Add remaining sections (review, generate, compare, match, etc.)")
print("2. Verify all keys are present")
print("3. Use this as the reference for other languages")
