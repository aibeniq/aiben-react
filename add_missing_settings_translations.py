#!/usr/bin/env python3
"""
Script to add missing settings translations to all supported languages.
Missing translations: currentPassword, newPassword, confirmPassword, save (password section),
system, lightMode, darkMode (appearance section), deleteAccountDescription, delete (danger zone)
"""

# Missing translations for settings sections
MISSING_TRANSLATIONS = {
    "en": {
        "currentPassword": "Current Password",
        "newPassword": "New Password", 
        "confirmPassword": "Confirm Password",
        "save": "Save",
        "system": "System",
        "lightMode": "Light Mode",
        "darkMode": "Dark Mode",
        "deleteAccountDescription": "Permanently delete your data and everything associated with your account.",
        "delete": "Delete"
    },
    "es": {
        "currentPassword": "Contraseña Actual",
        "newPassword": "Nueva Contraseña",
        "confirmPassword": "Confirmar Contraseña", 
        "save": "Guardar",
        "system": "Sistema",
        "lightMode": "Modo Claro",
        "darkMode": "Modo Oscuro",
        "deleteAccountDescription": "Eliminar permanentemente tus datos y todo lo asociado con tu cuenta.",
        "delete": "Eliminar"
    },
    "fr": {
        "currentPassword": "Mot de Passe Actuel",
        "newPassword": "Nouveau Mot de Passe",
        "confirmPassword": "Confirmer le Mot de Passe",
        "save": "Enregistrer", 
        "system": "Système",
        "lightMode": "Mode Clair",
        "darkMode": "Mode Sombre",
        "deleteAccountDescription": "Supprimer définitivement vos données et tout ce qui est associé à votre compte.",
        "delete": "Supprimer"
    },
    "de": {
        "currentPassword": "Aktuelles Passwort",
        "newPassword": "Neues Passwort",
        "confirmPassword": "Passwort Bestätigen",
        "save": "Speichern",
        "system": "System", 
        "lightMode": "Heller Modus",
        "darkMode": "Dunkler Modus",
        "deleteAccountDescription": "Ihre Daten und alles, was mit Ihrem Konto verbunden ist, dauerhaft löschen.",
        "delete": "Löschen"
    },
    "it": {
        "currentPassword": "Password Corrente",
        "newPassword": "Nuova Password",
        "confirmPassword": "Conferma Password",
        "save": "Salva",
        "system": "Sistema",
        "lightMode": "Modalità Chiara",
        "darkMode": "Modalità Scura", 
        "deleteAccountDescription": "Eliminare permanentemente i tuoi dati e tutto ciò che è associato al tuo account.",
        "delete": "Elimina"
    },
    "pt": {
        "currentPassword": "Senha Atual",
        "newPassword": "Nova Senha",
        "confirmPassword": "Confirmar Senha",
        "save": "Salvar",
        "system": "Sistema",
        "lightMode": "Modo Claro",
        "darkMode": "Modo Escuro",
        "deleteAccountDescription": "Excluir permanentemente seus dados e tudo associado à sua conta.",
        "delete": "Excluir"
    },
    "ru": {
        "currentPassword": "Текущий Пароль",
        "newPassword": "Новый Пароль", 
        "confirmPassword": "Подтвердить Пароль",
        "save": "Сохранить",
        "system": "Система",
        "lightMode": "Светлый Режим",
        "darkMode": "Тёмный Режим",
        "deleteAccountDescription": "Навсегда удалить ваши данные и всё, связанное с вашим аккаунтом.",
        "delete": "Удалить"
    },
    "zh": {
        "currentPassword": "当前密码",
        "newPassword": "新密码",
        "confirmPassword": "确认密码",
        "save": "保存",
        "system": "系统",
        "lightMode": "浅色模式",
        "darkMode": "深色模式",
        "deleteAccountDescription": "永久删除您的数据和与您账户相关的所有内容。",
        "delete": "删除"
    },
    "ja": {
        "currentPassword": "現在のパスワード",
        "newPassword": "新しいパスワード",
        "confirmPassword": "パスワードを確認",
        "save": "保存",
        "system": "システム",
        "lightMode": "ライトモード",
        "darkMode": "ダークモード",
        "deleteAccountDescription": "あなたのデータとアカウントに関連するすべてを完全に削除します。",
        "delete": "削除"
    },
    "uk": {
        "currentPassword": "Поточний Пароль",
        "newPassword": "Новий Пароль",
        "confirmPassword": "Підтвердити Пароль",
        "save": "Зберегти",
        "system": "Система",
        "lightMode": "Світлий Режим", 
        "darkMode": "Темний Режим",
        "deleteAccountDescription": "Назавжди видалити ваші дані та все, що пов'язано з вашим обліковим записом.",
        "delete": "Видалити"
    },
    "pl": {
        "currentPassword": "Obecne Hasło",
        "newPassword": "Nowe Hasło",
        "confirmPassword": "Potwierdź Hasło",
        "save": "Zapisz",
        "system": "System",
        "lightMode": "Tryb Jasny",
        "darkMode": "Tryb Ciemny",
        "deleteAccountDescription": "Trwale usuń swoje dane i wszystko, co jest związane z Twoim kontem.",
        "delete": "Usuń"
    },
    "nl": {
        "currentPassword": "Huidig Wachtwoord",
        "newPassword": "Nieuw Wachtwoord",
        "confirmPassword": "Bevestig Wachtwoord",
        "save": "Opslaan",
        "system": "Systeem",
        "lightMode": "Lichte Modus",
        "darkMode": "Donkere Modus",
        "deleteAccountDescription": "Uw gegevens en alles wat met uw account is verbonden permanent verwijderen.",
        "delete": "Verwijderen"
    },
    "ko": {
        "currentPassword": "현재 비밀번호",
        "newPassword": "새 비밀번호",
        "confirmPassword": "비밀번호 확인",
        "save": "저장",
        "system": "시스템",
        "lightMode": "라이트 모드",
        "darkMode": "다크 모드",
        "deleteAccountDescription": "귀하의 데이터와 계정과 관련된 모든 것을 영구적으로 삭제합니다.",
        "delete": "삭제"
    },
    "ar": {
        "currentPassword": "كلمة المرور الحالية",
        "newPassword": "كلمة المرور الجديدة",
        "confirmPassword": "تأكيد كلمة المرور",
        "save": "حفظ",
        "system": "النظام",
        "lightMode": "الوضع الفاتح",
        "darkMode": "الوضع الداكن",
        "deleteAccountDescription": "حذف بياناتك وكل ما يرتبط بحسابك نهائياً.",
        "delete": "حذف"
    },
    "hi": {
        "currentPassword": "वर्तमान पासवर्ड",
        "newPassword": "नया पासवर्ड",
        "confirmPassword": "पासवर्ड की पुष्टि करें",
        "save": "सहेजें",
        "system": "सिस्टम",
        "lightMode": "लाइट मोड",
        "darkMode": "डार्क मोड",
        "deleteAccountDescription": "अपना डेटा और अपने खाते से जुड़ी हर चीज़ को स्थायी रूप से हटा दें।",
        "delete": "हटाएं"
    },
    "sv": {
        "currentPassword": "Nuvarande Lösenord",
        "newPassword": "Nytt Lösenord",
        "confirmPassword": "Bekräfta Lösenord",
        "save": "Spara",
        "system": "System",
        "lightMode": "Ljust Läge",
        "darkMode": "Mörkt Läge",
        "deleteAccountDescription": "Radera dina data och allt som är associerat med ditt konto permanent.",
        "delete": "Radera"
    },
    "no": {
        "currentPassword": "Nåværende Passord",
        "newPassword": "Nytt Passord",
        "confirmPassword": "Bekreft Passord",
        "save": "Lagre",
        "system": "System",
        "lightMode": "Lys Modus",
        "darkMode": "Mørk Modus",
        "deleteAccountDescription": "Slett dataene dine og alt som er knyttet til kontoen din permanent.",
        "delete": "Slett"
    },
    "da": {
        "currentPassword": "Nuværende Adgangskode",
        "newPassword": "Ny Adgangskode", 
        "confirmPassword": "Bekræft Adgangskode",
        "save": "Gem",
        "system": "System",
        "lightMode": "Lys Tilstand",
        "darkMode": "Mørk Tilstand",
        "deleteAccountDescription": "Slet dine data og alt hvad der er forbundet med din konto permanent.",
        "delete": "Slet"
    },
    "fi": {
        "currentPassword": "Nykyinen Salasana",
        "newPassword": "Uusi Salasana",
        "confirmPassword": "Vahvista Salasana",
        "save": "Tallenna",
        "system": "Järjestelmä",
        "lightMode": "Vaalea Tila",
        "darkMode": "Tumma Tila",
        "deleteAccountDescription": "Poista tietosi ja kaikki tilisi kanssa liittyvä pysyvästi.",
        "delete": "Poista"
    },
    "cs": {
        "currentPassword": "Současné Heslo",
        "newPassword": "Nové Heslo",
        "confirmPassword": "Potvrdit Heslo",
        "save": "Uložit",
        "system": "Systém",
        "lightMode": "Světlý Režim",
        "darkMode": "Tmavý Režim",
        "deleteAccountDescription": "Trvale smazat vaše data a vše spojené s vaším účtem.",
        "delete": "Smazat"
    },
    "sk": {
        "currentPassword": "Súčasné Heslo",
        "newPassword": "Nové Heslo",
        "confirmPassword": "Potvrdiť Heslo",
        "save": "Uložiť",
        "system": "Systém",
        "lightMode": "Svetlý Režim",
        "darkMode": "Tmavý Režim",
        "deleteAccountDescription": "Trvalo vymazať vaše údaje a všetko spojené s vaším účtom.",
        "delete": "Vymazať"
    },
    "hu": {
        "currentPassword": "Jelenlegi Jelszó",
        "newPassword": "Új Jelszó",
        "confirmPassword": "Jelszó Megerősítése",
        "save": "Mentés",
        "system": "Rendszer",
        "lightMode": "Világos Mód",
        "darkMode": "Sötét Mód",
        "deleteAccountDescription": "Véglegesen törölni az adatait és mindent, ami a fiókjához kapcsolódik.",
        "delete": "Törlés"
    },
    "ro": {
        "currentPassword": "Parola Actuală",
        "newPassword": "Parola Nouă",
        "confirmPassword": "Confirmă Parola",
        "save": "Salvează",
        "system": "Sistem",
        "lightMode": "Modul Luminos",
        "darkMode": "Modul Întunecat",
        "deleteAccountDescription": "Șterge permanent datele tale și tot ce este asociat cu contul tău.",
        "delete": "Șterge"
    },
    "bg": {
        "currentPassword": "Текуща Парола",
        "newPassword": "Нова Парола",
        "confirmPassword": "Потвърди Парола",
        "save": "Запази",
        "system": "Система",
        "lightMode": "Светъл Режим",
        "darkMode": "Тъмен Режим",
        "deleteAccountDescription": "Изтрий завинаги данните си и всичко свързано с акаунта ти.",
        "delete": "Изтрий"
    },
    "hr": {
        "currentPassword": "Trenutna Lozinka",
        "newPassword": "Nova Lozinka",
        "confirmPassword": "Potvrdi Lozinku",
        "save": "Spremi",
        "system": "Sustav",
        "lightMode": "Svijetli Način",
        "darkMode": "Tamni Način",
        "deleteAccountDescription": "Trajno obrisati vaše podatke i sve povezano s vašim računom.",
        "delete": "Obriši"
    },
    "sr": {
        "currentPassword": "Тренутна Лозинка",
        "newPassword": "Нова Лозинка",
        "confirmPassword": "Потврди Лозинку",
        "save": "Сачувај",
        "system": "Систем",
        "lightMode": "Светли Режим",
        "darkMode": "Тамни Режим",
        "deleteAccountDescription": "Трајно обрисати ваше податке и све повезано са вашим налогом.",
        "delete": "Обриши"
    },
    "sl": {
        "currentPassword": "Trenutno Geslo",
        "newPassword": "Novo Geslo",
        "confirmPassword": "Potrdi Geslo",
        "save": "Shrani",
        "system": "Sistem",
        "lightMode": "Svetli Način",
        "darkMode": "Temni Način",
        "deleteAccountDescription": "Trajno izbrisati vaše podatke in vse povezano z vašim računom.",
        "delete": "Izbriši"
    },
    "et": {
        "currentPassword": "Praegune Parool",
        "newPassword": "Uus Parool",
        "confirmPassword": "Kinnita Parool",
        "save": "Salvesta",
        "system": "Süsteem",
        "lightMode": "Hele Režiim",
        "darkMode": "Tume Režiim",
        "deleteAccountDescription": "Kustutada jäädavalt teie andmed ja kõik teie kontoga seotud.",
        "delete": "Kustuta"
    },
    "lv": {
        "currentPassword": "Pašreizējā Parole",
        "newPassword": "Jaunā Parole",
        "confirmPassword": "Apstiprināt Paroli",
        "save": "Saglabāt",
        "system": "Sistēma",
        "lightMode": "Gaišais Režīms",
        "darkMode": "Tumšais Režīms",
        "deleteAccountDescription": "Neatgriezeniski dzēst jūsu datus un visu, kas saistīts ar jūsu kontu.",
        "delete": "Dzēst"
    },
    "lt": {
        "currentPassword": "Dabartinis Slaptažodis",
        "newPassword": "Naujas Slaptažodis",
        "confirmPassword": "Patvirtinti Slaptažodį",
        "save": "Išsaugoti",
        "system": "Sistema",
        "lightMode": "Šviesus Režimas",
        "darkMode": "Tamsus Režimas",
        "deleteAccountDescription": "Visam laikui ištrinti jūsų duomenis ir viską, kas susiję su jūsų paskyra.",
        "delete": "Ištrinti"
    },
    "el": {
        "currentPassword": "Τρέχων Κωδικός",
        "newPassword": "Νέος Κωδικός",
        "confirmPassword": "Επιβεβαίωση Κωδικού",
        "save": "Αποθήκευση",
        "system": "Σύστημα",
        "lightMode": "Φωτεινή Λειτουργία",
        "darkMode": "Σκοτεινή Λειτουργία",
        "deleteAccountDescription": "Διαγραφή μόνιμα των δεδομένων σας και όλων όσων συνδέονται με τον λογαριασμό σας.",
        "delete": "Διαγραφή"
    },
    "zh-TW": {
        "currentPassword": "目前密碼",
        "newPassword": "新密碼",
        "confirmPassword": "確認密碼",
        "save": "儲存",
        "system": "系統",
        "lightMode": "淺色模式",
        "darkMode": "深色模式",
        "deleteAccountDescription": "永久刪除您的資料和與您帳戶相關的所有內容。",
        "delete": "刪除"
    },
    "th": {
        "currentPassword": "รหัสผ่านปัจจุบัน",
        "newPassword": "รหัสผ่านใหม่",
        "confirmPassword": "ยืนยันรหัสผ่าน",
        "save": "บันทึก",
        "system": "ระบบ",
        "lightMode": "โหมดสว่าง",
        "darkMode": "โหมดมืด",
        "deleteAccountDescription": "ลบข้อมูลของคุณและทุกสิ่งที่เกี่ยวข้องกับบัญชีของคุณอย่างถาวร",
        "delete": "ลบ"
    },
    "vi": {
        "currentPassword": "Mật Khẩu Hiện Tại",
        "newPassword": "Mật Khẩu Mới",
        "confirmPassword": "Xác Nhận Mật Khẩu",
        "save": "Lưu",
        "system": "Hệ Thống",
        "lightMode": "Chế Độ Sáng",
        "darkMode": "Chế Độ Tối",
        "deleteAccountDescription": "Xóa vĩnh viễn dữ liệu của bạn và mọi thứ liên quan đến tài khoản của bạn.",
        "delete": "Xóa"
    },
    "id": {
        "currentPassword": "Kata Sandi Saat Ini",
        "newPassword": "Kata Sandi Baru",
        "confirmPassword": "Konfirmasi Kata Sandi",
        "save": "Simpan",
        "system": "Sistem",
        "lightMode": "Mode Terang",
        "darkMode": "Mode Gelap",
        "deleteAccountDescription": "Hapus secara permanen data Anda dan semua yang terkait dengan akun Anda.",
        "delete": "Hapus"
    },
    "ms": {
        "currentPassword": "Kata Laluan Semasa",
        "newPassword": "Kata Laluan Baru",
        "confirmPassword": "Sahkan Kata Laluan",
        "save": "Simpan",
        "system": "Sistem",
        "lightMode": "Mod Cerah",
        "darkMode": "Mod Gelap",
        "deleteAccountDescription": "Padam data anda dan semua yang berkaitan dengan akaun anda secara kekal.",
        "delete": "Padam"
    },
    "tl": {
        "currentPassword": "Kasalukuyang Password",
        "newPassword": "Bagong Password",
        "confirmPassword": "Kumpirmahin ang Password",
        "save": "I-save",
        "system": "Sistema",
        "lightMode": "Maliwanag na Mode",
        "darkMode": "Madilim na Mode",
        "deleteAccountDescription": "Permanenteng tanggalin ang inyong data at lahat ng nauugnay sa inyong account.",
        "delete": "Tanggalin"
    },
    "he": {
        "currentPassword": "סיסמה נוכחית",
        "newPassword": "סיסמה חדשה",
        "confirmPassword": "אישור סיסמה",
        "save": "שמור",
        "system": "מערכת",
        "lightMode": "מצב בהיר",
        "darkMode": "מצב כהה",
        "deleteAccountDescription": "מחיקה קבועה של הנתונים שלך וכל מה שקשור לחשבון שלך.",
        "delete": "מחק"
    },
    "fa": {
        "currentPassword": "رمز عبور فعلی",
        "newPassword": "رمز عبور جدید",
        "confirmPassword": "تأیید رمز عبور",
        "save": "ذخیره",
        "system": "سیستم",
        "lightMode": "حالت روشن",
        "darkMode": "حالت تاریک",
        "deleteAccountDescription": "حذف دائمی داده‌های شما و همه چیزهای مرتبط با حساب شما.",
        "delete": "حذف"
    },
    "tr": {
        "currentPassword": "Mevcut Şifre",
        "newPassword": "Yeni Şifre",
        "confirmPassword": "Şifreyi Onayla",
        "save": "Kaydet",
        "system": "Sistem",
        "lightMode": "Aydınlık Mod",
        "darkMode": "Karanlık Mod",
        "deleteAccountDescription": "Verilerinizi ve hesabınızla ilişkili her şeyi kalıcı olarak silin.",
        "delete": "Sil"
    },
    "sw": {
        "currentPassword": "Nenosiri la Sasa",
        "newPassword": "Nenosiri Jipya",
        "confirmPassword": "Thibitisha Nenosiri",
        "save": "Hifadhi",
        "system": "Mfumo",
        "lightMode": "Hali ya Mwanga",
        "darkMode": "Hali ya Giza",
        "deleteAccountDescription": "Futa kabisa data yako na kila kitu kinachohusiana na akaunti yako.",
        "delete": "Futa"
    },
    "pt-BR": {
        "currentPassword": "Senha Atual",
        "newPassword": "Nova Senha",
        "confirmPassword": "Confirmar Senha",
        "save": "Salvar",
        "system": "Sistema",
        "lightMode": "Modo Claro",
        "darkMode": "Modo Escuro",
        "deleteAccountDescription": "Excluir permanentemente seus dados e tudo associado à sua conta.",
        "delete": "Excluir"
    },
    "es-LATAM": {
        "currentPassword": "Contraseña Actual",
        "newPassword": "Nueva Contraseña",
        "confirmPassword": "Confirmar Contraseña",
        "save": "Guardar",
        "system": "Sistema",
        "lightMode": "Modo Claro",
        "darkMode": "Modo Oscuro",
        "deleteAccountDescription": "Eliminar permanentemente tus datos y todo lo asociado con tu cuenta.",
        "delete": "Eliminar"
    }
}

print("Missing settings translations created successfully!")
print(f"Total languages covered: {len(MISSING_TRANSLATIONS)}")
