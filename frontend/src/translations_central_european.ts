// Central European Languages Translations
// Czech (cs), Slovak (sk), Hungarian (hu), Romanian (ro), Bulgarian (bg), Croatian (hr), Serbian (sr), Slovenian (sl)

export const addCentralEuropeanTranslations = (resources: any) => {
  // Czech
  resources.cs = {
    common: {
      navigation: {
        dashboard: "Nástěnka",
        review: "Přehled",
        generate: "Generovat",
        compare: "Porovnat",
        match: "Shoda",
        modelSelection: "Výběr modelu",
        knowledgeBases: "Znalostní báze",
        archive: "Archiv",
        settings: "Nastavení",
        admin: "Správce",
        menu: "Menu",
        tools: "Nástroje",
        configurations: "Konfigurace",
        myProfile: "Můj profil",
        logout: "Odhlásit se",
        loggedInAs: "Přihlášen jako: {{email}}",
      },
      buttons: {
        upload: "Nahrát",
        download: "Stáhnout",
        save: "Uložit",
        cancel: "Zrušit",
        delete: "Smazat",
        edit: "Upravit",
        submit: "Odeslat",
        close: "Zavřít",
        next: "Další",
        previous: "Předchozí",
        confirm: "Potvrdit",
        back: "Zpět",
      },
      forms: {
        firstName: "Jméno",
        lastName: "Příjmení",
        email: "E-mail",
        password: "Heslo",
        confirmPassword: "Potvrdit heslo",
        currentPassword: "Současné heslo",
        newPassword: "Nové heslo",
        required: "Povinné",
        optional: "Volitelné",
        emailPlaceholder: "Zadejte svou e-mailovou adresu",
        passwordPlaceholder: "Zadejte své heslo",
      },
      chatbot: {
        placeholder: "Napište svou zprávu zde...",
        send: "Odeslat",
        newChat: "Nový chat",
        clearHistory: "Vymazat historii",
        typing: "AI píše...",
        error: "Omlouváme se, něco se pokazilo. Zkuste to znovu.",
        welcome: "Ahoj! Jak vám dnes mohu pomoci?",
      },
      settings: {
        title: "Nastavení",
        account: "Účet",
        language: "Jazyk",
        dangerZone: "Nebezpečná zóna",
        preferredLanguage: "Preferovaný jazyk",
        saveLanguagePreference: "Uložit jazykové preference",
        deleteAccount: "Smazat účet",
        deleteAccountWarning: "Tuto akci nelze vrátit zpět.",
        profile: "Profil",
        security: "Bezpečnost",
        changePassword: "Změnit heslo",
        appearance: "Vzhled",
      },
      errors: {
        somethingWentWrong: "Něco se pokazilo",
        tryAgain: "Zkuste to znovu",
        invalidEmail: "Neplatná e-mailová adresa",
        passwordTooShort: "Heslo je příliš krátké",
        passwordsDoNotMatch: "Hesla se neshodují",
        networkError: "Chyba sítě. Zkontrolujte připojení.",
        unauthorized: "Nemáte oprávnění k provedení této akce.",
        notFound: "Požadovaný zdroj nebyl nalezen.",
      },
      common: {
        loading: "Načítání...",
        noData: "Žádná data nejsou k dispozici",
        success: "Úspěch!",
        failed: "Neúspěšné",
        welcome: "Vítejte",
        goodbye: "Na shledanou",
        yes: "Ano",
        no: "Ne",
        ok: "OK",
        search: "Hledat",
        filter: "Filtr",
        sort: "Seřadit",
        view: "Zobrazit",
        copy: "Kopírovat",
        paste: "Vložit",
        cut: "Vyjmout",
      },
      review: {
        pageTitle: "Kontrolovat Dokumenty",
        pageDescription: "Kontrolovat dokument na základě uživatelem definovaného kontrolního seznamu a databáze politik.",
        knowledgeBaseTitle: "Znalostní Báze",
        knowledgeBaseDescription: "Klikněte pro výběr",
        checklistTitle: "Kontrolní Seznam",
        checklistDescription: "Klikněte pro výběr",
        customInstructionsTitle: "Vlastní Pokyny (Volitelné)",
        customInstructionsPlaceholder: "Zadejte další pokyny, které by měly být zváženy při odpovídání na otázky kontrolního seznamu...",
        customInstructionsHelp: "{count}/2000 znaků. Tyto pokyny budou přidány ke každé otázce během zpracování.",
        searchModeHelp: "Vektorové vyhledávání poskytuje rychlé, cílené výsledky. Úplná analýza dokumentu zkoumá veškerý obsah znalostní báze.",
        processingFile: "Zpracovávání souboru...",
        processingFiles: "Zpracovávání souborů...",
        selectKnowledgeBaseTitle: "Vybrat Znalostní Bázi",
        selectChecklistTitle: "Vybrat Kontrolní Seznam",
        noResults: "Zatím žádné výsledky",
        uploadDocuments: "Nahrajte jeden nebo více dokumentů ke kontrole proti vašemu vybranému kontrolnímu seznamu",
        results: "Výsledky",
        downloadReport: "Stáhnout Zprávu",
        downloadCsv: "Stáhnout CSV",
        clearResults: "Vymazat Výsledky",
        copyReport: "Kopírovat Zprávu",
        reportCopied: "Zpráva zkopírována do schránky!",
        reviewButton: "Kontrolovat",
        consultDocuments: "Konzultovat dokumenty",
        noChecklistsAvailable: "Žádné kontrolní seznamy nejsou k dispozici. Vytvořte svůj první kontrolní seznam pro začátek.",
        createChecklist: "Vytvořit Kontrolní Seznam",
        editChecklist: "Upravit Kontrolní Seznam",
        checklistName: "Název Kontrolního Seznamu",
        checklistNamePlaceholder: "Zadejte název kontrolního seznamu...",
        checklistDescriptionLabel: "Popis",
        checklistDescriptionPlaceholder: "Zadejte popis kontrolního seznamu pro automatické návrhy otázek (minimálně 10 znaků)...",
        questions: "Otázky",
        suggest: "Navrhnout",
        suggesting: "Navrhování...",
        optimize: "Optimalizovat",
        optimizeTooltip: "Znalostní Báze musí být vybrána pro aktivaci funkce Optimalizovat",
        optimizeTooltipEnabled: "Optimalizovat otázky na základě vybrané Znalostní Báze",
        uploadFiles: "Nahrát Soubory",
        knowledgeBase: "Znalostní Báze",
        referenceDocuments: "Referenční Dokumenty (Volitelné)",
        selectKnowledgeBasePlaceholder: "Vybrat Znalostní Bázi...",
        noKnowledgeBasesAvailable: "Žádná Znalostní Báze není k dispozici. Nejprve ji vytvořte pro použití této funkce.",
        copyQuestions: "Kopírovat Otázky",
        questionsCopied: "Otázky zkopírovány do schránky",
        noQuestionsToCopy: "Žádné otázky ke kopírování",
        failedToCopyQuestions: "Nepodařilo se zkopírovat otázky do schránky",
        saveChecklist: "Uložit Kontrolní Seznam",
        cancel: "Zrušit",
        deleteChecklist: "Smazat Kontrolní Seznam"
      },
    },
  }

  // Slovak
  resources.sk = {
    common: {
      navigation: {
        dashboard: "Nástenka",
        review: "Prehľad",
        generate: "Generovať",
        compare: "Porovnať",
        match: "Zhoda",
        modelSelection: "Výber modelu",
        knowledgeBases: "Znalostné bázy",
        archive: "Archív",
        settings: "Nastavenia",
        admin: "Správca",
        menu: "Menu",
        tools: "Nástroje",
        configurations: "Konfigurácie",
        myProfile: "Môj profil",
        logout: "Odhlásiť sa",
        loggedInAs: "Prihlásený ako: {{email}}",
      },
      buttons: {
        upload: "Nahrať",
        download: "Stiahnuť",
        save: "Uložiť",
        cancel: "Zrušiť",
        delete: "Zmazať",
        edit: "Upraviť",
        submit: "Odoslať",
        close: "Zavrieť",
        next: "Ďalší",
        previous: "Predchádzajúci",
        confirm: "Potvrdiť",
        back: "Späť",
      },
      forms: {
        firstName: "Meno",
        lastName: "Priezvisko",
        email: "E-mail",
        password: "Heslo",
        confirmPassword: "Potvrdiť heslo",
        currentPassword: "Súčasné heslo",
        newPassword: "Nové heslo",
        required: "Povinné",
        optional: "Voliteľné",
        emailPlaceholder: "Zadajte svoju e-mailovú adresu",
        passwordPlaceholder: "Zadajte svoje heslo",
      },
      chatbot: {
        placeholder: "Napíšte svoju správu sem...",
        send: "Odoslať",
        newChat: "Nový chat",
        clearHistory: "Vymazať históriu",
        typing: "AI píše...",
        error: "Ospravedlňujeme sa, niečo sa pokazilo. Skúste to znovu.",
        welcome: "Ahoj! Ako vám dnes môžem pomôcť?",
      },
      settings: {
        title: "Nastavenia",
        account: "Účet",
        language: "Jazyk",
        dangerZone: "Nebezpečná zóna",
        preferredLanguage: "Preferovaný jazyk",
        saveLanguagePreference: "Uložiť jazykové predvoľby",
        deleteAccount: "Zmazať účet",
        deleteAccountWarning: "Túto akciu nie je možné vrátiť späť.",
        profile: "Profil",
        security: "Bezpečnosť",
        changePassword: "Zmeniť heslo",
        appearance: "Vzhľad",
      },
      errors: {
        somethingWentWrong: "Niečo sa pokazilo",
        tryAgain: "Skúste to znovu",
        invalidEmail: "Neplatná e-mailová adresa",
        passwordTooShort: "Heslo je príliš krátke",
        passwordsDoNotMatch: "Heslá sa nezhodujú",
        networkError: "Chyba siete. Skontrolujte pripojenie.",
        unauthorized: "Nemáte oprávnenie na vykonanie tejto akcie.",
        notFound: "Požadovaný zdroj nebol nájdený.",
      },
      common: {
        loading: "Načítavanie...",
        noData: "Žiadne údaje nie sú k dispozícii",
        success: "Úspech!",
        failed: "Neúspešné",
        welcome: "Vitajte",
        goodbye: "Dovidenia",
        yes: "Áno",
        no: "Nie",
        ok: "OK",
        search: "Hľadať",
        filter: "Filter",
        sort: "Zoradiť",
        view: "Zobraziť",
        copy: "Kopírovať",
        paste: "Vložiť",
        cut: "Vystrihnúť",
      },
      review: {
        pageTitle: "Kontrolovať Dokumenty",
        pageDescription: "Kontrolovať dokument na základe používateľom definovaného kontrolného zoznamu a databázy politík.",
        knowledgeBaseTitle: "Znalostná Báza",
        knowledgeBaseDescription: "Kliknite pre výber",
        checklistTitle: "Kontrolný Zoznam",
        checklistDescription: "Kliknite pre výber",
        customInstructionsTitle: "Vlastné Pokyny (Voliteľné)",
        customInstructionsPlaceholder: "Zadajte ďalšie pokyny, ktoré by mali byť zvážené pri odpovedaní na otázky kontrolného zoznamu...",
        customInstructionsHelp: "{count}/2000 znakov. Tieto pokyny budú pridané ku každej otázke počas spracovania.",
        searchModeHelp: "Vektorové vyhľadávanie poskytuje rýchle, cielené výsledky. Úplná analýza dokumentu skúma všetok obsah znalostnej bázy.",
        processingFile: "Spracovávanie súboru...",
        processingFiles: "Spracovávanie súborov...",
        selectKnowledgeBaseTitle: "Vybrať Znalostnú Bázu",
        selectChecklistTitle: "Vybrať Kontrolný Zoznam",
        noResults: "Zatiaľ žiadne výsledky",
        uploadDocuments: "Nahrajte jeden alebo viac dokumentov na kontrolu proti vášmu vybranému kontrolnému zoznamu",
        results: "Výsledky",
        downloadReport: "Stiahnuť Správu",
        downloadCsv: "Stiahnuť CSV",
        clearResults: "Vymazať Výsledky",
        copyReport: "Kopírovať Správu",
        reportCopied: "Správa skopírovaná do schránky!",
        reviewButton: "Kontrolovať",
        consultDocuments: "Konzultovať dokumenty",
        noChecklistsAvailable: "Žiadne kontrolné zoznamy nie sú k dispozícii. Vytvorte svoj prvý kontrolný zoznam na začiatok.",
        createChecklist: "Vytvoriť Kontrolný Zoznam",
        editChecklist: "Upraviť Kontrolný Zoznam",
        checklistName: "Názov Kontrolného Zoznamu",
        checklistNamePlaceholder: "Zadajte názov kontrolného zoznamu...",
        checklistDescriptionLabel: "Popis",
        checklistDescriptionPlaceholder: "Zadajte popis kontrolného zoznamu pre automatické návrhy otázok (minimálne 10 znakov)...",
        questions: "Otázky",
        suggest: "Navrhnúť",
        suggesting: "Navrhovanie...",
        optimize: "Optimalizovať",
        optimizeTooltip: "Znalostná Báza musí byť vybraná pre aktiváciu funkcie Optimalizovať",
        optimizeTooltipEnabled: "Optimalizovať otázky na základe vybranej Znalostnej Bázy",
        uploadFiles: "Nahrať Súbory",
        knowledgeBase: "Znalostná Báza",
        referenceDocuments: "Referenčné Dokumenty (Voliteľné)",
        selectKnowledgeBasePlaceholder: "Vybrať Znalostnú Bázu...",
        noKnowledgeBasesAvailable: "Žiadna Znalostná Báza nie je k dispozícii. Najprv ju vytvorte pre použitie tejto funkcie.",
        copyQuestions: "Kopírovať Otázky",
        questionsCopied: "Otázky skopírované do schránky",
        noQuestionsToCopy: "Žiadne otázky na kopírovanie",
        failedToCopyQuestions: "Nepodarilo sa skopírovať otázky do schránky",
        saveChecklist: "Uložiť Kontrolný Zoznam",
        cancel: "Zrušiť",
        deleteChecklist: "Zmazať Kontrolný Zoznam"
      },
    },
  }

  // Hungarian
  resources.hu = {
    common: {
      navigation: {
        dashboard: "Irányítópult",
        review: "Áttekintés",
        generate: "Generálás",
        compare: "Összehasonlítás",
        match: "Egyezés",
        modelSelection: "Modell kiválasztása",
        knowledgeBases: "Tudásbázisok",
        archive: "Archívum",
        settings: "Beállítások",
        admin: "Adminisztrátor",
        menu: "Menü",
        tools: "Eszközök",
        configurations: "Konfigurációk",
        myProfile: "Profilom",
        logout: "Kijelentkezés",
        loggedInAs: "Bejelentkezve mint: {{email}}",
      },
      buttons: {
        upload: "Feltöltés",
        download: "Letöltés",
        save: "Mentés",
        cancel: "Mégse",
        delete: "Törlés",
        edit: "Szerkesztés",
        submit: "Küldés",
        close: "Bezárás",
        next: "Következő",
        previous: "Előző",
        confirm: "Megerősítés",
        back: "Vissza",
      },
      forms: {
        firstName: "Keresztnév",
        lastName: "Vezetéknév",
        email: "E-mail",
        password: "Jelszó",
        confirmPassword: "Jelszó megerősítése",
        currentPassword: "Jelenlegi jelszó",
        newPassword: "Új jelszó",
        required: "Kötelező",
        optional: "Opcionális",
        emailPlaceholder: "Adja meg az e-mail címét",
        passwordPlaceholder: "Adja meg a jelszavát",
      },
      chatbot: {
        placeholder: "Írja be üzenetét ide...",
        send: "Küldés",
        newChat: "Új beszélgetés",
        clearHistory: "Előzmények törlése",
        typing: "Az AI gépel...",
        error: "Sajnáljuk, valami hiba történt. Próbálja újra.",
        welcome: "Üdvözöljük! Hogyan segíthetek ma?",
      },
      settings: {
        title: "Beállítások",
        account: "Fiók",
        language: "Nyelv",
        dangerZone: "Veszélyes zóna",
        preferredLanguage: "Előnyben részesített nyelv",
        saveLanguagePreference: "Nyelvi beállítások mentése",
        deleteAccount: "Fiók törlése",
        deleteAccountWarning: "Ez a művelet nem vonható vissza.",
        profile: "Profil",
        security: "Biztonság",
        changePassword: "Jelszó módosítása",
        appearance: "Megjelenés",
      },
      errors: {
        somethingWentWrong: "Valami hiba történt",
        tryAgain: "Próbálja újra",
        invalidEmail: "Érvénytelen e-mail cím",
        passwordTooShort: "A jelszó túl rövid",
        passwordsDoNotMatch: "A jelszavak nem egyeznek",
        networkError: "Hálózati hiba. Ellenőrizze a kapcsolatot.",
        unauthorized: "Nincs jogosultsága ehhez a művelethez.",
        notFound: "A kért erőforrás nem található.",
      },
      common: {
        loading: "Betöltés...",
        noData: "Nincs elérhető adat",
        success: "Sikeres!",
        failed: "Sikertelen",
        welcome: "Üdvözöljük",
        goodbye: "Viszlát",
        yes: "Igen",
        no: "Nem",
        ok: "OK",
        search: "Keresés",
        filter: "Szűrő",
        sort: "Rendezés",
        view: "Nézet",
        copy: "Másolás",
        paste: "Beillesztés",
        cut: "Kivágás",
      },
      review: {
        pageTitle: "Dokumentumok Áttekintése",
        pageDescription: "Dokumentum áttekintése felhasználó által definiált ellenőrzőlista és szabályzat adatbázis alapján.",
        knowledgeBaseTitle: "Tudásbázis",
        knowledgeBaseDescription: "Kattintson a kiválasztáshoz",
        checklistTitle: "Ellenőrzőlista",
        checklistDescription: "Kattintson a kiválasztáshoz",
        customInstructionsTitle: "Egyéni Utasítások (Opcionális)",
        customInstructionsPlaceholder: "Adjon meg további utasításokat, amelyeket figyelembe kell venni az ellenőrzőlista kérdéseinek megválaszolásakor...",
        customInstructionsHelp: "{count}/2000 karakter. Ezek az utasítások minden kérdéshez hozzáadásra kerülnek a feldolgozás során.",
        searchModeHelp: "A vektorkeresés gyors, célzott eredményeket biztosít. A teljes dokumentumelemzés a tudásbázis összes tartalmát megvizsgálja.",
        processingFile: "Fájl feldolgozása...",
        processingFiles: "Fájlok feldolgozása...",
        selectKnowledgeBaseTitle: "Tudásbázis Kiválasztása",
        selectChecklistTitle: "Ellenőrzőlista Kiválasztása",
        noResults: "Még nincsenek eredmények",
        uploadDocuments: "Töltsön fel egy vagy több dokumentumot a kiválasztott ellenőrzőlistával való áttekintéshez",
        results: "Eredmények",
        downloadReport: "Jelentés Letöltése",
        downloadCsv: "CSV Letöltése",
        clearResults: "Eredmények Törlése",
        copyReport: "Jelentés Másolása",
        reportCopied: "Jelentés vágólapra másolva!",
        reviewButton: "Áttekintés",
        consultDocuments: "Dokumentumok konzultálása",
        noChecklistsAvailable: "Nincsenek elérhető ellenőrzőlisták. Hozza létre az első ellenőrzőlistáját a kezdéshez.",
        createChecklist: "Ellenőrzőlista Létrehozása",
        editChecklist: "Ellenőrzőlista Szerkesztése",
        checklistName: "Ellenőrzőlista Neve",
        checklistNamePlaceholder: "Adja meg az ellenőrzőlista nevét...",
        checklistDescriptionLabel: "Leírás",
        checklistDescriptionPlaceholder: "Adja meg az ellenőrzőlista leírását automatikus kérdésjavaslatokhoz (minimum 10 karakter)...",
        questions: "Kérdések",
        suggest: "Javaslat",
        suggesting: "Javasolás...",
        optimize: "Optimalizálás",
        optimizeTooltip: "Tudásbázist kell kiválasztani az Optimalizálás funkció aktiválásához",
        optimizeTooltipEnabled: "Kérdések optimalizálása a kiválasztott Tudásbázis alapján",
        uploadFiles: "Fájlok Feltöltése",
        knowledgeBase: "Tudásbázis",
        referenceDocuments: "Referenciadokumentumok (Opcionális)",
        selectKnowledgeBasePlaceholder: "Tudásbázis kiválasztása...",
        noKnowledgeBasesAvailable: "Nincs elérhető Tudásbázis. Először hozzon létre egyet a funkció használatához.",
        copyQuestions: "Kérdések Másolása",
        questionsCopied: "Kérdések vágólapra másolva",
        noQuestionsToCopy: "Nincsenek másolandó kérdések",
        failedToCopyQuestions: "Nem sikerült a kérdéseket vágólapra másolni",
        saveChecklist: "Ellenőrzőlista Mentése",
        cancel: "Mégse",
        deleteChecklist: "Ellenőrzőlista Törlése"
      },
    },
  }

  // Romanian
  resources.ro = {
    common: {
      navigation: {
        dashboard: "Tablou de bord",
        review: "Revizuire",
        generate: "Generare",
        compare: "Comparare",
        match: "Potrivire",
        modelSelection: "Selecția modelului",
        knowledgeBases: "Baze de cunoștințe",
        archive: "Arhivă",
        settings: "Setări",
        admin: "Administrator",
        menu: "Meniu",
        tools: "Instrumente",
        configurations: "Configurații",
        myProfile: "Profilul meu",
        logout: "Deconectare",
        loggedInAs: "Conectat ca: {{email}}",
      },
      buttons: {
        upload: "Încărcare",
        download: "Descărcare",
        save: "Salvare",
        cancel: "Anulare",
        delete: "Ștergere",
        edit: "Editare",
        submit: "Trimitere",
        close: "Închidere",
        next: "Următorul",
        previous: "Anteriorul",
        confirm: "Confirmare",
        back: "Înapoi",
      },
      forms: {
        firstName: "Prenume",
        lastName: "Nume",
        email: "Email",
        password: "Parolă",
        confirmPassword: "Confirmă parola",
        currentPassword: "Parola curentă",
        newPassword: "Parolă nouă",
        required: "Obligatoriu",
        optional: "Opțional",
        emailPlaceholder: "Introduceți adresa de email",
        passwordPlaceholder: "Introduceți parola",
      },
      chatbot: {
        placeholder: "Scrieți mesajul aici...",
        send: "Trimite",
        newChat: "Chat nou",
        clearHistory: "Șterge istoricul",
        typing: "AI scrie...",
        error: "Ne pare rău, ceva a mers prost. Încercați din nou.",
        welcome: "Salut! Cum vă pot ajuta astăzi?",
      },
      settings: {
        title: "Setări",
        account: "Cont",
        language: "Limbă",
        dangerZone: "Zona de pericol",
        preferredLanguage: "Limba preferată",
        saveLanguagePreference: "Salvează preferința de limbă",
        deleteAccount: "Șterge contul",
        deleteAccountWarning: "Această acțiune nu poate fi anulată.",
        profile: "Profil",
        security: "Securitate",
        changePassword: "Schimbă parola",
        appearance: "Aspect",
      },
      errors: {
        somethingWentWrong: "Ceva a mers prost",
        tryAgain: "Încercați din nou",
        invalidEmail: "Adresă de email invalidă",
        passwordTooShort: "Parola este prea scurtă",
        passwordsDoNotMatch: "Parolele nu se potrivesc",
        networkError: "Eroare de rețea. Verificați conexiunea.",
        unauthorized: "Nu aveți autorizarea pentru această acțiune.",
        notFound: "Resursa solicitată nu a fost găsită.",
      },
      common: {
        loading: "Se încarcă...",
        noData: "Nu sunt date disponibile",
        success: "Succes!",
        failed: "Eșuat",
        welcome: "Bun venit",
        goodbye: "La revedere",
        yes: "Da",
        no: "Nu",
        ok: "OK",
        search: "Căutare",
        filter: "Filtru",
        sort: "Sortare",
        view: "Vizualizare",
        copy: "Copiere",
        paste: "Lipire",
        cut: "Tăiere",
      },
      review: {
        pageTitle: "Revizuire Documente",
        pageDescription: "Revizuiți un document pe baza unei liste de verificare și baze de date de politici definite de utilizator.",
        knowledgeBaseTitle: "Baza de Cunoștințe",
        knowledgeBaseDescription: "Faceți clic pentru a selecta",
        checklistTitle: "Lista de Verificare",
        checklistDescription: "Faceți clic pentru a selecta",
        customInstructionsTitle: "Instrucțiuni Personalizate (Opțional)",
        customInstructionsPlaceholder: "Introduceți instrucțiuni suplimentare care ar trebui luate în considerare la răspunsul la întrebările din lista de verificare...",
        customInstructionsHelp: "{count}/2000 caractere. Aceste instrucțiuni vor fi adăugate la fiecare întrebare în timpul procesării.",
        searchModeHelp: "Căutarea vectorială oferă rezultate rapide și țintite. Analiza completă a documentului examinează tot conținutul din baza de cunoștințe.",
        processingFile: "Se procesează fișierul...",
        processingFiles: "Se procesează fișierele...",
        selectKnowledgeBaseTitle: "Selectați Baza de Cunoștințe",
        selectChecklistTitle: "Selectați Lista de Verificare",
        noResults: "Încă nu există rezultate",
        uploadDocuments: "Încărcați unul sau mai multe documente pentru revizuire împotriva listei dvs. de verificare selectate",
        results: "Rezultate",
        downloadReport: "Descărcați Raportul",
        downloadCsv: "Descărcați CSV",
        clearResults: "Ștergeți Rezultatele",
        copyReport: "Copiați Raportul",
        reportCopied: "Raport copiat în clipboard!",
        reviewButton: "Revizuire",
        consultDocuments: "Consultați documentele",
        noChecklistsAvailable: "Nu sunt disponibile liste de verificare. Creați prima listă de verificare pentru a începe.",
        createChecklist: "Creați Lista de Verificare",
        editChecklist: "Editați Lista de Verificare",
        checklistName: "Numele Listei de Verificare",
        checklistNamePlaceholder: "Introduceți numele listei de verificare...",
        checklistDescriptionLabel: "Descriere",
        checklistDescriptionPlaceholder: "Introduceți descrierea listei de verificare pentru sugestii automate de întrebări (minimum 10 caractere)...",
        questions: "Întrebări",
        suggest: "Sugerați",
        suggesting: "Se sugerează...",
        optimize: "Optimizați",
        optimizeTooltip: "O Bază de Cunoștințe trebuie selectată pentru a activa funcția Optimizare",
        optimizeTooltipEnabled: "Optimizați întrebările pe baza Bazei de Cunoștințe selectate",
        uploadFiles: "Încărcați Fișiere",
        knowledgeBase: "Baza de Cunoștințe",
        referenceDocuments: "Documente de Referință (Opțional)",
        selectKnowledgeBasePlaceholder: "Selectați Baza de Cunoștințe...",
        noKnowledgeBasesAvailable: "Nu este disponibilă nicio Bază de Cunoștințe. Creați mai întâi una pentru a utiliza această funcție.",
        copyQuestions: "Copiați Întrebările",
        questionsCopied: "Întrebări copiate în clipboard",
        noQuestionsToCopy: "Nu sunt întrebări de copiat",
        failedToCopyQuestions: "Nu s-au putut copia întrebările în clipboard",
        saveChecklist: "Salvați Lista de Verificare",
        cancel: "Anulați",
        deleteChecklist: "Ștergeți Lista de Verificare"
      },
    },
  }

  // Bulgarian
  resources.bg = {
    common: {
      navigation: {
        dashboard: "Табло",
        review: "Преглед",
        generate: "Генериране",
        compare: "Сравнение",
        match: "Съвпадение",
        modelSelection: "Избор на модел",
        knowledgeBases: "Бази знания",
        archive: "Архив",
        settings: "Настройки",
        admin: "Администратор",
        menu: "Меню",
        tools: "Инструменти",
        configurations: "Конфигурации",
        myProfile: "Моят профил",
        logout: "Излизане",
        loggedInAs: "Влязъл като: {{email}}",
      },
      buttons: {
        upload: "Качване",
        download: "Изтегляне",
        save: "Запазване",
        cancel: "Отказ",
        delete: "Изтриване",
        edit: "Редактиране",
        submit: "Изпращане",
        close: "Затваряне",
        next: "Следващ",
        previous: "Предишен",
        confirm: "Потвърждение",
        back: "Назад",
      },
      forms: {
        firstName: "Собствено име",
        lastName: "Фамилия",
        email: "Имейл",
        password: "Парола",
        confirmPassword: "Потвърди паролата",
        currentPassword: "Текуща парола",
        newPassword: "Нова парола",
        required: "Задължително",
        optional: "По избор",
        emailPlaceholder: "Въведете имейл адреса си",
        passwordPlaceholder: "Въведете паролата си",
      },
      chatbot: {
        placeholder: "Напишете съобщението си тук...",
        send: "Изпрати",
        newChat: "Нов чат",
        clearHistory: "Изчисти историята",
        typing: "ИИ пише...",
        error: "Съжаляваме, нещо се обърка. Опитайте отново.",
        welcome: "Здравейте! Как мога да ви помогна днес?",
      },
      settings: {
        title: "Настройки",
        account: "Акаунт",
        language: "Език",
        dangerZone: "Опасна зона",
        preferredLanguage: "Предпочитан език",
        saveLanguagePreference: "Запази езиковите предпочитания",
        deleteAccount: "Изтрий акаунта",
        deleteAccountWarning: "Това действие не може да бъде отменено.",
        profile: "Профил",
        security: "Сигурност",
        changePassword: "Промени паролата",
        appearance: "Външен вид",
      },
      errors: {
        somethingWentWrong: "Нещо се обърка",
        tryAgain: "Опитайте отново",
        invalidEmail: "Невалиден имейл адрес",
        passwordTooShort: "Паролата е твърде кратка",
        passwordsDoNotMatch: "Паролите не съвпадат",
        networkError: "Мрежова грешка. Проверете връзката си.",
        unauthorized: "Нямате разрешение за това действие.",
        notFound: "Заявеният ресурс не е намерен.",
      },
      common: {
        loading: "Зарежда се...",
        noData: "Няма налични данни",
        success: "Успех!",
        failed: "Неуспешно",
        welcome: "Добре дошли",
        goodbye: "Довиждане",
        yes: "Да",
        no: "Не",
        ok: "ОК",
        search: "Търсене",
        filter: "Филтър",
        sort: "Сортиране",
        view: "Преглед",
        copy: "Копиране",
        paste: "Поставяне",
        cut: "Изрязване",
      },
      review: {
        pageTitle: "Преглед на документи",
        pageDescription: "Прегледайте документ въз основа на дефиниран от потребителя списък за проверка и база данни с политики.",
        knowledgeBaseTitle: "База знания",
        knowledgeBaseDescription: "Кликнете за избор",
        checklistTitle: "Списък за проверка",
        checklistDescription: "Кликнете за избор",
        customInstructionsTitle: "Персонализирани инструкции (по избор)",
        customInstructionsPlaceholder: "Въведете допълнителни инструкции, които да бъдат взети предвид при отговарянето на въпросите от списъка за проверка...",
        customInstructionsHelp: "{count}/2000 знака. Тези инструкции ще бъдат добавени към всеки въпрос по време на обработката.",
        searchModeHelp: "Векторното търсене предоставя бързи, целенасочени резултати. Анализът на пълния документ изследва цялото съдържание на базата знания.",
        processingFile: "Обработка на файл...",
        processingFiles: "Обработка на файлове...",
        selectKnowledgeBaseTitle: "Изберете база знания",
        selectChecklistTitle: "Изберете списък за проверка",
        noResults: "Все още няма резултати",
        uploadDocuments: "Качете един или повече документи за преглед спрямо избрания списък за проверка",
        results: "Резултати",
        downloadReport: "Изтеглете отчет",
        downloadCsv: "Изтеглете CSV",
        clearResults: "Изчистете резултатите",
        copyReport: "Копирайте отчета",
        reportCopied: "Отчетът е копиран в клипборда!",
        reviewButton: "Преглед",
        consultDocuments: "Консултирайте документи",
        noChecklistsAvailable: "Няма налични списъци за проверка. Създайте първия си списък за проверка, за да започнете.",
        createChecklist: "Създайте списък за проверка",
        editChecklist: "Редактирайте списъка за проверка",
        checklistName: "Име на списъка за проверка",
        checklistNamePlaceholder: "Въведете име на списъка за проверка...",
        checklistDescriptionLabel: "Описание",
        checklistDescriptionPlaceholder: "Въведете описание на списъка за проверка за автоматични предложения за въпроси (поне 10 знака)...",
        questions: "Въпроси",
        suggest: "Предложете",
        suggesting: "Предлагане...",
        optimize: "Оптимизирайте",
        optimizeTooltip: "Трябва да бъде избрана база знания, за да се активира функцията за оптимизация",
        optimizeTooltipEnabled: "Оптимизирайте въпросите въз основа на избраната база знания",
        uploadFiles: "Качете файлове",
        knowledgeBase: "База знания",
        referenceDocuments: "Референтни документи (по избор)",
        selectKnowledgeBasePlaceholder: "Изберете база знания...",
        noKnowledgeBasesAvailable: "Няма налични бази знания. Първо създайте такава, за да използвате тази функция.",
        copyQuestions: "Копирайте въпросите",
        questionsCopied: "Въпросите са копирани в клипборда",
        noQuestionsToCopy: "Няма въпроси за копиране",
        failedToCopyQuestions: "Неуспешно копиране на въпросите в клипборда",
        saveChecklist: "Запазете списъка за проверка",
        cancel: "Отказ",
        deleteChecklist: "Изтрийте списъка за проверка"
      },
    },
  }

  // Croatian
  resources.hr = {
    common: {
      navigation: {
        dashboard: "Nadzorna ploča",
        review: "Pregled",
        generate: "Generiraj",
        compare: "Usporedi",
        match: "Podudaranje",
        modelSelection: "Odabir modela",
        knowledgeBases: "Baze znanja",
        archive: "Arhiv",
        settings: "Postavke",
        admin: "Administrator",
        menu: "Izbornik",
        tools: "Alati",
        configurations: "Konfiguracije",
        myProfile: "Moj profil",
        logout: "Odjava",
        loggedInAs: "Prijavljen kao: {{email}}",
      },
      buttons: {
        upload: "Prenesi",
        download: "Preuzmi",
        save: "Spremi",
        cancel: "Odustani",
        delete: "Obriši",
        edit: "Uredi",
        submit: "Pošalji",
        close: "Zatvori",
        next: "Sljedeći",
        previous: "Prethodni",
        confirm: "Potvrdi",
        back: "Natrag",
      },
      forms: {
        firstName: "Ime",
        lastName: "Prezime",
        email: "E-pošta",
        password: "Lozinka",
        confirmPassword: "Potvrdi lozinku",
        currentPassword: "Trenutna lozinka",
        newPassword: "Nova lozinka",
        required: "Obavezno",
        optional: "Neobavezno",
        emailPlaceholder: "Unesite svoju e-mail adresu",
        passwordPlaceholder: "Unesite svoju lozinku",
      },
      chatbot: {
        placeholder: "Upišite svoju poruku ovdje...",
        send: "Pošalji",
        newChat: "Novi razgovor",
        clearHistory: "Obriši povijest",
        typing: "AI piše...",
        error: "Žao nam je, nešto je pošlo po zlu. Pokušajte ponovno.",
        welcome: "Pozdrav! Kako vam mogu pomoći danas?",
      },
      settings: {
        title: "Postavke",
        account: "Račun",
        language: "Jezik",
        dangerZone: "Opasna zona",
        preferredLanguage: "Preferirani jezik",
        saveLanguagePreference: "Spremi jezične postavke",
        deleteAccount: "Obriši račun",
        deleteAccountWarning: "Ova radnja se ne može poništiti.",
        profile: "Profil",
        security: "Sigurnost",
        changePassword: "Promijeni lozinku",
        appearance: "Izgled",
      },
      errors: {
        somethingWentWrong: "Nešto je pošlo po zlu",
        tryAgain: "Pokušajte ponovno",
        invalidEmail: "Neispravna e-mail adresa",
        passwordTooShort: "Lozinka je prekratka",
        passwordsDoNotMatch: "Lozinke se ne podudaraju",
        networkError: "Mrežna greška. Provjerite vezu.",
        unauthorized: "Nemate ovlasti za ovu radnju.",
        notFound: "Traženi resurs nije pronađen.",
      },
      common: {
        loading: "Učitava se...",
        noData: "Nema dostupnih podataka",
        success: "Uspjeh!",
        failed: "Neuspješno",
        welcome: "Dobrodošli",
        goodbye: "Doviđenja",
        yes: "Da",
        no: "Ne",
        ok: "U redu",
        search: "Pretraži",
        filter: "Filtar",
        sort: "Sortiraj",
        view: "Prikaz",
        copy: "Kopiraj",
        paste: "Zalijepi",
        cut: "Izreži",
      },
      review: {
        pageTitle: "Pregled dokumenata",
        pageDescription: "Pregledajte dokument na temelju korisničke liste provjere i baze podataka politika.",
        knowledgeBaseTitle: "Baza znanja",
        knowledgeBaseDescription: "Kliknite za odabir",
        checklistTitle: "Lista provjere",
        checklistDescription: "Kliknite za odabir",
        customInstructionsTitle: "Prilagođene upute (neobavezno)",
        customInstructionsPlaceholder: "Unesite dodatne upute koje treba razmotriti pri odgovaranju na pitanja liste provjere...",
        customInstructionsHelp: "{count}/2000 znakova. Ove upute će se dodati svakom pitanju tijekom obrade.",
        searchModeHelp: "Vektorska pretraga pruža brze, ciljane rezultate. Analiza cijelog dokumenta istražuje sav sadržaj baze znanja.",
        processingFile: "Obrada datoteke...",
        processingFiles: "Obrada datoteka...",
        selectKnowledgeBaseTitle: "Odaberite bazu znanja",
        selectChecklistTitle: "Odaberite listu provjere",
        noResults: "Još nema rezultata",
        uploadDocuments: "Prenesite jedan ili više dokumenata za pregled u odnosu na odabranu listu provjere",
        results: "Rezultati",
        downloadReport: "Preuzmi izvještaj",
        downloadCsv: "Preuzmi CSV",
        clearResults: "Obriši rezultate",
        copyReport: "Kopiraj izvještaj",
        reportCopied: "Izvještaj je kopiran u međuspremnik!",
        reviewButton: "Pregled",
        consultDocuments: "Konzultiraj dokumente",
        noChecklistsAvailable: "Nema dostupnih lista provjere. Stvorite svoju prvu listu provjere za početak.",
        createChecklist: "Stvori listu provjere",
        editChecklist: "Uredi listu provjere",
        checklistName: "Naziv liste provjere",
        checklistNamePlaceholder: "Unesite naziv liste provjere...",
        checklistDescriptionLabel: "Opis",
        checklistDescriptionPlaceholder: "Unesite opis liste provjere za automatske prijedloge pitanja (najmanje 10 znakova)...",
        questions: "Pitanja",
        suggest: "Predloži",
        suggesting: "Predlažem...",
        optimize: "Optimiziraj",
        optimizeTooltip: "Baza znanja mora biti odabrana da bi se omogućila funkcija optimizacije",
        optimizeTooltipEnabled: "Optimiziraj pitanja na temelju odabrane baze znanja",
        uploadFiles: "Prenesi datoteke",
        knowledgeBase: "Baza znanja",
        referenceDocuments: "Referentni dokumenti (neobavezno)",
        selectKnowledgeBasePlaceholder: "Odaberite bazu znanja...",
        noKnowledgeBasesAvailable: "Nema dostupnih baza znanja. Prvo stvorite jednu da biste koristili ovu funkciju.",
        copyQuestions: "Kopiraj pitanja",
        questionsCopied: "Pitanja su kopirana u međuspremnik",
        noQuestionsToCopy: "Nema pitanja za kopiranje",
        failedToCopyQuestions: "Neuspješno kopiranje pitanja u međuspremnik",
        saveChecklist: "Spremi listu provjere",
        cancel: "Odustani",
        deleteChecklist: "Obriši listu provjere"
      },
    },
  }

  // Serbian
  resources.sr = {
    common: {
      navigation: {
        dashboard: "Контролна табла",
        review: "Преглед",
        generate: "Генериши",
        compare: "Упореди",
        match: "Подударање",
        modelSelection: "Избор модела",
        knowledgeBases: "Базе знања",
        archive: "Архива",
        settings: "Подешавања",
        admin: "Администратор",
        menu: "Мени",
        tools: "Алати",
        configurations: "Конфигурације",
        myProfile: "Мој профил",
        logout: "Одјава",
        loggedInAs: "Пријављен као: {{email}}",
      },
      buttons: {
        upload: "Отпреми",
        download: "Преузми",
        save: "Сачувај",
        cancel: "Откажи",
        delete: "Обриши",
        edit: "Уреди",
        submit: "Пошаљи",
        close: "Затвори",
        next: "Следеће",
        previous: "Претходно",
        confirm: "Потврди",
        back: "Назад",
      },
      forms: {
        firstName: "Име",
        lastName: "Презиме",
        email: "Е-пошта",
        password: "Лозинка",
        confirmPassword: "Потврди лозинку",
        currentPassword: "Тренутна лозинка",
        newPassword: "Нова лозинка",
        required: "Обавезно",
        optional: "Необавезно",
        emailPlaceholder: "Унесите своју е-мејл адресу",
        passwordPlaceholder: "Унесите своју лозинку",
      },
      chatbot: {
        placeholder: "Упишите своју поруку овде...",
        send: "Пошаљи",
        newChat: "Нови разговор",
        clearHistory: "Обриши историју",
        typing: "АИ куца...",
        error: "Жао нам је, нешто је пошло по злу. Покушајте поново.",
        welcome: "Здраво! Како могу да вам помогнем данас?",
      },
      settings: {
        title: "Подешавања",
        account: "Налог",
        language: "Језик",
        dangerZone: "Опасна зона",
        preferredLanguage: "Омиљени језик",
        saveLanguagePreference: "Сачувај језичка подешавања",
        deleteAccount: "Обриши налог",
        deleteAccountWarning: "Ова акција се не може поништити.",
        profile: "Профил",
        security: "Безбедност",
        changePassword: "Промени лозинку",
        appearance: "Изглед",
      },
      errors: {
        somethingWentWrong: "Нешто је пошло по злу",
        tryAgain: "Покушајте поново",
        invalidEmail: "Неисправна е-мејл адреса",
        passwordTooShort: "Лозинка је прекратка",
        passwordsDoNotMatch: "Лозинке се не подударају",
        networkError: "Грешка мреже. Проверите везу.",
        unauthorized: "Немате овлашћења за ову акцију.",
        notFound: "Тражени ресурс није пронађен.",
      },
      common: {
        loading: "Учитава се...",
        noData: "Нема доступних података",
        success: "Успех!",
        failed: "Неуспешно",
        welcome: "Добродошли",
        goodbye: "Довиђења",
        yes: "Да",
        no: "Не",
        ok: "У реду",
        search: "Претрага",
        filter: "Филтер",
        sort: "Сортирај",
        view: "Приказ",
        copy: "Копирај",
        paste: "Налепи",
        cut: "Исеци",
      },
      review: {
        pageTitle: "Преглед докумената",
        pageDescription: "Прегледајте документ на основу корисничке листе провере и базе података политика.",
        knowledgeBaseTitle: "База знања",
        knowledgeBaseDescription: "Кликните за избор",
        checklistTitle: "Листа провере",
        checklistDescription: "Кликните за избор",
        customInstructionsTitle: "Прилагођена упутства (необавезно)",
        customInstructionsPlaceholder: "Унесите додатна упутства која треба размотрити при одговарању на питања листе провере...",
        customInstructionsHelp: "{count}/2000 карактера. Ова упутства ће бити додата сваком питању током обраде.",
        searchModeHelp: "Векторска претрага пружа брзе, циљане резултате. Анализа целог документа истражује сав садржај базе знања.",
        processingFile: "Обрада датотеке...",
        processingFiles: "Обрада датотека...",
        selectKnowledgeBaseTitle: "Изаберите базу знања",
        selectChecklistTitle: "Изаберите листу провере",
        noResults: "Још нема резултата",
        uploadDocuments: "Отпремите један или више докумената за преглед у односу на изабрану листу провере",
        results: "Резултати",
        downloadReport: "Преузми извештај",
        downloadCsv: "Преузми CSV",
        clearResults: "Обриши резултате",
        copyReport: "Копирај извештај",
        reportCopied: "Извештај је копиран у остављач!",
        reviewButton: "Преглед",
        consultDocuments: "Консултуј документе",
        noChecklistsAvailable: "Нема доступних листа провере. Направите своју прву листу провере за почетак.",
        createChecklist: "Направи листу провере",
        editChecklist: "Уреди листу провере",
        checklistName: "Назив листе провере",
        checklistNamePlaceholder: "Унесите назив листе провере...",
        checklistDescriptionLabel: "Опис",
        checklistDescriptionPlaceholder: "Унесите опис листе провере за аутоматске предлоге питања (најмање 10 карактера)...",
        questions: "Питања",
        suggest: "Предложи",
        suggesting: "Предлажем...",
        optimize: "Оптимизуј",
        optimizeTooltip: "База знања мора бити изабрана да би се омогућила функција оптимизације",
        optimizeTooltipEnabled: "Оптимизуј питања на основу изабране базе знања",
        uploadFiles: "Отпреми датотеке",
        knowledgeBase: "База знања",
        referenceDocuments: "Референтни документи (необавезно)",
        selectKnowledgeBasePlaceholder: "Изаберите базу знања...",
        noKnowledgeBasesAvailable: "Нема доступних база знања. Прво направите једну да бисте користили ову функцију.",
        copyQuestions: "Копирај питања",
        questionsCopied: "Питања су копирана у остављач",
        noQuestionsToCopy: "Нема питања за копирање",
        failedToCopyQuestions: "Неуспешно копирање питања у остављач",
        saveChecklist: "Сачувај листу провере",
        cancel: "Откажи",
        deleteChecklist: "Обриши листу провере"
      },
    },
  }

  // Slovenian
  resources.sl = {
    common: {
      navigation: {
        dashboard: "Nadzorna plošča",
        review: "Pregled",
        generate: "Generiraj",
        compare: "Primerjaj",
        match: "Ujemanje",
        modelSelection: "Izbira modela",
        knowledgeBases: "Baze znanja",
        archive: "Arhiv",
        settings: "Nastavitve",
        admin: "Skrbnik",
        menu: "Meni",
        tools: "Orodja",
        configurations: "Konfiguracije",
        myProfile: "Moj profil",
        logout: "Odjava",
        loggedInAs: "Prijavljen kot: {{email}}",
      },
      buttons: {
        upload: "Naloži",
        download: "Prenesi",
        save: "Shrani",
        cancel: "Prekliči",
        delete: "Izbriši",
        edit: "Uredi",
        submit: "Pošlji",
        close: "Zapri",
        next: "Naslednji",
        previous: "Prejšnji",
        confirm: "Potrdi",
        back: "Nazaj",
      },
      forms: {
        firstName: "Ime",
        lastName: "Priimek",
        email: "E-pošta",
        password: "Geslo",
        confirmPassword: "Potrdi geslo",
        currentPassword: "Trenutno geslo",
        newPassword: "Novo geslo",
        required: "Obvezno",
        optional: "Neobvezno",
        emailPlaceholder: "Vnesite svoj e-poštni naslov",
        passwordPlaceholder: "Vnesite svoje geslo",
      },
      chatbot: {
        placeholder: "Vnesite svoje sporočilo tukaj...",
        send: "Pošlji",
        newChat: "Nov klepet",
        clearHistory: "Počisti zgodovino",
        typing: "AI tipka...",
        error: "Oprostite, nekaj je šlo narobe. Poskusite znova.",
        welcome: "Pozdravljeni! Kako vam lahko danes pomagam?",
      },
      settings: {
        title: "Nastavitve",
        account: "Račun",
        language: "Jezik",
        dangerZone: "Nevarna cona",
        preferredLanguage: "Prednostni jezik",
        saveLanguagePreference: "Shrani jezikovne nastavitve",
        deleteAccount: "Izbriši račun",
        deleteAccountWarning: "Tega dejanja ni mogoče razveljaviti.",
        profile: "Profil",
        security: "Varnost",
        changePassword: "Spremeni geslo",
        appearance: "Videz",
      },
      errors: {
        somethingWentWrong: "Nekaj je šlo narobe",
        tryAgain: "Poskusite znova",
        invalidEmail: "Neveljaven e-poštni naslov",
        passwordTooShort: "Geslo je prekratko",
        passwordsDoNotMatch: "Gesli se ne ujemata",
        networkError: "Omrežna napaka. Preverite povezavo.",
        unauthorized: "Nimate dovoljenja za to dejanje.",
        notFound: "Zahtevani vir ni bil najden.",
      },
      common: {
        loading: "Nalaganje...",
        noData: "Ni razpoložljivih podatkov",
        success: "Uspeh!",
        failed: "Neuspešno",
        welcome: "Dobrodošli",
        goodbye: "Nasvidenje",
        yes: "Da",
        no: "Ne",
        ok: "V redu",
        search: "Iskanje",
        filter: "Filter",
        sort: "Razvrsti",
        view: "Ogled",
        copy: "Kopiraj",
        paste: "Prilepi",
        cut: "Izreži",
      },
      review: {
        pageTitle: "Pregled dokumentov",
        pageDescription: "Preglejte dokument na podlagi uporabniško definirane kontrolne liste in baze podatkov politik.",
        knowledgeBaseTitle: "Baza znanja",
        knowledgeBaseDescription: "Kliknite za izbiro",
        checklistTitle: "Kontrolna lista",
        checklistDescription: "Kliknite za izbiro",
        customInstructionsTitle: "Prilagojene navodila (neobvezno)",
        customInstructionsPlaceholder: "Vnesite dodatna navodila, ki jih je treba upoštevati pri odgovarjanju na vprašanja kontrolne liste...",
        customInstructionsHelp: "{count}/2000 znakov. Ta navodila bodo dodana vsakemu vprašanju med obdelavo.",
        searchModeHelp: "Vektorsko iskanje zagotavlja hitre, ciljne rezultate. Analiza celotnega dokumenta raziskuje vso vsebino baze znanja.",
        processingFile: "Obdelava datoteke...",
        processingFiles: "Obdelava datotek...",
        selectKnowledgeBaseTitle: "Izberite bazo znanja",
        selectChecklistTitle: "Izberite kontrolno listo",
        noResults: "Še ni rezultatov",
        uploadDocuments: "Naložite enega ali več dokumentov za pregled glede na izbrano kontrolno listo",
        results: "Rezultati",
        downloadReport: "Prenesi poročilo",
        downloadCsv: "Prenesi CSV",
        clearResults: "Počisti rezultate",
        copyReport: "Kopiraj poročilo",
        reportCopied: "Poročilo je kopirano v odložišče!",
        reviewButton: "Pregled",
        consultDocuments: "Posvetuj se z dokumenti",
        noChecklistsAvailable: "Na voljo ni nobenih kontrolnih list. Ustvarite svojo prvo kontrolno listo za začetek.",
        createChecklist: "Ustvari kontrolno listo",
        editChecklist: "Uredi kontrolno listo",
        checklistName: "Ime kontrolne liste",
        checklistNamePlaceholder: "Vnesite ime kontrolne liste...",
        checklistDescriptionLabel: "Opis",
        checklistDescriptionPlaceholder: "Vnesite opis kontrolne liste za samodejne predloge vprašanj (najmanj 10 znakov)...",
        questions: "Vprašanja",
        suggest: "Predlagaj",
        suggesting: "Predlagam...",
        optimize: "Optimiziraj",
        optimizeTooltip: "Baza znanja mora biti izbrana za omogočitev funkcije optimizacije",
        optimizeTooltipEnabled: "Optimiziraj vprašanja na podlagi izbrane baze znanja",
        uploadFiles: "Naloži datoteke",
        knowledgeBase: "Baza znanja",
        referenceDocuments: "Referenčni dokumenti (neobvezno)",
        selectKnowledgeBasePlaceholder: "Izberite bazo znanja...",
        noKnowledgeBasesAvailable: "Na voljo ni nobenih baz znanja. Najprej ustvarite eno za uporabo te funkcije.",
        copyQuestions: "Kopiraj vprašanja",
        questionsCopied: "Vprašanja so kopirana v odložišče",
        noQuestionsToCopy: "Ni vprašanj za kopiranje",
        failedToCopyQuestions: "Kopiranje vprašanj v odložišče ni uspelo",
        saveChecklist: "Shrani kontrolno listo",
        cancel: "Prekliči",
        deleteChecklist: "Izbriši kontrolno listo"
      },
    },
  }

  // Add Model Selection translations to Czech
  resources.cs.common.modelSelection = {
    llmManagement: "Správa LLM",
    llmDescription: "Nakonfigurujte a spravujte LLM používané pro generování textových odpovědí. Výchozí model bude použit pro všechny operace.",
    addNewLlm: "Přidat nový LLM",
    noLlmsConfigured: "Žádné LLM nejsou nakonfigurovány",
    addNewLlmToGetStarted: "Přidejte nový LLM a začněte",
    embeddingModelManagement: "Správa embedding modelů",
    embeddingDescription: "Nakonfigurujte a spravujte embedding modely používané pro indexování a vyhledávání ve znalostních bázích. Výchozí model bude použit při vytváření nových znalostních bází, ale každá znalostní báze bude nadále používat svůj původní embedding model, i když se výchozí později změní.",
    addEmbeddingModel: "Přidat embedding model",
    noEmbeddingModelsConfigured: "Žádné embedding modely nejsou nakonfigurovány",
    addNewEmbeddingModelToGetStarted: "Přidejte nový embedding model a začněte",
    tableHeaders: {
      name: "Název",
      modelId: "ID modelu",
      provider: "Poskytovatel",
      description: "Popis",
      status: "Stav",
      actions: "Akce"
    },
    status: {
      default: "Výchozí",
      available: "Dostupný"
    },
    actions: {
      setAsDefault: "Nastavit jako výchozí",
      delete: "Smazat",
      validate: "Ověřit",
      validating: "Ověřování"
    },
    dialog: {
      addNewLlm: "Přidat nový LLM",
      addEmbeddingModel: "Přidat embedding model",
      displayName: "Zobrazovaný název",
      provider: "Poskytovatel",
      modelId: "ID modelu",
      description: "Popis",
      cancel: "Zrušit",
      addModel: "Přidat model"
    },
    placeholders: {
      customModel: "např., Můj vlastní model",
      embeddingModelId: "např., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Popište model, jeho charakteristiky a kdy jej použít"
    },
    validation: {
      pleaseEnterModelId: "Zadejte prosím ID modelu"
    }
  }

  // Add Model Selection translations to Slovak
  resources.sk.common.modelSelection = {
    llmManagement: "Správa LLM",
    llmDescription: "Nakonfigurujte a spravujte LLM používané na generovanie textových odpovedí. Predvolený model sa použije pre všetky operácie.",
    addNewLlm: "Pridať nový LLM",
    noLlmsConfigured: "Žiadne LLM nie sú nakonfigurované",
    addNewLlmToGetStarted: "Pridajte nový LLM a začnite",
    embeddingModelManagement: "Správa embedding modelov",
    embeddingDescription: "Nakonfigurujte a spravujte embedding modely používané na indexovanie a vyhľadávanie v znalostných bázach. Predvolený model sa použije pri vytváraní nových znalostných báz, ale každá znalostná báza bude naďalej používať svoj pôvodný embedding model, aj keď sa predvolený neskôr zmení.",
    addEmbeddingModel: "Pridať embedding model",
    noEmbeddingModelsConfigured: "Žiadne embedding modely nie sú nakonfigurované",
    addNewEmbeddingModelToGetStarted: "Pridajte nový embedding model a začnite",
    tableHeaders: {
      name: "Názov",
      modelId: "ID modelu",
      provider: "Poskytovateľ",
      description: "Popis",
      status: "Stav",
      actions: "Akcie"
    },
    status: {
      default: "Predvolený",
      available: "Dostupný"
    },
    actions: {
      setAsDefault: "Nastaviť ako predvolený",
      delete: "Odstrániť",
      validate: "Overiť",
      validating: "Overovanie"
    },
    dialog: {
      addNewLlm: "Pridať nový LLM",
      addEmbeddingModel: "Pridať embedding model",
      displayName: "Zobrazovaný názov",
      provider: "Poskytovateľ",
      modelId: "ID modelu",
      description: "Popis",
      cancel: "Zrušiť",
      addModel: "Pridať model"
    },
    placeholders: {
      customModel: "napr., Môj vlastný model",
      embeddingModelId: "napr., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Opíšte model, jeho charakteristiky a kedy ho použiť"
    },
    validation: {
      pleaseEnterModelId: "Zadajte prosím ID modelu"
    }
  }

  // Add Model Selection translations to Hungarian
  resources.hu.common.modelSelection = {
    llmManagement: "LLM Kezelés",
    llmDescription: "Konfigurálja és kezelje a szövegválaszok generálásához használt LLM-eket. Az alapértelmezett modell minden művelethez használva lesz.",
    addNewLlm: "Új LLM hozzáadása",
    noLlmsConfigured: "Nincsenek konfigurált LLM-ek",
    addNewLlmToGetStarted: "Adjon hozzá egy új LLM-et a kezdéshez",
    embeddingModelManagement: "Beágyazási modell kezelés",
    embeddingDescription: "Konfigurálja és kezelje a tudásbázis indexeléshez és lekérdezéshez használt beágyazási modelleket. Az alapértelmezett modell az új tudásbázisok létrehozásakor lesz használva, de minden tudásbázis továbbra is az eredeti beágyazási modelljét fogja használni, még akkor is, ha az alapértelmezett később megváltozik.",
    addEmbeddingModel: "Beágyazási modell hozzáadása",
    noEmbeddingModelsConfigured: "Nincsenek konfigurált beágyazási modellek",
    addNewEmbeddingModelToGetStarted: "Adjon hozzá egy új beágyazási modellt a kezdéshez",
    tableHeaders: {
      name: "Név",
      modelId: "Modell ID",
      provider: "Szolgáltató",
      description: "Leírás",
      status: "Állapot",
      actions: "Műveletek"
    },
    status: {
      default: "Alapértelmezett",
      available: "Elérhető"
    },
    actions: {
      setAsDefault: "Beállítás alapértelmezettként",
      delete: "Törlés",
      validate: "Validálás",
      validating: "Validálás folyamatban"
    },
    dialog: {
      addNewLlm: "Új LLM hozzáadása",
      addEmbeddingModel: "Beágyazási modell hozzáadása",
      displayName: "Megjelenített név",
      provider: "Szolgáltató",
      modelId: "Modell ID",
      description: "Leírás",
      cancel: "Mégse",
      addModel: "Modell hozzáadása"
    },
    placeholders: {
      customModel: "pl., Saját egyéni modell",
      embeddingModelId: "pl., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Írja le a modellt, jellemzőit és mikor használja"
    },
    validation: {
      pleaseEnterModelId: "Kérjük, adjon meg egy modell ID-t"
    }
  }

  // Add Model Selection translations to Romanian
  resources.ro.common.modelSelection = {
    llmManagement: "Gestionarea LLM",
    llmDescription: "Configurați și gestionați LLM-urile folosite pentru generarea răspunsurilor text. Modelul implicit va fi folosit pentru toate operațiunile.",
    addNewLlm: "Adăugați LLM nou",
    noLlmsConfigured: "Nu sunt configurate LLM-uri",
    addNewLlmToGetStarted: "Adăugați un LLM nou pentru a începe",
    embeddingModelManagement: "Gestionarea modelelor de încorporare",
    embeddingDescription: "Configurați și gestionați modelele de încorporare folosite pentru indexarea și recuperarea bazelor de cunoștințe. Modelul implicit va fi folosit la crearea de noi baze de cunoștințe, dar fiecare bază de cunoștințe va continua să folosească modelul său original de încorporare chiar dacă implicit se schimbă mai târziu.",
    addEmbeddingModel: "Adăugați model de încorporare",
    noEmbeddingModelsConfigured: "Nu sunt configurate modele de încorporare",
    addNewEmbeddingModelToGetStarted: "Adăugați un model nou de încorporare pentru a începe",
    tableHeaders: {
      name: "Nume",
      modelId: "ID Model",
      provider: "Furnizor",
      description: "Descriere",
      status: "Stare",
      actions: "Acțiuni"
    },
    status: {
      default: "Implicit",
      available: "Disponibil"
    },
    actions: {
      setAsDefault: "Setează ca implicit",
      delete: "Șterge",
      validate: "Validează",
      validating: "Se validează"
    },
    dialog: {
      addNewLlm: "Adăugați LLM nou",
      addEmbeddingModel: "Adăugați model de încorporare",
      displayName: "Nume afișat",
      provider: "Furnizor",
      modelId: "ID Model",
      description: "Descriere",
      cancel: "Anulează",
      addModel: "Adăugați model"
    },
    placeholders: {
      customModel: "ex., Modelul meu personalizat",
      embeddingModelId: "ex., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Descrieți modelul, caracteristicile sale și când să îl folosiți"
    },
    validation: {
      pleaseEnterModelId: "Vă rugăm să introduceți un ID de model"
    }
  }

  // Add Model Selection translations to Bulgarian
  resources.bg.common.modelSelection = {
    llmManagement: "Управление на LLM",
    llmDescription: "Конфигурирайте и управлявайте LLM, използвани за генериране на текстови отговори. Моделът по подразбиране ще се използва за всички операции.",
    addNewLlm: "Добавяне на нов LLM",
    noLlmsConfigured: "Няма конфигурирани LLM",
    addNewLlmToGetStarted: "Добавете нов LLM, за да започнете",
    embeddingModelManagement: "Управление на модели за вграждане",
    embeddingDescription: "Конфигурирайте и управлявайте модели за вграждане, използвани за индексиране и извличане на бази от знания. Моделът по подразбиране ще се използва при създаване на нови бази от знания, но всяка база от знания ще продължи да използва своя оригинален модел за вграждане, дори ако по-късно се промени този по подразбиране.",
    addEmbeddingModel: "Добавяне на модел за вграждане",
    noEmbeddingModelsConfigured: "Няма конфигурирани модели за вграждане",
    addNewEmbeddingModelToGetStarted: "Добавете нов модел за вграждане, за да започнете",
    tableHeaders: {
      name: "Име",
      modelId: "ID на модел",
      provider: "Доставчик",
      description: "Описание",
      status: "Състояние",
      actions: "Действия"
    },
    status: {
      default: "По подразбиране",
      available: "Достъпен"
    },
    actions: {
      setAsDefault: "Задай като по подразбиране",
      delete: "Изтрий",
      validate: "Валидирай",
      validating: "Валидиране"
    },
    dialog: {
      addNewLlm: "Добавяне на нов LLM",
      addEmbeddingModel: "Добавяне на модел за вграждане",
      displayName: "Показвано име",
      provider: "Доставчик",
      modelId: "ID на модел",
      description: "Описание",
      cancel: "Отказ",
      addModel: "Добавяне на модел"
    },
    placeholders: {
      customModel: "напр., Моят персонализиран модел",
      embeddingModelId: "напр., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Опишете модела, неговите характеристики и кога да го използвате"
    },
    validation: {
      pleaseEnterModelId: "Моля, въведете ID на модел"
    }
  }

  // Add Model Selection translations to Croatian
  resources.hr.common.modelSelection = {
    llmManagement: "Upravljanje LLM-ovima",
    llmDescription: "Konfigurirajte i upravljajte LLM-ovima koji se koriste za generiranje tekstualnih odgovora. Zadani model će se koristiti za sve operacije.",
    addNewLlm: "Dodaj novi LLM",
    noLlmsConfigured: "Nema konfiguriranih LLM-ova",
    addNewLlmToGetStarted: "Dodajte novi LLM za početak",
    embeddingModelManagement: "Upravljanje modelima ugrađivanja",
    embeddingDescription: "Konfigurirajte i upravljajte modelima ugrađivanja koji se koriste za indeksiranje i dohvaćanje baza znanja. Zadani model će se koristiti pri stvaranju novih baza znanja, ali svaka baza znanja će i dalje koristiti svoj izvorni model ugrađivanja čak i ako se zadani kasnije promijeni.",
    addEmbeddingModel: "Dodaj model ugrađivanja",
    noEmbeddingModelsConfigured: "Nema konfiguriranih modela ugrađivanja",
    addNewEmbeddingModelToGetStarted: "Dodajte novi model ugrađivanja za početak",
    tableHeaders: {
      name: "Ime",
      modelId: "ID modela",
      provider: "Pružatelj usluge",
      description: "Opis",
      status: "Status",
      actions: "Radnje"
    },
    status: {
      default: "Zadani",
      available: "Dostupan"
    },
    actions: {
      setAsDefault: "Postavi kao zadani",
      delete: "Obriši",
      validate: "Potvrdi",
      validating: "Potvrđivanje"
    },
    dialog: {
      addNewLlm: "Dodaj novi LLM",
      addEmbeddingModel: "Dodaj model ugrađivanja",
      displayName: "Prikazno ime",
      provider: "Pružatelj usluge",
      modelId: "ID modela",
      description: "Opis",
      cancel: "Otkaži",
      addModel: "Dodaj model"
    },
    placeholders: {
      customModel: "npr., Moj prilagođeni model",
      embeddingModelId: "npr., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Opišite model, njegove karakteristike i kada ga koristiti"
    },
    validation: {
      pleaseEnterModelId: "Molimo unesite ID modela"
    }
  }

  // Add Model Selection translations to Serbian
  resources.sr.common.modelSelection = {
    llmManagement: "Управљање LLM-овима",
    llmDescription: "Конфигуришите и управљајте LLM-овима који се користе за генерисање текстуалних одговора. Подразумевани модел ће се користити за све операције.",
    addNewLlm: "Додај нови LLM",
    noLlmsConfigured: "Нема конфигурисаних LLM-ова",
    addNewLlmToGetStarted: "Додајте нови LLM за почетак",
    embeddingModelManagement: "Управљање моделима уграђивања",
    embeddingDescription: "Конфигуришите и управљајте моделима уграђивања који се користе за индексирање и дохватање база знања. Подразумевани модел ће се користити при стварању нових база знања, али свака база знања ће и даље користити свој изворни модел уграђивања чак и ако се подразумевани касније промени.",
    addEmbeddingModel: "Додај модел уграђивања",
    noEmbeddingModelsConfigured: "Нема конфигурисаних модела уграђивања",
    addNewEmbeddingModelToGetStarted: "Додајте нови модел уграђивања за почетак",
    tableHeaders: {
      name: "Име",
      modelId: "ИД модела",
      provider: "Пружалац услуге",
      description: "Опис",
      status: "Статус",
      actions: "Радње"
    },
    status: {
      default: "Подразумевани",
      available: "Доступан"
    },
    actions: {
      setAsDefault: "Постави као подразумевани",
      delete: "Обриши",
      validate: "Потврди",
      validating: "Потврђивање"
    },
    dialog: {
      addNewLlm: "Додај нови LLM",
      addEmbeddingModel: "Додај модел уграђивања",
      displayName: "Приказно име",
      provider: "Пружалац услуге",
      modelId: "ИД модела",
      description: "Опис",
      cancel: "Откажи",
      addModel: "Додај модел"
    },
    placeholders: {
      customModel: "нпр., Мој прилагођени модел",
      embeddingModelId: "нпр., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Опишите модел, његове карактеристике и када га користити"
    },
    validation: {
      pleaseEnterModelId: "Молимо унесите ИД модела"
    }
  }

  // Add Model Selection translations to Slovenian
  resources.sl.common.modelSelection = {
    llmManagement: "Upravljanje LLM",
    llmDescription: "Konfigurirajte in upravljajte LLM, ki se uporabljajo za generiranje besedilnih odgovorov. Privzeti model bo uporabljen za vse operacije.",
    addNewLlm: "Dodaj nov LLM",
    noLlmsConfigured: "Ni konfiguriranih LLM-jev",
    addNewLlmToGetStarted: "Dodajte nov LLM za začetek",
    embeddingModelManagement: "Upravljanje modelov vgrajevanja",
    embeddingDescription: "Konfigurirajte in upravljajte modele vgrajevanja, ki se uporabljajo za indeksiranje in pridobivanje baz znanja. Privzeti model bo uporabljen pri ustvarjanju novih baz znanja, vendar bo vsaka baza znanja še naprej uporabljala svoj izvirni model vgrajevanja, tudi če se privzeti pozneje spremeni.",
    addEmbeddingModel: "Dodaj model vgrajevanja",
    noEmbeddingModelsConfigured: "Ni konfiguriranih modelov vgrajevanja",
    addNewEmbeddingModelToGetStarted: "Dodajte nov model vgrajevanja za začetek",
    tableHeaders: {
      name: "Ime",
      modelId: "ID modela",
      provider: "Ponudnik",
      description: "Opis",
      status: "Status",
      actions: "Dejanja"
    },
    status: {
      default: "Privzeti",
      available: "Na voljo"
    },
    actions: {
      setAsDefault: "Nastavi kot privzeti",
      delete: "Izbriši",
      validate: "Potrdi",
      validating: "Potrjevanje"
    },
    dialog: {
      addNewLlm: "Dodaj nov LLM",
      addEmbeddingModel: "Dodaj model vgrajevanja",
      displayName: "Prikazno ime",
      provider: "Ponudnik",
      modelId: "ID modela",
      description: "Opis",
      cancel: "Prekliči",
      addModel: "Dodaj model"
    },
    placeholders: {
      customModel: "npr., Moj prilagojen model",
      embeddingModelId: "npr., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Opišite model, njegove značilnosti in kdaj ga uporabiti"
    },
    validation: {
      pleaseEnterModelId: "Prosimo, vnesite ID modela"
    }
  }

  // Add Knowledge Bases translations for Central European languages
  
  // Czech
  if (!resources.cs.common.knowledgeBases) {
    resources.cs.common.knowledgeBases = {
      title: "Znalostní báze",
      description: "Spravujte a organizujte své dokumenty do znalostních bází pro efektivní AI-podporované interakce.",
      createNew: "Vytvořit novou znalostní bázi",
      noKnowledgeBases: "Zatím nebyla vytvořena žádná znalostní báze",
      getStarted: "Vytvořte svou první znalostní bázi a začněte",
      tableHeaders: {
        name: "Název",
        description: "Popis",
        documents: "Dokumenty",
        createdAt: "Vytvořeno",
        actions: "Akce"
      },
      actions: {
        view: "Zobrazit",
        edit: "Upravit",
        delete: "Smazat",
        configure: "Konfigurovat"
      },
      dialog: {
        createNew: "Vytvořit novou znalostní bázi",
        editKnowledgeBase: "Upravit znalostní bázi",
        name: "Název",
        description: "Popis",
        cancel: "Zrušit",
        create: "Vytvořit",
        save: "Uložit"
      },
      placeholders: {
        knowledgeBaseName: "např., Firemní zásady",
        knowledgeBaseDescription: "Popište, co tato znalostní báze obsahuje a její účel"
      },
      validation: {
        pleaseEnterName: "Zadejte prosím název znalostní báze"
      }
    }
  }

  // Slovak
  if (!resources.sk.common.knowledgeBases) {
    resources.sk.common.knowledgeBases = {
      title: "Znalostné bázy",
      description: "Spravujte a organizujte svoje dokumenty do znalostných báz pre efektívne AI-podporované interakcie.",
      createNew: "Vytvoriť novú znalostnú bázu",
      noKnowledgeBases: "Zatiaľ nebola vytvorená žiadna znalostná báza",
      getStarted: "Vytvorte svoju prvú znalostnú bázu a začnite",
      tableHeaders: {
        name: "Názov",
        description: "Popis",
        documents: "Dokumenty",
        createdAt: "Vytvorené",
        actions: "Akcie"
      },
      actions: {
        view: "Zobraziť",
        edit: "Upraviť",
        delete: "Zmazať",
        configure: "Konfigurovať"
      },
      dialog: {
        createNew: "Vytvoriť novú znalostnú bázu",
        editKnowledgeBase: "Upraviť znalostnú bázu",
        name: "Názov",
        description: "Popis",
        cancel: "Zrušiť",
        create: "Vytvoriť",
        save: "Uložiť"
      },
      placeholders: {
        knowledgeBaseName: "napr., Firemné zásady",
        knowledgeBaseDescription: "Opíšte, čo táto znalostná báza obsahuje a jej účel"
      },
      validation: {
        pleaseEnterName: "Zadajte prosím názov znalostnej bázy"
      }
    }
  }

  // Hungarian
  if (!resources.hu.common.knowledgeBases) {
    resources.hu.common.knowledgeBases = {
      title: "Tudásbázisok",
      description: "Kezelje és rendezze dokumentumait tudásbázisokban a hatékony AI-támogatott interakciókhoz.",
      createNew: "Új tudásbázis létrehozása",
      noKnowledgeBases: "Még nem lett tudásbázis létrehozva",
      getStarted: "Hozza létre az első tudásbázisát a kezdéshez",
      tableHeaders: {
        name: "Név",
        description: "Leírás",
        documents: "Dokumentumok",
        createdAt: "Létrehozva",
        actions: "Műveletek"
      },
      actions: {
        view: "Megtekintés",
        edit: "Szerkesztés",
        delete: "Törlés",
        configure: "Konfigurálás"
      },
      dialog: {
        createNew: "Új tudásbázis létrehozása",
        editKnowledgeBase: "Tudásbázis szerkesztése",
        name: "Név",
        description: "Leírás",
        cancel: "Mégse",
        create: "Létrehozás",
        save: "Mentés"
      },
      placeholders: {
        knowledgeBaseName: "pl., Vállalati irányelvek",
        knowledgeBaseDescription: "Írja le, mit tartalmaz ez a tudásbázis és mi a célja"
      },
      validation: {
        pleaseEnterName: "Kérjük, adjon meg egy nevet a tudásbázisnak"
      }
    }
  }

  // Romanian
  if (!resources.ro.common.knowledgeBases) {
    resources.ro.common.knowledgeBases = {
      title: "Baze de cunoștințe",
      description: "Gestionați și organizați documentele dvs. în baze de cunoștințe pentru interacțiuni eficiente asistate de AI.",
      createNew: "Creați o nouă bază de cunoștințe",
      noKnowledgeBases: "Încă nu a fost creată nicio bază de cunoștințe",
      getStarted: "Creați prima dvs. bază de cunoștințe pentru a începe",
      tableHeaders: {
        name: "Nume",
        description: "Descriere",
        documents: "Documente",
        createdAt: "Creat",
        actions: "Acțiuni"
      },
      actions: {
        view: "Vizualizare",
        edit: "Editare",
        delete: "Ștergere",
        configure: "Configurare"
      },
      dialog: {
        createNew: "Creați o nouă bază de cunoștințe",
        editKnowledgeBase: "Editați baza de cunoștințe",
        name: "Nume",
        description: "Descriere",
        cancel: "Anulare",
        create: "Creare",
        save: "Salvare"
      },
      placeholders: {
        knowledgeBaseName: "ex., Politici companiei",
        knowledgeBaseDescription: "Descrieți ce conține această bază de cunoștințe și scopul său"
      },
      validation: {
        pleaseEnterName: "Vă rugăm să introduceți un nume pentru baza de cunoștințe"
      }
    }
  }

  // Bulgarian
  if (!resources.bg.common.knowledgeBases) {
    resources.bg.common.knowledgeBases = {
      title: "Бази знания",
      description: "Управлявайте и организирайте документите си в бази знания за ефективни AI-подпомогнати взаимодействия.",
      createNew: "Създайте нова база знания",
      noKnowledgeBases: "Все още не са създадени бази знания",
      getStarted: "Създайте първата си база знания, за да започнете",
      tableHeaders: {
        name: "Име",
        description: "Описание",
        documents: "Документи",
        createdAt: "Създадено",
        actions: "Действия"
      },
      actions: {
        view: "Преглед",
        edit: "Редактиране",
        delete: "Изтриване",
        configure: "Конфигуриране"
      },
      dialog: {
        createNew: "Създайте нова база знания",
        editKnowledgeBase: "Редактирайте база знания",
        name: "Име",
        description: "Описание",
        cancel: "Отказ",
        create: "Създаване",
        save: "Запазване"
      },
      placeholders: {
        knowledgeBaseName: "напр., Политики на компанията",
        knowledgeBaseDescription: "Опишете какво съдържа тази база знания и нейната цел"
      },
      validation: {
        pleaseEnterName: "Моля, въведете име за базата знания"
      }
    }
  }

  // Croatian
  if (!resources.hr.common.knowledgeBases) {
    resources.hr.common.knowledgeBases = {
      title: "Baze znanja",
      description: "Upravljajte i organizirajte svoje dokumente u bazama znanja za učinkovite AI-podržane interakcije.",
      createNew: "Stvorite novu bazu znanja",
      noKnowledgeBases: "Još nisu stvorene baze znanja",
      getStarted: "Stvorite svoju prvu bazu znanja za početak",
      tableHeaders: {
        name: "Ime",
        description: "Opis",
        documents: "Dokumenti",
        createdAt: "Stvoreno",
        actions: "Radnje"
      },
      actions: {
        view: "Prikaži",
        edit: "Uredi",
        delete: "Obriši",
        configure: "Konfiguriraj"
      },
      dialog: {
        createNew: "Stvorite novu bazu znanja",
        editKnowledgeBase: "Uređivanje baze znanja",
        name: "Ime",
        description: "Opis",
        cancel: "Otkaži",
        create: "Stvori",
        save: "Spremi"
      },
      placeholders: {
        knowledgeBaseName: "npr., Pravila tvrtke",
        knowledgeBaseDescription: "Opišite što sadrži ova baza znanja i njezinu svrhu"
      },
      validation: {
        pleaseEnterName: "Molimo unesite ime za bazu znanja"
      }
    }
  }

  // Serbian
  if (!resources.sr.common.knowledgeBases) {
    resources.sr.common.knowledgeBases = {
      title: "Базе знања",
      description: "Управљајте и организујте своје документе у базама знања за ефикасне АИ-подржане интеракције.",
      createNew: "Направите нову базу знања",
      noKnowledgeBases: "Још увек нису направљене базе знања",
      getStarted: "Направите своју прву базу знања да почнете",
      tableHeaders: {
        name: "Име",
        description: "Опис",
        documents: "Документи",
        createdAt: "Направљено",
        actions: "Радње"
      },
      actions: {
        view: "Прикажи",
        edit: "Уреди",
        delete: "Обриши",
        configure: "Конфигуриши"
      },
      dialog: {
        createNew: "Направите нову базу знања",
        editKnowledgeBase: "Уређивање базе знања",
        name: "Име",
        description: "Опис",
        cancel: "Откажи",
        create: "Направи",
        save: "Сачувај"
      },
      placeholders: {
        knowledgeBaseName: "нпр., Правила компаније",
        knowledgeBaseDescription: "Опишите шта садржи ова база знања и њену сврху"
      },
      validation: {
        pleaseEnterName: "Молимо унесите име за базу знања"
      }
    }
  }

  // Slovenian
  if (!resources.sl.common.knowledgeBases) {
    resources.sl.common.knowledgeBases = {
      title: "Baze znanja",
      description: "Upravljajte in organizirajte svoje dokumente v bazah znanja za učinkovite AI-podprte interakcije.",
      createNew: "Ustvarite novo bazo znanja",
      noKnowledgeBases: "Še niso bile ustvarjene baze znanja",
      getStarted: "Ustvarite svojo prvo bazo znanja za začetek",
      tableHeaders: {
        name: "Ime",
        description: "Opis",
        documents: "Dokumenti",
        createdAt: "Ustvarjeno",
        actions: "Dejanja"
      },
      actions: {
        view: "Prikaži",
        edit: "Uredi",
        delete: "Izbriši",
        configure: "Konfiguriraj"
      },
      dialog: {
        createNew: "Ustvarite novo bazo znanja",
        editKnowledgeBase: "Urejanje baze znanja",
        name: "Ime",
        description: "Opis",
        cancel: "Prekliči",
        create: "Ustvari",
        save: "Shrani"
      },
      placeholders: {
        knowledgeBaseName: "npr., Pravila podjetja",
        knowledgeBaseDescription: "Opišite, kaj vsebuje ta baza znanja in njen namen"
      },
      validation: {
        pleaseEnterName: "Prosimo, vnesite ime za bazo znanja"
      }
    }
  }
}
