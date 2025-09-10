// Baltic and Eastern European Languages Translations
// Estonian (et), Latvian (lv), Lithuanian (lt), Greek (el)

export const addBalticEasternEuropeanTranslations = (resources: any) => {
  // Estonian
  resources.et = {
    common: {
      navigation: {
        dashboard: "Armatuurlaud",
        review: "Ülevaade",
        generate: "Genereeri",
        compare: "Võrdle",
        match: "Sobivus",
        modelSelection: "Mudeli valik",
        knowledgeBases: "Teadmusbaasid",
        archive: "Arhiiv",
        settings: "Seaded",
        admin: "Administraator",
        menu: "Menüü",
        tools: "Tööriistad",
        configurations: "Konfiguratsioonid",
        myProfile: "Minu profiil",
        logout: "Logi välja",
        loggedInAs: "Sisse logitud kui: {{email}}",
      },
      buttons: {
        upload: "Laadi üles",
        download: "Laadi alla",
        save: "Salvesta",
        cancel: "Tühista",
        delete: "Kustuta",
        edit: "Muuda",
        submit: "Saada",
        close: "Sulge",
        next: "Järgmine",
        previous: "Eelmine",
        confirm: "Kinnita",
        back: "Tagasi",
      },
      forms: {
        firstName: "Eesnimi",
        lastName: "Perekonnanimi",
        email: "E-post",
        password: "Parool",
        confirmPassword: "Kinnita parool",
        currentPassword: "Praegune parool",
        newPassword: "Uus parool",
        required: "Nõutav",
        optional: "Valikuline",
        emailPlaceholder: "Sisesta oma e-posti aadress",
        passwordPlaceholder: "Sisesta oma parool",
      },
      dropdowns: {
        selectKnowledgeBase: "Vali teadmusbaas...",
      },
      chatbot: {
        placeholder: "Kirjuta oma sõnum siia...",
        send: "Saada",
        newChat: "Uus vestlus",
        clearHistory: "Kustuta ajalugu",
        typing: "AI kirjutab...",
        error: "Vabandust, midagi läks valesti. Proovi uuesti.",
        welcome: "Tere! Kuidas saan teid täna aidata?",
        welcomeMessageWithSource: "Valige teadmusbaas või laadige üles failid, seejärel esitage küsimus.",
        welcomeMessageGeneral: "Küsige mult mida tahes! Teadmusbaasi otsinguks valige esmalt teadmusbaas.",
      },
      settings: {
        title: "Seaded",
        account: "Konto",
        language: "Keel",
        dangerZone: "Ohutsoon",
        preferredLanguage: "Eelistatud keel",
        saveLanguagePreference: "Salvesta keele eelistus",
        deleteAccount: "Kustuta konto",
        deleteAccountWarning: "Seda toimingut ei saa tagasi võtta.",
        profile: "Profiil",
        security: "Turvalisus",
        changePassword: "Muuda parool",
        appearance: "Välimus",
      },
      errors: {
        somethingWentWrong: "Midagi läks valesti",
        tryAgain: "Proovi uuesti",
        invalidEmail: "Vigane e-posti aadress",
        passwordTooShort: "Parool on liiga lühike",
        passwordsDoNotMatch: "Paroolid ei ühti",
        networkError: "Võrgu viga. Kontrolli ühendust.",
        unauthorized: "Sul pole selle toimingu sooritamiseks õigust.",
        notFound: "Taotletud ressurssi ei leitud.",
      },
      common: {
        loading: "Laadimine...",
        noData: "Andmed pole saadaval",
        success: "Edukas!",
        failed: "Ebaõnnestus",
        welcome: "Tere tulemast",
        goodbye: "Nägemist",
        yes: "Jah",
        no: "Ei",
        ok: "OK",
        search: "Otsi",
        filter: "Filter",
        sort: "Sorteeri",
        view: "Vaata",
        copy: "Kopeeri",
        paste: "Kleebi",
        cut: "Lõika",
      },
      review: {
        pageTitle: "Dokumentide ülevaade",
        pageDescription: "Vaadake üle dokument kasutaja määratletud kontrollnimekirja ja poliitika andmebaasi alusel.",
        knowledgeBaseTitle: "Teadmusbaas",
        knowledgeBaseDescription: "Klõpsake valimiseks",
        checklistTitle: "Kontrollnimekiri",
        checklistDescription: "Klõpsake valimiseks",
        customInstructionsTitle: "Kohandatud juhised (valikuline)",
        customInstructionsPlaceholder: "Sisestage täiendavad juhised, mida tuleb arvestada kontrollnimekirja küsimustele vastamisel...",
        customInstructionsHelp: "{{count}}/2000 märki. Need juhised lisatakse töötlemise ajal igale küsimusele.",
        searchModeHelp: "Vektorotsing annab kiireid, sihipäraseid tulemusi. Täisdokumendi analüüs uurib kogu teadmusbaasi sisu.",
        processingFile: "Faili töötlemine...",
        processingFiles: "Failide töötlemine...",
        selectKnowledgeBaseTitle: "Valige teadmusbaas",
        selectChecklistTitle: "Valige kontrollnimekiri",
        noResults: "Tulemusi pole veel",
        uploadDocuments: "Laadige üles üks või mitu dokumenti valitud kontrollnimekirja suhtes ülevaatamiseks",
        results: "Tulemused",
        downloadReport: "Laadi alla aruanne",
        downloadCsv: "Laadi alla CSV",
        clearResults: "Tühjenda tulemused",
        copyReport: "Kopeeri aruanne",
        reportCopied: "Aruanne kopeeriti lõikelauale!",
        reviewButton: "Ülevaade",
        consultDocuments: "Konsulteeri dokumentidega",
        noChecklistsAvailable: "Kontrollnimekirju pole saadaval. Alustamiseks looge oma esimene kontrollnimekiri.",
        createChecklist: "Loo kontrollnimekiri",
        editChecklist: "Redigeeri kontrollnimekirja",
        checklistName: "Kontrollnimekirja nimi",
        checklistNamePlaceholder: "Sisestage kontrollnimekirja nimi...",
        checklistDescriptionLabel: "Kirjeldus",
        checklistDescriptionPlaceholder: "Sisestage kontrollnimekirja kirjeldus automaatsete küsimuste soovituste jaoks (vähemalt 10 märki)...",
        questions: "Küsimused",
        suggest: "Soovita",
        suggesting: "Soovitan...",
        optimize: "Optimeeri",
        optimizeTooltip: "Optimeerimisfunktsiooni lubamiseks peab olema valitud teadmusbaas",
        optimizeTooltipEnabled: "Optimeeri küsimusi valitud teadmusbaasi põhjal",
        allUsersToggleTooltip: "Lülita ainult oma ajaloo või kõigi kasutajate ajaloo vaatamise vahel",
        uploadFiles: "Laadi üles failid",
        knowledgeBase: "Teadmusbaas",
        referenceDocuments: "Viitedokumendid (valikuline)",
        selectKnowledgeBasePlaceholder: "Valige teadmusbaas...",
        noKnowledgeBasesAvailable: "Teadmusbaase pole saadaval. Selle funktsiooni kasutamiseks looge esmalt üks.",
        copyQuestions: "Kopeeri küsimused",
        questionsCopied: "Küsimused kopeeriti lõikelauale",
        noQuestionsToCopy: "Kopeerimiseks küsimusi pole",
        failedToCopyQuestions: "Küsimuste lõikelauale kopeerimine ebaõnnestus",
        saveChecklist: "Salvesta kontrollnimekiri",
        cancel: "Tühista",
        deleteChecklist: "Kustuta kontrollnimekiri"
      },
      compare: {
        title: "Dokumentide võrdlus",
        subtitle: "Valige kaks dokumenti võrdlemiseks",
        selectFirstDocument: "Valige esimene dokument",
        selectSecondDocument: "Valige teine dokument",
        pleaseSelect: "Palun valige...",
        documentA: "Dokument A",
        documentB: "Dokument B",
        compareDocuments: "Võrdle dokumente",
        comparison: "Võrdlus",
        noDocumentsFound: "Dokumente ei leitud",
        selectTwoDocuments: "Palun valige kaks dokumenti võrdlemiseks",
        loadingComparison: "Võrdluse laadimine...",
        topicList: "Teemade loend",
        clickToBrowse: "Klõpsake sirvimiseks või lohistage siia",
        supportedFormats: "Toetatud vormingud: PDF, TXT, DOCX",
        analysisType: "Analüüsi tüüp",
        quickAnalysis: "Kiire analüüs",
        detailedAnalysis: "Üksikasjalik analüüs",
        comprehensiveAnalysis: "Põhjalik analüüs",
        analysisDepth: "Analüüsi sügavus",
        surfaceLevel: "Pindmine tase",
        moderate: "Mõõdukas",
        deep: "Sügav",
        veryDeep: "Väga sügav",
        editTopicList: "Muuda teemade loendit"
      },
      match: {
        title: "Dokumentide vastavus",
        subtitle: "Leidke sarnased dokumendid sisu põhjal",
        selectDocument: "Valige dokument vastete leidmiseks",
        pleaseSelect: "Palun valige dokument...",
        sourceDocument: "Lähte dokument",
        matchingDocuments: "Vastavad dokumendid",
        findMatches: "Leia vasteid",
        similarityScore: "Sarnasus skoor",
        noDocumentsFound: "Dokumente ei leitud",
        selectDocumentToMatch: "Palun valige dokument vastete leidmiseks",
        loadingMatches: "Vastete otsimine...",
        noMatchesFound: "Sarnaseid dokumente ei leitud",
        matchResults: "Vastete tulemused",
        similarity: "Sarnasus",
        matchingCriteria: "Vastete kriteeriumid",
        semanticSimilarity: "Semantiline sarnasus",
        keywordMatching: "Märksõnade vastavus",
        structuralSimilarity: "Struktuuriline sarnasus",
        threshold: "Lävi",
        minimumSimilarity: "Minimaalne sarnasus",
        searchDepth: "Otsingu sügavus",
        maxResults: "Maksimaalne tulemuste arv",
        editFormTemplate: "Muuda vormi malli"
      },
      knowledgeBases: {
        title: "Teadmusbaaside haldamine",
        addKnowledgeBase: "Lisa teadmusbaas",
        emptyStateTitle: "Teil pole veel teadmusbaase",
        emptyStateDescription: "Alustamiseks lisage uus teadmusbaas",
        tableHeaders: {
          title: "Pealkiri",
          description: "Kirjeldus",
          numberOfSources: "Allikate arv",
          embeddingModel: "Põimimismudel",
          dateCreated: "Loomise kuupäev",
          dateModified: "Muutmise kuupäev",
          actions: "Tegevused"
        },
        status: {
          default: "Vaikimisi",
          na: "Pole saadaval"
        },
        actions: {
          view: "Vaata",
          edit: "Muuda",
          delete: "Kustuta",
          configure: "Seadista"
        },
        deleteModal: {
          title: "Kustuta teadmusbaas",
          buttonText: "Kustuta teadmusbaas",
          description: "See teadmusbaas kustutatakse jäädavalt. Kas olete kindel? Seda toimingut ei saa tagasi võtta.",
          confirmButton: "Kustuta",
          cancelButton: "Tühista",
          successMessage: "Teadmusbaas kustutati edukalt",
          errorMessage: "Teadmusbaasi kustutamisel tekkis viga"
        },
        modals: {
          add: {
            title: "Lisa teadmusbaas",
            description: "Looge uus teadmusbaas, andes üksikasjad ja laadides dokumendid allpool üles.",
            fields: {
              title: "Pealkiri",
              titlePlaceholder: "Pealkiri",
              titleRequired: "Pealkiri on nõutav",
              description: "Kirjeldus",
              descriptionPlaceholder: "Kirjeldus",
            },
            fileUpload: {
              dragAndDrop: "Lohistage failid siia või klõpsake sirvimiseks",
              dropFiles: "Kukutage failid siia...",
              selectedFiles: "Valitud failid:",
              removeFile: "Eemalda fail",
            },
            buttons: {
              cancel: "Tühista",
              save: "Salvesta",
              creating: "Loomine...",
            },
            validation: {
              atLeastOneFile: "Vähemalt üks fail on vajalik.",
            },
            success: "Teadmusbaas loodi edukalt.",
          },
          edit: {
            title: "Muuda teadmusbaasi",
            description: "Värskendage teadmusbaasi üksikasju allpool.",
            fields: {
              title: "Pealkiri",
              titlePlaceholder: "Pealkiri",
              titleRequired: "Pealkiri on nõutav",
              description: "Kirjeldus",
              descriptionPlaceholder: "Kirjeldus",
            },
            fileUpload: {
              currentFiles: "Praegused failid:",
              dragAndDrop: "Lohistage failid siia või klõpsake sirvimiseks",
              dropFiles: "Kukutage failid siia...",
              selectedFiles: "Valitud failid:",
              removeFile: "Eemalda fail",
            },
            buttons: {
              cancel: "Tühista",
              save: "Salvesta",
              saving: "Salvestamine...",
            },
            success: "Teadmusbaas värskendati edukalt.",
          },
          editFormTemplateModal: {
            title: "Muuda Vormi Malli",
            formTemplateName: "Vormi Malli Nimi",
            formTemplateDescription: "Vormi Malli Kirjeldus",
            descriptionPlaceholder: "Sisesta vormi malli kirjeldus...",
            referenceDocuments: "Viitedokumendid (Valikuline)",
            uploadFiles: "Laadi Failid Üles",
            knowledgeBase: "Teadmusbaas",
            formFields: "Vormi Väljad",
            suggest: "Soovita",
            fieldPlaceholder: "Lisa välja nimi...",
            cancel: "Tühista",
            updateFormTemplate: "Värskenda Vormi Malli"
          },
        },
        editCustom: {
          title: "Muuda kohandatud juhiseid",
          currentInstructions: "Praegused juhised:",
          save: "Salvesta",
          cancel: "Tühista",
        },
      },
      optimizeChecklistModal: {
        title: "Optimeerige Kontroll-loend",
        customInstructionsLabel: "Kohandatud Juhised (Valikuline)",
        customInstructionsHelperText: "Sisestage täiendavad juhised, mida tuleks kontroll-loendi küsimustele vastamisel arvesse võtta",
        analyzing: "Analüüsimine...",
        analyzeButton: "Analüüsi Kontroll-loend",
        analyzingMessage: "Analüüsitakse teie kontroll-loendit optimeerimise võimaluste jaoks...",
        cancelAnalysis: "Tühista Analüüs",
        downloading: "Allalaadimine...",
        downloadCsv: "Laadi alla CSV",
        questionsNeedingOptimization: "Optimeerimist Vajavad Küsimused",
        questionsAlreadyOptimized: "Juba Optimeeritud Küsimused",
        selected: "Valitud",
        select: "Vali",
        original: "Algne",
        suggestedImprovement: "Soovitatud Parandus",
        policyContext: "Poliitika Kontekst",
        currentAnswer: "Praegune Vastus",
        showLess: "Näita Vähem",
        showMore: "Näita Rohkem",
        optimizationsSelectedText: "optimeerimist valitud rakendamiseks",
        applying: "Rakendamine...",
        applySelectedOptimizations: "Rakenda Valitud Optimeerimised",
        uploadDocumentsTitle: "Laadige üles dokument(id), mida kontroll-loend peaks aktsepteerima *",
        uploadDocumentsHelperText: "Laadige üles dokumendid, mis peaksid vastama kõigile kontroll-loendi nõuetele, et aidata tuvastada küsimusi, mis võivad olla liiga ranged",
        customInstructionsPlaceholder: "nt, Arvestage, et see on lasteuuringu puhul vanusega seotud nõuete hindamisel, See protokoll on madala riskiga sekkumiseks, jne."
      },
      optimizeOutlineModal: {
        title: "Optimeerige Ülevaade",
        description: "Laadige üles referentsdokument, mis esindab kõrgekvaliteetset näidet aruande tüübist, mida soovite genereerida. Süsteem genereerib aruande, kasutades teie praegust ülevaadet ja teadmusbaasi, võrdleb seda referentsiga ja soovitab parandusi ülevaate jaotistele.",
        groundTruthDocument: "Referentsdokument",
        customInstructionsLabel: "Kohandatud Juhised (Valikuline)",
        customInstructionsHelperText: "Andke täiendavad juhised optimeerimisprotsessiks",
        customInstructionsPlaceholder: "nt, Keskenduge tehnilise sügavuse parandamisele, tagage vastavus konkreetsetele standarditele, jne.",
        characters: "tähemärki",
        analyzingOutline: "Analüüsitakse ülevaadet ja genereeritakse optimeerimisi...",
        cancelAnalysis: "Tühista Analüüs",
        optimizationResults: "Optimeerimise Tulemused",
        sectionsNeedOptimization: "jaotist vajab optimeerimist",
        downloadCsv: "Laadi alla CSV",
        section: "Jaotis",
        accepted: "Aktsepteeritud",
        accept: "Aktsepteeri",
        originalSectionDescription: "Algne Jaotise Kirjeldus",
        suggestedSectionDescription: "Soovitatud Jaotise Kirjeldus",
        generatedContent: "Genereeritud Sisu (praeguse kirjeldusega)",
        groundTruthReference: "Referentsviide",
        showLess: "Näita Vähem",
        showMore: "Näita Rohkem",
        close: "Sulge",
        cancel: "Tühista",
        optimizing: "Optimeerimine...",
        optimizeOutline: "Optimeerige Ülevaade",
        applyOptimizations: "Rakenda {{count}} Optimeerimist"
      }
    },
  }

  // Latvian
  resources.lv = {
    common: {
      navigation: {
        dashboard: "Vadības panelis",
        review: "Pārskats",
        generate: "Ģenerēt",
        compare: "Salīdzināt",
        match: "Atbilstība",
        modelSelection: "Modeļa izvēle",
        knowledgeBases: "Zināšanu bāzes",
        archive: "Arhīvs",
        settings: "Iestatījumi",
        admin: "Administrators",
        menu: "Izvēlne",
        tools: "Rīki",
        configurations: "Konfigurācijas",
        myProfile: "Mans profils",
        logout: "Iziet",
        loggedInAs: "Pieteicies kā: {{email}}",
      },
      buttons: {
        upload: "Augšupielādēt",
        download: "Lejupielādēt",
        save: "Saglabāt",
        cancel: "Atcelt",
        delete: "Dzēst",
        edit: "Rediģēt",
        submit: "Iesniegt",
        close: "Aizvērt",
        next: "Nākamais",
        previous: "Iepriekšējais",
        confirm: "Apstiprināt",
        back: "Atpakaļ",
      },
      forms: {
        firstName: "Vārds",
        lastName: "Uzvārds",
        email: "E-pasts",
        password: "Parole",
        confirmPassword: "Apstiprināt paroli",
        currentPassword: "Pašreizējā parole",
        newPassword: "Jaunā parole",
        required: "Obligāts",
        optional: "Neobligāts",
        emailPlaceholder: "Ievadiet savu e-pasta adresi",
        passwordPlaceholder: "Ievadiet savu paroli",
      },
      dropdowns: {
        selectKnowledgeBase: "Izvēlieties zināšanu bāzi...",
      },
      chatbot: {
        placeholder: "Ierakstiet savu ziņu šeit...",
        send: "Sūtīt",
        newChat: "Jauna saruna",
        clearHistory: "Dzēst vēsturi",
        typing: "AI raksta...",
        error: "Atvainojiet, kaut kas nogāja greizi. Mēģiniet vēlreiz.",
        welcome: "Sveiki! Kā es varu jums palīdzēt šodien?",
        welcomeMessageWithSource: "Izvēlieties zināšanu bāzi vai augšupielādējiet failus, pēc tam uzdodiet jautājumu.",
        welcomeMessageGeneral: "Jautājiet man jebko! Zināšanu bāzes meklēšanai vispirms izvēlieties zināšanu bāzi.",
      },
      settings: {
        title: "Iestatījumi",
        account: "Konts",
        language: "Valoda",
        dangerZone: "Bīstamā zona",
        preferredLanguage: "Vēlamā valoda",
        saveLanguagePreference: "Saglabāt valodas izvēli",
        deleteAccount: "Dzēst kontu",
        deleteAccountWarning: "Šo darbību nevar atsaukt.",
        profile: "Profils",
        security: "Drošība",
        changePassword: "Mainīt paroli",
        appearance: "Izskats",
      },
      errors: {
        somethingWentWrong: "Kaut kas nogāja greizi",
        tryAgain: "Mēģiniet vēlreiz",
        invalidEmail: "Nederīga e-pasta adrese",
        passwordTooShort: "Parole ir pārāk īsa",
        passwordsDoNotMatch: "Paroles nesakrīt",
        networkError: "Tīkla kļūda. Pārbaudiet savienojumu.",
        unauthorized: "Jums nav atļaujas veikt šo darbību.",
        notFound: "Pieprasītais resurss nav atrasts.",
      },
      common: {
        loading: "Ielādē...",
        noData: "Nav pieejamu datu",
        success: "Panākumi!",
        failed: "Neizdevās",
        welcome: "Laipni lūdzam",
        goodbye: "Uz redzēšanos",
        yes: "Jā",
        no: "Nē",
        ok: "Labi",
        search: "Meklēt",
        filter: "Filtrs",
        sort: "Kārtot",
        view: "Skatīt",
        copy: "Kopēt",
        paste: "Ielīmēt",
        cut: "Izgriezt",
      },
      review: {
        pageTitle: "Dokumentu pārskats",
        pageDescription: "Pārskatiet dokumentu, pamatojoties uz lietotāja definēto kontrolsarakstu un politikas datubāzi.",
        knowledgeBaseTitle: "Zināšanu bāze",
        knowledgeBaseDescription: "Noklikšķiniet, lai atlasītu",
        checklistTitle: "Kontrolsaraksts",
        checklistDescription: "Noklikšķiniet, lai atlasītu",
        customInstructionsTitle: "Pielāgotas instrukcijas (neobligāti)",
        customInstructionsPlaceholder: "Ievadiet papildu instrukcijas, kas jāņem vērā, atbildot uz kontrolsaraksta jautājumiem...",
        customInstructionsHelp: "{{count}}/2000 rakstzīmes. Šīs instrukcijas tiks pievienotas katram jautājumam apstrādes laikā.",
        searchModeHelp: "Vektoru meklēšana nodrošina ātrus, mērķtiecīgus rezultātus. Pilna dokumenta analīze pēta visu zināšanu bāzes saturu.",
        processingFile: "Apstrādā failu...",
        processingFiles: "Apstrādā failus...",
        selectKnowledgeBaseTitle: "Atlasiet zināšanu bāzi",
        selectChecklistTitle: "Atlasiet kontrolsarakstu",
        noResults: "Vēl nav rezultātu",
        uploadDocuments: "Augšupielādējiet vienu vai vairākus dokumentus pārskatīšanai pret atlasīto kontrolsarakstu",
        results: "Rezultāti",
        downloadReport: "Lejupielādēt pārskatu",
        downloadCsv: "Lejupielādēt CSV",
        clearResults: "Notīrīt rezultātus",
        copyReport: "Kopēt pārskatu",
        reportCopied: "Pārskats nokopēts starpliktuvē!",
        reviewButton: "Pārskats",
        consultDocuments: "Konsultēties ar dokumentiem",
        noChecklistsAvailable: "Nav pieejamu kontrolsarakstu. Izveidojiet savu pirmo kontrolsarakstu, lai sāktu.",
        createChecklist: "Izveidot kontrolsarakstu",
        editChecklist: "Rediģēt kontrolsarakstu",
        checklistName: "Kontrolsaraksta nosaukums",
        checklistNamePlaceholder: "Ievadiet kontrolsaraksta nosaukumu...",
        checklistDescriptionLabel: "Apraksts",
        checklistDescriptionPlaceholder: "Ievadiet kontrolsaraksta aprakstu automātiskajiem jautājumu ieteikumiem (vismaz 10 rakstzīmes)...",
        questions: "Jautājumi",
        suggest: "Ieteikt",
        suggesting: "Ieteic...",
        optimize: "Optimizēt",
        optimizeTooltip: "Lai iespējotu optimizācijas funkciju, jāatlasa zināšanu bāze",
        optimizeTooltipEnabled: "Optimizēt jautājumus, pamatojoties uz atlasīto zināšanu bāzi",
        allUsersToggleTooltip: "Pārslēgties starp tikai savas vēstures vai visu lietotāju vēstures skatīšanu",
        uploadFiles: "Augšupielādēt failus",
        knowledgeBase: "Zināšanu bāze",
        referenceDocuments: "Atsauces dokumenti (neobligāti)",
        selectKnowledgeBasePlaceholder: "Atlasiet zināšanu bāzi...",
        noKnowledgeBasesAvailable: "Nav pieejamu zināšanu bāzu. Vispirms izveidojiet vienu, lai izmantotu šo funkciju.",
        copyQuestions: "Kopēt jautājumus",
        questionsCopied: "Jautājumi nokopēti starpliktuvē",
        noQuestionsToCopy: "Nav jautājumu, ko kopēt",
        failedToCopyQuestions: "Neizdevās nokopēt jautājumus starpliktuvē",
        saveChecklist: "Saglabāt kontrolsarakstu",
        cancel: "Atcelt",
        deleteChecklist: "Dzēst kontrolsarakstu"
      },
      compare: {
        title: "Salīdzināt dokumentus",
        subtitle: "Atlasiet divus dokumentus salīdzināšanai",
        selectFirstDocument: "Atlasiet pirmo dokumentu",
        selectSecondDocument: "Atlasiet otro dokumentu",
        pleaseSelect: "Lūdzu atlasiet...",
        documentA: "Dokuments A",
        documentB: "Dokuments B",
        compareDocuments: "Salīdzināt dokumentus",
        comparison: "Salīdzinājums",
        noDocumentsFound: "Dokumenti nav atrasti",
        selectTwoDocuments: "Lūdzu atlasiet divus dokumentus salīdzināšanai",
        loadingComparison: "Salīdzinājuma ielāde...",
        topicList: "Tēmu saraksts",
        clickToBrowse: "Noklikšķiniet pārlūkošanai vai velciet šeit",
        supportedFormats: "Atbalstītie formāti: PDF, TXT, DOCX",
        analysisType: "Analīzes veids",
        quickAnalysis: "Ātra analīze",
        detailedAnalysis: "Detalizēta analīze",
        comprehensiveAnalysis: "Visaptveroša analīze",
        analysisDepth: "Analīzes dziļums",
        surfaceLevel: "Virsmas līmenis",
        moderate: "Mērens",
        deep: "Dziļš",
        veryDeep: "Ļoti dziļš",
        editTopicList: "Rediģēt tēmu sarakstu"
      },
      match: {
        title: "Dokumentu atbilstība",
        subtitle: "Atrodiet līdzīgus dokumentus, pamatojoties uz saturu",
        selectDocument: "Atlasiet dokumentu atbilstību meklēšanai",
        pleaseSelect: "Lūdzu atlasiet dokumentu...",
        sourceDocument: "Avota dokuments",
        matchingDocuments: "Atbilstošie dokumenti",
        findMatches: "Atrast atbilstības",
        similarityScore: "Līdzības rādītājs",
        noDocumentsFound: "Dokumenti nav atrasti",
        selectDocumentToMatch: "Lūdzu atlasiet dokumentu atbilstību meklēšanai",
        loadingMatches: "Atbilstību meklēšana...",
        noMatchesFound: "Līdzīgi dokumenti nav atrasti",
        matchResults: "Atbilstību rezultāti",
        similarity: "Līdzība",
        matchingCriteria: "Atbilstības kritēriji",
        semanticSimilarity: "Semantiskā līdzība",
        keywordMatching: "Atslēgvārdu atbilstība",
        structuralSimilarity: "Strukturālā līdzība",
        threshold: "Slieksnis",
        minimumSimilarity: "Minimālā līdzība",
        searchDepth: "Meklēšanas dziļums",
        maxResults: "Maksimālais rezultātu skaits",
        editFormTemplate: "Rediģēt formas veidni"
      },
      knowledgeBases: {
        title: "Zināšanu bāzu pārvaldība",
        addKnowledgeBase: "Pievienot zināšanu bāzi",
        emptyStateTitle: "Jums vēl nav zināšanu bāzu",
        emptyStateDescription: "Pievienojiet jaunu zināšanu bāzi, lai sāktu",
        tableHeaders: {
          title: "Virsraksts",
          description: "Apraksts",
          numberOfSources: "Avotu skaits",
          embeddingModel: "Iegulšanas modelis",
          dateCreated: "Izveides datums",
          dateModified: "Modificēšanas datums",
          actions: "Darbības"
        },
        status: {
          default: "Noklusējuma",
          na: "Nav pieejams"
        },
        actions: {
          view: "Skatīt",
          edit: "Rediģēt",
          delete: "Dzēst",
          configure: "Konfigurēt"
        },
        deleteModal: {
          title: "Dzēst zināšanu bāzi",
          buttonText: "Dzēst zināšanu bāzi",
          description: "Šī zināšanu bāze tiks neatgriezeniski dzēsta. Vai esat pārliecināts? Jūs nevarēsiet atsaukt šo darbību.",
          confirmButton: "Dzēst",
          cancelButton: "Atcelt",
          successMessage: "Zināšanu bāze tika veiksmīgi dzēsta",
          errorMessage: "Radās kļūda, dzēšot zināšanu bāzi"
        },
        modals: {
          add: {
            title: "Pievienot zināšanu bāzi",
            description: "Izveidojiet jaunu zināšanu bāzi, norādot detaļas un augšupielādējot dokumentus zemāk.",
            fields: {
              title: "Virsraksts",
              titlePlaceholder: "Virsraksts",
              titleRequired: "Virsraksts ir obligāts",
              description: "Apraksts",
              descriptionPlaceholder: "Apraksts",
            },
            fileUpload: {
              dragAndDrop: "Velciet failus šeit vai noklikšķiniet pārlūkošanai",
              dropFiles: "Nometiet failus šeit...",
              selectedFiles: "Atlasītie faili:",
              removeFile: "Noņemt failu",
            },
            buttons: {
              cancel: "Atcelt",
              save: "Saglabāt",
              creating: "Izveide...",
            },
            validation: {
              atLeastOneFile: "Nepieciešams vismaz viens fails.",
            },
            success: "Zināšanu bāze tika veiksmīgi izveidota.",
          },
          edit: {
            title: "Rediģēt zināšanu bāzi",
            description: "Atjauniniet zināšanu bāzes detaļas zemāk.",
            fields: {
              title: "Virsraksts",
              titlePlaceholder: "Virsraksts",
              titleRequired: "Virsraksts ir obligāts",
              description: "Apraksts",
              descriptionPlaceholder: "Apraksts",
            },
            fileUpload: {
              currentFiles: "Pašreizējie faili:",
              dragAndDrop: "Velciet failus šeit vai noklikšķiniet pārlūkošanai",
              dropFiles: "Nometiet failus šeit...",
              selectedFiles: "Atlasītie faili:",
              removeFile: "Noņemt failu",
            },
            buttons: {
              cancel: "Atcelt",
              save: "Saglabāt",
              saving: "Saglabāšana...",
            },
            success: "Zināšanu bāze tika veiksmīgi atjaunināta.",
          },
          editFormTemplateModal: {
            title: "Rediģēt Formas Veidni",
            formTemplateName: "Formas Veidnes Nosaukums",
            formTemplateDescription: "Formas Veidnes Apraksts",
            descriptionPlaceholder: "Ievadiet formas veidnes aprakstu...",
            referenceDocuments: "Atsauces Dokumenti (Izvēles)",
            uploadFiles: "Augšupielādēt Failus",
            knowledgeBase: "Zināšanu Bāze",
            formFields: "Formas Lauki",
            suggest: "Ieteikt",
            fieldPlaceholder: "Pievienot lauka nosaukumu...",
            cancel: "Atcelt",
            updateFormTemplate: "Atjaunināt Formas Veidni"
          },
        },
        editCustom: {
          title: "Rediģēt pielāgotās instrukcijas",
          currentInstructions: "Pašreizējās instrukcijas:",
          save: "Saglabāt",
          cancel: "Atcelt",
        },
      },
      optimizeChecklistModal: {
        title: "Optimizēt Kontrolsarakstu",
        customInstructionsLabel: "Pielāgotas Instrukcijas (Neobligāti)",
        customInstructionsHelperText: "Ievadiet papildu instrukcijas, kas jāņem vērā, atbildot uz kontrolsaraksta jautājumiem",
        analyzing: "Analizē...",
        analyzeButton: "Analizēt Kontrolsarakstu",
        analyzingMessage: "Analizē jūsu kontrolsarakstu optimizācijas iespējām...",
        cancelAnalysis: "Atcelt Analīzi",
        downloading: "Lejupielādē...",
        downloadCsv: "Lejupielādēt CSV",
        questionsNeedingOptimization: "Jautājumi, Kam Nepieciešama Optimizācija",
        questionsAlreadyOptimized: "Jau Optimizēti Jautājumi",
        selected: "Atlasīts",
        select: "Atlasīt",
        original: "Oriģināls",
        suggestedImprovement: "Ieteiktais Uzlabojums",
        policyContext: "Politikas Konteksts",
        currentAnswer: "Pašreizējā Atbilde",
        showLess: "Rādīt Mazāk",
        showMore: "Rādīt Vairāk",
        optimizationsSelectedText: "optimizācijas atlasītas lietošanai",
        applying: "Piemēro...",
        applySelectedOptimizations: "Piemērot Atlasītās Optimizācijas",
        uploadDocumentsTitle: "Augšupielādējiet dokumentu(s), ko kontrolsarakstam jāpieņem *",
        uploadDocumentsHelperText: "Augšupielādējiet dokumentus, kam jāatbilst visām kontrolsaraksta prasībām, lai palīdzētu identificēt jautājumus, kas var būt pārāk stingri",
        customInstructionsPlaceholder: "piem., Ņemiet vērā, ka šī ir pediatriska pētījuma gadījumā, novērtējot ar vecumu saistītās prasības, Šis protokols ir zema riska iejaukšanās gadījumam, utt."
      },
      optimizeOutlineModal: {
        title: "Optimizēt Apceri",
        description: "Augšupielādējiet atsauces dokumentu, kas reprezentē augstas kvalitātes piemēru atskaites tipam, ko vēlaties ģenerēt. Sistēma ģenerēs atskaiti, izmantojot jūsu pašreizējo apceri un zināšanu bāzi, salīdzinās to ar atsauci un ieteiks uzlabojumus apceres sadaļām.",
        groundTruthDocument: "Atsauces Dokuments",
        customInstructionsLabel: "Pielāgotas Instrukcijas (Neobligāti)",
        customInstructionsHelperText: "Sniedziet papildu norādījumus optimizācijas procesam",
        customInstructionsPlaceholder: "piem., Koncentrējieties uz tehniskā dziļuma uzlabošanu, nodrošiniet atbilstību konkrētiem standartiem, utt.",
        characters: "rakstzīmes",
        analyzingOutline: "Analizē apceri un ģenerē optimizācijas...",
        cancelAnalysis: "Atcelt Analīzi",
        optimizationResults: "Optimizācijas Rezultāti",
        sectionsNeedOptimization: "sadaļas nepieciešama optimizācija",
        downloadCsv: "Lejupielādēt CSV",
        section: "Sadaļa",
        accepted: "Pieņemts",
        accept: "Pieņemt",
        originalSectionDescription: "Oriģinālais Sadaļas Apraksts",
        suggestedSectionDescription: "Ieteiktais Sadaļas Apraksts",
        generatedContent: "Ģenerētais Saturs (ar pašreizējo aprakstu)",
        groundTruthReference: "Atsauces Atsauce",
        showLess: "Rādīt Mazāk",
        showMore: "Rādīt Vairāk",
        close: "Aizvērt",
        cancel: "Atcelt",
        optimizing: "Optimizē...",
        optimizeOutline: "Optimizēt Apceri",
        applyOptimizations: "Piemērot {{count}} Optimizācijas"
      }
    },
  }

  // Lithuanian
  resources.lt = {
    common: {
      navigation: {
        dashboard: "Valdymo skydas",
        review: "Peržiūra",
        generate: "Generuoti",
        compare: "Palyginti",
        match: "Atitikimas",
        modelSelection: "Modelio pasirinkimas",
        knowledgeBases: "Žinių bazės",
        archive: "Archyvas",
        settings: "Nustatymai",
        admin: "Administratorius",
        menu: "Meniu",
        tools: "Įrankiai",
        configurations: "Konfigūracijos",
        myProfile: "Mano profilis",
        logout: "Atsijungti",
        loggedInAs: "Prisijungęs kaip: {{email}}",
      },
      buttons: {
        upload: "Įkelti",
        download: "Atsisiųsti",
        save: "Išsaugoti",
        cancel: "Atšaukti",
        delete: "Ištrinti",
        edit: "Redaguoti",
        submit: "Pateikti",
        close: "Uždaryti",
        next: "Kitas",
        previous: "Ankstesnis",
        confirm: "Patvirtinti",
        back: "Atgal",
      },
      forms: {
        firstName: "Vardas",
        lastName: "Pavardė",
        email: "El. paštas",
        password: "Slaptažodis",
        confirmPassword: "Patvirtinti slaptažodį",
        currentPassword: "Dabartinis slaptažodis",
        newPassword: "Naujas slaptažodis",
        required: "Privalomas",
        optional: "Neprivalomas",
        emailPlaceholder: "Įveskite savo el. pašto adresą",
        passwordPlaceholder: "Įveskite savo slaptažodį",
      },
      dropdowns: {
        selectKnowledgeBase: "Pasirinkite žinių bazę...",
      },
      chatbot: {
        placeholder: "Įrašykite savo žinutę čia...",
        send: "Siųsti",
        newChat: "Naujas pokalbis",
        clearHistory: "Išvalyti istoriją",
        typing: "AI rašo...",
        error: "Atsiprašome, kažkas nutiko. Bandykite dar kartą.",
        welcome: "Sveiki! Kaip galiu jums šiandien padėti?",
        welcomeMessageWithSource: "Pasirinkite žinių bazę arba įkelkite failus, tada užduokite klausimą.",
        welcomeMessageGeneral: "Klausykite manęs bet ko! Žinių bazės paieškai pirmiausia pasirinkite žinių bazę.",
      },
      settings: {
        title: "Nustatymai",
        account: "Paskyra",
        language: "Kalba",
        dangerZone: "Pavojaus zona",
        preferredLanguage: "Pageidaujama kalba",
        saveLanguagePreference: "Išsaugoti kalbos nustatymus",
        deleteAccount: "Ištrinti paskyrą",
        deleteAccountWarning: "Šio veiksmo negalima atšaukti.",
        profile: "Profilis",
        security: "Saugumas",
        changePassword: "Keisti slaptažodį",
        appearance: "Išvaizda",
      },
      errors: {
        somethingWentWrong: "Kažkas nutiko",
        tryAgain: "Bandykite dar kartą",
        invalidEmail: "Neteisingas el. pašto adresas",
        passwordTooShort: "Slaptažodis per trumpas",
        passwordsDoNotMatch: "Slaptažodžiai nesutampa",
        networkError: "Tinklo klaida. Patikrinkite ryšį.",
        unauthorized: "Neturite leidimo atlikti šį veiksmą.",
        notFound: "Prašomas išteklius nerastas.",
      },
      common: {
        loading: "Kraunama...",
        noData: "Nėra prieinamų duomenų",
        success: "Sėkmė!",
        failed: "Nepavyko",
        welcome: "Sveiki atvykę",
        goodbye: "Iki pasimatymo",
        yes: "Taip",
        no: "Ne",
        ok: "Gerai",
        search: "Ieškoti",
        filter: "Filtras",
        sort: "Rūšiuoti",
        view: "Peržiūrėti",
        copy: "Kopijuoti",
        paste: "Įklijuoti",
        cut: "Iškirpti",
      },
      review: {
        pageTitle: "Dokumentų peržiūra",
        pageDescription: "Peržiūrėkite dokumentą pagal vartotojo apibrėžtą kontrolinį sąrašą ir politikos duomenų bazę.",
        knowledgeBaseTitle: "Žinių bazė",
        knowledgeBaseDescription: "Spustelėkite pasirinkimui",
        checklistTitle: "Kontrolinis sąrašas",
        checklistDescription: "Spustelėkite pasirinkimui",
        customInstructionsTitle: "Pasirinktinės instrukcijos (neprivaloma)",
        customInstructionsPlaceholder: "Įveskite papildomas instrukcijas, kurias reikia atsižvelgti atsakant į kontrolinio sąrašo klausimus...",
        customInstructionsHelp: "{{count}}/2000 simbolių. Šios instrukcijos bus pridėtos prie kiekvieno klausimo apdorojimo metu.",
        searchModeHelp: "Vektorinė paieška pateikia greitus, tikslius rezultatus. Viso dokumento analizė tiria visą žinių bazės turinį.",
        processingFile: "Apdorojamas failas...",
        processingFiles: "Apdorojami failai...",
        selectKnowledgeBaseTitle: "Pasirinkite žinių bazę",
        selectChecklistTitle: "Pasirinkite kontrolinį sąrašą",
        noResults: "Dar nėra rezultatų",
        uploadDocuments: "Įkelkite vieną ar daugiau dokumentų peržiūrai pagal pasirinktą kontrolinį sąrašą",
        results: "Rezultatai",
        downloadReport: "Atsisiųsti ataskaitą",
        downloadCsv: "Atsisiųsti CSV",
        clearResults: "Išvalyti rezultatus",
        copyReport: "Kopijuoti ataskaitą",
        reportCopied: "Ataskaita nukopijuota į iškarpinę!",
        reviewButton: "Peržiūra",
        consultDocuments: "Konsultuotis su dokumentais",
        noChecklistsAvailable: "Nėra prieinamų kontrolinių sąrašų. Sukurkite savo pirmą kontrolinį sąrašą, kad pradėtumėte.",
        createChecklist: "Sukurti kontrolinį sąrašą",
        editChecklist: "Redaguoti kontrolinį sąrašą",
        checklistName: "Kontrolinio sąrašo pavadinimas",
        checklistNamePlaceholder: "Įveskite kontrolinio sąrašo pavadinimą...",
        checklistDescriptionLabel: "Aprašymas",
        checklistDescriptionPlaceholder: "Įveskite kontrolinio sąrašo aprašymą automatiniams klausimų pasiūlymams (mažiausiai 10 simbolių)...",
        questions: "Klausimai",
        suggest: "Pasiūlyti",
        suggesting: "Siūloma...",
        optimize: "Optimizuoti",
        optimizeTooltip: "Kad būtų įjungta optimizavimo funkcija, reikia pasirinkti žinių bazę",
        optimizeTooltipEnabled: "Optimizuoti klausimus pagal pasirinktą žinių bazę",
        allUsersToggleTooltip: "Perjungti tarp tik savo istorijos arba visų vartotojų istorijos peržiūros",
        uploadFiles: "Įkelti failus",
        knowledgeBase: "Žinių bazė",
        referenceDocuments: "Atskaitos dokumentai (neprivaloma)",
        selectKnowledgeBasePlaceholder: "Pasirinkite žinių bazę...",
        noKnowledgeBasesAvailable: "Nėra prieinamų žinių bazių. Pirmiausia sukurkite vieną, kad galėtumėte naudoti šią funkciją.",
        copyQuestions: "Kopijuoti klausimus",
        questionsCopied: "Klausimai nukopijuoti į iškarpinę",
        noQuestionsToCopy: "Nėra klausimų kopijuoti",
        failedToCopyQuestions: "Nepavyko nukopijuoti klausimų į iškarpinę",
        saveChecklist: "Išsaugoti kontrolinį sąrašą",
        cancel: "Atšaukti",
        deleteChecklist: "Ištrinti kontrolinį sąrašą"
      },
      compare: {
        title: "Palyginti dokumentus",
        subtitle: "Pasirinkite du dokumentus palyginimui",
        selectFirstDocument: "Pasirinkite pirmą dokumentą",
        selectSecondDocument: "Pasirinkite antrą dokumentą",
        pleaseSelect: "Prašome pasirinkti...",
        documentA: "Dokumentas A",
        documentB: "Dokumentas B",
        compareDocuments: "Palyginti dokumentus",
        comparison: "Palyginimas",
        noDocumentsFound: "Dokumentų nerasta",
        selectTwoDocuments: "Prašome pasirinkti du dokumentus palyginimui",
        loadingComparison: "Palyginimo įkėlimas...",
        topicList: "Temų sąrašas",
        clickToBrowse: "Spustelėkite naršymui arba nuvilkite čia",
        supportedFormats: "Palaikomi formatai: PDF, TXT, DOCX",
        analysisType: "Analizės tipas",
        quickAnalysis: "Greita analizė",
        detailedAnalysis: "Detali analizė",
        comprehensiveAnalysis: "Išsami analizė",
        analysisDepth: "Analizės gylis",
        surfaceLevel: "Paviršiaus lygis",
        moderate: "Vidutinis",
        deep: "Gilus",
        veryDeep: "Labai gilus",
        editTopicList: "Redaguoti temų sąrašą"
      },
      match: {
        title: "Dokumentų atitikimas",
        subtitle: "Raskite panašius dokumentus pagal turinį",
        selectDocument: "Pasirinkite dokumentą atitikimų paieškai",
        pleaseSelect: "Prašome pasirinkti dokumentą...",
        sourceDocument: "Šaltinio dokumentas",
        matchingDocuments: "Atitinkantys dokumentai",
        findMatches: "Rasti atitikimus",
        similarityScore: "Panašumo balas",
        noDocumentsFound: "Dokumentų nerasta",
        selectDocumentToMatch: "Prašome pasirinkti dokumentą atitikimų paieškai",
        loadingMatches: "Atitikimų paieška...",
        noMatchesFound: "Panašių dokumentų nerasta",
        matchResults: "Atitikimų rezultatai",
        similarity: "Panašumas",
        matchingCriteria: "Atitikimo kriterijai",
        semanticSimilarity: "Semantinis panašumas",
        keywordMatching: "Raktažodžių atitikimas",
        structuralSimilarity: "Struktūrinis panašumas",
        threshold: "Slenkstis",
        minimumSimilarity: "Minimalus panašumas",
        searchDepth: "Paieškos gylis",
        maxResults: "Maksimalus rezultatų skaičius",
        editFormTemplate: "Redaguoti formos šabloną"
      },
      knowledgeBases: {
        title: "Žinių bazių valdymas",
        addKnowledgeBase: "Pridėti žinių bazę",
        emptyStateTitle: "Dar neturite žinių bazių",
        emptyStateDescription: "Pridėkite naują žinių bazę, kad pradėtumėte",
        tableHeaders: {
          title: "Pavadinimas",
          description: "Aprašymas",
          numberOfSources: "Šaltinių skaičius",
          embeddingModel: "Įterpimo modelis",
          dateCreated: "Sukūrimo data",
          dateModified: "Modifikavimo data",
          actions: "Veiksmai"
        },
        status: {
          default: "Numatytasis",
          na: "Nepasiekiama"
        },
        actions: {
          view: "Peržiūrėti",
          edit: "Redaguoti",
          delete: "Ištrinti",
          configure: "Konfigūruoti"
        },
        deleteModal: {
          title: "Ištrinti žinių bazę",
          buttonText: "Ištrinti žinių bazę",
          description: "Ši žinių bazė bus negrįžtamai ištrinta. Ar esate tikri? Šio veiksmo negalėsite atšaukti.",
          confirmButton: "Ištrinti",
          cancelButton: "Atšaukti",
          successMessage: "Žinių bazė sėkmingai ištrinta",
          errorMessage: "Ištrynant žinių bazę įvyko klaida"
        },
        modals: {
          add: {
            title: "Pridėti žinių bazę",
            description: "Sukurkite naują žinių bazę pateikdami išsamią informaciją ir įkeldami dokumentus žemiau.",
            fields: {
              title: "Pavadinimas",
              titlePlaceholder: "Pavadinimas",
              titleRequired: "Pavadinimas yra privalomas",
              description: "Aprašymas",
              descriptionPlaceholder: "Aprašymas",
            },
            fileUpload: {
              dragAndDrop: "Nuvilkite failus čia arba spustelėkite naršymui",
              dropFiles: "Numeskite failus čia...",
              selectedFiles: "Pasirinkti failai:",
              removeFile: "Pašalinti failą",
            },
            buttons: {
              cancel: "Atšaukti",
              save: "Išsaugoti",
              creating: "Kuriama...",
            },
            validation: {
              atLeastOneFile: "Reikalingas bent vienas failas.",
            },
            success: "Žinių bazė sėkmingai sukurta.",
          },
          edit: {
            title: "Redaguoti žinių bazę",
            description: "Atnaujinkite žinių bazės informaciją žemiau.",
            fields: {
              title: "Pavadinimas",
              titlePlaceholder: "Pavadinimas",
              titleRequired: "Pavadinimas yra privalomas",
              description: "Aprašymas",
              descriptionPlaceholder: "Aprašymas",
            },
            fileUpload: {
              currentFiles: "Dabartiniai failai:",
              dragAndDrop: "Nuvilkite failus čia arba spustelėkite naršymui",
              dropFiles: "Numeskite failus čia...",
              selectedFiles: "Pasirinkti failai:",
              removeFile: "Pašalinti failą",
            },
            buttons: {
              cancel: "Atšaukti",
              save: "Išsaugoti",
              saving: "Išsaugoma...",
            },
            success: "Žinių bazė sėkmingai atnaujinta.",
          },
          editFormTemplateModal: {
            title: "Redaguoti Formos Šabloną",
            formTemplateName: "Formos Šablono Pavadinimas",
            formTemplateDescription: "Formos Šablono Aprašymas",
            descriptionPlaceholder: "Įveskite formos šablono aprašymą...",
            referenceDocuments: "Nuorodos Dokumentai (Neprivaloma)",
            uploadFiles: "Įkelti Failus",
            knowledgeBase: "Žinių Bazė",
            formFields: "Formos Laukai",
            suggest: "Siūlyti",
            fieldPlaceholder: "Pridėti lauko pavadinimą...",
            cancel: "Atšaukti",
            updateFormTemplate: "Atnaujinti Formos Šabloną"
          },
        },
        editCustom: {
          title: "Redaguoti pasirinktines instrukcijas",
          currentInstructions: "Dabartinės instrukcijos:",
          save: "Išsaugoti",
          cancel: "Atšaukti",
        },
      },
      optimizeChecklistModal: {
        title: "Optimizuoti Kontrolės Sąrašą",
        customInstructionsLabel: "Pritaikyti Nurodymai (Neprivaloma)",
        customInstructionsHelperText: "Įveskite papildomus nurodymus, kuriuos reikia atsižvelgti atsakant į kontrolės sąrašo klausimus",
        analyzing: "Analizuoja...",
        analyzeButton: "Analizuoti Kontrolės Sąrašą",
        analyzingMessage: "Analizuojamas jūsų kontrolės sąrašas optimizavimo galimybėms...",
        cancelAnalysis: "Atšaukti Analizę",
        downloading: "Atsisiųs...",
        downloadCsv: "Atsisiųsti CSV",
        questionsNeedingOptimization: "Klausimai, Kuriems Reikia Optimizavimo",
        questionsAlreadyOptimized: "Jau Optimizuoti Klausimai",
        selected: "Pasirinkta",
        select: "Pasirinkti",
        original: "Originalus",
        suggestedImprovement: "Siūlomas Pagerinimas",
        policyContext: "Politikos Kontekstas",
        currentAnswer: "Dabartinis Atsakymas",
        showLess: "Rodyti Mažiau",
        showMore: "Rodyti Daugiau",
        optimizationsSelectedText: "optimizavimai pasirinkti taikymui",
        applying: "Taiko...",
        applySelectedOptimizations: "Taikyti Pasirinktus Optimizavimus",
        uploadDocumentsTitle: "Įkelkite dokument(us), kuriuos kontrolės sąrašas turėtų priimti *",
        uploadDocumentsHelperText: "Įkelkite dokumentus, kurie turėtų atitikti visus kontrolės sąrašo reikalavimus, kad padėtų nustatyti klausimus, kurie gali būti per griežti",
        customInstructionsPlaceholder: "pvz., Atsižvelgkite, kad tai pediatrinis tyrimas vertinant su amžiumi susijusius reikalavimus, Šis protokolas skirtas mažo rizikos intervencijai ir t.t."
      },
      optimizeOutlineModal: {
        title: "Optimizuoti Planą",
        description: "Įkelkite etaloninį dokumentą, kuris reprezentuoja aukštos kokybės ataskaitos tipo, kurį norite generuoti, pavyzdį. Sistema generuos ataskaitą naudodama jūsų dabartinį planą ir žinių bazę, palygints ją su etalonu ir pasiūlys plano skyrių pagerinimus.",
        groundTruthDocument: "Etaloninis Dokumentas",
        customInstructionsLabel: "Pritaikyti Nurodymai (Neprivaloma)",
        customInstructionsHelperText: "Pateikite papildomus nurodymus optimizavimo procesui",
        customInstructionsPlaceholder: "pvz., Sutelkite dėmesį į techninio gylio pagerinimą, užtikrinkite atitiktį konkretiems standartams ir t.t.",
        characters: "simbolių",
        analyzingOutline: "Analizuojamas planas ir generuojami optimizavimai...",
        cancelAnalysis: "Atšaukti Analizę",
        optimizationResults: "Optimizavimo Rezultatai",
        sectionsNeedOptimization: "skyrių reikia optimizavimo",
        downloadCsv: "Atsisiųsti CSV",
        section: "Skyrius",
        accepted: "Priimta",
        accept: "Priimti",
        originalSectionDescription: "Originalus Skyriaus Aprašymas",
        suggestedSectionDescription: "Siūlomas Skyriaus Aprašymas",
        generatedContent: "Sugeneruotas Turinys (su dabartiniu aprašymu)",
        groundTruthReference: "Etaloninė Nuoroda",
        showLess: "Rodyti Mažiau",
        showMore: "Rodyti Daugiau",
        close: "Uždaryti",
        cancel: "Atšaukti",
        optimizing: "Optimizuoja...",
        optimizeOutline: "Optimizuoti Planą",
        applyOptimizations: "Taikyti {{count}} Optimizavimą/ų"
      }
    },
  }

  // Greek
  resources.el = {
    common: {
      navigation: {
        dashboard: "Πίνακας ελέγχου",
        review: "Επισκόπηση",
        generate: "Δημιουργία",
        compare: "Σύγκριση",
        match: "Αντιστοίχιση",
        modelSelection: "Επιλογή μοντέλου",
        knowledgeBases: "Βάσεις γνώσης",
        archive: "Αρχείο",
        settings: "Ρυθμίσεις",
        admin: "Διαχειριστής",
        menu: "Μενού",
        tools: "Εργαλεία",
        configurations: "Διαμορφώσεις",
        myProfile: "Το προφίλ μου",
        logout: "Αποσύνδεση",
        loggedInAs: "Συνδεδεμένος ως: {{email}}",
      },
      buttons: {
        upload: "Ανέβασμα",
        download: "Κατέβασμα",
        save: "Αποθήκευση",
        cancel: "Ακύρωση",
        delete: "Διαγραφή",
        edit: "Επεξεργασία",
        submit: "Υποβολή",
        close: "Κλείσιμο",
        next: "Επόμενο",
        previous: "Προηγούμενο",
        confirm: "Επιβεβαίωση",
        back: "Πίσω",
      },
      forms: {
        firstName: "Όνομα",
        lastName: "Επώνυμο",
        email: "Email",
        password: "Κωδικός πρόσβασης",
        confirmPassword: "Επιβεβαίωση κωδικού",
        currentPassword: "Τρέχων κωδικός",
        newPassword: "Νέος κωδικός",
        required: "Απαιτούμενο",
        optional: "Προαιρετικό",
        emailPlaceholder: "Εισάγετε τη διεύθυνση email σας",
        passwordPlaceholder: "Εισάγετε τον κωδικό σας",
      },
      dropdowns: {
        selectKnowledgeBase: "Επιλέξτε Βάση Γνώσεων...",
      },
      chatbot: {
        placeholder: "Γράψτε το μήνυμά σας εδώ...",
        send: "Αποστολή",
        newChat: "Νέα συνομιλία",
        clearHistory: "Διαγραφή ιστορικού",
        typing: "Το AI γράφει...",
        error: "Συγγνώμη, κάτι πήγε στραβά. Δοκιμάστε ξανά.",
        welcome: "Γεια σας! Πώς μπορώ να σας βοηθήσω σήμερα;",
        welcomeMessageWithSource: "Επιλέξτε μια βάση γνώσεων ή ανεβάστε αρχεία, στη συνέχεια κάντε μια ερώτηση.",
        welcomeMessageGeneral: "Ρωτήστε με οτιδήποτε! Για αναζήτηση στη βάση γνώσεων, επιλέξτε πρώτα μια βάση γνώσεων.",
      },
      settings: {
        title: "Ρυθμίσεις",
        account: "Λογαριασμός",
        language: "Γλώσσα",
        dangerZone: "Επικίνδυνη ζώνη",
        preferredLanguage: "Προτιμώμενη γλώσσα",
        saveLanguagePreference: "Αποθήκευση γλωσσικών προτιμήσεων",
        deleteAccount: "Διαγραφή λογαριασμού",
        deleteAccountWarning: "Αυτή η ενέργεια δεν μπορεί να αναιρεθεί.",
        profile: "Προφίλ",
        security: "Ασφάλεια",
        changePassword: "Αλλαγή κωδικού",
        appearance: "Εμφάνιση",
      },
      errors: {
        somethingWentWrong: "Κάτι πήγε στραβά",
        tryAgain: "Δοκιμάστε ξανά",
        invalidEmail: "Μη έγκυρη διεύθυνση email",
        passwordTooShort: "Ο κωδικός είναι πολύ μικρός",
        passwordsDoNotMatch: "Οι κωδικοί δεν ταιριάζουν",
        networkError: "Σφάλμα δικτύου. Ελέγξτε τη σύνδεσή σας.",
        unauthorized: "Δεν έχετε εξουσιοδότηση για αυτή την ενέργεια.",
        notFound: "Ο ζητούμενος πόρος δεν βρέθηκε.",
      },
      common: {
        loading: "Φόρτωση...",
        noData: "Δεν υπάρχουν διαθέσιμα δεδομένα",
        success: "Επιτυχία!",
        failed: "Αποτυχία",
        welcome: "Καλώς ήρθατε",
        goodbye: "Αντίο",
        yes: "Ναι",
        no: "Όχι",
        ok: "Εντάξει",
        search: "Αναζήτηση",
        filter: "Φίλτρο",
        sort: "Ταξινόμηση",
        view: "Προβολή",
        copy: "Αντιγραφή",
        paste: "Επικόλληση",
        cut: "Αποκοπή",
      },
      review: {
        pageTitle: "Επισκόπηση εγγράφων",
        pageDescription: "Επισκοπήστε ένα έγγραφο βάσει μιας λίστας ελέγχου που ορίζεται από τον χρήστη και μιας βάσης δεδομένων πολιτικής.",
        knowledgeBaseTitle: "Βάση γνώσης",
        knowledgeBaseDescription: "Κάντε κλικ για επιλογή",
        checklistTitle: "Λίστα ελέγχου",
        checklistDescription: "Κάντε κλικ για επιλογή",
        customInstructionsTitle: "Προσαρμοσμένες οδηγίες (προαιρετικό)",
        customInstructionsPlaceholder: "Εισάγετε πρόσθετες οδηγίες που πρέπει να λαμβάνονται υπόψη κατά την απάντηση στις ερωτήσεις της λίστας ελέγχου...",
        customInstructionsHelp: "{{count}}/2000 χαρακτήρες. Αυτές οι οδηγίες θα προστεθούν σε κάθε ερώτηση κατά την επεξεργασία.",
        searchModeHelp: "Η διανυσματική αναζήτηση παρέχει γρήγορα, στοχευμένα αποτελέσματα. Η ανάλυση πλήρους εγγράφου εξετάζει όλο το περιεχόμενο της βάσης γνώσης.",
        processingFile: "Επεξεργασία αρχείου...",
        processingFiles: "Επεξεργασία αρχείων...",
        selectKnowledgeBaseTitle: "Επιλέξτε βάση γνώσης",
        selectChecklistTitle: "Επιλέξτε λίστα ελέγχου",
        noResults: "Δεν υπάρχουν ακόμα αποτελέσματα",
        uploadDocuments: "Ανεβάστε ένα ή περισσότερα έγγραφα για επισκόπηση έναντι της επιλεγμένης λίστας ελέγχου",
        results: "Αποτελέσματα",
        downloadReport: "Λήψη αναφοράς",
        downloadCsv: "Λήψη CSV",
        clearResults: "Καθαρισμός αποτελεσμάτων",
        copyReport: "Αντιγραφή αναφοράς",
        reportCopied: "Η αναφορά αντιγράφηκε στο πρόχειρο!",
        reviewButton: "Επισκόπηση",
        consultDocuments: "Συμβουλευτείτε έγγραφα",
        noChecklistsAvailable: "Δεν υπάρχουν διαθέσιμες λίστες ελέγχου. Δημιουργήστε την πρώτη σας λίστα ελέγχου για να ξεκινήσετε.",
        createChecklist: "Δημιουργία λίστας ελέγχου",
        editChecklist: "Επεξεργασία λίστας ελέγχου",
        checklistName: "Όνομα λίστας ελέγχου",
        checklistNamePlaceholder: "Εισάγετε όνομα λίστας ελέγχου...",
        checklistDescriptionLabel: "Περιγραφή",
        checklistDescriptionPlaceholder: "Εισάγετε περιγραφή λίστας ελέγχου για αυτόματες προτάσεις ερωτήσεων (τουλάχιστον 10 χαρακτήρες)...",
        questions: "Ερωτήσεις",
        suggest: "Πρότεινε",
        suggesting: "Προτείνω...",
        optimize: "Βελτιστοποίηση",
        optimizeTooltip: "Πρέπει να επιλεγεί μια βάση γνώσης για να ενεργοποιηθεί η λειτουργία βελτιστοποίησης",
        optimizeTooltipEnabled: "Βελτιστοποίηση ερωτήσεων βάσει της επιλεγμένης βάσης γνώσης",
        allUsersToggleTooltip: "Εναλλαγή μεταξύ προβολής μόνο του ιστορικού σας ή του ιστορικού όλων των χρηστών",
        uploadFiles: "Ανέβασμα αρχείων",
        knowledgeBase: "Βάση γνώσης",
        referenceDocuments: "Έγγραφα αναφοράς (προαιρετικό)",
        selectKnowledgeBasePlaceholder: "Επιλέξτε βάση γνώσης...",
        noKnowledgeBasesAvailable: "Δεν υπάρχουν διαθέσιμες βάσεις γνώσης. Δημιουργήστε πρώτα μία για να χρησιμοποιήσετε αυτή τη λειτουργία.",
        copyQuestions: "Αντιγραφή ερωτήσεων",
        questionsCopied: "Οι ερωτήσεις αντιγράφηκαν στο πρόχειρο",
        noQuestionsToCopy: "Δεν υπάρχουν ερωτήσεις για αντιγραφή",
        failedToCopyQuestions: "Αποτυχία αντιγραφής ερωτήσεων στο πρόχειρο",
        saveChecklist: "Αποθήκευση λίστας ελέγχου",
        cancel: "Ακύρωση",
        deleteChecklist: "Διαγραφή λίστας ελέγχου"
      },
      compare: {
        title: "Σύγκριση εγγράφων",
        subtitle: "Επιλέξτε δύο έγγραφα για σύγκριση",
        selectFirstDocument: "Επιλέξτε το πρώτο έγγραφο",
        selectSecondDocument: "Επιλέξτε το δεύτερο έγγραφο",
        pleaseSelect: "Παρακαλώ επιλέξτε...",
        documentA: "Έγγραφο Α",
        documentB: "Έγγραφο Β",
        compareDocuments: "Σύγκριση εγγράφων",
        comparison: "Σύγκριση",
        noDocumentsFound: "Δεν βρέθηκαν έγγραφα",
        selectTwoDocuments: "Παρακαλώ επιλέξτε δύο έγγραφα για σύγκριση",
        loadingComparison: "Φόρτωση σύγκρισης...",
        topicList: "Λίστα θεμάτων",
        clickToBrowse: "Κάντε κλικ για περιήγηση ή σύρετε εδώ",
        supportedFormats: "Υποστηριζόμενες μορφές: PDF, TXT, DOCX",
        analysisType: "Τύπος ανάλυσης",
        quickAnalysis: "Γρήγορη ανάλυση",
        detailedAnalysis: "Λεπτομερής ανάλυση",
        comprehensiveAnalysis: "Εκτενής ανάλυση",
        analysisDepth: "Βάθος ανάλυσης",
        surfaceLevel: "Επιφανειακό επίπεδο",
        moderate: "Μέτριο",
        deep: "Βαθύ",
        veryDeep: "Πολύ βαθύ",
        editTopicList: "Επεξεργασία λίστας θεμάτων"
      },
      match: {
        title: "Αντιστοίχιση εγγράφων",
        subtitle: "Βρείτε παρόμοια έγγραφα βάσει περιεχομένου",
        selectDocument: "Επιλέξτε έγγραφο για εύρεση αντιστοιχιών",
        pleaseSelect: "Παρακαλώ επιλέξτε έγγραφο...",
        sourceDocument: "Έγγραφο πηγής",
        matchingDocuments: "Αντιστοιχισμένα έγγραφα",
        findMatches: "Εύρεση αντιστοιχιών",
        similarityScore: "Βαθμολογία ομοιότητας",
        noDocumentsFound: "Δεν βρέθηκαν έγγραφα",
        selectDocumentToMatch: "Παρακαλώ επιλέξτε έγγραφο για εύρεση αντιστοιχιών",
        loadingMatches: "Αναζήτηση αντιστοιχιών...",
        noMatchesFound: "Δεν βρέθηκαν παρόμοια έγγραφα",
        matchResults: "Αποτελέσματα αντιστοίχισης",
        similarity: "Ομοιότητα",
        matchingCriteria: "Κριτήρια αντιστοίχισης",
        semanticSimilarity: "Σημασιολογική ομοιότητα",
        keywordMatching: "Αντιστοίχιση λέξεων-κλειδιών",
        structuralSimilarity: "Δομική ομοιότητα",
        threshold: "Κατώφλι",
        minimumSimilarity: "Ελάχιστη ομοιότητα",
        searchDepth: "Βάθος αναζήτησης",
        maxResults: "Μέγιστος αριθμός αποτελεσμάτων",
        editFormTemplate: "Επεξεργασία προτύπου φόρμας"
      },
      knowledgeBases: {
        title: "Διαχείριση βάσεων γνώσης",
        addKnowledgeBase: "Προσθήκη βάσης γνώσης",
        emptyStateTitle: "Δεν έχετε ακόμη βάσεις γνώσης",
        emptyStateDescription: "Προσθέστε μια νέα βάση γνώσης για να ξεκινήσετε",
        tableHeaders: {
          title: "Τίτλος",
          description: "Περιγραφή",
          numberOfSources: "Αριθμός πηγών",
          embeddingModel: "Μοντέλο ενσωμάτωσης",
          dateCreated: "Ημερομηνία δημιουργίας",
          dateModified: "Ημερομηνία τροποποίησης",
          actions: "Ενέργειες"
        },
        status: {
          default: "Προεπιλογή",
          na: "Μη διαθέσιμο"
        },
        actions: {
          view: "Προβολή",
          edit: "Επεξεργασία",
          delete: "Διαγραφή",
          configure: "Διαμόρφωση"
        },
        deleteModal: {
          title: "Διαγραφή βάσης γνώσης",
          buttonText: "Διαγραφή βάσης γνώσης",
          description: "Αυτή η βάση γνώσης θα διαγραφεί μόνιμα. Είστε σίγουροι; Δεν θα μπορείτε να αναιρέσετε αυτή την ενέργεια.",
          confirmButton: "Διαγραφή",
          cancelButton: "Ακύρωση",
          successMessage: "Η βάση γνώσης διαγράφηκε επιτυχώς",
          errorMessage: "Παρουσιάστηκε σφάλμα κατά τη διαγραφή της βάσης γνώσης"
        },
        modals: {
          add: {
            title: "Προσθήκη βάσης γνώσης",
            description: "Δημιουργήστε μια νέα βάση γνώσης παρέχοντας λεπτομέρειες και ανεβάζοντας έγγραφα παρακάτω.",
            fields: {
              title: "Τίτλος",
              titlePlaceholder: "Τίτλος",
              titleRequired: "Ο τίτλος είναι υποχρεωτικός",
              description: "Περιγραφή",
              descriptionPlaceholder: "Περιγραφή",
            },
            fileUpload: {
              dragAndDrop: "Σύρετε αρχεία εδώ ή κάντε κλικ για περιήγηση",
              dropFiles: "Αφήστε τα αρχεία εδώ...",
              selectedFiles: "Επιλεγμένα αρχεία:",
              removeFile: "Αφαίρεση αρχείου",
            },
            buttons: {
              cancel: "Ακύρωση",
              save: "Αποθήκευση",
              creating: "Δημιουργία...",
            },
            validation: {
              atLeastOneFile: "Απαιτείται τουλάχιστον ένα αρχείο.",
            },
            success: "Η βάση γνώσης δημιουργήθηκε επιτυχώς.",
          },
          edit: {
            title: "Επεξεργασία βάσης γνώσης",
            description: "Ενημερώστε τις λεπτομέρειες της βάσης γνώσης παρακάτω.",
            fields: {
              title: "Τίτλος",
              titlePlaceholder: "Τίτλος",
              titleRequired: "Ο τίτλος είναι υποχρεωτικός",
              description: "Περιγραφή",
              descriptionPlaceholder: "Περιγραφή",
            },
            fileUpload: {
              currentFiles: "Τρέχοντα αρχεία:",
              dragAndDrop: "Σύρετε αρχεία εδώ ή κάντε κλικ για περιήγηση",
              dropFiles: "Αφήστε τα αρχεία εδώ...",
              selectedFiles: "Επιλεγμένα αρχεία:",
              removeFile: "Αφαίρεση αρχείου",
            },
            buttons: {
              cancel: "Ακύρωση",
              save: "Αποθήκευση",
              saving: "Αποθήκευση...",
            },
            success: "Η βάση γνώσης ενημερώθηκε επιτυχώς.",
          },
          editFormTemplateModal: {
            title: "Επεξεργασία Προτύπου Φόρμας",
            formTemplateName: "Όνομα Προτύπου Φόρμας",
            formTemplateDescription: "Περιγραφή Προτύπου Φόρμας",
            descriptionPlaceholder: "Εισάγετε περιγραφή προτύπου φόρμας...",
            referenceDocuments: "Έγγραφα Αναφοράς (Προαιρετικό)",
            uploadFiles: "Μεταφόρτωση Αρχείων",
            knowledgeBase: "Βάση Γνώσης",
            formFields: "Πεδία Φόρμας",
            suggest: "Πρόταση",
            fieldPlaceholder: "Προσθήκη ονόματος πεδίου...",
            cancel: "Ακύρωση",
            updateFormTemplate: "Ενημέρωση Προτύπου Φόρμας"
          },
        },
        editCustom: {
          title: "Επεξεργασία προσαρμοσμένων οδηγιών",
          currentInstructions: "Τρέχουσες οδηγίες:",
          save: "Αποθήκευση",
          cancel: "Ακύρωση",
        },
      },
      optimizeChecklistModal: {
        title: "Βελτιστοποίηση Λίστας Ελέγχου",
        customInstructionsLabel: "Προσαρμοσμένες Οδηγίες (Προαιρετικό)",
        customInstructionsHelperText: "Εισάγετε πρόσθετες οδηγίες που πρέπει να ληφθούν υπόψη κατά την απάντηση στις ερωτήσεις της λίστας ελέγχου",
        analyzing: "Ανάλυση...",
        analyzeButton: "Ανάλυση Λίστας Ελέγχου",
        analyzingMessage: "Ανάλυση της λίστας ελέγχου σας για ευκαιρίες βελτιστοποίησης...",
        cancelAnalysis: "Ακύρωση Ανάλυσης",
        downloading: "Λήψη...",
        downloadCsv: "Λήψη CSV",
        questionsNeedingOptimization: "Ερωτήσεις που Χρειάζονται Βελτιστοποίηση",
        questionsAlreadyOptimized: "Ήδη Βελτιστοποιημένες Ερωτήσεις",
        selected: "Επιλεγμένο",
        select: "Επιλογή",
        original: "Πρωτότυπο",
        suggestedImprovement: "Προτεινόμενη Βελτίωση",
        policyContext: "Πλαίσιο Πολιτικής",
        currentAnswer: "Τρέχουσα Απάντηση",
        showLess: "Εμφάνιση Λιγότερων",
        showMore: "Εμφάνιση Περισσότερων",
        optimizationsSelectedText: "βελτιστοποιήσεις επιλέχθηκαν για εφαρμογή",
        applying: "Εφαρμογή...",
        applySelectedOptimizations: "Εφαρμογή Επιλεγμένων Βελτιστοποιήσεων",
        uploadDocumentsTitle: "Ανεβάστε έγγραφο/α που πρέπει να γίνουν δεκτά από τη λίστα ελέγχου *",
        uploadDocumentsHelperText: "Ανεβάστε έγγραφα που πρέπει να πληρούν όλες τις απαιτήσεις της λίστας ελέγχου για να βοηθήσουν στην αναγνώριση ερωτήσεων που μπορεί να είναι πολύ αυστηρές",
        customInstructionsPlaceholder: "π.χ., Λάβετε υπόψη ότι αυτή είναι μια παιδιατρική μελέτη κατά την αξιολόγηση των απαιτήσεων που σχετίζονται με την ηλικία, Αυτό το πρωτόκολλο είναι για παρέμβαση χαμηλού κινδύνου, κ.λπ."
      },
      optimizeOutlineModal: {
        title: "Βελτιστοποίηση Περιγράμματος",
        description: "Ανεβάστε ένα έγγραφο αναφοράς που αντιπροσωπεύει ένα υψηλής ποιότητας παράδειγμα του τύπου αναφοράς που θέλετε να δημιουργήσετε. Το σύστημα θα δημιουργήσει μια αναφορά χρησιμοποιώντας το τρέχον περίγραμμα και τη βάση γνώσεων σας, θα το συγκρίνει με την αναφορά και θα προτείνει βελτιώσεις για τις ενότητες του περιγράμματος.",
        groundTruthDocument: "Έγγραφο Αναφοράς",
        customInstructionsLabel: "Προσαρμοσμένες Οδηγίες (Προαιρετικό)",
        customInstructionsHelperText: "Παρέχετε πρόσθετες οδηγίες για τη διαδικασία βελτιστοποίησης",
        customInstructionsPlaceholder: "π.χ., Επικεντρωθείτε στη βελτίωση του τεχνικού βάθους, εξασφαλίστε συμμόρφωση με συγκεκριμένα πρότυπα, κ.λπ.",
        characters: "χαρακτήρες",
        analyzingOutline: "Ανάλυση περιγράμματος και δημιουργία βελτιστοποιήσεων...",
        cancelAnalysis: "Ακύρωση Ανάλυσης",
        optimizationResults: "Αποτελέσματα Βελτιστοποίησης",
        sectionsNeedOptimization: "ενότητες χρειάζονται βελτιστοποίηση",
        downloadCsv: "Λήψη CSV",
        section: "Ενότητα",
        accepted: "Αποδεκτό",
        accept: "Αποδοχή",
        originalSectionDescription: "Πρωτότυπη Περιγραφή Ενότητας",
        suggestedSectionDescription: "Προτεινόμενη Περιγραφή Ενότητας",
        generatedContent: "Δημιουργημένο Περιεχόμενο (με την τρέχουσα περιγραφή)",
        groundTruthReference: "Αναφορά Αναφοράς",
        showLess: "Εμφάνιση Λιγότερων",
        showMore: "Εμφάνιση Περισσότερων",
        close: "Κλείσιμο",
        cancel: "Ακύρωση",
        optimizing: "Βελτιστοποίηση...",
        optimizeOutline: "Βελτιστοποίηση Περιγράμματος",
        applyOptimizations: "Εφαρμογή {{count}} Βελτιστοποιήσεων"
      }
    },
  }

  // Add Model Selection translations to Estonian
  resources.et.common.modelSelection = {
    llmManagement: "LLM haldamine",
    llmDescription: "Konfigureerige ja hallake tekstivastuste genereerimiseks kasutatavaid LLM-e. Vaikemudel kasutatakse kõigi operatsioonide jaoks.",
    addNewLlm: "Lisa uus LLM",
    noLlmsConfigured: "LLM-e pole konfigureeritud",
    addNewLlmToGetStarted: "Alustamiseks lisage uus LLM",
    embeddingModelManagement: "Sisestusmudelite haldamine",
    embeddingDescription: "Konfigureerige ja hallake teadmisbaaside indekseerimiseks ja otsingeks kasutatavaid sisestusmudeleid. Vaikemudel kasutatakse uute teadmisbaaside loomisel, kuid iga teadmusbaas jätkab oma algse sisestusmudeli kasutamist isegi siis, kui vaikemudel hiljem muutub.",
    addEmbeddingModel: "Lisa sisestusmudel",
    noEmbeddingModelsConfigured: "Sisestusmudeleid pole konfigureeritud",
    addNewEmbeddingModelToGetStarted: "Alustamiseks lisage uus sisestusmudel",
    tableHeaders: {
      name: "Nimi",
      modelId: "Mudeli ID",
      provider: "Pakkuja",
      description: "Kirjeldus",
      status: "Olek",
      actions: "Tegevused"
    },
    status: {
      default: "Vaikimisi",
      available: "Saadaval"
    },
    actions: {
      setAsDefault: "Määra vaikimisiks",
      delete: "Kustuta",
      validate: "Kinnita",
      validating: "Kinnitamine"
    },
    dialog: {
      addNewLlm: "Lisa uus LLM",
      addEmbeddingModel: "Lisa sisestusmudel",
      displayName: "Kuvatav nimi",
      provider: "Pakkuja",
      modelId: "Mudeli ID",
      description: "Kirjeldus",
      cancel: "Tühista",
      addModel: "Lisa mudel"
    },
    placeholders: {
      customModel: "nt, Minu kohandatud mudel",
      embeddingModelId: "nt, sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Kirjeldage mudelit, selle omadusi ja millal seda kasutada"
    },
    validation: {
      pleaseEnterModelId: "Palun sisestage mudeli ID"
    }
  }

  // Add Model Selection translations to Latvian
  resources.lv.common.modelSelection = {
    llmManagement: "LLM pārvaldība",
    llmDescription: "Konfigurējiet un pārvaldiet LLM, kas tiek izmantoti teksta atbilžu ģenerēšanai. Noklusējuma modelis tiks izmantots visām operācijām.",
    addNewLlm: "Pievienot jaunu LLM",
    noLlmsConfigured: "Nav konfigurēti LLM",
    addNewLlmToGetStarted: "Pievienojiet jaunu LLM, lai sāktu",
    embeddingModelManagement: "Iegulšanas modeļu pārvaldība",
    embeddingDescription: "Konfigurējiet un pārvaldiet iegulšanas modeļus, kas tiek izmantoti zināšanu bāzu indeksēšanai un meklēšanai. Noklusējuma modelis tiks izmantots, veidojot jaunas zināšanu bāzes, bet katra zināšanu bāze turpinās izmantot savu sākotnējo iegulšanas modeli pat tad, ja noklusējuma modelis vēlāk mainās.",
    addEmbeddingModel: "Pievienot iegulšanas modeli",
    noEmbeddingModelsConfigured: "Nav konfigurēti iegulšanas modeļi",
    addNewEmbeddingModelToGetStarted: "Pievienojiet jaunu iegulšanas modeli, lai sāktu",
    tableHeaders: {
      name: "Nosaukums",
      modelId: "Modeļa ID",
      provider: "Pakalpojumu sniedzējs",
      description: "Apraksts",
      status: "Statuss",
      actions: "Darbības"
    },
    status: {
      default: "Noklusējuma",
      available: "Pieejams"
    },
    actions: {
      setAsDefault: "Iestatīt kā noklusējuma",
      delete: "Dzēst",
      validate: "Apstiprināt",
      validating: "Apstiprina"
    },
    dialog: {
      addNewLlm: "Pievienot jaunu LLM",
      addEmbeddingModel: "Pievienot iegulšanas modeli",
      displayName: "Attēlotais nosaukums",
      provider: "Pakalpojumu sniedzējs",
      modelId: "Modeļa ID",
      description: "Apraksts",
      cancel: "Atcelt",
      addModel: "Pievienot modeli"
    },
    placeholders: {
      customModel: "piem., Mans pielāgotais modelis",
      embeddingModelId: "piem., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Aprakstiet modeli, tā raksturlielumus un kad to izmantot"
    },
    validation: {
      pleaseEnterModelId: "Lūdzu, ievadiet modeļa ID"
    }
  }

  // Add Model Selection translations to Lithuanian
  resources.lt.common.modelSelection = {
    llmManagement: "LLM valdymas",
    llmDescription: "Sukonfigūruokite ir valdykite LLM, naudojamus teksto atsakymų generavimui. Numatytasis modelis bus naudojamas visoms operacijoms.",
    addNewLlm: "Pridėti naują LLM",
    noLlmsConfigured: "Nesukonfigūruota LLM",
    addNewLlmToGetStarted: "Pridėkite naują LLM, kad pradėtumėte",
    embeddingModelManagement: "Įterpimo modelių valdymas",
    embeddingDescription: "Sukonfigūruokite ir valdykite įterpimo modelius, naudojamus žinių bazių indeksavimui ir paieškai. Numatytasis modelis bus naudojamas kuriant naujas žinių bazes, tačiau kiekviena žinių bazė ir toliau naudos savo pradinį įterpimo modelį, net jei numatytasis vėliau pasikeis.",
    addEmbeddingModel: "Pridėti įterpimo modelį",
    noEmbeddingModelsConfigured: "Nesukonfigūruota įterpimo modelių",
    addNewEmbeddingModelToGetStarted: "Pridėkite naują įterpimo modelį, kad pradėtumėte",
    tableHeaders: {
      name: "Pavadinimas",
      modelId: "Modelio ID",
      provider: "Teikėjas",
      description: "Aprašymas",
      status: "Būsena",
      actions: "Veiksmai"
    },
    status: {
      default: "Numatytasis",
      available: "Prieinamas"
    },
    actions: {
      setAsDefault: "Nustatyti kaip numatytąjį",
      delete: "Ištrinti",
      validate: "Patvirtinti",
      validating: "Patvirtinama"
    },
    dialog: {
      addNewLlm: "Pridėti naują LLM",
      addEmbeddingModel: "Pridėti įterpimo modelį",
      displayName: "Rodomas pavadinimas",
      provider: "Teikėjas",
      modelId: "Modelio ID",
      description: "Aprašymas",
      cancel: "Atšaukti",
      addModel: "Pridėti modelį"
    },
    placeholders: {
      customModel: "pvz., Mano pritaikytas modelis",
      embeddingModelId: "pvz., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Aprašykite modelį, jo charakteristikas ir kada jį naudoti"
    },
    validation: {
      pleaseEnterModelId: "Prašome įvesti modelio ID"
    }
  }

  // Add Model Selection translations to Greek
  resources.el.common.modelSelection = {
    llmManagement: "Διαχείριση LLM",
    llmDescription: "Διαμορφώστε και διαχειριστείτε τα LLM που χρησιμοποιούνται για τη δημιουργία κειμενικών απαντήσεων. Το προεπιλεγμένο μοντέλο θα χρησιμοποιηθεί για όλες τις λειτουργίες.",
    addNewLlm: "Προσθήκη νέου LLM",
    noLlmsConfigured: "Δεν έχουν διαμορφωθεί LLM",
    addNewLlmToGetStarted: "Προσθέστε ένα νέο LLM για να ξεκινήσετε",
    embeddingModelManagement: "Διαχείριση μοντέλων ενσωμάτωσης",
    embeddingDescription: "Διαμορφώστε και διαχειριστείτε τα μοντέλα ενσωμάτωσης που χρησιμοποιούνται για την ευρετηρίαση και ανάκτηση βάσεων γνώσης. Το προεπιλεγμένο μοντέλο θα χρησιμοποιηθεί κατά τη δημιουργία νέων βάσεων γνώσης, αλλά κάθε βάση γνώσης θα συνεχίσει να χρησιμοποιεί το αρχικό της μοντέλο ενσωμάτωσης ακόμη και αν το προεπιλεγμένο αλλάξει αργότερα.",
    addEmbeddingModel: "Προσθήκη μοντέλου ενσωμάτωσης",
    noEmbeddingModelsConfigured: "Δεν έχουν διαμορφωθεί μοντέλα ενσωμάτωσης",
    addNewEmbeddingModelToGetStarted: "Προσθέστε ένα νέο μοντέλο ενσωμάτωσης για να ξεκινήσετε",
    tableHeaders: {
      name: "Όνομα",
      modelId: "ID μοντέλου",
      provider: "Πάροχος",
      description: "Περιγραφή",
      status: "Κατάσταση",
      actions: "Ενέργειες"
    },
    status: {
      default: "Προεπιλογή",
      available: "Διαθέσιμο"
    },
    actions: {
      setAsDefault: "Ορισμός ως προεπιλογή",
      delete: "Διαγραφή",
      validate: "Επικύρωση",
      validating: "Επικυρώνεται"
    },
    dialog: {
      addNewLlm: "Προσθήκη νέου LLM",
      addEmbeddingModel: "Προσθήκη μοντέλου ενσωμάτωσης",
      displayName: "Εμφανιζόμενο όνομα",
      provider: "Πάροχος",
      modelId: "ID μοντέλου",
      description: "Περιγραφή",
      cancel: "Ακύρωση",
      addModel: "Προσθήκη μοντέλου"
    },
    placeholders: {
      customModel: "π.χ., Το προσαρμοσμένο μου μοντέλο",
      embeddingModelId: "π.χ., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Περιγράψτε το μοντέλο, τα χαρακτηριστικά του και πότε να το χρησιμοποιήσετε"
    },
    validation: {
      pleaseEnterModelId: "Παρακαλώ εισαγάγετε ένα ID μοντέλου"
    }
  }

  // Add Knowledge Bases translations for Baltic and Eastern European languages

  // Estonian
  if (!resources.et.common.knowledgeBases) {
    resources.et.common.knowledgeBases = {
      title: "Teadmusbaasid",
      addKnowledgeBase: "Lisa teadmusbaas",
      description: "Hallake ja korraldage oma dokumente teadmusbaasides tõhusate AI-toetatud interaktsioonide jaoks.",
      createNew: "Loo uus teadmusbaas",
      noKnowledgeBases: "Teadmusbaase pole veel loodud",
      getStarted: "Alustamiseks looge oma esimene teadmusbaas",
      tableHeaders: {
        name: "Nimi",
        description: "Kirjeldus",
        documents: "Dokumendid",
        createdAt: "Loodud",
        actions: "Tegevused"
      },
      actions: {
        view: "Vaata",
        edit: "Muuda",
        delete: "Kustuta",
        configure: "Konfigureeri"
      },
      dialog: {
        createNew: "Loo uus teadmusbaas",
        editKnowledgeBase: "Muuda teadmusbaasi",
        name: "Nimi",
        description: "Kirjeldus",
        cancel: "Tühista",
        create: "Loo",
        save: "Salvesta"
      },
      placeholders: {
        knowledgeBaseName: "nt, Ettevõtte poliitikad",
        knowledgeBaseDescription: "Kirjeldage, mida see teadmusbaas sisaldab ja mis on selle eesmärk"
      },
      validation: {
        pleaseEnterName: "Palun sisestage teadmusbaasi nimi"
      }
    }
  }

  // Latvian
  if (!resources.lv.common.knowledgeBases) {
    resources.lv.common.knowledgeBases = {
      title: "Zināšanu bāzes",
      addKnowledgeBase: "Pievienot zināšanu bāzi",
      description: "Pārvaldiet un organizējiet savus dokumentus zināšanu bāzēs efektīvām AI atbalstītām mijiedarbībām.",
      createNew: "Izveidot jaunu zināšanu bāzi",
      noKnowledgeBases: "Zināšanu bāzes vēl nav izveidotas",
      getStarted: "Izveidojiet savu pirmo zināšanu bāzi, lai sāktu",
      tableHeaders: {
        name: "Nosaukums",
        description: "Apraksts",
        documents: "Dokumenti",
        createdAt: "Izveidots",
        actions: "Darbības"
      },
      actions: {
        view: "Skatīt",
        edit: "Rediģēt",
        delete: "Dzēst",
        configure: "Konfigurēt"
      },
      dialog: {
        createNew: "Izveidot jaunu zināšanu bāzi",
        editKnowledgeBase: "Rediģēt zināšanu bāzi",
        name: "Nosaukums",
        description: "Apraksts",
        cancel: "Atcelt",
        create: "Izveidot",
        save: "Saglabāt"
      },
      placeholders: {
        knowledgeBaseName: "piemēram, Uzņēmuma politikas",
        knowledgeBaseDescription: "Aprakstiet, ko satur šī zināšanu bāze un tās mērķi"
      },
      validation: {
        pleaseEnterName: "Lūdzu, ievadiet zināšanu bāzes nosaukumu"
      }
    }
  }

  // Lithuanian
  if (!resources.lt.common.knowledgeBases) {
    resources.lt.common.knowledgeBases = {
      title: "Žinių bazės",
      addKnowledgeBase: "Pridėti žinių bazę",
      description: "Tvarkykite ir organizuokite savo dokumentus žinių bazėse efektyviems AI palaikomiems sąveikoms.",
      createNew: "Sukurti naują žinių bazę",
      noKnowledgeBases: "Žinių bazės dar nesukurtos",
      getStarted: "Sukurkite savo pirmą žinių bazę, kad pradėtumėte",
      tableHeaders: {
        name: "Pavadinimas",
        description: "Aprašymas",
        documents: "Dokumentai",
        createdAt: "Sukurta",
        actions: "Veiksmai"
      },
      actions: {
        view: "Žiūrėti",
        edit: "Redaguoti",
        delete: "Ištrinti",
        configure: "Konfigūruoti"
      },
      dialog: {
        createNew: "Sukurti naują žinių bazę",
        editKnowledgeBase: "Redaguoti žinių bazę",
        name: "Pavadinimas",
        description: "Aprašymas",
        cancel: "Atšaukti",
        create: "Sukurti",
        save: "Išsaugoti"
      },
      placeholders: {
        knowledgeBaseName: "pvz., Įmonės politikos",
        knowledgeBaseDescription: "Aprašykite, ką šioje žinių bazėje yra ir jos tikslą"
      },
      validation: {
        pleaseEnterName: "Prašome įvesti žinių bazės pavadinimą"
      }
    }
  }

  // Greek
  if (!resources.el.common.knowledgeBases) {
    resources.el.common.knowledgeBases = {
      title: "Βάσεις γνώσης",
      addKnowledgeBase: "Προσθήκη βάσης γνώσης",
      description: "Διαχειριστείτε και οργανώστε τα έγγραφά σας σε βάσεις γνώσης για αποτελεσματικές αλληλεπιδράσεις με υποστήριξη AI.",
      createNew: "Δημιουργήστε νέα βάση γνώσης",
      noKnowledgeBases: "Δεν έχουν δημιουργηθεί ακόμη βάσεις γνώσης",
      getStarted: "Δημιουργήστε την πρώτη σας βάση γνώσης για να ξεκινήσετε",
      tableHeaders: {
        name: "Όνομα",
        description: "Περιγραφή",
        documents: "Έγγραφα",
        createdAt: "Δημιουργήθηκε",
        actions: "Ενέργειες"
      },
      actions: {
        view: "Προβολή",
        edit: "Επεξεργασία",
        delete: "Διαγραφή",
        configure: "Διαμόρφωση"
      },
      dialog: {
        createNew: "Δημιουργήστε νέα βάση γνώσης",
        editKnowledgeBase: "Επεξεργασία βάσης γνώσης",
        name: "Όνομα",
        description: "Περιγραφή",
        cancel: "Ακύρωση",
        create: "Δημιουργία",
        save: "Αποθήκευση"
      },
      placeholders: {
        knowledgeBaseName: "π.χ., Πολιτικές εταιρείας",
        knowledgeBaseDescription: "Περιγράψτε τι περιέχει αυτή η βάση γνώσης και τον σκοπό της"
      },
      validation: {
        pleaseEnterName: "Παρακαλώ εισαγάγετε ένα όνομα για τη βάση γνώσης"
      }
    }
  }

  // Add Archive translations for Baltic and Eastern European languages
  if (!resources.et.common.archive) {
    resources.et.common.archive = {
      tabs: {
        review: "Ülevaatus",
        generate: "Genereeri",
        compare: "Võrdle",
        match: "Sobita"
      },
      metadata: {
        questions: "küsimust",
        questions_one: "küsimus",
        fields: "välja",
        fields_one: "väli",
        documents: "dokumenti",
        documents_one: "dokument",
        digitized: "digiteeritud",
        handwritten: "käsitsi kirjutatud"
      },
      feedback: {
        positive: "Anna positiivset tagasisidet selle tulemuse kohta",
        negative: "Anna negatiivset tagasisidet selle tulemuse kohta",
        hasFeedback: "Sellel tulemusel on tagasiside"
      },
      emptyMessages: {
        review: "Ülevaatuse ajalugu puudub",
        generate: "Genereerimise ajalugu puudub",
        compare: "Võrdluse ajalugu puudub",
        match: "Sobitamise ajalugu puudub"
      },
      deleteConfirmation: "Kas olete kindel, et soovite selle üksuse kustutada?",
      history: "Ajalugu",
      allUsers: "Kõik kasutajad"
    }
  }

  if (!resources.lv.common.archive) {
    resources.lv.common.archive = {
      tabs: {
        review: "Pārskats",
        generate: "Ģenerēt",
        compare: "Salīdzināt",
        match: "Saskaņot"
      },
      metadata: {
        questions: "jautājumi",
        questions_one: "jautājums",
        fields: "lauki",
        fields_one: "lauks",
        documents: "dokumenti",
        documents_one: "dokuments",
        digitized: "digitalizēts",
        handwritten: "rokraksts"
      },
      feedback: {
        positive: "Dot pozitīvu atgriezenisko saiti par šo rezultātu",
        negative: "Dot negatīvu atgriezenisko saiti par šo rezultātu",
        hasFeedback: "Šim rezultātam ir atgriezeniskā saite"
      },
      emptyMessages: {
        review: "Nav pārskata vēstures",
        generate: "Nav ģenerēšanas vēstures",
        compare: "Nav salīdzināšanas vēstures",
        match: "Nav saskaņošanas vēstures"
      },
      deleteConfirmation: "Vai esat pārliecināts, ka vēlaties dzēst šo vienumu?",
      history: "Vēsture",
      allUsers: "Visi lietotāji"
    }
  }

  if (!resources.lt.common.archive) {
    resources.lt.common.archive = {
      tabs: {
        review: "Peržiūra",
        generate: "Generuoti",
        compare: "Palyginti",
        match: "Suderinti"
      },
      metadata: {
        questions: "klausimai",
        questions_one: "klausimas",
        fields: "laukai",
        fields_one: "laukas",
        documents: "dokumentai",
        documents_one: "dokumentas",
        digitized: "skaitmenizuotas",
        handwritten: "rašytas ranka"
      },
      feedback: {
        positive: "Pateikti teigiamą atsiliepimą apie šį rezultatą",
        negative: "Pateikti neigiamą atsiliepimą apie šį rezultatą",
        hasFeedback: "Šis rezultatas turi atsiliepimą"
      },
      emptyMessages: {
        review: "Kol kas nėra peržiūros istorijos",
        generate: "Kol kas nėra generavimo istorijos",
        compare: "Kol kas nėra palyginimo istorijos",
        match: "Kol kas nėra suderinimo istorijos"
      },
      deleteConfirmation: "Ar tikrai norite ištrinti šį elementą?",
      history: "Istorija",
      allUsers: "Visi vartotojai"
    }
  }

  if (!resources.pl.common.archive) {
    resources.pl.common.archive = {
      tabs: {
        review: "Przegląd",
        generate: "Generuj",
        compare: "Porównaj",
        match: "Dopasuj"
      },
      metadata: {
        questions: "pytania",
        questions_one: "pytanie",
        fields: "pola",
        fields_one: "pole",
        documents: "dokumenty",
        documents_one: "dokument",
        digitized: "zdigitalizowany",
        handwritten: "odręczny"
      },
      feedback: {
        positive: "Przekaż pozytywną opinię o tym wyniku",
        negative: "Przekaż negatywną opinię o tym wyniku",
        hasFeedback: "Ten wynik ma opinię"
      },
      emptyMessages: {
        review: "Brak historii przeglądów",
        generate: "Brak historii generowania",
        compare: "Brak historii porównań",
        match: "Brak historii dopasowań"
      },
      deleteConfirmation: "Czy na pewno chcesz usunąć ten element?",
      history: "Historia",
      allUsers: "Wszyscy użytkownicy"
    }
  }

  if (!resources.ru.common.archive) {
    resources.ru.common.archive = {
      tabs: {
        review: "Обзор",
        generate: "Генерировать",
        compare: "Сравнить",
        match: "Сопоставить"
      },
      metadata: {
        questions: "вопросов",
        questions_one: "вопрос",
        fields: "полей",
        fields_one: "поле",
        documents: "документов",
        documents_one: "документ",
        digitized: "оцифрованный",
        handwritten: "рукописный"
      },
      feedback: {
        positive: "Дать положительный отзыв об этом результате",
        negative: "Дать отрицательный отзыв об этом результате",
        hasFeedback: "У этого результата есть отзыв"
      },
      emptyMessages: {
        review: "Пока нет истории обзоров",
        generate: "Пока нет истории генерации",
        compare: "Пока нет истории сравнений",
        match: "Пока нет истории сопоставлений"
      },
      deleteConfirmation: "Вы уверены, что хотите удалить этот элемент?",
      history: "История",
      allUsers: "Все пользователи"
    }
  }

  if (!resources.uk.common.archive) {
    resources.uk.common.archive = {
      tabs: {
        review: "Огляд",
        generate: "Генерувати",
        compare: "Порівняти",
        match: "Співставити"
      },
      metadata: {
        questions: "питань",
        questions_one: "питання",
        fields: "полів",
        fields_one: "поле",
        documents: "документів",
        documents_one: "документ",
        digitized: "оцифрований",
        handwritten: "рукописний"
      },
      feedback: {
        positive: "Дати позитивний відгук про цей результат",
        negative: "Дати негативний відгук про цей результат",
        hasFeedback: "Цей результат має відгук"
      },
      emptyMessages: {
        review: "Поки немає історії оглядів",
        generate: "Поки немає історії генерації",
        compare: "Поки немає історії порівнянь",
        match: "Поки немає історії співставлень"
      },
      deleteConfirmation: "Ви впевнені, що хочете видалити цей елемент?",
      history: "Історія",
      allUsers: "Всі користувачі"
    }
  }

  if (!resources.bg.common.archive) {
    resources.bg.common.archive = {
      tabs: {
        review: "Преглед",
        generate: "Генериране",
        compare: "Сравняване",
        match: "Съпоставяне"
      },
      metadata: {
        questions: "въпроса",
        questions_one: "въпрос",
        fields: "полета",
        fields_one: "поле",
        documents: "документа",
        documents_one: "документ",
        digitized: "дигитализиран",
        handwritten: "ръкописен"
      },
      feedback: {
        positive: "Дайте положителна обратна връзка за този резултат",
        negative: "Дайте отрицателна обратна връзка за този резултат",
        hasFeedback: "Този резултат има обратна връзка"
      },
      emptyMessages: {
        review: "Все още няма история на прегледи",
        generate: "Все още няма история на генериране",
        compare: "Все още няма история на сравняване",
        match: "Все още няма история на съпоставяне"
      },
      deleteConfirmation: "Сигурни ли сте, че искате да изтриете този елемент?",
      history: "История",
      allUsers: "Всички потребители"
    }
  }

  if (!resources.ro.common.archive) {
    resources.ro.common.archive = {
      tabs: {
        review: "Revizuire",
        generate: "Generare",
        compare: "Comparare",
        match: "Potrivire"
      },
      metadata: {
        questions: "întrebări",
        questions_one: "întrebare",
        fields: "câmpuri",
        fields_one: "câmp",
        documents: "documente",
        documents_one: "document",
        digitized: "digitalizat",
        handwritten: "scris de mână"
      },
      feedback: {
        positive: "Oferă feedback pozitiv pentru acest rezultat",
        negative: "Oferă feedback negativ pentru acest rezultat",
        hasFeedback: "Acest rezultat are feedback"
      },
      emptyMessages: {
        review: "Încă nu există istoric de revizuiri",
        generate: "Încă nu există istoric de generare",
        compare: "Încă nu există istoric de comparare",
        match: "Încă nu există istoric de potriviri"
      },
      deleteConfirmation: "Ești sigur că vrei să ștergi acest element?",
      history: "Istoric",
      allUsers: "Toți utilizatorii"
    }
  }

  if (!resources.hr.common.archive) {
    resources.hr.common.archive = {
      tabs: {
        review: "Pregled",
        generate: "Generiraj",
        compare: "Usporedi",
        match: "Uskladi"
      },
      metadata: {
        questions: "pitanja",
        questions_one: "pitanje",
        fields: "polja",
        fields_one: "polje",
        documents: "dokumenti",
        documents_one: "dokument",
        digitized: "digitalizirano",
        handwritten: "rukopisno"
      },
      feedback: {
        positive: "Daj pozitivnu povratnu informaciju za ovaj rezultat",
        negative: "Daj negativnu povratnu informaciju za ovaj rezultat",
        hasFeedback: "Ovaj rezultat ima povratnu informaciju"
      },
      emptyMessages: {
        review: "Još nema povijesti pregleda",
        generate: "Još nema povijesti generiranja",
        compare: "Još nema povijesti usporedbe",
        match: "Još nema povijesti usklađivanja"
      },
      deleteConfirmation: "Jeste li sigurni da želite obrisati ovaj element?",
      history: "Povijest",
      allUsers: "Svi korisnici"
    }
  }

  if (!resources.sr.common.archive) {
    resources.sr.common.archive = {
      tabs: {
        review: "Преглед",
        generate: "Генериши",
        compare: "Упореди",
        match: "Усклади"
      },
      metadata: {
        questions: "питања",
        questions_one: "питање",
        fields: "поља",
        fields_one: "поље",
        documents: "документи",
        documents_one: "документ",
        digitized: "дигитализовано",
        handwritten: "рукописно"
      },
      feedback: {
        positive: "Дај позитивну повратну информацију за овај резултат",
        negative: "Дај негативну повратну информацију за овај резултат",
        hasFeedback: "Овај резултат има повратну информацију"
      },
      emptyMessages: {
        review: "Још нема историје прегледа",
        generate: "Још нема историје генерисања",
        compare: "Још нема историје поређења",
        match: "Још нема историје усклађивања"
      },
      deleteConfirmation: "Да ли сте сигурни да желите да обришете овај елемент?",
      history: "Историја",
      allUsers: "Сви корисници"
    }
  }

  if (!resources.el.common.archive) {
    resources.el.common.archive = {
      tabs: {
        review: "Αναθεώρηση",
        generate: "Δημιουργία",
        compare: "Σύγκριση",
        match: "Αντιστοίχιση"
      },
      metadata: {
        questions: "ερωτήσεις",
        questions_one: "ερώτηση",
        fields: "πεδία",
        fields_one: "πεδίο",
        documents: "έγγραφα",
        documents_one: "έγγραφο",
        digitized: "ψηφιοποιημένο",
        handwritten: "χειρόγραφο"
      },
      feedback: {
        positive: "Δώστε θετική ανατροφοδότηση για αυτό το αποτέλεσμα",
        negative: "Δώστε αρνητική ανατροφοδότηση για αυτό το αποτέλεσμα",
        hasFeedback: "Αυτό το αποτέλεσμα έχει ανατροφοδότηση"
      },
      emptyMessages: {
        review: "Δεν υπάρχει ιστορικό αναθεώρησης ακόμη",
        generate: "Δεν υπάρχει ιστορικό δημιουργίας ακόμη",
        compare: "Δεν υπάρχει ιστορικό σύγκρισης ακόμη",
        match: "Δεν υπάρχει ιστορικό αντιστοίχισης ακόμη"
      },
      deleteConfirmation: "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το στοιχείο;",
      history: "Ιστορικό",
      allUsers: "Όλοι οι χρήστες"
    }
  }

  // Add Settings extensions for Baltic and Eastern European languages
  if (resources.et.common.settings) {
    Object.assign(resources.et.common.settings, {
      currentPassword: "Praegune Parool",
      newPassword: "Uus Parool",
      confirmPassword: "Kinnita Parool",
      save: "Salvesta",
      system: "Süsteem",
      lightMode: "Hele Režiim",
      darkMode: "Tume Režiim",
      deleteAccountDescription: "Kustuta oma andmed ja kõik, mis on seotud teie kontoga, jäädavalt.",
      delete: "Kustuta"
    })
  }

  if (resources.lv.common.settings) {
    Object.assign(resources.lv.common.settings, {
      currentPassword: "Pašreizējā Parole",
      newPassword: "Jauna Parole",
      confirmPassword: "Apstiprināt Paroli",
      save: "Saglabāt",
      system: "Sistēma",
      lightMode: "Gaišais Režīms",
      darkMode: "Tumšais Režīms",
      deleteAccountDescription: "Neatgriezeniski dzēst jūsu datus un visu, kas saistīts ar jūsu kontu.",
      delete: "Dzēst"
    })
  }

  if (resources.lt.common.settings) {
    Object.assign(resources.lt.common.settings, {
      currentPassword: "Dabartinis Slaptažodis",
      newPassword: "Naujas Slaptažodis",
      confirmPassword: "Patvirtinti Slaptažodį",
      save: "Išsaugoti",
      system: "Sistema",
      lightMode: "Šviesus Režimas",
      darkMode: "Tamsus Režimas",
      deleteAccountDescription: "Visam laikui ištrinti jūsų duomenis ir viską, kas susiję su jūsų paskyra.",
      delete: "Ištrinti"
    })
  }

  if (resources.pl.common.settings) {
    Object.assign(resources.pl.common.settings, {
      currentPassword: "Obecne Hasło",
      newPassword: "Nowe Hasło",
      confirmPassword: "Potwierdź Hasło",
      save: "Zapisz",
      system: "System",
      lightMode: "Tryb Jasny",
      darkMode: "Tryb Ciemny",
      deleteAccountDescription: "Trwale usuń swoje dane i wszystko, co jest związane z Twoim kontem.",
      delete: "Usuń"
    })
  }

  if (resources.ru.common.settings) {
    Object.assign(resources.ru.common.settings, {
      currentPassword: "Текущий пароль",
      newPassword: "Новый пароль",
      confirmPassword: "Подтвердить пароль",
      save: "Сохранить",
      system: "Система",
      lightMode: "Светлый режим",
      darkMode: "Тёмный режим",
      deleteAccountDescription: "Навсегда удалить ваши данные и все, что связано с вашим аккаунтом.",
      delete: "Удалить"
    })
  }

  if (resources.uk.common.settings) {
    Object.assign(resources.uk.common.settings, {
      currentPassword: "Поточний пароль",
      newPassword: "Новий пароль",
      confirmPassword: "Підтвердити пароль",
      save: "Зберегти",
      system: "Система",
      lightMode: "Світлий режим",
      darkMode: "Темний режим",
      deleteAccountDescription: "Назавжди видалити ваші дані та все, що пов'язано з вашим акаунтом.",
      delete: "Видалити"
    })
  }

  if (resources.bg.common.settings) {
    Object.assign(resources.bg.common.settings, {
      currentPassword: "Текуща парола",
      newPassword: "Нова парола",
      confirmPassword: "Потвърди парола",
      save: "Запази",
      system: "Система",
      lightMode: "Светъл режим",
      darkMode: "Тъмен режим",
      deleteAccountDescription: "Завинаги изтрий данните си и всичко, което е свързано с акаунта ти.",
      delete: "Изтрий"
    })
  }

  if (resources.ro.common.settings) {
    Object.assign(resources.ro.common.settings, {
      currentPassword: "Parola Curentă",
      newPassword: "Parolă Nouă",
      confirmPassword: "Confirmă Parola",
      save: "Salvează",
      system: "Sistem",
      lightMode: "Mod Luminos",
      darkMode: "Mod Întunecat",
      deleteAccountDescription: "Șterge permanent datele tale și tot ce este asociat cu contul tău.",
      delete: "Șterge"
    })
  }

  if (resources.hr.common.settings) {
    Object.assign(resources.hr.common.settings, {
      currentPassword: "Trenutna Lozinka",
      newPassword: "Nova Lozinka",
      confirmPassword: "Potvrdi Lozinku",
      save: "Spremi",
      system: "Sustav",
      lightMode: "Svijetli Način",
      darkMode: "Tamni Način",
      deleteAccountDescription: "Trajno obriši svoje podatke i sve što je povezano s tvojim računom.",
      delete: "Obriši"
    })
  }

  if (resources.sr.common.settings) {
    Object.assign(resources.sr.common.settings, {
      currentPassword: "Тренутна Лозинка",
      newPassword: "Нова Лозинка",
      confirmPassword: "Потврди Лозинку",
      save: "Сачувај",
      system: "Систем",
      lightMode: "Светли Режим",
      darkMode: "Тамни Режим",
      deleteAccountDescription: "Трајно обриши своје податке и све што је повезано са твојим налогом.",
      delete: "Обриши"
    })
  }

  if (resources.el.common.settings) {
    Object.assign(resources.el.common.settings, {
      currentPassword: "Τρέχων Κωδικός",
      newPassword: "Νέος Κωδικός",
      confirmPassword: "Επιβεβαίωση Κωδικού",
      save: "Αποθήκευση",
      system: "Σύστημα",
      lightMode: "Φωτεινή Λειτουργία",
      darkMode: "Σκοτεινή Λειτουργία",
      deleteAccountDescription: "Διαγραφή των δεδομένων σας και όλων όσων συνδέονται με τον λογαριασμό σας μόνιμα.",
      delete: "Διαγραφή"
    })
  }
}
