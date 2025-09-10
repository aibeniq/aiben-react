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
        welcomeBack: "Vítejte zpět, je hezké vás znovu vidět!",
        hiUser: "Ahoj, {{name}} 👋",
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
        allUsersToggleTooltip: "Přepínat mezi zobrazením pouze vaší historie nebo historie všech uživatelů",
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
      compare: {
        title: "Porovnat dokumenty",
        subtitle: "Vyberte dva dokumenty k porovnání",
        selectFirstDocument: "Vybrat první dokument",
        selectSecondDocument: "Vybrat druhý dokument",
        pleaseSelect: "Prosím vyberte...",
        documentA: "Dokument A",
        documentB: "Dokument B",
        compareDocuments: "Porovnat dokumenty",
        comparison: "Porovnání",
        noDocumentsFound: "Nebyly nalezeny žádné dokumenty",
        selectTwoDocuments: "Prosím vyberte dva dokumenty k porovnání",
        loadingComparison: "Načítání porovnání...",
        topicList: "Seznam témat",
        clickToBrowse: "Klikněte pro procházení nebo přetáhněte",
        supportedFormats: "Podporované formáty: PDF, TXT, DOCX",
        analysisType: "Typ analýzy",
        quickAnalysis: "Rychlá analýza",
        detailedAnalysis: "Podrobná analýza",
        comprehensiveAnalysis: "Komplexní analýza",
        analysisDepth: "Hloubka analýzy",
        surfaceLevel: "Povrchová úroveň",
        moderate: "Střední",
        deep: "Hluboká",
        veryDeep: "Velmi hluboká",
        editTopicList: "Upravit seznam témat"
      },
      match: {
        title: "Párování dokumentů",
        subtitle: "Najít podobné dokumenty na základě obsahu",
        selectDocument: "Vyberte dokument pro hledání shod",
        pleaseSelect: "Prosím vyberte dokument...",
        sourceDocument: "Zdrojový dokument",
        matchingDocuments: "Odpovídající dokumenty",
        findMatches: "Najít shody",
        similarityScore: "Skóre podobnosti",
        noDocumentsFound: "Nebyly nalezeny žádné dokumenty",
        selectDocumentToMatch: "Prosím vyberte dokument pro hledání shod",
        loadingMatches: "Hledání shod...",
        noMatchesFound: "Nebyly nalezeny žádné podobné dokumenty",
        matchResults: "Výsledky párování",
        similarity: "Podobnost",
        matchingCriteria: "Kritéria párování",
        semanticSimilarity: "Sémantická podobnost",
        keywordMatching: "Párování klíčových slov",
        structuralSimilarity: "Strukturální podobnost",
        threshold: "Prahová hodnota",
        minimumSimilarity: "Minimální podobnost",
        searchDepth: "Hloubka vyhledávání",
        maxResults: "Maximální počet výsledků",
        editFormTemplate: "Upravit šablonu formuláře"
      },
      knowledgeBases: {
        title: "Správa znalostních bází",
        addKnowledgeBase: "Přidat znalostní bázi",
        emptyStateTitle: "Zatím nemáte žádné znalostní báze",
        emptyStateDescription: "Přidejte novou znalostní bázi pro začátek",
        tableHeaders: {
          title: "Název",
          description: "Popis",
          numberOfSources: "Počet zdrojů",
          embeddingModel: "Model vkládání",
          dateCreated: "Datum vytvoření",
          dateModified: "Datum úpravy",
          actions: "Akce"
        },
        status: {
          default: "Výchozí",
          na: "Není k dispozici"
        },
        actions: {
          view: "Zobrazit",
          edit: "Upravit",
          delete: "Smazat",
          configure: "Konfigurovat"
        },
        deleteModal: {
          title: "Smazat znalostní bázi",
          buttonText: "Smazat znalostní bázi",
          description: "Tato znalostní báze bude trvale smazána. Jste si jisti? Tuto akci nebude možné vrátit zpět.",
          confirmButton: "Smazat",
          cancelButton: "Zrušit",
          successMessage: "Znalostní báze byla úspěšně smazána",
          errorMessage: "Při mazání znalostní báze došlo k chybě"
        },
        modals: {
          add: {
            title: "Přidat znalostní bázi",
            description: "Vytvořte novou znalostní bázi zadáním podrobností a nahráním dokumentů níže.",
            fields: {
              title: "Název",
              titlePlaceholder: "Název",
              titleRequired: "Název je povinný",
              description: "Popis",
              descriptionPlaceholder: "Popis",
            },
            fileUpload: {
              dragAndDrop: "Přetáhněte soubory sem nebo klikněte pro procházení",
              dropFiles: "Přetáhněte soubory sem...",
              selectedFiles: "Vybrané soubory:",
              removeFile: "Odebrat soubor",
            },
            buttons: {
              cancel: "Zrušit",
              save: "Uložit",
              creating: "Vytváření...",
            },
            validation: {
              atLeastOneFile: "Je vyžadován alespoň jeden soubor.",
            },
            success: "Znalostní báze byla úspěšně vytvořena.",
          },
          edit: {
            title: "Upravit znalostní bázi",
            description: "Aktualizujte podrobnosti znalostní báze níže.",
            fields: {
              title: "Název",
              titlePlaceholder: "Název",
              titleRequired: "Název je povinný",
              description: "Popis",
              descriptionPlaceholder: "Popis",
            },
            fileUpload: {
              currentFiles: "Aktuální soubory:",
              dragAndDrop: "Přetáhněte soubory sem nebo klikněte pro procházení",
              dropFiles: "Přetáhněte soubory sem...",
              selectedFiles: "Vybrané soubory:",
              removeFile: "Odebrat soubor",
            },
            buttons: {
              cancel: "Zrušit",
              save: "Uložit",
              saving: "Ukládání...",
            },
            success: "Znalostní báze byla úspěšně aktualizována.",
          },
        },
        editCustom: {
          title: "Upravit vlastní pokyny",
          currentInstructions: "Aktuální pokyny:",
          save: "Uložit",
          cancel: "Zrušit",
        },
        editFormTemplateModal: {
          title: "Upravit Šablonu Formuláře",
          formTemplateName: "Název Šablony Formuláře",
          formTemplateDescription: "Popis Šablony Formuláře",
          descriptionPlaceholder: "Zadejte popis šablony formuláře pro automatické návrhy polí (minimálně 10 znaků)...",
          referenceDocuments: "Referenční Dokumenty (Volitelné)",
          uploadFiles: "Nahrát Soubory",
          knowledgeBase: "Znalostní Báze",
          formFields: "Pole Formuláře",
          suggest: "Navrhnout",
          fieldPlaceholder: "Přidejte název pole (např. Jméno, Adresa, Rodné číslo) nebo navrhněte z popisu",
          cancel: "Zrušit",
          updateFormTemplate: "Aktualizovat Šablonu Formuláře"
        }
      },
      dropdowns: {
        selectKnowledgeBase: "Vyberte znalostní bázi",
        selectFile: "Vyberte soubor",
        selectModel: "Vyberte model",
        defaultOption: "Vyberte možnost"
      },
      optimizeChecklistModal: {
        optimizeChecklistTitle: "Optimalizovat kontrolní seznam",
        optimizeChecklistDescription: "Nahrajte dokumenty, které by měl kontrolní seznam přijmout",
        uploadDocumentPrompt: "Nahrajte dokument(y), které by měl kontrolní seznam přijmout",
        fileDropMessage: "Přetáhněte soubory sem nebo klikněte pro výběr",
        optimizeButton: "Optimalizovat"
      },
      optimizeOutlineModal: {
        optimizeOutlineTitle: "Optimalizovat osnovu",
        optimizeOutlineDescription: "Vyberte znalostní bázi",
        selectKnowledgeBase: "Vyberte znalostní bázi",
        selectKnowledgeBasePlaceholder: "Vyberte znalostní bázi",
        optimizeButton: "Optimalizovat",
        createPediatricStudyPlaceholder: "např., vytvořte pediatrickou studii pro diabetes 1. typu"
      }
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
        welcomeBack: "Vitajte späť, je pekné vás znovu vidieť!",
        hiUser: "Ahoj, {{name}} 👋",
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
        allUsersToggleTooltip: "Prepínať medzi zobrazením iba vašej histórie alebo histórie všetkých používateľov",
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
      compare: {
        title: "Porovnať dokumenty",
        subtitle: "Vyberte dva dokumenty na porovnanie",
        selectFirstDocument: "Vybrať prvý dokument",
        selectSecondDocument: "Vybrať druhý dokument",
        pleaseSelect: "Prosím vyberte...",
        documentA: "Dokument A",
        documentB: "Dokument B",
        compareDocuments: "Porovnať dokumenty",
        comparison: "Porovnanie",
        noDocumentsFound: "Neboli nájdené žiadne dokumenty",
        selectTwoDocuments: "Prosím vyberte dva dokumenty na porovnanie",
        loadingComparison: "Načítavanie porovnania...",
        topicList: "Zoznam tém",
        clickToBrowse: "Kliknite na prehliadanie alebo pretiahnite",
        supportedFormats: "Podporované formáty: PDF, TXT, DOCX",
        analysisType: "Typ analýzy",
        quickAnalysis: "Rýchla analýza",
        detailedAnalysis: "Podrobná analýza",
        comprehensiveAnalysis: "Komplexná analýza",
        analysisDepth: "Hĺbka analýzy",
        surfaceLevel: "Povrchová úroveň",
        moderate: "Stredná",
        deep: "Hlboká",
        veryDeep: "Veľmi hlboká",
        editTopicList: "Upraviť zoznam tém"
      },
      match: {
        title: "Párovanie dokumentov",
        subtitle: "Nájsť podobné dokumenty na základe obsahu",
        selectDocument: "Vyberte dokument pre hľadanie zhôd",
        pleaseSelect: "Prosím vyberte dokument...",
        sourceDocument: "Zdrojový dokument",
        matchingDocuments: "Zodpovedajúce dokumenty",
        findMatches: "Nájsť zhody",
        similarityScore: "Skóre podobnosti",
        noDocumentsFound: "Neboli nájdené žiadne dokumenty",
        selectDocumentToMatch: "Prosím vyberte dokument pre hľadanie zhôd",
        loadingMatches: "Hľadanie zhôd...",
        noMatchesFound: "Neboli nájdené žiadne podobné dokumenty",
        matchResults: "Výsledky párovania",
        similarity: "Podobnosť",
        matchingCriteria: "Kritériá párovania",
        semanticSimilarity: "Sémantická podobnosť",
        keywordMatching: "Párovanie kľúčových slov",
        structuralSimilarity: "Štruktúrna podobnosť",
        threshold: "Prahová hodnota",
        minimumSimilarity: "Minimálna podobnosť",
        searchDepth: "Hĺbka vyhľadávania",
        maxResults: "Maximálny počet výsledkov",
        editFormTemplate: "Upraviť šablónu formulára"
      },
      knowledgeBases: {
        title: "Správa znalostných bází",
        addKnowledgeBase: "Pridať znalostnú bázu",
        emptyStateTitle: "Zatiaľ nemáte žiadne znalostné bázy",
        emptyStateDescription: "Pridajte novú znalostnú bázu pre začiatok",
        tableHeaders: {
          title: "Názov",
          description: "Popis",
          numberOfSources: "Počet zdrojov",
          embeddingModel: "Model vkladania",
          dateCreated: "Dátum vytvorenia",
          dateModified: "Dátum úpravy",
          actions: "Akcie"
        },
        status: {
          default: "Predvolené",
          na: "Nie je k dispozícii"
        },
        actions: {
          view: "Zobraziť",
          edit: "Upraviť",
          delete: "Zmazať",
          configure: "Konfigurovať"
        },
        deleteModal: {
          title: "Zmazať znalostnú bázu",
          buttonText: "Zmazať znalostnú bázu",
          description: "Táto znalostná báza bude trvalo zmazaná. Ste si istí? Túto akciu nebude možné vrátiť späť.",
          confirmButton: "Zmazať",
          cancelButton: "Zrušiť",
          successMessage: "Znalostná báza bola úspešne zmazaná",
          errorMessage: "Pri mazaní znalostnej bázy došlo k chybe"
        },
        modals: {
          add: {
            title: "Pridať znalostnú bázu",
            description: "Vytvorte novú znalostnú bázu zadaním podrobností a nahraním dokumentov nižšie.",
            fields: {
              title: "Názov",
              titlePlaceholder: "Názov",
              titleRequired: "Názov je povinný",
              description: "Popis",
              descriptionPlaceholder: "Popis",
            },
            fileUpload: {
              dragAndDrop: "Pretiahnite súbory sem alebo kliknite na prehliadanie",
              dropFiles: "Pretiahnite súbory sem...",
              selectedFiles: "Vybrané súbory:",
              removeFile: "Odobrať súbor",
            },
            buttons: {
              cancel: "Zrušiť",
              save: "Uložiť",
              creating: "Vytváranie...",
            },
            validation: {
              atLeastOneFile: "Je vyžadovaný aspoň jeden súbor.",
            },
            success: "Znalostná báza bola úspešne vytvorená.",
          },
          edit: {
            title: "Upraviť znalostnú bázu",
            description: "Aktualizujte podrobnosti znalostnej bázy nižšie.",
            fields: {
              title: "Názov",
              titlePlaceholder: "Názov",
              titleRequired: "Názov je povinný",
              description: "Popis",
              descriptionPlaceholder: "Popis",
            },
            fileUpload: {
              currentFiles: "Aktuálne súbory:",
              dragAndDrop: "Pretiahnite súbory sem alebo kliknite na prehliadanie",
              dropFiles: "Pretiahnite súbory sem...",
              selectedFiles: "Vybrané súbory:",
              removeFile: "Odobrať súbor",
            },
            buttons: {
              cancel: "Zrušiť",
              save: "Uložiť",
              saving: "Ukladanie...",
            },
            success: "Znalostná báza bola úspešne aktualizovaná.",
          },
        },
        editCustom: {
          title: "Upraviť vlastné pokyny",
          currentInstructions: "Aktuálne pokyny:",
          save: "Uložiť",
          cancel: "Zrušiť",
        },
        editFormTemplateModal: {
          title: "Upraviť Šablónu Formulára",
          formTemplateName: "Názov Šablóny Formulára",
          formTemplateDescription: "Popis Šablóny Formulára",
          descriptionPlaceholder: "Zadajte popis šablóny formulára pre automatické návrhy polí (minimálne 10 znakov)...",
          referenceDocuments: "Referenčné Dokumenty (Voliteľné)",
          uploadFiles: "Nahrať Súbory",
          knowledgeBase: "Znalostná Báza",
          formFields: "Polia Formulára",
          suggest: "Navrhnúť",
          fieldPlaceholder: "Pridajte názov poľa (napr. Meno, Adresa, Rodné číslo) alebo navrhujte z popisu",
          cancel: "Zrušiť",
          updateFormTemplate: "Aktualizovať Šablónu Formulára"
        }
      },
      optimizeChecklistModal: {
        title: "Optimalizovať kontrolný zoznam",
        customInstructionsLabel: "Vlastné pokyny (Voliteľné)",
        customInstructionsHelperText: "Zadajte dodatočné pokyny, ktoré by mali byť zohľadnené pri odpovedaní na otázky kontrolného zoznamu",
        analyzing: "Analyzuje sa...",
        analyzeButton: "Analyzovať kontrolný zoznam",
        analyzingMessage: "Analyzuje sa váš kontrolný zoznam pre možnosti optimalizácie...",
        cancelAnalysis: "Zrušiť analýzu",
        downloading: "Sťahuje sa...",
        downloadCsv: "Stiahnuť CSV",
        questionsNeedingOptimization: "Otázky potrebujúce optimalizáciu",
        questionsAlreadyOptimized: "Otázky už optimalizované",
        selected: "Vybrané",
        select: "Vybrať",
        original: "Pôvodné",
        suggestedImprovement: "Navrhované zlepšenie",
        policyContext: "Kontext politiky",
        currentAnswer: "Aktuálna odpoveď",
        showLess: "Zobraziť menej",
        showMore: "Zobraziť viac",
        optimizationsSelectedText: "optimalizáci{{a|e|í}} vybraných na použitie",
        applying: "Aplikuje sa...",
        applySelectedOptimizations: "Aplikovať vybrané optimalizácie",
        uploadDocumentsTitle: "Nahrať dokument(y), ktoré by mal kontrolný zoznam akceptovať *",
        uploadDocumentsHelperText: "Nahrajte dokumenty, ktoré by mali spĺňať všetky požiadavky kontrolného zoznamu na pomoc identifikácie otázok, ktoré môžu byť príliš prísne",
        customInstructionsPlaceholder: "napr., Zvážte, že ide o pediatrickú štúdiu pri hodnotení požiadaviek súvisiacich s vekom, Tento protokol je pre nízko-rizikový zásah, atď."
      },
      optimizeOutlineModal: {
        title: "Optimalizovať osnovu",
        description: "Nahrajte referenčný dokument, ktorý predstavuje vysokokvalitný príklad typu správy, ktorú chcete generovať. Systém vygeneruje správu použijúc vašu aktuálnu osnovu a znalostnú bázu, porovná ju s referenciou a navrhne zlepšenia pre vaše sekcie osnovy.",
        groundTruthDocument: "Referenčný dokument",
        customInstructionsLabel: "Vlastné pokyny (Voliteľné)",
        customInstructionsHelperText: "Poskytnite dodatočné pokyny pre proces optimalizácie",
        customInstructionsPlaceholder: "napr., Zamerajte sa na zlepšenie technickej hĺbky, zabezpečte súlad s konkrétnymi štandardmi, atď.",
        characters: "znakov",
        analyzingOutline: "Analyzuje sa osnova a generujú sa optimalizácie...",
        cancelAnalysis: "Zrušiť analýzu",
        optimizationResults: "Výsledky optimalizácie",
        sectionsNeedOptimization: "sekcií potrebuje optimalizáciu",
        downloadCsv: "Stiahnuť CSV",
        section: "Sekcia",
        accepted: "Akceptované",
        accept: "Akceptovať",
        originalSectionDescription: "Pôvodný popis sekcie",
        suggestedSectionDescription: "Navrhovaný popis sekcie",
        generatedContent: "Generovaný obsah (s aktuálnym popisom)",
        groundTruthReference: "Referenčná referencia",
        showLess: "Zobraziť menej",
        showMore: "Zobraziť viac",
        close: "Zavrieť",
        cancel: "Zrušiť",
        optimizing: "Optimalizuje sa...",
        optimizeOutline: "Optimalizovať osnovu",
        applyOptimizations: "Aplikovať {{count}} optimalizáci{{u|e|í}}"
      }
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
        welcomeBack: "Isten hozott vissza, jó újra látni!",
        hiUser: "Szia, {{name}} 👋",
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
        allUsersToggleTooltip: "Váltás a csak saját előzmények vagy az összes felhasználó előzményeinek megjelenítése között",
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
      compare: {
        title: "Dokumentumok összehasonlítása",
        subtitle: "Válasszon ki két dokumentumot az összehasonlításhoz",
        selectFirstDocument: "Első dokumentum kiválasztása",
        selectSecondDocument: "Második dokumentum kiválasztása",
        pleaseSelect: "Kérjük válasszon...",
        documentA: "A dokumentum",
        documentB: "B dokumentum",
        compareDocuments: "Dokumentumok összehasonlítása",
        comparison: "Összehasonlítás",
        noDocumentsFound: "Nem találhatók dokumentumok",
        selectTwoDocuments: "Kérjük válasszon ki két dokumentumot az összehasonlításhoz",
        loadingComparison: "Összehasonlítás betöltése...",
        topicList: "Témák listája",
        clickToBrowse: "Kattintson a böngészéshez vagy húzza ide",
        supportedFormats: "Támogatott formátumok: PDF, TXT, DOCX",
        analysisType: "Elemzés típusa",
        quickAnalysis: "Gyors elemzés",
        detailedAnalysis: "Részletes elemzés",
        comprehensiveAnalysis: "Átfogó elemzés",
        analysisDepth: "Elemzés mélysége",
        surfaceLevel: "Felületi szint",
        moderate: "Közepes",
        deep: "Mély",
        veryDeep: "Nagyon mély",
        editTopicList: "Témalista szerkesztése"
      },
      match: {
        title: "Dokumentumok párosítása",
        subtitle: "Hasonló dokumentumok keresése tartalom alapján",
        selectDocument: "Válasszon dokumentumot a párosításhoz",
        pleaseSelect: "Kérjük válasszon dokumentumot...",
        sourceDocument: "Forrás dokumentum",
        matchingDocuments: "Egyező dokumentumok",
        findMatches: "Párosítások keresése",
        similarityScore: "Hasonlósági pontszám",
        noDocumentsFound: "Nem találhatók dokumentumok",
        selectDocumentToMatch: "Kérjük válasszon dokumentumot a párosításhoz",
        loadingMatches: "Párosítások keresése...",
        noMatchesFound: "Nem találhatók hasonló dokumentumok",
        matchResults: "Párosítási eredmények",
        similarity: "Hasonlóság",
        matchingCriteria: "Párosítási kritériumok",
        semanticSimilarity: "Szemantikai hasonlóság",
        keywordMatching: "Kulcsszó párosítás",
        structuralSimilarity: "Strukturális hasonlóság",
        threshold: "Küszöbérték",
        minimumSimilarity: "Minimális hasonlóság",
        searchDepth: "Keresési mélység",
        maxResults: "Maximális eredmények száma",
        editFormTemplate: "Űrlapsablon szerkesztése"
      },
      knowledgeBases: {
        title: "Tudásbázisok kezelése",
        addKnowledgeBase: "Tudásbázis hozzáadása",
        emptyStateTitle: "Még nincsenek tudásbázisai",
        emptyStateDescription: "Adjon hozzá egy új tudásbázist a kezdéshez",
        tableHeaders: {
          title: "Cím",
          description: "Leírás",
          numberOfSources: "Források száma",
          embeddingModel: "Beágyazási modell",
          dateCreated: "Létrehozás dátuma",
          dateModified: "Módosítás dátuma",
          actions: "Műveletek"
        },
        status: {
          default: "Alapértelmezett",
          na: "Nem elérhető"
        },
        actions: {
          view: "Megtekintés",
          edit: "Szerkesztés",
          delete: "Törlés",
          configure: "Konfigurálás"
        },
        deleteModal: {
          title: "Tudásbázis törlése",
          buttonText: "Tudásbázis törlése",
          description: "Ez a tudásbázis véglegesen törlésre kerül. Biztos benne? Ezt a műveletet nem lehet visszavonni.",
          confirmButton: "Törlés",
          cancelButton: "Mégse",
          successMessage: "A tudásbázis sikeresen törölve lett",
          errorMessage: "Hiba történt a tudásbázis törlése során"
        },
        modals: {
          add: {
            title: "Tudásbázis hozzáadása",
            description: "Hozzon létre egy új tudásbázist részletek megadásával és dokumentumok feltöltésével alább.",
            fields: {
              title: "Cím",
              titlePlaceholder: "Cím",
              titleRequired: "A cím megadása kötelező",
              description: "Leírás",
              descriptionPlaceholder: "Leírás",
            },
            fileUpload: {
              dragAndDrop: "Húzza ide a fájlokat vagy kattintson a böngészéshez",
              dropFiles: "Húzza ide a fájlokat...",
              selectedFiles: "Kiválasztott fájlok:",
              removeFile: "Fájl eltávolítása",
            },
            buttons: {
              cancel: "Mégse",
              save: "Mentés",
              creating: "Létrehozás...",
            },
            validation: {
              atLeastOneFile: "Legalább egy fájl szükséges.",
            },
            success: "A tudásbázis sikeresen létrehozva.",
          },
          edit: {
            title: "Tudásbázis szerkesztése",
            description: "Frissítse a tudásbázis részleteit alább.",
            fields: {
              title: "Cím",
              titlePlaceholder: "Cím",
              titleRequired: "A cím megadása kötelező",
              description: "Leírás",
              descriptionPlaceholder: "Leírás",
            },
            fileUpload: {
              currentFiles: "Jelenlegi fájlok:",
              dragAndDrop: "Húzza ide a fájlokat vagy kattintson a böngészéshez",
              dropFiles: "Húzza ide a fájlokat...",
              selectedFiles: "Kiválasztott fájlok:",
              removeFile: "Fájl eltávolítása",
            },
            buttons: {
              cancel: "Mégse",
              save: "Mentés",
              saving: "Mentés...",
            },
            success: "A tudásbázis sikeresen frissítve.",
          },
        },
        editCustom: {
          title: "Egyéni utasítások szerkesztése",
          currentInstructions: "Jelenlegi utasítások:",
          save: "Mentés",
          cancel: "Mégse",
        },
        editFormTemplateModal: {
          title: "Űrlapsablon Szerkesztése",
          formTemplateName: "Űrlapsablon Neve",
          formTemplateDescription: "Űrlapsablon Leírása",
          descriptionPlaceholder: "Adja meg az űrlapsablon leírását a mezők automatikus javaslásához (legalább 10 karakter)...",
          referenceDocuments: "Referenciadokumentumok (Opcionális)",
          uploadFiles: "Fájlok Feltöltése",
          knowledgeBase: "Tudásbázis",
          formFields: "Űrlapmezők",
          suggest: "Javaslat",
          fieldPlaceholder: "Adjon hozzá egy mezőnevet (pl. Vezetéknév, Cím, Társadalombiztosítási szám) vagy javasoljon a leírásból",
          cancel: "Mégse",
          updateFormTemplate: "Űrlapsablon Frissítése"
        }
      },
      optimizeChecklistModal: {
        title: "Ellenőrzőlista optimalizálása",
        customInstructionsLabel: "Egyéni utasítások (Opcionális)",
        customInstructionsHelperText: "Adjon meg további utasításokat, amelyeket figyelembe kell venni az ellenőrzőlista kérdéseinek megválaszolásakor",
        analyzing: "Elemzés...",
        analyzeButton: "Ellenőrzőlista elemzése",
        analyzingMessage: "Az ellenőrzőlista elemzése optimalizálási lehetőségekért...",
        cancelAnalysis: "Elemzés megszakítása",
        downloading: "Letöltés...",
        downloadCsv: "CSV letöltése",
        questionsNeedingOptimization: "Optimalizálásra szoruló kérdések",
        questionsAlreadyOptimized: "Már optimalizált kérdések",
        selected: "Kiválasztott",
        select: "Kiválasztás",
        original: "Eredeti",
        suggestedImprovement: "Javasolt javítás",
        policyContext: "Szabályzat kontextus",
        currentAnswer: "Jelenlegi válasz",
        showLess: "Kevesebb mutatása",
        showMore: "Több mutatása",
        optimizationsSelectedText: "optimalizálás kiválasztva alkalmazásra",
        applying: "Alkalmazás...",
        applySelectedOptimizations: "Kiválasztott optimalizálások alkalmazása",
        uploadDocumentsTitle: "Töltsön fel dokumentum(ok)at, amelyeket az ellenőrzőlistának el kell fogadnia *",
        uploadDocumentsHelperText: "Töltsön fel olyan dokumentumokat, amelyeknek meg kell felelniük az összes ellenőrzőlista követelménynek, hogy segítsen azonosítani a túl szigorú kérdéseket",
        customInstructionsPlaceholder: "pl., Vegye figyelembe, hogy ez egy gyermekgyógyászati tanulmány az életkorral kapcsolatos követelmények értékelésekor, Ez a protokoll alacsony kockázatú beavatkozásra vonatkozik, stb."
      },
      optimizeOutlineModal: {
        title: "Vázlat optimalizálása",
        description: "Töltsön fel egy referencia dokumentumot, amely egy magas minőségű példát képvisel a generálni kívánt jelentés típusára. A rendszer jelentést generál a jelenlegi vázlata és tudásbázisa használatával, összehasonlítja a referenciával, és javaslatokat tesz a vázlat szakaszok javítására.",
        groundTruthDocument: "Referencia dokumentum",
        customInstructionsLabel: "Egyéni utasítások (Opcionális)",
        customInstructionsHelperText: "Adjon meg további útmutatást az optimalizálási folyamathoz",
        customInstructionsPlaceholder: "pl., Koncentráljon a technikai mélység javítására, biztosítsa a megfelelést az adott szabványokkal, stb.",
        characters: "karakter",
        analyzingOutline: "Vázlat elemzése és optimalizálások generálása...",
        cancelAnalysis: "Elemzés megszakítása",
        optimizationResults: "Optimalizálási eredmények",
        sectionsNeedOptimization: "szakasz igényel optimalizálást",
        downloadCsv: "CSV letöltése",
        section: "Szakasz",
        accepted: "Elfogadott",
        accept: "Elfogadás",
        originalSectionDescription: "Eredeti szakasz leírás",
        suggestedSectionDescription: "Javasolt szakasz leírás",
        generatedContent: "Generált tartalom (jelenlegi leírással)",
        groundTruthReference: "Referencia hivatkozás",
        showLess: "Kevesebb mutatása",
        showMore: "Több mutatása",
        close: "Bezárás",
        cancel: "Megszakítás",
        optimizing: "Optimalizálás...",
        optimizeOutline: "Vázlat optimalizálása",
        applyOptimizations: "{{count}} optimalizálás alkalmazása"
      }
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
        allUsersToggleTooltip: "Comutați între vizualizarea doar a istoricului dvs. sau a istoricului tuturor utilizatorilor",
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
      compare: {
        title: "Compararea documentelor",
        subtitle: "Selectați două documente pentru comparare",
        selectFirstDocument: "Selectați primul document",
        selectSecondDocument: "Selectați al doilea document",
        pleaseSelect: "Vă rugăm selectați...",
        documentA: "Documentul A",
        documentB: "Documentul B",
        compareDocuments: "Comparați documentele",
        comparison: "Comparație",
        noDocumentsFound: "Nu s-au găsit documente",
        selectTwoDocuments: "Vă rugăm selectați două documente pentru comparare",
        loadingComparison: "Se încarcă comparația...",
        topicList: "Lista subiectelor",
        clickToBrowse: "Faceți clic pentru a răsfoi sau trageți aici",
        supportedFormats: "Formate suportate: PDF, TXT, DOCX",
        analysisType: "Tipul analizei",
        quickAnalysis: "Analiză rapidă",
        detailedAnalysis: "Analiză detaliată",
        comprehensiveAnalysis: "Analiză cuprinzătoare",
        analysisDepth: "Profunzimea analizei",
        surfaceLevel: "Nivel de suprafață",
        moderate: "Moderat",
        deep: "Profund",
        veryDeep: "Foarte profund",
        editTopicList: "Editați lista de subiecte"
      },
      match: {
        title: "Potrivirea documentelor",
        subtitle: "Găsiți documente similare pe baza conținutului",
        selectDocument: "Selectați documentul pentru găsirea potrivirilor",
        pleaseSelect: "Vă rugăm selectați un document...",
        sourceDocument: "Document sursă",
        matchingDocuments: "Documente potrivite",
        findMatches: "Găsiți potriviri",
        similarityScore: "Scorul similarității",
        noDocumentsFound: "Nu s-au găsit documente",
        selectDocumentToMatch: "Vă rugăm selectați un document pentru găsirea potrivirilor",
        loadingMatches: "Se caută potriviri...",
        noMatchesFound: "Nu s-au găsit documente similare",
        matchResults: "Rezultatele potrivirii",
        similarity: "Similaritate",
        matchingCriteria: "Criterii de potrivire",
        semanticSimilarity: "Similaritate semantică",
        keywordMatching: "Potrivirea cuvintelor cheie",
        structuralSimilarity: "Similaritate structurală",
        threshold: "Prag",
        minimumSimilarity: "Similaritate minimă",
        searchDepth: "Profunzimea căutării",
        maxResults: "Numărul maxim de rezultate",
        editFormTemplate: "Editați șablonul formularului"
      },
      knowledgeBases: {
        title: "Gestionarea bazelor de cunoștințe",
        addKnowledgeBase: "Adăugați baza de cunoștințe",
        emptyStateTitle: "Nu aveți încă baze de cunoștințe",
        emptyStateDescription: "Adăugați o nouă bază de cunoștințe pentru a începe",
        tableHeaders: {
          title: "Titlu",
          description: "Descriere",
          numberOfSources: "Numărul surselor",
          embeddingModel: "Modelul de încorporare",
          dateCreated: "Data creării",
          dateModified: "Data modificării",
          actions: "Acțiuni"
        },
        status: {
          default: "Implicit",
          na: "Nu este disponibil"
        },
        actions: {
          view: "Vizualizare",
          edit: "Editare",
          delete: "Ștergere",
          configure: "Configurare"
        },
        deleteModal: {
          title: "Ștergeți baza de cunoștințe",
          buttonText: "Ștergeți baza de cunoștințe",
          description: "Această bază de cunoștințe va fi ștearsă permanent. Sunteți sigur? Nu veți putea anula această acțiune.",
          confirmButton: "Ștergere",
          cancelButton: "Anulare",
          successMessage: "Baza de cunoștințe a fost ștearsă cu succes",
          errorMessage: "A apărut o eroare la ștergerea bazei de cunoștințe"
        },
        modals: {
          add: {
            title: "Adăugați baza de cunoștințe",
            description: "Creați o nouă bază de cunoștințe furnizând detalii și încărcând documente mai jos.",
            fields: {
              title: "Titlu",
              titlePlaceholder: "Titlu",
              titleRequired: "Titlul este necesar",
              description: "Descriere",
              descriptionPlaceholder: "Descriere",
            },
            fileUpload: {
              dragAndDrop: "Trageți fișierele aici sau faceți clic pentru a răsfoi",
              dropFiles: "Plasați fișierele aici...",
              selectedFiles: "Fișiere selectate:",
              removeFile: "Eliminați fișierul",
            },
            buttons: {
              cancel: "Anulare",
              save: "Salvare",
              creating: "Se creează...",
            },
            validation: {
              atLeastOneFile: "Este necesar cel puțin un fișier.",
            },
            success: "Baza de cunoștințe a fost creată cu succes.",
          },
          edit: {
            title: "Editați baza de cunoștințe",
            description: "Actualizați detaliile bazei de cunoștințe mai jos.",
            fields: {
              title: "Titlu",
              titlePlaceholder: "Titlu",
              titleRequired: "Titlul este necesar",
              description: "Descriere",
              descriptionPlaceholder: "Descriere",
            },
            fileUpload: {
              currentFiles: "Fișiere curente:",
              dragAndDrop: "Trageți fișierele aici sau faceți clic pentru a răsfoi",
              dropFiles: "Plasați fișierele aici...",
              selectedFiles: "Fișiere selectate:",
              removeFile: "Eliminați fișierul",
            },
            buttons: {
              cancel: "Anulare",
              save: "Salvare",
              saving: "Se salvează...",
            },
            success: "Baza de cunoștințe a fost actualizată cu succes.",
          },
        },
        editCustom: {
          title: "Editați instrucțiunile personalizate",
          currentInstructions: "Instrucțiuni curente:",
          save: "Salvare",
          cancel: "Anulare",
        },
        editFormTemplateModal: {
          title: "Editați Șablonul de Formular",
          formTemplateName: "Numele Șablonului de Formular",
          formTemplateDescription: "Descrierea Șablonului de Formular",
          descriptionPlaceholder: "Introduceți descrierea șablonului de formular pentru a sugera automat câmpurile (minimum 10 caractere)...",
          referenceDocuments: "Documente de Referință (Opțional)",
          uploadFiles: "Încărcați Fișiere",
          knowledgeBase: "Baza de Cunoștințe",
          formFields: "Câmpurile Formularului",
          suggest: "Sugerează",
          fieldPlaceholder: "Adăugați un nume de câmp (ex. Prenume, Adresă, CNP) sau sugerați din descriere",
          cancel: "Anulare",
          updateFormTemplate: "Actualizați Șablonul de Formular"
        }
      },
      optimizeChecklistModal: {
        title: "Optimizează Lista de Verificare",
        customInstructionsLabel: "Instrucțiuni Personalizate (Opțional)",
        customInstructionsHelperText: "Introduceți instrucțiuni suplimentare care ar trebui luate în considerare la răspunsul la întrebările listei de verificare",
        analyzing: "Se analizează...",
        analyzeButton: "Analizează Lista de Verificare",
        analyzingMessage: "Se analizează lista dvs. de verificare pentru oportunități de optimizare...",
        cancelAnalysis: "Anulează Analiza",
        downloading: "Se descarcă...",
        downloadCsv: "Descarcă CSV",
        questionsNeedingOptimization: "Întrebări care Necesită Optimizare",
        questionsAlreadyOptimized: "Întrebări Deja Optimizate",
        selected: "Selectat",
        select: "Selectează",
        original: "Original",
        suggestedImprovement: "Îmbunătățire Sugerată",
        policyContext: "Context Politică",
        currentAnswer: "Răspuns Curent",
        showLess: "Afișează Mai Puțin",
        showMore: "Afișează Mai Mult",
        optimizationsSelectedText: "optimizări selectate pentru aplicare",
        applying: "Se aplică...",
        applySelectedOptimizations: "Aplică Optimizările Selectate",
        uploadDocumentsTitle: "Încărcați document(e) care ar trebui acceptate de lista de verificare *",
        uploadDocumentsHelperText: "Încărcați documente care ar trebui să îndeplinească toate cerințele listei de verificare pentru a ajuta la identificarea întrebărilor care pot fi prea stricte",
        customInstructionsPlaceholder: "de ex., Luați în considerare că acesta este un studiu pediatric când evaluați cerințele legate de vârstă, Acest protocol este pentru o intervenție cu risc scăzut, etc."
      },
      optimizeOutlineModal: {
        title: "Optimizează Schița",
        description: "Încărcați un document de referință care reprezintă un exemplu de înaltă calitate al tipului de raport pe care doriți să îl generați. Sistemul va genera un raport folosind schița și baza de cunoștințe actuală, îl va compara cu referința și va sugera îmbunătățiri pentru secțiunile schiței.",
        groundTruthDocument: "Document de Referință",
        customInstructionsLabel: "Instrucțiuni Personalizate (Opțional)",
        customInstructionsHelperText: "Furnizați îndrumări suplimentare pentru procesul de optimizare",
        customInstructionsPlaceholder: "de ex., Concentrați-vă pe îmbunătățirea profunzimii tehnice, asigurați conformitatea cu standarde specifice, etc.",
        characters: "caractere",
        analyzingOutline: "Se analizează schița și se generează optimizări...",
        cancelAnalysis: "Anulează Analiza",
        optimizationResults: "Rezultatele Optimizării",
        sectionsNeedOptimization: "secțiuni necesită optimizare",
        downloadCsv: "Descarcă CSV",
        section: "Secțiune",
        accepted: "Acceptat",
        accept: "Acceptă",
        originalSectionDescription: "Descrierea Secțiunii Originale",
        suggestedSectionDescription: "Descrierea Secțiunii Sugerate",
        generatedContent: "Conținut Generat (cu descrierea actuală)",
        groundTruthReference: "Referința de Bază",
        showLess: "Afișează Mai Puțin",
        showMore: "Afișează Mai Mult",
        close: "Închide",
        cancel: "Anulează",
        optimizing: "Se optimizează...",
        optimizeOutline: "Optimizează Schița",
        applyOptimizations: "Aplică {{count}} Optimizări"
      }
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
        allUsersToggleTooltip: "Превключване между показване само на вашата история или историята на всички потребители",
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
      compare: {
        title: "Сравняване на документи",
        subtitle: "Изберете два документа за сравняване",
        selectFirstDocument: "Изберете първия документ",
        selectSecondDocument: "Изберете втория документ",
        pleaseSelect: "Моля изберете...",
        documentA: "Документ А",
        documentB: "Документ Б",
        compareDocuments: "Сравнете документите",
        comparison: "Сравнение",
        noDocumentsFound: "Не са намерени документи",
        selectTwoDocuments: "Моля изберете два документа за сравняване",
        loadingComparison: "Зареждане на сравнението...",
        topicList: "Списък с теми",
        clickToBrowse: "Кликнете за разглеждане или плъзнете тук",
        supportedFormats: "Поддържани формати: PDF, TXT, DOCX",
        analysisType: "Тип анализ",
        quickAnalysis: "Бърз анализ",
        detailedAnalysis: "Детайлен анализ",
        comprehensiveAnalysis: "Изчерпателен анализ",
        analysisDepth: "Дълбочина на анализа",
        surfaceLevel: "Повърхностно ниво",
        moderate: "Умерено",
        deep: "Дълбоко",
        veryDeep: "Много дълбоко",
        editTopicList: "Редактирайте списъка с теми"
      },
      match: {
        title: "Съвпадение на документи",
        subtitle: "Намерете подобни документи въз основа на съдържанието",
        selectDocument: "Изберете документ за намиране на съвпадения",
        pleaseSelect: "Моля изберете документ...",
        sourceDocument: "Изходен документ",
        matchingDocuments: "Съвпадащи документи",
        findMatches: "Намерете съвпадения",
        similarityScore: "Резултат за сходство",
        noDocumentsFound: "Не са намерени документи",
        selectDocumentToMatch: "Моля изберете документ за намиране на съвпадения",
        loadingMatches: "Търсене на съвпадения...",
        noMatchesFound: "Не са намерени подобни документи",
        matchResults: "Резултати от съвпадението",
        similarity: "Сходство",
        matchingCriteria: "Критерии за съвпадение",
        semanticSimilarity: "Семантично сходство",
        keywordMatching: "Съвпадение на ключови думи",
        structuralSimilarity: "Структурно сходство",
        threshold: "Праг",
        minimumSimilarity: "Минимално сходство",
        searchDepth: "Дълбочина на търсенето",
        maxResults: "Максимален брой резултати",
        editFormTemplate: "Редактирайте шаблона на формуляра"
      },
      knowledgeBases: {
        title: "Управление на бази знания",
        addKnowledgeBase: "Добавяне на база знания",
        emptyStateTitle: "Все още нямате бази знания",
        emptyStateDescription: "Добавете нова база знания за да започнете",
        tableHeaders: {
          title: "Заглавие",
          description: "Описание",
          numberOfSources: "Брой източници",
          embeddingModel: "Модел за вграждане",
          dateCreated: "Дата на създаване",
          dateModified: "Дата на промяна",
          actions: "Действия"
        },
        status: {
          default: "По подразбиране",
          na: "Не е налично"
        },
        actions: {
          view: "Преглед",
          edit: "Редактиране",
          delete: "Изтриване",
          configure: "Конфигуриране"
        },
        deleteModal: {
          title: "Изтриване на база знания",
          buttonText: "Изтриване на база знания",
          description: "Тази база знания ще бъде изтрита завинаги. Сигурни ли сте? Няма да можете да отмените това действие.",
          confirmButton: "Изтриване",
          cancelButton: "Отказ",
          successMessage: "Базата знания беше успешно изтрита",
          errorMessage: "Възникна грешка при изтриването на базата знания"
        },
        modals: {
          add: {
            title: "Добавяне на база знания",
            description: "Създайте нова база знания като предоставите подробности и качите документи по-долу.",
            fields: {
              title: "Заглавие",
              titlePlaceholder: "Заглавие",
              titleRequired: "Заглавието е задължително",
              description: "Описание",
              descriptionPlaceholder: "Описание",
            },
            fileUpload: {
              dragAndDrop: "Плъзнете файловете тук или кликнете за разглеждане",
              dropFiles: "Пуснете файловете тук...",
              selectedFiles: "Избрани файлове:",
              removeFile: "Премахване на файл",
            },
            buttons: {
              cancel: "Отказ",
              save: "Запазване",
              creating: "Създаване...",
            },
            validation: {
              atLeastOneFile: "Необходим е поне един файл.",
            },
            success: "Базата знания беше успешно създадена.",
          },
          edit: {
            title: "Редактиране на база знания",
            description: "Актуализирайте подробностите за базата знания по-долу.",
            fields: {
              title: "Заглавие",
              titlePlaceholder: "Заглавие",
              titleRequired: "Заглавието е задължително",
              description: "Описание",
              descriptionPlaceholder: "Описание",
            },
            fileUpload: {
              currentFiles: "Текущи файлове:",
              dragAndDrop: "Плъзнете файловете тук или кликнете за разглеждане",
              dropFiles: "Пуснете файловете тук...",
              selectedFiles: "Избрани файлове:",
              removeFile: "Премахване на файл",
            },
            buttons: {
              cancel: "Отказ",
              save: "Запазване",
              saving: "Запазване...",
            },
            success: "Базата знания беше успешно актуализирана.",
          },
        },
        editCustom: {
          title: "Редактиране на персонализирани инструкции",
          currentInstructions: "Текущи инструкции:",
          save: "Запазване",
          cancel: "Отказ",
        },
        editFormTemplateModal: {
          title: "Редактиране на Шаблон на Формуляр",
          formTemplateName: "Име на Шаблона на Формуляра",
          formTemplateDescription: "Описание на Шаблона на Формуляра",
          descriptionPlaceholder: "Въведете описание на шаблона на формуляра за автоматично предлагане на полета (минимум 10 знака)...",
          referenceDocuments: "Референтни Документи (Опционално)",
          uploadFiles: "Качване на Файлове",
          knowledgeBase: "База от Знания",
          formFields: "Полета на Формуляра",
          suggest: "Предложи",
          fieldPlaceholder: "Добавете име на поле (напр. Име, Адрес, ЕГН) или предложете от описанието",
          cancel: "Отказ",
          updateFormTemplate: "Актуализиране на Шаблона на Формуляра"
        }
      },
      optimizeChecklistModal: {
        title: "Оптимизиране на Контролния Списък",
        customInstructionsLabel: "Персонализирани Инструкции (Незадължително)",
        customInstructionsHelperText: "Въведете допълнителни инструкции, които трябва да бъдат взети предвид при отговарянето на въпросите от контролния списък",
        analyzing: "Анализира се...",
        analyzeButton: "Анализирай Контролния Списък",
        analyzingMessage: "Анализира се вашият контролен списък за възможности за оптимизация...",
        cancelAnalysis: "Отмени Анализа",
        downloading: "Изтегля се...",
        downloadCsv: "Изтегли CSV",
        questionsNeedingOptimization: "Въпроси, Нуждаещи се от Оптимизация",
        questionsAlreadyOptimized: "Вече Оптимизирани Въпроси",
        selected: "Избрано",
        select: "Избери",
        original: "Оригинал",
        suggestedImprovement: "Предложено Подобрение",
        policyContext: "Контекст на Политиката",
        currentAnswer: "Текущ Отговор",
        showLess: "Покажи По-малко",
        showMore: "Покажи Повече",
        optimizationsSelectedText: "оптимизации избрани за прилагане",
        applying: "Прилага се...",
        applySelectedOptimizations: "Приложи Избраните Оптимизации",
        uploadDocumentsTitle: "Качете документ(и), които трябва да бъдат приети от контролния списък *",
        uploadDocumentsHelperText: "Качете документи, които трябва да отговарят на всички изисквания на контролния списък, за да помогнете за идентифициране на въпроси, които могат да бъдат твърде строги",
        customInstructionsPlaceholder: "напр., Вземете предвид, че това е педиатрично изследване при оценяване на възрастови изисквания, Този протокол е за нискорискова интервенция, и т.н."
      },
      optimizeOutlineModal: {
        title: "Оптимизиране на Структурата",
        description: "Качете референтен документ, който представлява висококачествен пример от типа доклад, който искате да генерирате. Системата ще генерира доклад, използвайки вашата текуща структура и база знания, ще го сравни с референтния и ще предложи подобрения за секциите на структурата.",
        groundTruthDocument: "Референтен Документ",
        customInstructionsLabel: "Персонализирани Инструкции (Незадължително)",
        customInstructionsHelperText: "Предоставете допълнително ръководство за процеса на оптимизация",
        customInstructionsPlaceholder: "напр., Фокусирайте се върху подобряване на техническата дълбочина, осигурете съответствие с конкретни стандарти, и т.н.",
        characters: "символа",
        analyzingOutline: "Анализира се структурата и генерират се оптимизации...",
        cancelAnalysis: "Отмени Анализа",
        optimizationResults: "Резултати от Оптимизацията",
        sectionsNeedOptimization: "секции се нуждаят от оптимизация",
        downloadCsv: "Изтегли CSV",
        section: "Секция",
        accepted: "Прието",
        accept: "Приеми",
        originalSectionDescription: "Оригинално Описание на Секцията",
        suggestedSectionDescription: "Предложено Описание на Секцията",
        generatedContent: "Генериран Съдържание (с текущото описание)",
        groundTruthReference: "Референтна Справка",
        showLess: "Покажи По-малко",
        showMore: "Покажи Повече",
        close: "Затвори",
        cancel: "Отмени",
        optimizing: "Оптимизира се...",
        optimizeOutline: "Оптимизирай Структурата",
        applyOptimizations: "Приложи {{count}} Оптимизации"
      }
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
        allUsersToggleTooltip: "Prebacuj između prikaza samo tvoje povijesti ili povijesti svih korisnika",
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
      compare: {
        title: "Usporedi dokumente",
        subtitle: "Odaberite dva dokumenta za usporedbu",
        selectFirstDocument: "Odaberite prvi dokument",
        selectSecondDocument: "Odaberite drugi dokument",
        pleaseSelect: "Molimo odaberite...",
        documentA: "Dokument A",
        documentB: "Dokument B",
        compareDocuments: "Usporedi dokumente",
        comparison: "Usporedba",
        noDocumentsFound: "Nisu pronađeni dokumenti",
        selectTwoDocuments: "Molimo odaberite dva dokumenta za usporedbu",
        loadingComparison: "Učitavanje usporedbe...",
        topicList: "Popis tema",
        clickToBrowse: "Kliknite za pregled ili povucite ovdje",
        supportedFormats: "Podržani formati: PDF, TXT, DOCX",
        analysisType: "Vrsta analize",
        quickAnalysis: "Brza analiza",
        detailedAnalysis: "Detaljna analiza",
        comprehensiveAnalysis: "Sveobuhvatna analiza",
        analysisDepth: "Dubina analize",
        surfaceLevel: "Površinska razina",
        moderate: "Umjerena",
        deep: "Duboka",
        veryDeep: "Vrlo duboka",
        editTopicList: "Uredi listu tema"
      },
      match: {
        title: "Podudarne dokumente",
        subtitle: "Pronađite slične dokumente na temelju sadržaja",
        selectDocument: "Odaberite dokument za pronalaženje podudaranja",
        pleaseSelect: "Molimo odaberite dokument...",
        sourceDocument: "Izvorni dokument",
        matchingDocuments: "Podudaran dokumenti",
        findMatches: "Pronađi podudaranja",
        similarityScore: "Rezultat sličnosti",
        noDocumentsFound: "Nisu pronađeni dokumenti",
        selectDocumentToMatch: "Molimo odaberite dokument za pronalaženje podudaranja",
        loadingMatches: "Traženje podudaranja...",
        noMatchesFound: "Nisu pronađeni slični dokumenti",
        matchResults: "Rezultati podudaranja",
        similarity: "Sličnost",
        matchingCriteria: "Kriteriji podudaranja",
        semanticSimilarity: "Semantička sličnost",
        keywordMatching: "Podudaranje ključnih riječi",
        structuralSimilarity: "Strukturalna sličnost",
        threshold: "Prag",
        minimumSimilarity: "Minimalna sličnost",
        searchDepth: "Dubina pretraživanja",
        maxResults: "Maksimalan broj rezultata",
        editFormTemplate: "Uredi predložak obrasca"
      },
      knowledgeBases: {
        title: "Upravljanje bazama znanja",
        addKnowledgeBase: "Dodaj bazu znanja",
        emptyStateTitle: "Još nemate baze znanja",
        emptyStateDescription: "Dodajte novu bazu znanja za početak",
        tableHeaders: {
          title: "Naslov",
          description: "Opis",
          numberOfSources: "Broj izvora",
          embeddingModel: "Model ugrađivanja",
          dateCreated: "Datum stvaranja",
          dateModified: "Datum izmjene",
          actions: "Radnje"
        },
        status: {
          default: "Zadano",
          na: "Nije dostupno"
        },
        actions: {
          view: "Pregled",
          edit: "Uredi",
          delete: "Obriši",
          configure: "Konfiguriraj"
        },
        deleteModal: {
          title: "Obriši bazu znanja",
          buttonText: "Obriši bazu znanja",
          description: "Ova baza znanja će biti trajno obrisana. Jeste li sigurni? Nećete moći poništiti ovu radnju.",
          confirmButton: "Obriši",
          cancelButton: "Odustani",
          successMessage: "Baza znanja je uspješno obrisana",
          errorMessage: "Došlo je do greške prilikom brisanja baze znanja"
        },
        modals: {
          add: {
            title: "Dodaj bazu znanja",
            description: "Stvorite novu bazu znanja pružanjem detalja i prenosom dokumenata u nastavku.",
            fields: {
              title: "Naslov",
              titlePlaceholder: "Naslov",
              titleRequired: "Naslov je obavezan",
              description: "Opis",
              descriptionPlaceholder: "Opis",
            },
            fileUpload: {
              dragAndDrop: "Povucite datoteke ovdje ili kliknite za pregled",
              dropFiles: "Ispustite datoteke ovdje...",
              selectedFiles: "Odabrane datoteke:",
              removeFile: "Ukloni datoteku",
            },
            buttons: {
              cancel: "Odustani",
              save: "Spremi",
              creating: "Stvaranje...",
            },
            validation: {
              atLeastOneFile: "Potrebna je najmanje jedna datoteka.",
            },
            success: "Baza znanja je uspješno stvorena.",
          },
          edit: {
            title: "Uredi bazu znanja",
            description: "Ažurirajte detalje baze znanja u nastavku.",
            fields: {
              title: "Naslov",
              titlePlaceholder: "Naslov",
              titleRequired: "Naslov je obavezan",
              description: "Opis",
              descriptionPlaceholder: "Opis",
            },
            fileUpload: {
              currentFiles: "Trenutne datoteke:",
              dragAndDrop: "Povucite datoteke ovdje ili kliknite za pregled",
              dropFiles: "Ispustite datoteke ovdje...",
              selectedFiles: "Odabrane datoteke:",
              removeFile: "Ukloni datoteku",
            },
            buttons: {
              cancel: "Odustani",
              save: "Spremi",
              saving: "Spremanje...",
            },
            success: "Baza znanja je uspješno ažurirana.",
          },
          editFormTemplateModal: {
            title: "Uredi Predložak Obrasca",
            formTemplateName: "Naziv Predloška Obrasca",
            formTemplateDescription: "Opis Predloška Obrasca",
            descriptionPlaceholder: "Unesite opis predloška obrasca...",
            referenceDocuments: "Referentni Dokumenti (Neobavezno)",
            uploadFiles: "Prijenos Datoteka",
            knowledgeBase: "Baza Znanja",
            formFields: "Polja Obrasca",
            suggest: "Predloži",
            fieldPlaceholder: "Dodaj naziv polja...",
            cancel: "Odustani",
            updateFormTemplate: "Ažuriraj Predložak Obrasca"
          },
        },
        editCustom: {
          title: "Uredi prilagođene upute",
          currentInstructions: "Trenutne upute:",
          save: "Spremi",
          cancel: "Odustani",
        },
      },
      optimizeChecklistModal: {
        title: "Optimiziraj Kontrolnu Listu",
        customInstructionsLabel: "Prilagođene Upute (Neobavezno)",
        customInstructionsHelperText: "Unesite dodatne upute koje treba uzeti u obzir pri odgovaranju na pitanja kontrolne liste",
        analyzing: "Analizira se...",
        analyzeButton: "Analiziraj Kontrolnu Listu",
        analyzingMessage: "Analizira se vaša kontrolna lista za mogućnosti optimizacije...",
        cancelAnalysis: "Otkaži Analizu",
        downloading: "Preuzima se...",
        downloadCsv: "Preuzmi CSV",
        questionsNeedingOptimization: "Pitanja koja Trebaju Optimizaciju",
        questionsAlreadyOptimized: "Već Optimizirana Pitanja",
        selected: "Odabrano",
        select: "Odaberi",
        original: "Izvorni",
        suggestedImprovement: "Predloženo Poboljšanje",
        policyContext: "Kontekst Pravila",
        currentAnswer: "Trenutni Odgovor",
        showLess: "Prikaži Manje",
        showMore: "Prikaži Više",
        optimizationsSelectedText: "optimizacija odabrano za primjenu",
        applying: "Primjenjuje se...",
        applySelectedOptimizations: "Primijeni Odabrane Optimizacije",
        uploadDocumentsTitle: "Prenesite dokument(e) koje kontrolna lista treba prihvatiti *",
        uploadDocumentsHelperText: "Prenesite dokumente koji trebaju zadovoljiti sve zahtjeve kontrolne liste kako biste pomogli identificirati pitanja koja mogu biti prestriga",
        customInstructionsPlaceholder: "npr., Uzmite u obzir da je ovo pedijatrijska studija pri procjeni zahtjeva vezanih uz dob, Ovaj protokol je za intervenciju niskog rizika, itd."
      },
      optimizeOutlineModal: {
        title: "Optimiziraj Nacrt",
        description: "Prenesite referentni dokument koji predstavlja visokokvalitetan primjer vrste izvještaja koji želite generirati. Sustav će generirati izvještaj koristeći vaš trenutni nacrt i bazu znanja, usporediti ga s referentnim i predložiti poboljšanja za odjeljke nacrta.",
        groundTruthDocument: "Referentni Dokument",
        customInstructionsLabel: "Prilagođene Upute (Neobavezno)",
        customInstructionsHelperText: "Pružite dodatne smjernice za proces optimizacije",
        customInstructionsPlaceholder: "npr., Fokusirajte se na poboljšanje tehničke dubine, osigurajte usklađenost s određenim standardima, itd.",
        characters: "znakova",
        analyzingOutline: "Analizira se nacrt i generiraju optimizacije...",
        cancelAnalysis: "Otkaži Analizu",
        optimizationResults: "Rezultati Optimizacije",
        sectionsNeedOptimization: "odjeljaka treba optimizaciju",
        downloadCsv: "Preuzmi CSV",
        section: "Odjeljak",
        accepted: "Prihvaćeno",
        accept: "Prihvati",
        originalSectionDescription: "Izvorni Opis Odjeljka",
        suggestedSectionDescription: "Predloženi Opis Odjeljka",
        generatedContent: "Generirani Sadržaj (s trenutnim opisom)",
        groundTruthReference: "Referentna Poveznica",
        showLess: "Prikaži Manje",
        showMore: "Prikaži Više",
        close: "Zatvori",
        cancel: "Otkaži",
        optimizing: "Optimizira se...",
        optimizeOutline: "Optimiziraj Nacrt",
        applyOptimizations: "Primijeni {{count}} Optimizaciju/a"
      }
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
        allUsersToggleTooltip: "Пребацуј између приказа само твоје историје или историје свих корисника",
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
      compare: {
        title: "Упореди документе",
        subtitle: "Изаберите два документа за поређење",
        selectFirstDocument: "Изаберите први документ",
        selectSecondDocument: "Изаберите други документ",
        pleaseSelect: "Молимо изаберите...",
        documentA: "Документ А",
        documentB: "Документ Б",
        compareDocuments: "Упореди документе",
        comparison: "Поређење",
        noDocumentsFound: "Нису пронађени документи",
        selectTwoDocuments: "Молимо изаберите два документа за поређење",
        loadingComparison: "Учитавање поређења...",
        topicList: "Листа тема",
        clickToBrowse: "Кликните за претрагу или превуците овде",
        supportedFormats: "Подржани формати: PDF, TXT, DOCX",
        analysisType: "Тип анализе",
        quickAnalysis: "Брза анализа",
        detailedAnalysis: "Детаљна анализа",
        comprehensiveAnalysis: "Свеобухватна анализа",
        analysisDepth: "Дубина анализе",
        surfaceLevel: "Површински ниво",
        moderate: "Умерено",
        deep: "Дубоко",
        veryDeep: "Веома дубоко",
        editTopicList: "Уреди листу тема"
      },
      match: {
        title: "Подударање докумената",
        subtitle: "Пронађите сличне документе на основу садржаја",
        selectDocument: "Изаберите документ за проналажење подударања",
        pleaseSelect: "Молимо изаберите документ...",
        sourceDocument: "Изворни документ",
        matchingDocuments: "Подударни документи",
        findMatches: "Пронађи подударања",
        similarityScore: "Резултат сличности",
        noDocumentsFound: "Нису пронађени документи",
        selectDocumentToMatch: "Молимо изаберите документ за проналажење подударања",
        loadingMatches: "Тражење подударања...",
        noMatchesFound: "Нису пронађени слични документи",
        matchResults: "Резултати подударања",
        similarity: "Сличност",
        matchingCriteria: "Критеријуми подударања",
        semanticSimilarity: "Семантичка сличност",
        keywordMatching: "Подударање кључних речи",
        structuralSimilarity: "Структурална сличност",
        threshold: "Праг",
        minimumSimilarity: "Минимална сличност",
        searchDepth: "Дубина претраге",
        maxResults: "Максимални број резултата",
        editFormTemplate: "Уреди шаблон обрасца"
      },
      knowledgeBases: {
        title: "Управљање базама знања",
        addKnowledgeBase: "Додај базу знања",
        emptyStateTitle: "Још увек немате базе знања",
        emptyStateDescription: "Додајте нову базу знања за почетак",
        tableHeaders: {
          title: "Наслов",
          description: "Опис",
          numberOfSources: "Број извора",
          embeddingModel: "Модел уграђивања",
          dateCreated: "Датум стварања",
          dateModified: "Датум измене",
          actions: "Радње"
        },
        status: {
          default: "Подразумевано",
          na: "Није доступно"
        },
        actions: {
          view: "Преглед",
          edit: "Уреди",
          delete: "Обриши",
          configure: "Конфигуриши"
        },
        deleteModal: {
          title: "Обриши базу знања",
          buttonText: "Обриши базу знања",
          description: "Ова база знања ће бити трајно обрисана. Да ли сте сигурни? Нећете моћи да поништите ову радњу.",
          confirmButton: "Обриши",
          cancelButton: "Откажи",
          successMessage: "База знања је успешно обрисана",
          errorMessage: "Дошло је до грешке приликом брисања базе знања"
        },
        modals: {
          add: {
            title: "Додај базу знања",
            description: "Направите нову базу знања пружањем детаља и отпремањем докумената испод.",
            fields: {
              title: "Наслов",
              titlePlaceholder: "Наслов",
              titleRequired: "Наслов је обавезан",
              description: "Опис",
              descriptionPlaceholder: "Опис",
            },
            fileUpload: {
              dragAndDrop: "Превуците датотеке овде или кликните за претрагу",
              dropFiles: "Испустите датотеке овде...",
              selectedFiles: "Изабране датотеке:",
              removeFile: "Уклони датотеку",
            },
            buttons: {
              cancel: "Откажи",
              save: "Сачувај",
              creating: "Стварање...",
            },
            validation: {
              atLeastOneFile: "Потребна је најмање једна датотека.",
            },
            success: "База знања је успешно направљена.",
          },
          edit: {
            title: "Уреди базу знања",
            description: "Ажурирајте детаље базе знања испод.",
            fields: {
              title: "Наслов",
              titlePlaceholder: "Наслов",
              titleRequired: "Наслов је обавезан",
              description: "Опис",
              descriptionPlaceholder: "Опис",
            },
            fileUpload: {
              currentFiles: "Тренутне датотеке:",
              dragAndDrop: "Превуците датотеке овде или кликните за претрагу",
              dropFiles: "Испустите датотеке овде...",
              selectedFiles: "Изабране датотеке:",
              removeFile: "Уклони датотеку",
            },
            buttons: {
              cancel: "Откажи",
              save: "Сачувај",
              saving: "Чување...",
            },
            success: "База знања је успешно ажурирана.",
          },
          editFormTemplateModal: {
            title: "Уреди Шаблон Форме",
            formTemplateName: "Назив Шаблона Форме",
            formTemplateDescription: "Опис Шаблона Форме",
            descriptionPlaceholder: "Унесите опис шаблона форме...",
            referenceDocuments: "Референтни Документи (Опционо)",
            uploadFiles: "Отпремање Датотека",
            knowledgeBase: "База Знања",
            formFields: "Поља Форме",
            suggest: "Предложи",
            fieldPlaceholder: "Додајте назив поља...",
            cancel: "Откажи",
            updateFormTemplate: "Ажурирај Шаблон Форме"
          },
        },
        editCustom: {
          title: "Уреди прилагођена упутства",
          currentInstructions: "Тренутна упутства:",
          save: "Сачувај",
          cancel: "Откажи",
        },
      },
      optimizeChecklistModal: {
        title: "Оптимизуј Контролну Листу",
        customInstructionsLabel: "Прилагођена Упутства (Опционо)",
        customInstructionsHelperText: "Унесите додатна упутства која треба узети у обзир при одговарању на питања контролне листе",
        analyzing: "Анализира се...",
        analyzeButton: "Анализирај Контролну Листу",
        analyzingMessage: "Анализира се ваша контролна листа за могућности оптимизације...",
        cancelAnalysis: "Откажи Анализу",
        downloading: "Преузима се...",
        downloadCsv: "Преузми CSV",
        questionsNeedingOptimization: "Питања која Требају Оптимизацију",
        questionsAlreadyOptimized: "Већ Оптимизована Питања",
        selected: "Одабрано",
        select: "Одабери",
        original: "Изворни",
        suggestedImprovement: "Предложено Побољшање",
        policyContext: "Контекст Правила",
        currentAnswer: "Тренутни Одговор",
        showLess: "Прикажи Мање",
        showMore: "Прикажи Више",
        optimizationsSelectedText: "оптимизација одабрано за примену",
        applying: "Примењује се...",
        applySelectedOptimizations: "Примени Одабране Оптимизације",
        uploadDocumentsTitle: "Пренесите документ(е) које контролна листа треба да прихвати *",
        uploadDocumentsHelperText: "Пренесите документе који треба да задовоље све захтеве контролне листе како бисте помогли идентификовању питања која могу бити престрога",
        customInstructionsPlaceholder: "нпр., Узмите у обзир да је ово педијатријска студија при процени захтева везаних за узраст, Овај протокол је за интервенцију ниског ризика, итд."
      },
      optimizeOutlineModal: {
        title: "Оптимизуј Нацрт",
        description: "Пренесите референтни документ који представља висококвалитетан пример врсте извештаја који желите да генеришете. Систем ће генерисати извештај користећи ваш тренутни нацрт и базу знања, упоредити га са референтним и предложити побољшања за одељке нацрта.",
        groundTruthDocument: "Референтни Документ",
        customInstructionsLabel: "Прилагођена Упутства (Опционо)",
        customInstructionsHelperText: "Пружите додатне смернице за процес оптимизације",
        customInstructionsPlaceholder: "нпр., Фокусирајте се на побољшање техничке дубине, обезбедите усклађеност са одређеним стандардима, итд.",
        characters: "карактера",
        analyzingOutline: "Анализира се нацрт и генеришу оптимизације...",
        cancelAnalysis: "Откажи Анализу",
        optimizationResults: "Резултати Оптимизације",
        sectionsNeedOptimization: "одељака треба оптимизацију",
        downloadCsv: "Преузми CSV",
        section: "Одељак",
        accepted: "Прихваћено",
        accept: "Прихвати",
        originalSectionDescription: "Изворни Опис Одељка",
        suggestedSectionDescription: "Предложени Опис Одељка",
        generatedContent: "Генерисани Садржај (са тренутним описом)",
        groundTruthReference: "Референтна Веза",
        showLess: "Прикажи Мање",
        showMore: "Прикажи Више",
        close: "Затвори",
        cancel: "Откажи",
        optimizing: "Оптимизује се...",
        optimizeOutline: "Оптимизуј Нацрт",
        applyOptimizations: "Примени {{count}} Оптимизацију/а"
      }
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
        allUsersToggleTooltip: "Preklapljaj med prikazom samo tvoje zgodovine ali zgodovine vseh uporabnikov",
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
      compare: {
        title: "Primerjaj dokumente",
        subtitle: "Izberite dva dokumenta za primerjavo",
        selectFirstDocument: "Izberite prvi dokument",
        selectSecondDocument: "Izberite drugi dokument",
        pleaseSelect: "Prosimo izberite...",
        documentA: "Dokument A",
        documentB: "Dokument B",
        compareDocuments: "Primerjaj dokumente",
        comparison: "Primerjava",
        noDocumentsFound: "Ni najdenih dokumentov",
        selectTwoDocuments: "Prosimo izberite dva dokumenta za primerjavo",
        loadingComparison: "Nalaganje primerjave...",
        topicList: "Seznam tem",
        clickToBrowse: "Kliknite za brskanje ali povlecite sem",
        supportedFormats: "Podprti formati: PDF, TXT, DOCX",
        analysisType: "Vrsta analize",
        quickAnalysis: "Hitra analiza",
        detailedAnalysis: "Podrobna analiza",
        comprehensiveAnalysis: "Obsežna analiza",
        analysisDepth: "Globina analize",
        surfaceLevel: "Površinska raven",
        moderate: "Zmerna",
        deep: "Globoka",
        veryDeep: "Zelo globoka",
        editTopicList: "Uredi seznam tem"
      },
      match: {
        title: "Ujemanje dokumentov",
        subtitle: "Poiščite podobne dokumente na podlagi vsebine",
        selectDocument: "Izberite dokument za iskanje ujemanj",
        pleaseSelect: "Prosimo izberite dokument...",
        sourceDocument: "Izvorni dokument",
        matchingDocuments: "Ujemajoči dokumenti",
        findMatches: "Poišči ujemanja",
        similarityScore: "Rezultat podobnosti",
        noDocumentsFound: "Ni najdenih dokumentov",
        selectDocumentToMatch: "Prosimo izberite dokument za iskanje ujemanj",
        loadingMatches: "Iskanje ujemanj...",
        noMatchesFound: "Ni najdenih podobnih dokumentov",
        matchResults: "Rezultati ujemanja",
        similarity: "Podobnost",
        matchingCriteria: "Kriteriji ujemanja",
        semanticSimilarity: "Semantična podobnost",
        keywordMatching: "Ujemanje ključnih besed",
        structuralSimilarity: "Strukturna podobnost",
        threshold: "Prag",
        minimumSimilarity: "Minimalna podobnost",
        searchDepth: "Globina iskanja",
        maxResults: "Največje število rezultatov",
        editFormTemplate: "Uredi predlogo obrazca"
      },
      knowledgeBases: {
        title: "Upravljanje baz znanja",
        addKnowledgeBase: "Dodaj bazo znanja",
        emptyStateTitle: "Še nimate baz znanja",
        emptyStateDescription: "Dodajte novo bazo znanja za začetek",
        tableHeaders: {
          title: "Naslov",
          description: "Opis",
          numberOfSources: "Število virov",
          embeddingModel: "Model vgradnje",
          dateCreated: "Datum nastanka",
          dateModified: "Datum spremembe",
          actions: "Dejanja"
        },
        status: {
          default: "Privzeto",
          na: "Ni na voljo"
        },
        actions: {
          view: "Pregled",
          edit: "Uredi",
          delete: "Izbriši",
          configure: "Konfiguriraj"
        },
        deleteModal: {
          title: "Izbriši bazo znanja",
          buttonText: "Izbriši bazo znanja",
          description: "Ta baza znanja bo trajno izbrisana. Ste prepričani? Tega dejanja ne boste mogli razveljaviti.",
          confirmButton: "Izbriši",
          cancelButton: "Prekliči",
          successMessage: "Baza znanja je bila uspešno izbrisana",
          errorMessage: "Pri brisanju baze znanja je prišlo do napake"
        },
        modals: {
          add: {
            title: "Dodaj bazo znanja",
            description: "Ustvarite novo bazo znanja z zagotavljanjem podrobnosti in nalaganjem dokumentov spodaj.",
            fields: {
              title: "Naslov",
              titlePlaceholder: "Naslov",
              titleRequired: "Naslov je obvezen",
              description: "Opis",
              descriptionPlaceholder: "Opis",
            },
            fileUpload: {
              dragAndDrop: "Povlecite datoteke sem ali kliknite za brskanje",
              dropFiles: "Spustite datoteke sem...",
              selectedFiles: "Izbrane datoteke:",
              removeFile: "Odstrani datoteko",
            },
            buttons: {
              cancel: "Prekliči",
              save: "Shrani",
              creating: "Ustvarjanje...",
            },
            validation: {
              atLeastOneFile: "Potrebna je vsaj ena datoteka.",
            },
            success: "Baza znanja je bila uspešno ustvarjena.",
          },
          edit: {
            title: "Uredi bazo znanja",
            description: "Posodobite podrobnosti baze znanja spodaj.",
            fields: {
              title: "Naslov",
              titlePlaceholder: "Naslov",
              titleRequired: "Naslov je obvezen",
              description: "Opis",
              descriptionPlaceholder: "Opis",
            },
            fileUpload: {
              currentFiles: "Trenutne datoteke:",
              dragAndDrop: "Povlecite datoteke sem ali kliknite za brskanje",
              dropFiles: "Spustite datoteke sem...",
              selectedFiles: "Izbrane datoteke:",
              removeFile: "Odstrani datoteko",
            },
            buttons: {
              cancel: "Prekliči",
              save: "Shrani",
              saving: "Shranjevanje...",
            },
            success: "Baza znanja je bila uspešno posodobljena.",
          },
          editFormTemplateModal: {
            title: "Uredi Predlogo Obrazca",
            formTemplateName: "Ime Predloge Obrazca",
            formTemplateDescription: "Opis Predloge Obrazca",
            descriptionPlaceholder: "Vnesite opis predloge obrazca...",
            referenceDocuments: "Referenčni Dokumenti (Neobvezno)",
            uploadFiles: "Naložite Datoteke",
            knowledgeBase: "Baza Znanja",
            formFields: "Polja Obrazca",
            suggest: "Predlagaj",
            fieldPlaceholder: "Dodajte ime polja...",
            cancel: "Prekliči",
            updateFormTemplate: "Posodobi Predlogo Obrazca"
          },
        },
        editCustom: {
          title: "Uredi prilagojene navodila",
          currentInstructions: "Trenutna navodila:",
          save: "Shrani",
          cancel: "Prekliči",
        },
      },
      optimizeChecklistModal: {
        title: "Optimiziraj Kontrolni Seznam",
        customInstructionsLabel: "Prilagojeni Navodila (Neobvezno)",
        customInstructionsHelperText: "Vnesite dodatna navodila, ki jih je treba upoštevati pri odgovarjanju na vprašanja kontrolnega seznama",
        analyzing: "Analiziranje...",
        analyzeButton: "Analiziraj Kontrolni Seznam",
        analyzingMessage: "Analizira se vaš kontrolni seznam za možnosti optimizacije...",
        cancelAnalysis: "Prekini Analizo",
        downloading: "Prenašanje...",
        downloadCsv: "Prenesi CSV",
        questionsNeedingOptimization: "Vprašanja, ki Potrebujejo Optimizacijo",
        questionsAlreadyOptimized: "Že Optimizirana Vprašanja",
        selected: "Izbrano",
        select: "Izberi",
        original: "Izvirni",
        suggestedImprovement: "Predlagana Izboljšava",
        policyContext: "Kontekst Pravil",
        currentAnswer: "Trenutni Odgovor",
        showLess: "Prikaži Manj",
        showMore: "Prikaži Več",
        optimizationsSelectedText: "optimizacij izbranih za uporabo",
        applying: "Uveljavljanje...",
        applySelectedOptimizations: "Uveljavi Izbrane Optimizacije",
        uploadDocumentsTitle: "Naložite dokument(e), ki jih mora kontrolni seznam sprejeti *",
        uploadDocumentsHelperText: "Naložite dokumente, ki morajo izpolnjevati vse zahteve kontrolnega seznama, da pomagate identificirati vprašanja, ki so morda prestroga",
        customInstructionsPlaceholder: "npr., Upoštevajte, da je to pediatrična študija pri ocenjevanju starostnih zahtev, Ta protokol je za nizko tvegano intervencijo, itd."
      },
      optimizeOutlineModal: {
        title: "Optimiziraj Oris",
        description: "Naložite referenčni dokument, ki predstavlja visokokakovosten primer vrste poročila, ki ga želite ustvariti. Sistem bo ustvaril poročilo z uporabo vašega trenutnega orisa in baze znanja, ga primerjal z referenčnim in predlagal izboljšave za razdelke orisa.",
        groundTruthDocument: "Referenčni Dokument",
        customInstructionsLabel: "Prilagojeni Navodila (Neobvezno)",
        customInstructionsHelperText: "Zagotovite dodatne smernice za proces optimizacije",
        customInstructionsPlaceholder: "npr., Osredotočite se na izboljšanje tehnične globine, zagotovite skladnost s specifičnimi standardi, itd.",
        characters: "znakov",
        analyzingOutline: "Analiziranje orisa in ustvarjanje optimizacij...",
        cancelAnalysis: "Prekini Analizo",
        optimizationResults: "Rezultati Optimizacije",
        sectionsNeedOptimization: "razdelkov potrebuje optimizacijo",
        downloadCsv: "Prenesi CSV",
        section: "Razdelek",
        accepted: "Sprejeto",
        accept: "Sprejmi",
        originalSectionDescription: "Izvirni Opis Razdelka",
        suggestedSectionDescription: "Predlagani Opis Razdelka",
        generatedContent: "Ustvarjena Vsebina (s trenutnim opisom)",
        groundTruthReference: "Referenčna Povezava",
        showLess: "Prikaži Manj",
        showMore: "Prikaži Več",
        close: "Zapri",
        cancel: "Prekliči",
        optimizing: "Optimiziranje...",
        optimizeOutline: "Optimiziraj Oris",
        applyOptimizations: "Uveljavi {{count}} Optimizacij"
      }
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
      addKnowledgeBase: "Přidat znalostní bázi",
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
      addKnowledgeBase: "Pridať znalostnú bázu",
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
      addKnowledgeBase: "Tudásbázis hozzáadása",
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
      addKnowledgeBase: "Adăugați bază de cunoștințe",
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
      addKnowledgeBase: "Добавете база знания",
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
      addKnowledgeBase: "Dodajte bazu znanja",
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
      addKnowledgeBase: "Додајте базу знања",
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
      addKnowledgeBase: "Dodajte bazo znanja",
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

  // Add Archive translations for Central European languages
  if (!resources.de.common.archive) {
    resources.de.common.archive = {
      tabs: {
        review: "Überprüfen",
        generate: "Generieren",
        compare: "Vergleichen", 
        match: "Zuordnen"
      },
      metadata: {
        questions: "Fragen",
        questions_one: "Frage",
        fields: "Felder",
        fields_one: "Feld",
        documents: "Dokumente",
        documents_one: "Dokument",
        digitized: "digitalisiert",
        handwritten: "handgeschrieben"
      },
      feedback: {
        positive: "Positives Feedback für dieses Ergebnis geben",
        negative: "Negatives Feedback für dieses Ergebnis geben",
        hasFeedback: "Dieses Ergebnis hat Feedback"
      },
      emptyMessages: {
        review: "Noch keine Überprüfungshistorie",
        generate: "Noch keine Generierungshistorie",
        compare: "Noch keine Vergleichshistorie",
        match: "Noch keine Zuordnungshistorie"
      },
      deleteConfirmation: "Sind Sie sicher, dass Sie dieses Element löschen möchten?",
      history: "Historie",
      allUsers: "Alle Benutzer"
    }
  }

  if (!resources.fr.common.archive) {
    resources.fr.common.archive = {
      tabs: {
        review: "Réviser",
        generate: "Générer",
        compare: "Comparer",
        match: "Correspondre"
      },
      metadata: {
        questions: "questions",
        questions_one: "question", 
        fields: "champs",
        fields_one: "champ",
        documents: "documents",
        documents_one: "document",
        digitized: "numérisé",
        handwritten: "manuscrit"
      },
      feedback: {
        positive: "Donner un retour positif pour ce résultat",
        negative: "Donner un retour négatif pour ce résultat",
        hasFeedback: "Ce résultat a un retour"
      },
      emptyMessages: {
        review: "Aucun historique de révision encore",
        generate: "Aucun historique de génération encore",
        compare: "Aucun historique de comparaison encore",
        match: "Aucun historique de correspondance encore"
      },
      deleteConfirmation: "Êtes-vous sûr de vouloir supprimer cet élément?",
      history: "Historique",
      allUsers: "Tous les utilisateurs"
    }
  }

  if (!resources.it.common.archive) {
    resources.it.common.archive = {
      tabs: {
        review: "Rivedi",
        generate: "Genera",
        compare: "Confronta",
        match: "Abbina"
      },
      metadata: {
        questions: "domande",
        questions_one: "domanda",
        fields: "campi",
        fields_one: "campo",
        documents: "documenti",
        documents_one: "documento",
        digitized: "digitalizzato",
        handwritten: "scritto a mano"
      },
      feedback: {
        positive: "Dai feedback positivo per questo risultato",
        negative: "Dai feedback negativo per questo risultato",
        hasFeedback: "Questo risultato ha feedback"
      },
      emptyMessages: {
        review: "Nessuna cronologia di revisione ancora",
        generate: "Nessuna cronologia di generazione ancora",
        compare: "Nessuna cronologia di confronto ancora",
        match: "Nessuna cronologia di abbinamento ancora"
      },
      deleteConfirmation: "Sei sicuro di voler eliminare questo elemento?",
      history: "Cronologia",
      allUsers: "Tutti gli utenti"
    }
  }

  if (!resources.es.common.archive) {
    resources.es.common.archive = {
      tabs: {
        review: "Revisar",
        generate: "Generar",
        compare: "Comparar",
        match: "Coincidir"
      },
      metadata: {
        questions: "preguntas",
        questions_one: "pregunta",
        fields: "campos",
        fields_one: "campo",
        documents: "documentos", 
        documents_one: "documento",
        digitized: "digitalizado",
        handwritten: "manuscrito"
      },
      feedback: {
        positive: "Dar retroalimentación positiva para este resultado",
        negative: "Dar retroalimentación negativa para este resultado",
        hasFeedback: "Este resultado tiene retroalimentación"
      },
      emptyMessages: {
        review: "Aún no hay historial de revisión",
        generate: "Aún no hay historial de generación",
        compare: "Aún no hay historial de comparación",
        match: "Aún no hay historial de coincidencias"
      },
      deleteConfirmation: "¿Estás seguro de que quieres eliminar este elemento?",
      history: "Historial",
      allUsers: "Todos los usuarios"
    }
  }

  if (!resources.pt.common.archive) {
    resources.pt.common.archive = {
      tabs: {
        review: "Revisar",
        generate: "Gerar",
        compare: "Comparar",
        match: "Corresponder"
      },
      metadata: {
        questions: "perguntas",
        questions_one: "pergunta",
        fields: "campos",
        fields_one: "campo",
        documents: "documentos",
        documents_one: "documento",
        digitized: "digitalizado",
        handwritten: "manuscrito"
      },
      feedback: {
        positive: "Dar feedback positivo para este resultado",
        negative: "Dar feedback negativo para este resultado",
        hasFeedback: "Este resultado tem feedback"
      },
      emptyMessages: {
        review: "Ainda não há histórico de revisão",
        generate: "Ainda não há histórico de geração",
        compare: "Ainda não há histórico de comparação",
        match: "Ainda não há histórico de correspondência"
      },
      deleteConfirmation: "Tem certeza de que deseja excluir este item?",
      history: "Histórico",
      allUsers: "Todos os usuários"
    }
  }

  if (!resources.nl.common.archive) {
    resources.nl.common.archive = {
      tabs: {
        review: "Beoordelen",
        generate: "Genereren",
        compare: "Vergelijken",
        match: "Matchen"
      },
      metadata: {
        questions: "vragen",
        questions_one: "vraag",
        fields: "velden",
        fields_one: "veld",
        documents: "documenten",
        documents_one: "document",
        digitized: "gedigitaliseerd",
        handwritten: "handgeschreven"
      },
      feedback: {
        positive: "Geef positieve feedback voor dit resultaat",
        negative: "Geef negatieve feedback voor dit resultaat",
        hasFeedback: "Dit resultaat heeft feedback"
      },
      emptyMessages: {
        review: "Nog geen beoordelingsgeschiedenis",
        generate: "Nog geen genereringsgeschiedenis", 
        compare: "Nog geen vergelijkingsgeschiedenis",
        match: "Nog geen matchgeschiedenis"
      },
      deleteConfirmation: "Weet je zeker dat je dit item wilt verwijderen?",
      history: "Geschiedenis",
      allUsers: "Alle gebruikers"
    }
  }

  if (!resources.hu.common.archive) {
    resources.hu.common.archive = {
      tabs: {
        review: "Áttekintés",
        generate: "Generálás",
        compare: "Összehasonlítás",
        match: "Egyeztetés"
      },
      metadata: {
        questions: "kérdések",
        questions_one: "kérdés",
        fields: "mezők",
        fields_one: "mező",
        documents: "dokumentumok",
        documents_one: "dokumentum",
        digitized: "digitalizált",
        handwritten: "kézzel írt"
      },
      feedback: {
        positive: "Pozitív visszajelzés adása ehhez az eredményhez",
        negative: "Negatív visszajelzés adása ehhez az eredményhez",
        hasFeedback: "Ennek az eredménynek van visszajelzése"
      },
      emptyMessages: {
        review: "Még nincs áttekintési előzmény",
        generate: "Még nincs generálási előzmény",
        compare: "Még nincs összehasonlítási előzmény",
        match: "Még nincs egyeztetési előzmény"
      },
      deleteConfirmation: "Biztosan törölni szeretné ezt az elemet?",
      history: "Előzmények",
      allUsers: "Minden felhasználó"
    }
  }

  if (!resources.cs.common.archive) {
    resources.cs.common.archive = {
      tabs: {
        review: "Kontrola",
        generate: "Generování",
        compare: "Porovnání",
        match: "Shoda"
      },
      metadata: {
        questions: "otázky",
        questions_one: "otázka",
        fields: "pole",
        fields_one: "pole",
        documents: "dokumenty",
        documents_one: "dokument",
        digitized: "digitalizovaný",
        handwritten: "ručně psaný"
      },
      feedback: {
        positive: "Poskytnout pozitivní zpětnou vazbu pro tento výsledek",
        negative: "Poskytnout negativní zpětnou vazbu pro tento výsledek",
        hasFeedback: "Tento výsledek má zpětnou vazbu"
      },
      emptyMessages: {
        review: "Zatím žádná historie kontroly",
        generate: "Zatím žádná historie generování",
        compare: "Zatím žádná historie porovnání",
        match: "Zatím žádná historie shod"
      },
      deleteConfirmation: "Jste si jisti, že chcete smazat tuto položku?",
      history: "Historie",
      allUsers: "Všichni uživatelé"
    }
  }

  if (!resources.sk.common.archive) {
    resources.sk.common.archive = {
      tabs: {
        review: "Kontrola",
        generate: "Generovanie",
        compare: "Porovnanie", 
        match: "Zhoda"
      },
      metadata: {
        questions: "otázky",
        questions_one: "otázka",
        fields: "polia",
        fields_one: "pole",
        documents: "dokumenty",
        documents_one: "dokument",
        digitized: "digitalizovaný",
        handwritten: "ručne písaný"
      },
      feedback: {
        positive: "Poskytnúť pozitívnu spätnú väzbu pre tento výsledok",
        negative: "Poskytnúť negatívnu spätnú väzbu pre tento výsledok",
        hasFeedback: "Tento výsledok má spätnú väzbu"
      },
      emptyMessages: {
        review: "Zatiaľ žiadna história kontroly",
        generate: "Zatiaľ žiadna história generovania",
        compare: "Zatiaľ žiadna história porovnania",
        match: "Zatiaľ žiadna história zhôd"
      },
      deleteConfirmation: "Ste si istí, že chcete zmazať túto položku?",
      history: "História",
      allUsers: "Všetci používatelia"
    }
  }

  if (!resources.sl.common.archive) {
    resources.sl.common.archive = {
      tabs: {
        review: "Pregled",
        generate: "Generiranje",
        compare: "Primerjava",
        match: "Ujemanje"
      },
      metadata: {
        questions: "vprašanja",
        questions_one: "vprašanje",
        fields: "polja",
        fields_one: "polje",
        documents: "dokumenti",
        documents_one: "dokument",
        digitized: "digitalizirano",
        handwritten: "ročno pisano"
      },
      feedback: {
        positive: "Podajte pozitivno povratno informacijo za ta rezultat",
        negative: "Podajte negativno povratno informacijo za ta rezultat",
        hasFeedback: "Ta rezultat ima povratno informacijo"
      },
      emptyMessages: {
        review: "Še ni zgodovine pregledov",
        generate: "Še ni zgodovine generiranja",
        compare: "Še ni zgodovine primerjav",
        match: "Še ni zgodovine ujemanj"
      },
      deleteConfirmation: "Ali ste prepričani, da želite izbrisati ta element?",
      history: "Zgodovina",
      allUsers: "Vsi uporabniki"
    }
  }

  // Add Settings extensions for Central European languages
  if (resources.de.common.settings) {
    Object.assign(resources.de.common.settings, {
      currentPassword: "Aktuelles Passwort",
      newPassword: "Neues Passwort",
      confirmPassword: "Passwort bestätigen",
      save: "Speichern",
      system: "System",
      lightMode: "Heller Modus",
      darkMode: "Dunkler Modus",
      deleteAccountDescription: "Ihre Daten und alles, was mit Ihrem Konto verknüpft ist, dauerhaft löschen.",
      delete: "Löschen"
    })
  }

  if (resources.fr.common.settings) {
    Object.assign(resources.fr.common.settings, {
      currentPassword: "Mot de Passe Actuel",
      newPassword: "Nouveau Mot de Passe",
      confirmPassword: "Confirmer le Mot de Passe",
      save: "Enregistrer",
      system: "Système",
      lightMode: "Mode Clair",
      darkMode: "Mode Sombre",
      deleteAccountDescription: "Supprimer définitivement vos données et tout ce qui est associé à votre compte.",
      delete: "Supprimer"
    })
  }

  if (resources.it.common.settings) {
    Object.assign(resources.it.common.settings, {
      currentPassword: "Password Attuale",
      newPassword: "Nuova Password",
      confirmPassword: "Conferma Password",
      save: "Salva",
      system: "Sistema",
      lightMode: "Modalità Chiara",
      darkMode: "Modalità Scura",
      deleteAccountDescription: "Elimina permanentemente i tuoi dati e tutto ciò che è associato al tuo account.",
      delete: "Elimina"
    })
  }

  if (resources.es.common.settings) {
    Object.assign(resources.es.common.settings, {
      currentPassword: "Contraseña Actual",
      newPassword: "Nueva Contraseña",
      confirmPassword: "Confirmar Contraseña",
      save: "Guardar",
      system: "Sistema",
      lightMode: "Modo Claro",
      darkMode: "Modo Oscuro",
      deleteAccountDescription: "Eliminar permanentemente tus datos y todo lo asociado con tu cuenta.",
      delete: "Eliminar"
    })
  }

  if (resources.pt.common.settings) {
    Object.assign(resources.pt.common.settings, {
      currentPassword: "Senha Atual",
      newPassword: "Nova Senha",
      confirmPassword: "Confirmar Senha",
      save: "Salvar",
      system: "Sistema",
      lightMode: "Modo Claro",
      darkMode: "Modo Escuro",
      deleteAccountDescription: "Excluir permanentemente seus dados e tudo associado à sua conta.",
      delete: "Excluir"
    })
  }

  if (resources.nl.common.settings) {
    Object.assign(resources.nl.common.settings, {
      currentPassword: "Huidig Wachtwoord",
      newPassword: "Nieuw Wachtwoord",
      confirmPassword: "Bevestig Wachtwoord",
      save: "Opslaan",
      system: "Systeem",
      lightMode: "Lichte Modus",
      darkMode: "Donkere Modus",
      deleteAccountDescription: "Verwijder je gegevens en alles wat aan je account is gekoppeld permanent.",
      delete: "Verwijderen"
    })
  }

  if (resources.hu.common.settings) {
    Object.assign(resources.hu.common.settings, {
      currentPassword: "Jelenlegi Jelszó",
      newPassword: "Új Jelszó",
      confirmPassword: "Jelszó Megerősítése",
      save: "Mentés",
      system: "Rendszer",
      lightMode: "Világos Mód",
      darkMode: "Sötét Mód",
      deleteAccountDescription: "Véglegesen törölje adatait és mindent, ami a fiókjához kapcsolódik.",
      delete: "Törlés"
    })
  }

  if (resources.cs.common.settings) {
    Object.assign(resources.cs.common.settings, {
      currentPassword: "Aktuální Heslo",
      newPassword: "Nové Heslo",
      confirmPassword: "Potvrdit Heslo",
      save: "Uložit",
      system: "Systém",
      lightMode: "Světlý Režim",
      darkMode: "Tmavý Režim",
      deleteAccountDescription: "Trvale smazat vaše data a vše, co je spojeno s vaším účtem.",
      delete: "Smazat"
    })
  }

  if (resources.sk.common.settings) {
    Object.assign(resources.sk.common.settings, {
      currentPassword: "Aktuálne Heslo",
      newPassword: "Nové Heslo",
      confirmPassword: "Potvrdiť Heslo",
      save: "Uložiť",
      system: "Systém",
      lightMode: "Svetlý Režim",
      darkMode: "Tmavý Režim",
      deleteAccountDescription: "Trvalo zmazať vaše údaje a všetko, čo je spojené s vaším účtom.",
      delete: "Zmazať"
    })
  }

  if (resources.sl.common.settings) {
    Object.assign(resources.sl.common.settings, {
      currentPassword: "Trenutno Geslo",
      newPassword: "Novo Geslo",
      confirmPassword: "Potrdite Geslo",
      save: "Shrani",
      system: "Sistem",
      lightMode: "Svetli Način",
      darkMode: "Temni Način",
      deleteAccountDescription: "Trajno izbriši svoje podatke in vse, kar je povezano z vašim računom.",
      delete: "Izbriši"
    })
  }
}
