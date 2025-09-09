// Middle Eastern and Other Languages Translations
// Hebrew (he), Persian/Farsi (fa), Turkish (tr), Swahili (sw), Portuguese Brazilian (pt-BR), Spanish Latin America (es-LATAM)

export const addMiddleEasternOtherTranslations = (resources: any) => {
  // Hebrew
  resources.he = {
    common: {
      navigation: {
        dashboard: "לוח בקרה",
        review: "סקירה",
        generate: "יצירה",
        compare: "השוואה",
        match: "התאמה",
        modelSelection: "בחירת מודל",
        knowledgeBases: "בסיסי ידע",
        archive: "ארכיון",
        settings: "הגדרות",
        admin: "מנהל",
        menu: "תפריט",
        tools: "כלים",
        configurations: "תצורות",
        myProfile: "הפרופיל שלי",
        logout: "התנתקות",
        loggedInAs: "מחובר כ: {{email}}",
      },
      buttons: {
        upload: "העלאה",
        download: "הורדה",
        save: "שמירה",
        cancel: "ביטול",
        delete: "מחיקה",
        edit: "עריכה",
        submit: "שליחה",
        close: "סגירה",
        next: "הבא",
        previous: "הקודם",
        confirm: "אישור",
        back: "חזרה",
      },
      forms: {
        firstName: "שם פרטי",
        lastName: "שם משפחה",
        email: 'דוא"ל',
        password: "סיסמה",
        confirmPassword: "אישור סיסמה",
        currentPassword: "סיסמה נוכחית",
        newPassword: "סיסמה חדשה",
        required: "חובה",
        optional: "אופציונלי",
        emailPlaceholder: 'הזן את כתובת הדוא"ל שלך',
        passwordPlaceholder: "הזן את הסיסמה שלך",
      },
      chatbot: {
        placeholder: "הקלד את ההודעה שלך כאן...",
        send: "שלח",
        newChat: "צ'אט חדש",
        clearHistory: "נקה היסטוריה",
        typing: "הבינה המלאכותית כותבת...",
        error: "סליחה, משהו השתבש. נסה שוב.",
        welcome: "שלום! איך אני יכול לעזור לך היום?",
      },
      settings: {
        title: "הגדרות",
        account: "חשבון",
        language: "שפה",
        dangerZone: "אזור מסוכן",
        preferredLanguage: "שפה מועדפת",
        saveLanguagePreference: "שמור העדפת שפה",
        deleteAccount: "מחק חשבון",
        deleteAccountWarning: "פעולה זו לא ניתנת לביטול.",
        profile: "פרופיל",
        security: "אבטחה",
        changePassword: "שנה סיסמה",
        appearance: "מראה",
      },
      errors: {
        somethingWentWrong: "משהו השתבש",
        tryAgain: "נסה שוב",
        invalidEmail: 'כתובת דוא"ל לא חוקית',
        passwordTooShort: "הסיסמה קצרה מדי",
        passwordsDoNotMatch: "הסיסמות לא תואמות",
        networkError: "שגיאת רשת. בדוק את החיבור שלך.",
        unauthorized: "אין לך הרשאה לבצע פעולה זו.",
        notFound: "המשאב המבוקש לא נמצא.",
      },
      common: {
        loading: "טוען...",
        noData: "אין נתונים זמינים",
        success: "הצלחה!",
        failed: "נכשל",
        welcome: "ברוך הבא",
        goodbye: "להתראות",
        yes: "כן",
        no: "לא",
        ok: "אישור",
        search: "חיפוש",
        filter: "מסנן",
        sort: "מיון",
        view: "צפייה",
        copy: "העתקה",
        paste: "הדבקה",
        cut: "גזירה",
      },
      review: {
        pageTitle: "בדיקת מסמכים",
        pageDescription: "בדיקת מסמך על בסיס רשימת בדיקה ומאגר מדיניות שהוגדרו על ידי המשתמש.",
        knowledgeBaseTitle: "בסיס ידע",
        knowledgeBaseDescription: "לחץ לבחירה",
        checklistTitle: "רשימת בדיקה",
        checklistDescription: "לחץ לבחירה",
        customInstructionsTitle: "הוראות מותאמות אישית (אופציונלי)",
        customInstructionsPlaceholder: "הזן הוראות נוספות שיש לקחת בחשבון בעת מענה על שאלות רשימת הבדיקה...",
        customInstructionsHelp: "{count}/2000 תווים. הוראות אלה יתווספו לכל שאלה במהלך העיבוד.",
        searchModeHelp: "חיפוש וקטור מספק תוצאות מהירות וממוקדות. ניתוח מסמך מלא בוחן את כל התוכן בבסיס הידע.",
        processingFile: "מעבד קובץ...",
        processingFiles: "מעבד קבצים...",
        selectKnowledgeBaseTitle: "בחר בסיס ידע",
        selectChecklistTitle: "בחר רשימת בדיקה",
        noResults: "עדיין אין תוצאות",
        uploadDocuments: "העלה מסמך אחד או יותר לבדיקה מול רשימת הבדיקה שבחרת",
        results: "תוצאות",
        downloadReport: "הורד דוח",
        downloadCsv: "הורד CSV",
        clearResults: "נקה תוצאות",
        copyReport: "העתק דוח",
        reportCopied: "הדוח הועתק ללוח!",
        reviewButton: "בדוק",
        consultDocuments: "התייעץ עם מסמכים",
        noChecklistsAvailable: "אין רשימות בדיקה זמינות. צור את רשימת הבדיקה הראשונה שלך כדי להתחיל.",
        createChecklist: "צור רשימת בדיקה",
        editChecklist: "ערוך רשימת בדיקה",
        checklistName: "שם רשימת הבדיקה",
        checklistNamePlaceholder: "הזן שם רשימת בדיקה...",
        checklistDescriptionLabel: "תיאור",
        checklistDescriptionPlaceholder: "הזן תיאור רשימת בדיקה להצעות שאלות אוטומטיות (לפחות 10 תווים)...",
        questions: "שאלות",
        suggest: "הצע",
        suggesting: "מציע...",
        optimize: "אופטימיזציה",
        optimizeTooltip: "יש לבחור בסיס ידע כדי להפעיל את פונקציית האופטימיזציה",
        optimizeTooltipEnabled: "בצע אופטימיזציה לשאלות על בסיס בסיס הידע שנבחר",
        uploadFiles: "העלה קבצים",
        knowledgeBase: "בסיס ידע",
        referenceDocuments: "מסמכי עזר (אופציונלי)",
        selectKnowledgeBasePlaceholder: "בחר בסיס ידע...",
        noKnowledgeBasesAvailable: "אין בסיס ידע זמין. צור קודם כדי להשתמש בפונקציה זו.",
        copyQuestions: "העתק שאלות",
        questionsCopied: "השאלות הועתקו ללוח",
        noQuestionsToCopy: "אין שאלות להעתקה",
        failedToCopyQuestions: "נכשל בהעתקת השאלות ללוח",
        saveChecklist: "שמור רשימת בדיקה",
        cancel: "ביטול",
        deleteChecklist: "מחק רשימת בדיקה"
      },
    },
  }

  // Persian/Farsi
  resources.fa = {
    common: {
      navigation: {
        dashboard: "داشبورد",
        review: "بررسی",
        generate: "تولید",
        compare: "مقایسه",
        match: "تطبیق",
        modelSelection: "انتخاب مدل",
        knowledgeBases: "پایگاه‌های دانش",
        archive: "آرشیو",
        settings: "تنظیمات",
        admin: "مدیر",
        menu: "منو",
        tools: "ابزارها",
        configurations: "پیکربندی‌ها",
        myProfile: "پروفایل من",
        logout: "خروج",
        loggedInAs: "وارد شده به عنوان: {{email}}",
      },
      buttons: {
        upload: "بارگذاری",
        download: "دانلود",
        save: "ذخیره",
        cancel: "لغو",
        delete: "حذف",
        edit: "ویرایش",
        submit: "ارسال",
        close: "بستن",
        next: "بعدی",
        previous: "قبلی",
        confirm: "تأیید",
        back: "برگشت",
      },
      forms: {
        firstName: "نام",
        lastName: "نام خانوادگی",
        email: "ایمیل",
        password: "رمز عبور",
        confirmPassword: "تأیید رمز عبور",
        currentPassword: "رمز عبور فعلی",
        newPassword: "رمز عبور جدید",
        required: "اجباری",
        optional: "اختیاری",
        emailPlaceholder: "آدرس ایمیل خود را وارد کنید",
        passwordPlaceholder: "رمز عبور خود را وارد کنید",
      },
      chatbot: {
        placeholder: "پیام خود را اینجا بنویسید...",
        send: "ارسال",
        newChat: "چت جدید",
        clearHistory: "پاک کردن تاریخچه",
        typing: "هوش مصنوعی در حال نوشتن...",
        error: "متأسفیم، مشکلی پیش آمد. دوباره تلاش کنید.",
        welcome: "سلام! امروز چگونه می‌توانم کمکتان کنم؟",
      },
      settings: {
        title: "تنظیمات",
        account: "حساب",
        language: "زبان",
        dangerZone: "منطقه خطر",
        preferredLanguage: "زبان مرجح",
        saveLanguagePreference: "ذخیره ترجیح زبان",
        deleteAccount: "حذف حساب",
        deleteAccountWarning: "این عمل قابل برگشت نیست.",
        profile: "پروفایل",
        security: "امنیت",
        changePassword: "تغییر رمز عبور",
        appearance: "ظاهر",
      },
      errors: {
        somethingWentWrong: "مشکلی پیش آمد",
        tryAgain: "دوباره تلاش کنید",
        invalidEmail: "آدرس ایمیل نامعتبر",
        passwordTooShort: "رمز عبور خیلی کوتاه است",
        passwordsDoNotMatch: "رمزهای عبور مطابقت ندارند",
        networkError: "خطای شبکه. اتصال خود را بررسی کنید.",
        unauthorized: "شما مجوز انجام این عمل را ندارید.",
        notFound: "منبع درخواستی یافت نشد.",
      },
      common: {
        loading: "در حال بارگذاری...",
        noData: "داده‌ای موجود نیست",
        success: "موفق!",
        failed: "ناموفق",
        welcome: "خوش آمدید",
        goodbye: "خداحافظ",
        yes: "بله",
        no: "خیر",
        ok: "تایید",
        search: "جستجو",
        filter: "فیلتر",
        sort: "مرتب‌سازی",
        view: "نمایش",
        copy: "کپی",
        paste: "چسباندن",
        cut: "برش",
      },
      review: {
        pageTitle: "بررسی اسناد",
        pageDescription: "بررسی سند بر اساس چک‌لیست و پایگاه داده سیاست‌های تعریف شده توسط کاربر.",
        knowledgeBaseTitle: "پایگاه دانش",
        knowledgeBaseDescription: "برای انتخاب کلیک کنید",
        checklistTitle: "چک‌لیست",
        checklistDescription: "برای انتخاب کلیک کنید",
        customInstructionsTitle: "دستورالعمل‌های سفارشی (اختیاری)",
        customInstructionsPlaceholder: "دستورالعمل‌های اضافی که هنگام پاسخ به سوالات چک‌لیست باید در نظر گرفته شود را وارد کنید...",
        customInstructionsHelp: "{count}/2000 کاراکتر. این دستورالعمل‌ها به هر سوال در طول پردازش اضافه خواهد شد.",
        searchModeHelp: "جستجوی برداری نتایج سریع و هدفمند ارائه می‌دهد. تجزیه و تحلیل کامل سند تمام محتوای پایگاه دانش را بررسی می‌کند.",
        processingFile: "در حال پردازش فایل...",
        processingFiles: "در حال پردازش فایل‌ها...",
        selectKnowledgeBaseTitle: "انتخاب پایگاه دانش",
        selectChecklistTitle: "انتخاب چک‌لیست",
        noResults: "هنوز نتیجه‌ای نیست",
        uploadDocuments: "یک یا چند سند برای بررسی در برابر چک‌لیست انتخابی خود آپلود کنید",
        results: "نتایج",
        downloadReport: "دانلود گزارش",
        downloadCsv: "دانلود CSV",
        clearResults: "پاک کردن نتایج",
        copyReport: "کپی گزارش",
        reportCopied: "گزارش در کلیپ‌بورد کپی شد!",
        reviewButton: "بررسی",
        consultDocuments: "مشورت با اسناد",
        noChecklistsAvailable: "هیچ چک‌لیستی موجود نیست. اولین چک‌لیست خود را برای شروع ایجاد کنید.",
        createChecklist: "ایجاد چک‌لیست",
        editChecklist: "ویرایش چک‌لیست",
        checklistName: "نام چک‌لیست",
        checklistNamePlaceholder: "نام چک‌لیست را وارد کنید...",
        checklistDescriptionLabel: "توضیحات",
        checklistDescriptionPlaceholder: "توضیحات چک‌لیست را برای پیشنهادات خودکار سوال وارد کنید (حداقل 10 کاراکتر)...",
        questions: "سوالات",
        suggest: "پیشنهاد",
        suggesting: "در حال پیشنهاد...",
        optimize: "بهینه‌سازی",
        optimizeTooltip: "برای فعال کردن عملکرد بهینه‌سازی باید پایگاه دانش انتخاب شود",
        optimizeTooltipEnabled: "بهینه‌سازی سوالات بر اساس پایگاه دانش انتخاب شده",
        uploadFiles: "آپلود فایل‌ها",
        knowledgeBase: "پایگاه دانش",
        referenceDocuments: "اسناد مرجع (اختیاری)",
        selectKnowledgeBasePlaceholder: "انتخاب پایگاه دانش...",
        noKnowledgeBasesAvailable: "هیچ پایگاه دانشی موجود نیست. ابتدا یکی ایجاد کنید تا از این عملکرد استفاده کنید.",
        copyQuestions: "کپی سوالات",
        questionsCopied: "سوالات در کلیپ‌بورد کپی شد",
        noQuestionsToCopy: "سوالی برای کپی کردن نیست",
        failedToCopyQuestions: "کپی کردن سوالات در کلیپ‌بورد ناموفق بود",
        saveChecklist: "ذخیره چک‌لیست",
        cancel: "لغو",
        deleteChecklist: "حذف چک‌لیست"
      },
    },
  }

  // Turkish
  resources.tr = {
    common: {
      navigation: {
        dashboard: "Kontrol Paneli",
        review: "İnceleme",
        generate: "Oluştur",
        compare: "Karşılaştır",
        match: "Eşleştir",
        modelSelection: "Model Seçimi",
        knowledgeBases: "Bilgi Tabanları",
        archive: "Arşiv",
        settings: "Ayarlar",
        admin: "Yönetici",
        menu: "Menü",
        tools: "Araçlar",
        configurations: "Yapılandırmalar",
        myProfile: "Profilim",
        logout: "Çıkış",
        loggedInAs: "Giriş yapılan: {{email}}",
      },
      buttons: {
        upload: "Yükle",
        download: "İndir",
        save: "Kaydet",
        cancel: "İptal",
        delete: "Sil",
        edit: "Düzenle",
        submit: "Gönder",
        close: "Kapat",
        next: "Sonraki",
        previous: "Önceki",
        confirm: "Onayla",
        back: "Geri",
      },
      forms: {
        firstName: "Ad",
        lastName: "Soyad",
        email: "E-posta",
        password: "Şifre",
        confirmPassword: "Şifreyi Onayla",
        currentPassword: "Mevcut Şifre",
        newPassword: "Yeni Şifre",
        required: "Zorunlu",
        optional: "İsteğe Bağlı",
        emailPlaceholder: "E-posta adresinizi girin",
        passwordPlaceholder: "Şifrenizi girin",
      },
      chatbot: {
        placeholder: "Mesajınızı buraya yazın...",
        send: "Gönder",
        newChat: "Yeni Sohbet",
        clearHistory: "Geçmişi Temizle",
        typing: "AI yazıyor...",
        error: "Üzgünüz, bir şeyler ters gitti. Tekrar deneyin.",
        welcome: "Merhaba! Bugün size nasıl yardımcı olabilirim?",
      },
      settings: {
        title: "Ayarlar",
        account: "Hesap",
        language: "Dil",
        dangerZone: "Tehlike Bölgesi",
        preferredLanguage: "Tercih Edilen Dil",
        saveLanguagePreference: "Dil Tercihini Kaydet",
        deleteAccount: "Hesabı Sil",
        deleteAccountWarning: "Bu işlem geri alınamaz.",
        profile: "Profil",
        security: "Güvenlik",
        changePassword: "Şifre Değiştir",
        appearance: "Görünüm",
      },
      errors: {
        somethingWentWrong: "Bir şeyler ters gitti",
        tryAgain: "Tekrar deneyin",
        invalidEmail: "Geçersiz e-posta adresi",
        passwordTooShort: "Şifre çok kısa",
        passwordsDoNotMatch: "Şifreler eşleşmiyor",
        networkError: "Ağ hatası. Bağlantınızı kontrol edin.",
        unauthorized: "Bu eylemi gerçekleştirme yetkiniz yok.",
        notFound: "İstenen kaynak bulunamadı.",
      },
      common: {
        loading: "Yükleniyor...",
        noData: "Kullanılabilir veri yok",
        success: "Başarılı!",
        failed: "Başarısız",
        welcome: "Hoş geldiniz",
        goodbye: "Hoşça kalın",
        yes: "Evet",
        no: "Hayır",
        ok: "Tamam",
        search: "Ara",
        filter: "Filtre",
        sort: "Sırala",
        view: "Görüntüle",
        copy: "Kopyala",
        paste: "Yapıştır",
        cut: "Kes",
      },
      review: {
        pageTitle: "Belgeleri İncele",
        pageDescription: "Kullanıcı tanımlı kontrol listesi ve politika veritabanına dayalı olarak bir belgeyi inceleyin.",
        knowledgeBaseTitle: "Bilgi Tabanı",
        knowledgeBaseDescription: "Seçmek için tıklayın",
        checklistTitle: "Kontrol Listesi",
        checklistDescription: "Seçmek için tıklayın",
        customInstructionsTitle: "Özel Talimatlar (İsteğe Bağlı)",
        customInstructionsPlaceholder: "Kontrol listesi sorularını yanıtlarken dikkate alınması gereken ek talimatları girin...",
        customInstructionsHelp: "{count}/2000 karakter. Bu talimatlar işleme sırasında her soruya eklenecektir.",
        searchModeHelp: "Vektör arama hızlı, hedefli sonuçlar sağlar. Tam belge analizi bilgi tabanının tüm içeriğini inceler.",
        processingFile: "Dosya işleniyor...",
        processingFiles: "Dosyalar işleniyor...",
        selectKnowledgeBaseTitle: "Bilgi Tabanı Seç",
        selectChecklistTitle: "Kontrol Listesi Seç",
        noResults: "Henüz sonuç yok",
        uploadDocuments: "Seçili kontrol listenize karşı incelemek için bir veya daha fazla belge yükleyin",
        results: "Sonuçlar",
        downloadReport: "Raporu İndir",
        downloadCsv: "CSV İndir",
        clearResults: "Sonuçları Temizle",
        copyReport: "Raporu Kopyala",
        reportCopied: "Rapor panoya kopyalandı!",
        reviewButton: "İncele",
        consultDocuments: "Belgelere danış",
        noChecklistsAvailable: "Mevcut kontrol listesi yok. Başlamak için ilk kontrol listenizi oluşturun.",
        createChecklist: "Kontrol Listesi Oluştur",
        editChecklist: "Kontrol Listesini Düzenle",
        checklistName: "Kontrol Listesi Adı",
        checklistNamePlaceholder: "Kontrol listesi adını girin...",
        checklistDescriptionLabel: "Açıklama",
        checklistDescriptionPlaceholder: "Otomatik soru önerileri için kontrol listesi açıklamasını girin (en az 10 karakter)...",
        questions: "Sorular",
        suggest: "Öner",
        suggesting: "Öneriliyor...",
        optimize: "Optimize Et",
        optimizeTooltip: "Optimize Et işlevini etkinleştirmek için bir Bilgi Tabanı seçilmelidir",
        optimizeTooltipEnabled: "Seçili Bilgi Tabanına göre soruları optimize et",
        uploadFiles: "Dosyaları Yükle",
        knowledgeBase: "Bilgi Tabanı",
        referenceDocuments: "Referans Belgeler (İsteğe Bağlı)",
        selectKnowledgeBasePlaceholder: "Bilgi Tabanı Seç...",
        noKnowledgeBasesAvailable: "Kullanılabilir Bilgi Tabanı yok. Bu işlevi kullanmak için önce bir tane oluşturun.",
        copyQuestions: "Soruları Kopyala",
        questionsCopied: "Sorular panoya kopyalandı",
        noQuestionsToCopy: "Kopyalanacak soru yok",
        failedToCopyQuestions: "Sorular panoya kopyalanamadı",
        saveChecklist: "Kontrol Listesini Kaydet",
        cancel: "İptal",
        deleteChecklist: "Kontrol Listesini Sil"
      },
    },
  }

  // Swahili
  resources.sw = {
    common: {
      navigation: {
        dashboard: "Dashibodi",
        review: "Ukaguzi",
        generate: "Tengeneza",
        compare: "Linganisha",
        match: "Oanisha",
        modelSelection: "Uchaguzi wa Mfano",
        knowledgeBases: "Msingi wa Maarifa",
        archive: "Kumbukumbu",
        settings: "Mipangilio",
        admin: "Msimamizi",
        menu: "Menyu",
        tools: "Vifaa",
        configurations: "Mipangilio",
        myProfile: "Wasifu Wangu",
        logout: "Toka",
        loggedInAs: "Umeingia kama: {{email}}",
      },
      buttons: {
        upload: "Pakia",
        download: "Pakua",
        save: "Hifadhi",
        cancel: "Ghairi",
        delete: "Futa",
        edit: "Hariri",
        submit: "Wasilisha",
        close: "Funga",
        next: "Ifuatayo",
        previous: "Iliyotangulia",
        confirm: "Thibitisha",
        back: "Rudi",
      },
      forms: {
        firstName: "Jina la Kwanza",
        lastName: "Jina la Mwisho",
        email: "Barua Pepe",
        password: "Nenosiri",
        confirmPassword: "Thibitisha Nenosiri",
        currentPassword: "Nenosiri la Sasa",
        newPassword: "Nenosiri Jipya",
        required: "Inahitajika",
        optional: "Si Lazima",
        emailPlaceholder: "Ingiza anwani yako ya barua pepe",
        passwordPlaceholder: "Ingiza nenosiri lako",
      },
      chatbot: {
        placeholder: "Andika ujumbe wako hapa...",
        send: "Tuma",
        newChat: "Mazungumzo Mapya",
        clearHistory: "Futa Historia",
        typing: "AI inaandika...",
        error: "Samahani, kuna hitilafu. Jaribu tena.",
        welcome: "Hujambo! Ninawezaje kukusaidia leo?",
      },
      settings: {
        title: "Mipangilio",
        account: "Akaunti",
        language: "Lugha",
        dangerZone: "Eneo la Hatari",
        preferredLanguage: "Lugha Unayopendelea",
        saveLanguagePreference: "Hifadhi Chaguo la Lugha",
        deleteAccount: "Futa Akaunti",
        deleteAccountWarning: "Hatua hii haiwezi kutenduliwa.",
        profile: "Wasifu",
        security: "Usalama",
        changePassword: "Badilisha Nenosiri",
        appearance: "Mwonekano",
      },
      errors: {
        somethingWentWrong: "Kuna hitilafu",
        tryAgain: "Jaribu tena",
        invalidEmail: "Anwani ya barua pepe si sahihi",
        passwordTooShort: "Nenosiri ni fupi sana",
        passwordsDoNotMatch: "Nenosiri hazilingani",
        networkError: "Hitilafu ya mtandao. Angalia muunganisho wako.",
        unauthorized: "Huna ruhusa ya kufanya kitendo hiki.",
        notFound: "Rasilimali uliyoomba haikupatikana.",
      },
      common: {
        loading: "Inapakia...",
        noData: "Hakuna data inayopatikana",
        success: "Mafanikio!",
        failed: "Imeshindwa",
        welcome: "Karibu",
        goodbye: "Kwaheri",
        yes: "Ndiyo",
        no: "Hapana",
        ok: "Sawa",
        search: "Tafuta",
        filter: "Chuja",
        sort: "Panga",
        view: "Ona",
        copy: "Nakili",
        paste: "Bandika",
        cut: "Kata",
      },
      review: {
        pageTitle: "Ukaguzi wa Hati",
        pageDescription: "Kagua hati kulingana na orodha ya ukaguzi iliyofafanuliwa na mtumiaji na hifadhidata ya sera.",
        knowledgeBaseTitle: "Msingi wa Maarifa",
        knowledgeBaseDescription: "Bonyeza kuchagua",
        checklistTitle: "Orodha ya Ukaguzi",
        checklistDescription: "Bonyeza kuchagua",
        customInstructionsTitle: "Maelekezo Maalum (Hiari)",
        customInstructionsPlaceholder: "Ingiza maelekezo ya ziada ambayo yanapaswa kuzingatiwa wakati wa kujibu maswali ya orodha ya ukaguzi...",
        customInstructionsHelp: "Herufi {count}/2000. Maelekezo haya yataongezwa kwa kila swali wakati wa uchakataji.",
        searchModeHelp: "Utafutaji wa vector hutoa matokeo ya haraka na yaliyolengwa. Uchambuzi kamili wa hati huchunguza maudhui yote ya msingi wa maarifa.",
        processingFile: "Inachakata faili...",
        processingFiles: "Inachakata faili...",
        selectKnowledgeBaseTitle: "Chagua Msingi wa Maarifa",
        selectChecklistTitle: "Chagua Orodha ya Ukaguzi",
        noResults: "Hakuna matokeo bado",
        uploadDocuments: "Pakia hati moja au zaidi za kukaaguliwa dhidi ya orodha ya ukaguzi uliyochaguliwa",
        results: "Matokeo",
        downloadReport: "Pakua Ripoti",
        downloadCsv: "Pakua CSV",
        clearResults: "Futa Matokeo",
        copyReport: "Nakili Ripoti",
        reportCopied: "Ripoti imenakiliwa kwenye ubao wa kunakili!",
        reviewButton: "Ukaguzi",
        consultDocuments: "Shauriana na Hati",
        noChecklistsAvailable: "Hakuna orodha za ukaguzi zinazopatikana. Tengeneza orodha yako ya kwanza ya ukaguzi ili uanze.",
        createChecklist: "Tengeneza Orodha ya Ukaguzi",
        editChecklist: "Hariri Orodha ya Ukaguzi",
        checklistName: "Jina la Orodha ya Ukaguzi",
        checklistNamePlaceholder: "Ingiza jina la orodha ya ukaguzi...",
        checklistDescriptionLabel: "Maelezo",
        checklistDescriptionPlaceholder: "Ingiza maelezo ya orodha ya ukaguzi kwa mapendekezo ya otomatiki ya maswali (angalau herufi 10)...",
        questions: "Maswali",
        suggest: "Pendekeza",
        suggesting: "Inapendekeza...",
        optimize: "Boresha",
        optimizeTooltip: "Msingi wa maarifa unapaswa kuchaguliwa ili kuwezesha kipengele cha kuboresha",
        optimizeTooltipEnabled: "Boresha maswali kulingana na msingi wa maarifa uliyochaguliwa",
        uploadFiles: "Pakia Faili",
        knowledgeBase: "Msingi wa Maarifa",
        referenceDocuments: "Hati za Kumbuka (Hiari)",
        selectKnowledgeBasePlaceholder: "Chagua msingi wa maarifa...",
        noKnowledgeBasesAvailable: "Hakuna misingi ya maarifa inayopatikana. Tengeneza moja kwanza ili kutumia kipengele hiki.",
        copyQuestions: "Nakili Maswali",
        questionsCopied: "Maswali yamenakiliwa kwenye ubao wa kunakili",
        noQuestionsToCopy: "Hakuna maswali ya kunakili",
        failedToCopyQuestions: "Imeshindwa kunakili maswali kwenye ubao wa kunakili",
        saveChecklist: "Hifadhi Orodha ya Ukaguzi",
        cancel: "Ghairi",
        deleteChecklist: "Futa Orodha ya Ukaguzi"
      },
    },
  }

  // Portuguese (Brazil)
  resources["pt-BR"] = {
    common: {
      navigation: {
        dashboard: "Painel",
        review: "Revisão",
        generate: "Gerar",
        compare: "Comparar",
        match: "Corresponder",
        modelSelection: "Seleção de Modelo",
        knowledgeBases: "Bases de Conhecimento",
        archive: "Arquivo",
        settings: "Configurações",
        admin: "Administrador",
        menu: "Menu",
        tools: "Ferramentas",
        configurations: "Configurações",
        myProfile: "Meu Perfil",
        logout: "Sair",
        loggedInAs: "Logado como: {{email}}",
      },
      buttons: {
        upload: "Enviar",
        download: "Baixar",
        save: "Salvar",
        cancel: "Cancelar",
        delete: "Excluir",
        edit: "Editar",
        submit: "Enviar",
        close: "Fechar",
        next: "Próximo",
        previous: "Anterior",
        confirm: "Confirmar",
        back: "Voltar",
      },
      forms: {
        firstName: "Nome",
        lastName: "Sobrenome",
        email: "E-mail",
        password: "Senha",
        confirmPassword: "Confirmar Senha",
        currentPassword: "Senha Atual",
        newPassword: "Nova Senha",
        required: "Obrigatório",
        optional: "Opcional",
        emailPlaceholder: "Digite seu endereço de e-mail",
        passwordPlaceholder: "Digite sua senha",
      },
      chatbot: {
        placeholder: "Digite sua mensagem aqui...",
        send: "Enviar",
        newChat: "Nova Conversa",
        clearHistory: "Limpar Histórico",
        typing: "IA está digitando...",
        error: "Desculpe, algo deu errado. Tente novamente.",
        welcome: "Olá! Como posso te ajudar hoje?",
      },
      settings: {
        title: "Configurações",
        account: "Conta",
        language: "Idioma",
        dangerZone: "Zona de Perigo",
        preferredLanguage: "Idioma Preferido",
        saveLanguagePreference: "Salvar Preferência de Idioma",
        deleteAccount: "Excluir Conta",
        deleteAccountWarning: "Esta ação não pode ser desfeita.",
        profile: "Perfil",
        security: "Segurança",
        changePassword: "Alterar Senha",
        appearance: "Aparência",
      },
      errors: {
        somethingWentWrong: "Algo deu errado",
        tryAgain: "Tente novamente",
        invalidEmail: "Endereço de e-mail inválido",
        passwordTooShort: "Senha muito curta",
        passwordsDoNotMatch: "Senhas não conferem",
        networkError: "Erro de rede. Verifique sua conexão.",
        unauthorized: "Você não tem autorização para esta ação.",
        notFound: "Recurso solicitado não encontrado.",
      },
      common: {
        loading: "Carregando...",
        noData: "Nenhum dado disponível",
        success: "Sucesso!",
        failed: "Falhou",
        welcome: "Bem-vindo",
        goodbye: "Tchau",
        yes: "Sim",
        no: "Não",
        ok: "OK",
        search: "Buscar",
        filter: "Filtro",
        sort: "Ordenar",
        view: "Visualizar",
        copy: "Copiar",
        paste: "Colar",
        cut: "Cortar",
      },
    },
  }

  // Spanish (Latin America)
  resources["es-LATAM"] = {
    common: {
      navigation: {
        dashboard: "Panel de Control",
        review: "Revisión",
        generate: "Generar",
        compare: "Comparar",
        match: "Coincidir",
        modelSelection: "Selección de Modelo",
        knowledgeBases: "Bases de Conocimiento",
        archive: "Archivo",
        settings: "Configuraciones",
        admin: "Administrador",
        menu: "Menú",
        tools: "Herramientas",
        configurations: "Configuraciones",
        myProfile: "Mi Perfil",
        logout: "Cerrar Sesión",
        loggedInAs: "Conectado como: {{email}}",
      },
      buttons: {
        upload: "Subir",
        download: "Descargar",
        save: "Guardar",
        cancel: "Cancelar",
        delete: "Eliminar",
        edit: "Editar",
        submit: "Enviar",
        close: "Cerrar",
        next: "Siguiente",
        previous: "Anterior",
        confirm: "Confirmar",
        back: "Atrás",
      },
      forms: {
        firstName: "Nombre",
        lastName: "Apellido",
        email: "Correo Electrónico",
        password: "Contraseña",
        confirmPassword: "Confirmar Contraseña",
        currentPassword: "Contraseña Actual",
        newPassword: "Nueva Contraseña",
        required: "Requerido",
        optional: "Opcional",
        emailPlaceholder: "Ingresa tu dirección de correo",
        passwordPlaceholder: "Ingresa tu contraseña",
      },
      chatbot: {
        placeholder: "Escribe tu mensaje aquí...",
        send: "Enviar",
        newChat: "Nueva Conversación",
        clearHistory: "Limpiar Historial",
        typing: "IA está escribiendo...",
        error: "Lo sentimos, algo salió mal. Inténtalo de nuevo.",
        welcome: "¡Hola! ¿Cómo puedo ayudarte hoy?",
      },
      settings: {
        title: "Configuraciones",
        account: "Cuenta",
        language: "Idioma",
        dangerZone: "Zona Peligrosa",
        preferredLanguage: "Idioma Preferido",
        saveLanguagePreference: "Guardar Preferencia de Idioma",
        deleteAccount: "Eliminar Cuenta",
        deleteAccountWarning: "Esta acción no se puede deshacer.",
        profile: "Perfil",
        security: "Seguridad",
        changePassword: "Cambiar Contraseña",
        appearance: "Apariencia",
      },
      errors: {
        somethingWentWrong: "Algo salió mal",
        tryAgain: "Inténtalo de nuevo",
        invalidEmail: "Dirección de correo inválida",
        passwordTooShort: "La contraseña es muy corta",
        passwordsDoNotMatch: "Las contraseñas no coinciden",
        networkError: "Error de red. Verifica tu conexión.",
        unauthorized: "No tienes autorización para esta acción.",
        notFound: "No se encontró el recurso solicitado.",
      },
      common: {
        loading: "Cargando...",
        noData: "No hay datos disponibles",
        success: "¡Éxito!",
        failed: "Falló",
        welcome: "Bienvenido",
        goodbye: "Adiós",
        yes: "Sí",
        no: "No",
        ok: "OK",
        search: "Buscar",
        filter: "Filtro",
        sort: "Ordenar",
        view: "Ver",
        copy: "Copiar",
        paste: "Pegar",
        cut: "Cortar",
      },
    },
  }

  // Add Model Selection translations to Hebrew
  resources.he.common.modelSelection = {
    llmManagement: "ניהול LLM",
    llmDescription: "קבע תצורה ונהל את מודלי ה-LLM המשמשים ליצירת תגובות טקסט. המודל הברירת מחדל ישמש לכל הפעולות.",
    addNewLlm: "הוסף LLM חדש",
    noLlmsConfigured: "לא הוגדרו מודלי LLM",
    addNewLlmToGetStarted: "הוסף LLM חדש כדי להתחיל",
    embeddingModelManagement: "ניהול מודלי הטמעה",
    embeddingDescription: "קבע תצורה ונהל מודלי הטמעה המשמשים לאינדוקס ואחזור של בסיסי ידע. המודל הברירת מחדל ישמש בעת יצירת בסיסי ידע חדשים, אך כל בסיס ידע ימשיך להשתמש במודל ההטמעה המקורי שלו גם אם ברירת המחדל תשתנה מאוחר יותר.",
    addEmbeddingModel: "הוסף מודל הטמעה",
    noEmbeddingModelsConfigured: "לא הוגדרו מודלי הטמעה",
    addNewEmbeddingModelToGetStarted: "הוסף מודל הטמעה חדש כדי להתחיל",
    tableHeaders: {
      name: "שם",
      modelId: "מזהה מודל",
      provider: "ספק",
      description: "תיאור",
      status: "סטטוס",
      actions: "פעולות"
    },
    status: {
      default: "ברירת מחדל",
      available: "זמין"
    },
    actions: {
      setAsDefault: "קבע כברירת מחדל",
      delete: "מחק",
      validate: "אמת",
      validating: "מאמת"
    },
    dialog: {
      addNewLlm: "הוסף LLM חדש",
      addEmbeddingModel: "הוסף מודל הטמעה",
      displayName: "שם לתצוגה",
      provider: "ספק",
      modelId: "מזהה מודל",
      description: "תיאור",
      cancel: "ביטול",
      addModel: "הוסף מודל"
    },
    placeholders: {
      customModel: "לדוגמה, המודל המותאם שלי",
      embeddingModelId: "לדוגמה, sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "תאר את המודל, את המאפיינים שלו ומתי להשתמש בו"
    },
    validation: {
      pleaseEnterModelId: "אנא הזן מזהה מודל"
    }
  }

  // Add Model Selection translations to Persian/Farsi
  resources.fa.common.modelSelection = {
    llmManagement: "مدیریت LLM",
    llmDescription: "پیکربندی و مدیریت مدل‌های LLM که برای تولید پاسخ‌های متنی استفاده می‌شوند. مدل پیش‌فرض برای همه عملیات استفاده خواهد شد.",
    addNewLlm: "افزودن LLM جدید",
    noLlmsConfigured: "هیچ LLM پیکربندی نشده است",
    addNewLlmToGetStarted: "برای شروع یک LLM جدید اضافه کنید",
    embeddingModelManagement: "مدیریت مدل‌های تعبیه",
    embeddingDescription: "پیکربندی و مدیریت مدل‌های تعبیه که برای نمایه‌سازی و بازیابی پایگاه‌های دانش استفاده می‌شوند. مدل پیش‌فرض هنگام ایجاد پایگاه‌های دانش جدید استفاده خواهد شد، اما هر پایگاه دانش به استفاده از مدل تعبیه اصلی خود ادامه خواهد داد حتی اگر پیش‌فرض بعداً تغییر کند.",
    addEmbeddingModel: "افزودن مدل تعبیه",
    noEmbeddingModelsConfigured: "هیچ مدل تعبیه پیکربندی نشده است",
    addNewEmbeddingModelToGetStarted: "برای شروع یک مدل تعبیه جدید اضافه کنید",
    tableHeaders: {
      name: "نام",
      modelId: "شناسه مدل",
      provider: "ارائه‌دهنده",
      description: "توضیحات",
      status: "وضعیت",
      actions: "اقدامات"
    },
    status: {
      default: "پیش‌فرض",
      available: "در دسترس"
    },
    actions: {
      setAsDefault: "تنظیم به عنوان پیش‌فرض",
      delete: "حذف",
      validate: "اعتبارسنجی",
      validating: "در حال اعتبارسنجی"
    },
    dialog: {
      addNewLlm: "افزودن LLM جدید",
      addEmbeddingModel: "افزودن مدل تعبیه",
      displayName: "نام نمایشی",
      provider: "ارائه‌دهنده",
      modelId: "شناسه مدل",
      description: "توضیحات",
      cancel: "انصراف",
      addModel: "افزودن مدل"
    },
    placeholders: {
      customModel: "مثال، مدل سفارشی من",
      embeddingModelId: "مثال، sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "مدل، ویژگی‌های آن و زمان استفاده از آن را توصیف کنید"
    },
    validation: {
      pleaseEnterModelId: "لطفاً شناسه مدل را وارد کنید"
    }
  }

  // Add Model Selection translations to Turkish
  resources.tr.common.modelSelection = {
    llmManagement: "LLM Yönetimi",
    llmDescription: "Metin yanıtları oluşturmak için kullanılan LLM'leri yapılandırın ve yönetin. Varsayılan model tüm işlemler için kullanılacaktır.",
    addNewLlm: "Yeni LLM Ekle",
    noLlmsConfigured: "Yapılandırılmış LLM yok",
    addNewLlmToGetStarted: "Başlamak için yeni bir LLM ekleyin",
    embeddingModelManagement: "Gömme Modeli Yönetimi",
    embeddingDescription: "Bilgi tabanı indeksleme ve erişim için kullanılan gömme modellerini yapılandırın ve yönetin. Varsayılan model yeni bilgi tabanları oluştururken kullanılacaktır, ancak her bilgi tabanı varsayılan daha sonra değişse bile orijinal gömme modelini kullanmaya devam edecektir.",
    addEmbeddingModel: "Gömme Modeli Ekle",
    noEmbeddingModelsConfigured: "Yapılandırılmış gömme modeli yok",
    addNewEmbeddingModelToGetStarted: "Başlamak için yeni bir gömme modeli ekleyin",
    tableHeaders: {
      name: "Ad",
      modelId: "Model ID",
      provider: "Sağlayıcı",
      description: "Açıklama",
      status: "Durum",
      actions: "İşlemler"
    },
    status: {
      default: "Varsayılan",
      available: "Mevcut"
    },
    actions: {
      setAsDefault: "Varsayılan olarak ayarla",
      delete: "Sil",
      validate: "Doğrula",
      validating: "Doğrulanıyor"
    },
    dialog: {
      addNewLlm: "Yeni LLM Ekle",
      addEmbeddingModel: "Gömme Modeli Ekle",
      displayName: "Görünen Ad",
      provider: "Sağlayıcı",
      modelId: "Model ID",
      description: "Açıklama",
      cancel: "İptal",
      addModel: "Model Ekle"
    },
    placeholders: {
      customModel: "örn., Özel Modelim",
      embeddingModelId: "örn., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Modeli, özelliklerini ve ne zaman kullanılacağını açıklayın"
    },
    validation: {
      pleaseEnterModelId: "Lütfen model ID girin"
    }
  }

  // Add Model Selection translations to Swahili
  resources.sw.common.modelSelection = {
    llmManagement: "Usimamizi wa LLM",
    llmDescription: "Sanidi na simamia LLM zinazotumika kuzalisha majibu ya maandishi. Mfano chaguo-msingi utatumika kwa shughuli zote.",
    addNewLlm: "Ongeza LLM Mpya",
    noLlmsConfigured: "Hakuna LLM zilizosanidiwa",
    addNewLlmToGetStarted: "Ongeza LLM mpya kuanza",
    embeddingModelManagement: "Usimamizi wa Mifano ya Kuingiza",
    embeddingDescription: "Sanidi na simamia mifano ya kuingiza inayotumika kwa ufaharisaji na upatikanaji wa msingi wa maarifa. Mfano chaguo-msingi utatumika wakati wa kuunda misingi mipya ya maarifa, lakini kila msingi wa maarifa utaendelea kutumia mfano wake wa asili wa kuingiza hata kama chaguo-msingi litabadilika baadaye.",
    addEmbeddingModel: "Ongeza Mfano wa Kuingiza",
    noEmbeddingModelsConfigured: "Hakuna mifano ya kuingiza iliyosanidiwa",
    addNewEmbeddingModelToGetStarted: "Ongeza mfano mpya wa kuingiza kuanza",
    tableHeaders: {
      name: "Jina",
      modelId: "Kitambulisho cha Mfano",
      provider: "Mtoa Huduma",
      description: "Maelezo",
      status: "Hali",
      actions: "Vitendo"
    },
    status: {
      default: "Chaguo-msingi",
      available: "Inapatikana"
    },
    actions: {
      setAsDefault: "Weka kama Chaguo-msingi",
      delete: "Futa",
      validate: "Thibitisha",
      validating: "Inakagua"
    },
    dialog: {
      addNewLlm: "Ongeza LLM Mpya",
      addEmbeddingModel: "Ongeza Mfano wa Kuingiza",
      displayName: "Jina la Kuonyesha",
      provider: "Mtoa Huduma",
      modelId: "Kitambulisho cha Mfano",
      description: "Maelezo",
      cancel: "Ghairi",
      addModel: "Ongeza Mfano"
    },
    placeholders: {
      customModel: "k.m., Mfano Wangu Maalum",
      embeddingModelId: "k.m., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Eleza mfano, sifa zake, na lini wa kutumia"
    },
    validation: {
      pleaseEnterModelId: "Tafadhali ingiza kitambulisho cha mfano"
    }
  }

  // Add Model Selection translations to Portuguese Brazilian
  resources["pt-BR"].common.modelSelection = {
    llmManagement: "Gerenciamento de LLM",
    llmDescription: "Configure e gerencie os LLMs usados para gerar respostas de texto. O modelo padrão será usado para todas as operações.",
    addNewLlm: "Adicionar Novo LLM",
    noLlmsConfigured: "Nenhum LLM configurado",
    addNewLlmToGetStarted: "Adicione um novo LLM para começar",
    embeddingModelManagement: "Gerenciamento de Modelos de Embedding",
    embeddingDescription: "Configure e gerencie os modelos de embedding usados para indexação e recuperação de bases de conhecimento. O modelo padrão será usado ao criar novas bases de conhecimento, mas cada base de conhecimento continuará usando seu modelo de embedding original mesmo se o padrão mudar posteriormente.",
    addEmbeddingModel: "Adicionar Modelo de Embedding",
    noEmbeddingModelsConfigured: "Nenhum modelo de embedding configurado",
    addNewEmbeddingModelToGetStarted: "Adicione um novo modelo de embedding para começar",
    tableHeaders: {
      name: "Nome",
      modelId: "ID do Modelo",
      provider: "Provedor",
      description: "Descrição",
      status: "Status",
      actions: "Ações"
    },
    status: {
      default: "Padrão",
      available: "Disponível"
    },
    actions: {
      setAsDefault: "Definir como Padrão",
      delete: "Excluir",
      validate: "Validar",
      validating: "Validando"
    },
    dialog: {
      addNewLlm: "Adicionar Novo LLM",
      addEmbeddingModel: "Adicionar Modelo de Embedding",
      displayName: "Nome de Exibição",
      provider: "Provedor",
      modelId: "ID do Modelo",
      description: "Descrição",
      cancel: "Cancelar",
      addModel: "Adicionar Modelo"
    },
    placeholders: {
      customModel: "ex., Meu Modelo Personalizado",
      embeddingModelId: "ex., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Descreva o modelo, suas características e quando usá-lo"
    },
    validation: {
      pleaseEnterModelId: "Por favor, insira um ID de modelo"
    }
  }

  // Add Model Selection translations to Spanish Latin America
  resources["es-LATAM"].common.modelSelection = {
    llmManagement: "Gestión de LLM",
    llmDescription: "Configure y gestione los LLM utilizados para generar respuestas de texto. El modelo predeterminado se usará para todas las operaciones.",
    addNewLlm: "Agregar Nuevo LLM",
    noLlmsConfigured: "No hay LLM configurados",
    addNewLlmToGetStarted: "Agregue un nuevo LLM para comenzar",
    embeddingModelManagement: "Gestión de Modelos de Embedding",
    embeddingDescription: "Configure y gestione los modelos de embedding utilizados para la indexación y recuperación de bases de conocimiento. El modelo predeterminado se usará al crear nuevas bases de conocimiento, pero cada base de conocimiento continuará usando su modelo de embedding original incluso si el predeterminado cambia posteriormente.",
    addEmbeddingModel: "Agregar Modelo de Embedding",
    noEmbeddingModelsConfigured: "No hay modelos de embedding configurados",
    addNewEmbeddingModelToGetStarted: "Agregue un nuevo modelo de embedding para comenzar",
    tableHeaders: {
      name: "Nombre",
      modelId: "ID del Modelo",
      provider: "Proveedor",
      description: "Descripción",
      status: "Estado",
      actions: "Acciones"
    },
    status: {
      default: "Predeterminado",
      available: "Disponible"
    },
    actions: {
      setAsDefault: "Establecer como Predeterminado",
      delete: "Eliminar",
      validate: "Validar",
      validating: "Validando"
    },
    dialog: {
      addNewLlm: "Agregar Nuevo LLM",
      addEmbeddingModel: "Agregar Modelo de Embedding",
      displayName: "Nombre para Mostrar",
      provider: "Proveedor",
      modelId: "ID del Modelo",
      description: "Descripción",
      cancel: "Cancelar",
      addModel: "Agregar Modelo"
    },
    placeholders: {
      customModel: "ej., Mi Modelo Personalizado",
      embeddingModelId: "ej., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Describa el modelo, sus características y cuándo usarlo"
    },
    validation: {
      pleaseEnterModelId: "Por favor ingrese un ID de modelo"
    }
  }

  // Add Knowledge Bases translations for Middle Eastern and Other languages
  
  // Hebrew
  if (!resources.he.common.knowledgeBases) {
    resources.he.common.knowledgeBases = {
      title: "בסיסי ידע",
      description: "נהל וארגן את המסמכים שלך בבסיסי ידע לאינטראקציות יעילות הנתמכות על ידי AI.",
      createNew: "צור בסיס ידע חדש",
      noKnowledgeBases: "עדיין לא נוצרו בסיסי ידע",
      getStarted: "צור את בסיס הידע הראשון שלך כדי להתחיל",
      tableHeaders: {
        name: "שם",
        description: "תיאור",
        documents: "מסמכים",
        createdAt: "נוצר",
        actions: "פעולות"
      },
      actions: {
        view: "הצג",
        edit: "עריכה",
        delete: "מחיקה",
        configure: "הגדרה"
      },
      dialog: {
        createNew: "צור בסיס ידע חדש",
        editKnowledgeBase: "ערוך בסיס ידע",
        name: "שם",
        description: "תיאור",
        cancel: "ביטול",
        create: "צור",
        save: "שמור"
      },
      placeholders: {
        knowledgeBaseName: "למשל, מדיניות החברה",
        knowledgeBaseDescription: "תאר מה מכיל בסיס הידע הזה ומה המטרה שלו"
      },
      validation: {
        pleaseEnterName: "אנא הזן שם לבסיס הידע"
      }
    }
  }

  // Persian/Farsi
  if (!resources.fa.common.knowledgeBases) {
    resources.fa.common.knowledgeBases = {
      title: "پایگاه‌های دانش",
      description: "اسناد خود را در پایگاه‌های دانش مدیریت و سازماندهی کنید تا تعاملات کارآمد با پشتیبانی هوش مصنوعی داشته باشید.",
      createNew: "ایجاد پایگاه دانش جدید",
      noKnowledgeBases: "هنوز هیچ پایگاه دانشی ایجاد نشده است",
      getStarted: "اولین پایگاه دانش خود را برای شروع ایجاد کنید",
      tableHeaders: {
        name: "نام",
        description: "توضیحات",
        documents: "اسناد",
        createdAt: "ایجاد شده",
        actions: "عملیات"
      },
      actions: {
        view: "مشاهده",
        edit: "ویرایش",
        delete: "حذف",
        configure: "پیکربندی"
      },
      dialog: {
        createNew: "ایجاد پایگاه دانش جدید",
        editKnowledgeBase: "ویرایش پایگاه دانش",
        name: "نام",
        description: "توضیحات",
        cancel: "لغو",
        create: "ایجاد",
        save: "ذخیره"
      },
      placeholders: {
        knowledgeBaseName: "مثال: سیاست‌های شرکت",
        knowledgeBaseDescription: "توضیح دهید که این پایگاه دانش چه چیزی را شامل می‌شود و هدف آن چیست"
      },
      validation: {
        pleaseEnterName: "لطفاً نامی برای پایگاه دانش وارد کنید"
      }
    }
  }

  // Turkish
  if (!resources.tr.common.knowledgeBases) {
    resources.tr.common.knowledgeBases = {
      title: "Bilgi Tabanları",
      description: "Belgelerinizi bilgi tabanlarında yönetin ve düzenleyin, AI destekli etkili etkileşimler için.",
      createNew: "Yeni bilgi tabanı oluştur",
      noKnowledgeBases: "Henüz hiç bilgi tabanı oluşturulmamış",
      getStarted: "Başlamak için ilk bilgi tabanınızı oluşturun",
      tableHeaders: {
        name: "Ad",
        description: "Açıklama",
        documents: "Belgeler",
        createdAt: "Oluşturuldu",
        actions: "İşlemler"
      },
      actions: {
        view: "Görüntüle",
        edit: "Düzenle",
        delete: "Sil",
        configure: "Yapılandır"
      },
      dialog: {
        createNew: "Yeni bilgi tabanı oluştur",
        editKnowledgeBase: "Bilgi tabanını düzenle",
        name: "Ad",
        description: "Açıklama",
        cancel: "İptal",
        create: "Oluştur",
        save: "Kaydet"
      },
      placeholders: {
        knowledgeBaseName: "örn., Şirket Politikaları",
        knowledgeBaseDescription: "Bu bilgi tabanının ne içerdiğini ve amacını açıklayın"
      },
      validation: {
        pleaseEnterName: "Lütfen bilgi tabanı için bir ad girin"
      }
    }
  }

  // Swahili
  if (!resources.sw.common.knowledgeBases) {
    resources.sw.common.knowledgeBases = {
      title: "Misingi ya Ujuzi",
      description: "Simamia na panga hati zako katika misingi ya ujuzi kwa ajili ya mwingiliano wa ufanisi unaotumia AI.",
      createNew: "Unda msingi mpya wa ujuzi",
      noKnowledgeBases: "Bado hakuna misingi ya ujuzi iliyoundwa",
      getStarted: "Unda msingi wako wa kwanza wa ujuzi ili uanze",
      tableHeaders: {
        name: "Jina",
        description: "Maelezo",
        documents: "Hati",
        createdAt: "Iliundwa",
        actions: "Vitendo"
      },
      actions: {
        view: "Ona",
        edit: "Hariri",
        delete: "Futa",
        configure: "Sanidi"
      },
      dialog: {
        createNew: "Unda msingi mpya wa ujuzi",
        editKnowledgeBase: "Hariri msingi wa ujuzi",
        name: "Jina",
        description: "Maelezo",
        cancel: "Ghairi",
        create: "Unda",
        save: "Hifadhi"
      },
      placeholders: {
        knowledgeBaseName: "mfano, Sera za Kampuni",
        knowledgeBaseDescription: "Eleza kile msingi huu wa ujuzi unachohifadhi na lengo lake"
      },
      validation: {
        pleaseEnterName: "Tafadhali ingiza jina la msingi wa ujuzi"
      }
    }
  }

  // Portuguese Brazilian
  if (!resources["pt-BR"].common.knowledgeBases) {
    resources["pt-BR"].common.knowledgeBases = {
      title: "Bases de Conhecimento",
      description: "Gerencie e organize seus documentos em bases de conhecimento para interações eficientes com suporte de IA.",
      createNew: "Criar nova base de conhecimento",
      noKnowledgeBases: "Nenhuma base de conhecimento foi criada ainda",
      getStarted: "Crie sua primeira base de conhecimento para começar",
      tableHeaders: {
        name: "Nome",
        description: "Descrição",
        documents: "Documentos",
        createdAt: "Criado",
        actions: "Ações"
      },
      actions: {
        view: "Visualizar",
        edit: "Editar",
        delete: "Excluir",
        configure: "Configurar"
      },
      dialog: {
        createNew: "Criar nova base de conhecimento",
        editKnowledgeBase: "Editar base de conhecimento",
        name: "Nome",
        description: "Descrição",
        cancel: "Cancelar",
        create: "Criar",
        save: "Salvar"
      },
      placeholders: {
        knowledgeBaseName: "ex., Políticas da Empresa",
        knowledgeBaseDescription: "Descreva o que esta base de conhecimento contém e seu propósito"
      },
      validation: {
        pleaseEnterName: "Por favor, insira um nome para a base de conhecimento"
      }
    }
  }

  // Spanish Latin America
  if (!resources["es-LATAM"].common.knowledgeBases) {
    resources["es-LATAM"].common.knowledgeBases = {
      title: "Bases de Conocimiento",
      description: "Administra y organiza tus documentos en bases de conocimiento para interacciones eficientes con soporte de IA.",
      createNew: "Crear nueva base de conocimiento",
      noKnowledgeBases: "Aún no se han creado bases de conocimiento",
      getStarted: "Crea tu primera base de conocimiento para comenzar",
      tableHeaders: {
        name: "Nombre",
        description: "Descripción",
        documents: "Documentos",
        createdAt: "Creado",
        actions: "Acciones"
      },
      actions: {
        view: "Ver",
        edit: "Editar",
        delete: "Eliminar",
        configure: "Configurar"
      },
      dialog: {
        createNew: "Crear nueva base de conocimiento",
        editKnowledgeBase: "Editar base de conocimiento",
        name: "Nombre",
        description: "Descripción",
        cancel: "Cancelar",
        create: "Crear",
        save: "Guardar"
      },
      placeholders: {
        knowledgeBaseName: "ej., Políticas de la Empresa",
        knowledgeBaseDescription: "Describe qué contiene esta base de conocimiento y su propósito"
      },
      validation: {
        pleaseEnterName: "Por favor ingresa un nombre para la base de conocimiento"
      }
    }
  }
}
