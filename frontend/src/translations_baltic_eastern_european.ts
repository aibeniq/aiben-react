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
      chatbot: {
        placeholder: "Kirjuta oma sõnum siia...",
        send: "Saada",
        newChat: "Uus vestlus",
        clearHistory: "Kustuta ajalugu",
        typing: "AI kirjutab...",
        error: "Vabandust, midagi läks valesti. Proovi uuesti.",
        welcome: "Tere! Kuidas saan teid täna aidata?",
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
        customInstructionsHelp: "{count}/2000 märki. Need juhised lisatakse töötlemise ajal igale küsimusele.",
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
      chatbot: {
        placeholder: "Ierakstiet savu ziņu šeit...",
        send: "Sūtīt",
        newChat: "Jauna saruna",
        clearHistory: "Dzēst vēsturi",
        typing: "AI raksta...",
        error: "Atvainojiet, kaut kas nogāja greizi. Mēģiniet vēlreiz.",
        welcome: "Sveiki! Kā es varu jums palīdzēt šodien?",
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
        customInstructionsHelp: "{count}/2000 rakstzīmes. Šīs instrukcijas tiks pievienotas katram jautājumam apstrādes laikā.",
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
      chatbot: {
        placeholder: "Įrašykite savo žinutę čia...",
        send: "Siųsti",
        newChat: "Naujas pokalbis",
        clearHistory: "Išvalyti istoriją",
        typing: "AI rašo...",
        error: "Atsiprašome, kažkas nutiko. Bandykite dar kartą.",
        welcome: "Sveiki! Kaip galiu jums šiandien padėti?",
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
        customInstructionsHelp: "{count}/2000 simbolių. Šios instrukcijos bus pridėtos prie kiekvieno klausimo apdorojimo metu.",
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
      chatbot: {
        placeholder: "Γράψτε το μήνυμά σας εδώ...",
        send: "Αποστολή",
        newChat: "Νέα συνομιλία",
        clearHistory: "Διαγραφή ιστορικού",
        typing: "Το AI γράφει...",
        error: "Συγγνώμη, κάτι πήγε στραβά. Δοκιμάστε ξανά.",
        welcome: "Γεια σας! Πώς μπορώ να σας βοηθήσω σήμερα;",
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
        customInstructionsHelp: "{count}/2000 χαρακτήρες. Αυτές οι οδηγίες θα προστεθούν σε κάθε ερώτηση κατά την επεξεργασία.",
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
}
