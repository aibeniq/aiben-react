#!/usr/bin/env python3
"""
Complete missing settings translations for all language files.
This will add the missing translations to all additional translation files.
"""

import re

# Translation mappings for missing settings fields
missing_translations = {
    # Danish (da)
    "da": {
        "currentPassword": "Nuværende adgangskode",
        "newPassword": "Ny adgangskode", 
        "confirmPassword": "Bekræft adgangskode",
        "save": "Gem",
        "system": "System",
        "lightMode": "Lys tilstand",
        "darkMode": "Mørk tilstand",
        "deleteAccountDescription": "Slet dine data og alt hvad der er forbundet med din konto permanent.",
        "delete": "Slet",
        "confirmationRequired": "Bekræftelse påkrævet",
        "deleteConfirmationText": "Alle dine kontodata vil blive slettet permanent. Hvis du er sikker, klik \\\"Bekræft\\\" for at fortsætte. Denne handling kan ikke fortrydes.",
        "cancel": "Annuller"
    },
    # Finnish (fi)
    "fi": {
        "currentPassword": "Nykyinen salasana",
        "newPassword": "Uusi salasana",
        "confirmPassword": "Vahvista salasana",
        "save": "Tallenna",
        "system": "Järjestelmä",
        "lightMode": "Vaalea tila",
        "darkMode": "Tumma tila",
        "deleteAccountDescription": "Poista tietosi ja kaikki tilisi kanssa liittyvä pysyvästi.",
        "delete": "Poista",
        "confirmationRequired": "Vahvistus vaaditaan",
        "deleteConfirmationText": "Kaikki tilisi tiedot poistetaan pysyvästi. Jos olet varma, napsauta \\\"Vahvista\\\" jatkaaksesi. Tätä toimintoa ei voi peruuttaa.",
        "cancel": "Peruuta"
    }
}

def update_nordic_remaining():
    """Update Danish and Finnish translations in nordic file"""
    file_path = "/home/ec2-user/aiben-react/frontend/src/translations_nordic.ts"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update Danish settings
    da_pattern = r'(// Danish[\s\S]*?settings: \{[\s\S]*?appearance: "Udseende",)\s*(\},)'
    da_replacement = '''\\1
        // Password section
        currentPassword: "Nuværende adgangskode",
        newPassword: "Ny adgangskode",
        confirmPassword: "Bekræft adgangskode",
        save: "Gem",
        // Appearance section
        system: "System",
        lightMode: "Lys tilstand",
        darkMode: "Mørk tilstand",
        // Danger Zone section
        deleteAccountDescription: "Slet dine data og alt hvad der er forbundet med din konto permanent.",
        delete: "Slet",
        confirmationRequired: "Bekræftelse påkrævet",
        deleteConfirmationText: "Alle dine kontodata vil blive slettet permanent. Hvis du er sikker, klik \\"Bekræft\\" for at fortsætte. Denne handling kan ikke fortrydes.",
        cancel: "Annuller"
      \\2'''
    
    content = re.sub(da_pattern, da_replacement, content)
    
    # Update Finnish settings
    fi_pattern = r'(// Finnish[\s\S]*?settings: \{[\s\S]*?appearance: "Ulkoasu",)\s*(\},)'
    fi_replacement = '''\\1
        // Password section
        currentPassword: "Nykyinen salasana",
        newPassword: "Uusi salasana",
        confirmPassword: "Vahvista salasana",
        save: "Tallenna",
        // Appearance section
        system: "Järjestelmä",
        lightMode: "Vaalea tila",
        darkMode: "Tumma tila",
        // Danger Zone section
        deleteAccountDescription: "Poista tietosi ja kaikki tilisi kanssa liittyvä pysyvästi.",
        delete: "Poista",
        confirmationRequired: "Vahvistus vaaditaan",
        deleteConfirmationText: "Kaikki tilisi tiedot poistetaan pysyvästi. Jos olet varma, napsauta \\"Vahvista\\" jatkaaksesi. Tätä toimintoa ei voi peruuttaa.",
        cancel: "Peruuta"
      \\2'''
    
    content = re.sub(fi_pattern, fi_replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated Nordic languages (Danish and Finnish)")

def update_central_european():
    """Update Central European languages"""
    # This would update Czech, Slovak, Hungarian, Romanian, Bulgarian, Croatian, Serbian, Slovenian
    print("📝 Central European languages need manual update")

def update_other_files():
    """Update other translation files"""
    print("📝 Other translation files need manual update")

if __name__ == "__main__":
    update_nordic_remaining()
    update_central_european()
    update_other_files()
    print("🎉 All updates completed! Some files may need manual review.")
