import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { addNordicTranslations } from './translations_nordic'
import { addCentralEuropeanTranslations } from './translations_central_european'
import { addBalticEasternEuropeanTranslations } from './translations_baltic_eastern_european'
import { addAsianTranslations } from './translations_asian'
import { addMiddleEasternOtherTranslations } from './translations_middle_eastern_other'

// Generate all supported language resources with full translations
const generateAllLanguageResources = () => {
  const resources: any = {}

  // English (base)
  resources.en = {
    common: {
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
        "back": "Back"
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
        "passwordPlaceholder": "Enter your password"
      },
      "chatbot": {
        "placeholder": "Type your message here...",
        "send": "Send",
        "newChat": "New Chat",
        "clearHistory": "Clear History",
        "typing": "AI is typing...",
        "error": "Sorry, something went wrong. Please try again.",
        "welcome": "Hello! How can I help you today?"
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
        "appearance": "Appearance"
      },
      "errors": {
        "somethingWentWrong": "Something went wrong",
        "tryAgain": "Please try again",
        "invalidEmail": "Invalid email address",
        "passwordTooShort": "Password is too short",
        "passwordsDoNotMatch": "Passwords do not match",
        "networkError": "Network error. Please check your connection.",
        "unauthorized": "You are not authorized to perform this action.",
        "notFound": "The requested resource was not found."
      },
      "common": {
        "loading": "Loading...",
        "noData": "No data available",
        "success": "Success!",
        "failed": "Failed",
        "welcome": "Welcome",
        "goodbye": "Goodbye",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "search": "Search",
        "filter": "Filter",
        "sort": "Sort",
        "view": "View",
        "copy": "Copy",
        "paste": "Paste",
        "cut": "Cut"
      }
    }
  }

  // Spanish
  resources.es = {
    common: {
      "navigation": {
        "dashboard": "Panel de Control",
        "review": "Revisar",
        "generate": "Generar",
        "compare": "Comparar",
        "match": "Coincidir",
        "modelSelection": "Selección de Modelo",
        "knowledgeBases": "Bases de Conocimiento",
        "archive": "Archivo",
        "settings": "Configuración",
        "admin": "Administrador",
        "menu": "Menú",
        "tools": "Herramientas",
        "configurations": "Configuraciones",
        "myProfile": "Mi Perfil",
        "logout": "Cerrar Sesión",
        "loggedInAs": "Conectado como: {{email}}"
      },
      "buttons": {
        "upload": "Subir",
        "download": "Descargar",
        "save": "Guardar",
        "cancel": "Cancelar",
        "delete": "Eliminar",
        "edit": "Editar",
        "submit": "Enviar",
        "close": "Cerrar",
        "next": "Siguiente",
        "previous": "Anterior",
        "confirm": "Confirmar",
        "back": "Atrás"
      },
      "forms": {
        "firstName": "Nombre",
        "lastName": "Apellido",
        "email": "Correo Electrónico",
        "password": "Contraseña",
        "confirmPassword": "Confirmar Contraseña",
        "currentPassword": "Contraseña Actual",
        "newPassword": "Nueva Contraseña",
        "required": "Requerido",
        "optional": "Opcional",
        "emailPlaceholder": "Ingresa tu dirección de correo",
        "passwordPlaceholder": "Ingresa tu contraseña"
      },
      "chatbot": {
        "placeholder": "Escribe tu mensaje aquí...",
        "send": "Enviar",
        "newChat": "Nuevo Chat",
        "clearHistory": "Limpiar Historial",
        "typing": "La IA está escribiendo...",
        "error": "Lo siento, algo salió mal. Inténtalo de nuevo.",
        "welcome": "¡Hola! ¿Cómo puedo ayudarte hoy?"
      },
      "settings": {
        "title": "Configuración",
        "account": "Cuenta",
        "language": "Idioma",
        "dangerZone": "Zona de Peligro",
        "preferredLanguage": "Idioma Preferido",
        "saveLanguagePreference": "Guardar Preferencia de Idioma",
        "deleteAccount": "Eliminar Cuenta",
        "deleteAccountWarning": "Esta acción no se puede deshacer.",
        "profile": "Perfil",
        "security": "Seguridad",
        "changePassword": "Cambiar Contraseña",
        "appearance": "Apariencia"
      },
      "errors": {
        "somethingWentWrong": "Algo salió mal",
        "tryAgain": "Por favor, inténtalo de nuevo",
        "invalidEmail": "Dirección de correo inválida",
        "passwordTooShort": "La contraseña es muy corta",
        "passwordsDoNotMatch": "Las contraseñas no coinciden",
        "networkError": "Error de red. Verifica tu conexión.",
        "unauthorized": "No tienes autorización para realizar esta acción.",
        "notFound": "El recurso solicitado no fue encontrado."
      },
      "common": {
        "loading": "Cargando...",
        "noData": "No hay datos disponibles",
        "success": "¡Éxito!",
        "failed": "Falló",
        "welcome": "Bienvenido",
        "goodbye": "Adiós",
        "yes": "Sí",
        "no": "No",
        "ok": "OK",
        "search": "Buscar",
        "filter": "Filtrar",
        "sort": "Ordenar",
        "view": "Ver",
        "copy": "Copiar",
        "paste": "Pegar",
        "cut": "Cortar"
      }
    }
  }

  // French
  resources.fr = {
    common: {
      "navigation": {
        "dashboard": "Tableau de Bord",
        "review": "Réviser",
        "generate": "Générer",
        "compare": "Comparer",
        "match": "Correspondre",
        "modelSelection": "Sélection de Modèle",
        "knowledgeBases": "Bases de Connaissances",
        "archive": "Archive",
        "settings": "Paramètres",
        "admin": "Administrateur",
        "menu": "Menu",
        "tools": "Outils",
        "configurations": "Configurations",
        "myProfile": "Mon Profil",
        "logout": "Se Déconnecter",
        "loggedInAs": "Connecté en tant que : {{email}}"
      },
      "buttons": {
        "upload": "Télécharger",
        "download": "Télécharger",
        "save": "Enregistrer",
        "cancel": "Annuler",
        "delete": "Supprimer",
        "edit": "Modifier",
        "submit": "Soumettre",
        "close": "Fermer",
        "next": "Suivant",
        "previous": "Précédent",
        "confirm": "Confirmer",
        "back": "Retour"
      },
      "forms": {
        "firstName": "Prénom",
        "lastName": "Nom de Famille",
        "email": "Email",
        "password": "Mot de Passe",
        "confirmPassword": "Confirmer le Mot de Passe",
        "currentPassword": "Mot de Passe Actuel",
        "newPassword": "Nouveau Mot de Passe",
        "required": "Requis",
        "optional": "Optionnel",
        "emailPlaceholder": "Entrez votre adresse email",
        "passwordPlaceholder": "Entrez votre mot de passe"
      },
      "chatbot": {
        "placeholder": "Tapez votre message ici...",
        "send": "Envoyer",
        "newChat": "Nouveau Chat",
        "clearHistory": "Effacer l'Historique",
        "typing": "L'IA tape...",
        "error": "Désolé, quelque chose s'est mal passé. Veuillez réessayer.",
        "welcome": "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
      },
      "settings": {
        "title": "Paramètres",
        "account": "Compte",
        "language": "Langue",
        "dangerZone": "Zone de Danger",
        "preferredLanguage": "Langue Préférée",
        "saveLanguagePreference": "Enregistrer la Préférence de Langue",
        "deleteAccount": "Supprimer le Compte",
        "deleteAccountWarning": "Cette action ne peut pas être annulée.",
        "profile": "Profil",
        "security": "Sécurité",
        "changePassword": "Changer le Mot de Passe",
        "appearance": "Apparence"
      },
      "errors": {
        "somethingWentWrong": "Quelque chose s'est mal passé",
        "tryAgain": "Veuillez réessayer",
        "invalidEmail": "Adresse email invalide",
        "passwordTooShort": "Le mot de passe est trop court",
        "passwordsDoNotMatch": "Les mots de passe ne correspondent pas",
        "networkError": "Erreur réseau. Vérifiez votre connexion.",
        "unauthorized": "Vous n'êtes pas autorisé à effectuer cette action.",
        "notFound": "La ressource demandée n'a pas été trouvée."
      },
      "common": {
        "loading": "Chargement...",
        "noData": "Aucune donnée disponible",
        "success": "Succès !",
        "failed": "Échec",
        "welcome": "Bienvenue",
        "goodbye": "Au revoir",
        "yes": "Oui",
        "no": "Non",
        "ok": "OK",
        "search": "Rechercher",
        "filter": "Filtrer",
        "sort": "Trier",
        "view": "Voir",
        "copy": "Copier",
        "paste": "Coller",
        "cut": "Couper"
      }
    }
  }

  // German
  resources.de = {
    common: {
      "navigation": {
        "dashboard": "Dashboard",
        "review": "Überprüfen",
        "generate": "Generieren",
        "compare": "Vergleichen",
        "match": "Übereinstimmen",
        "modelSelection": "Modellauswahl",
        "knowledgeBases": "Wissensbasis",
        "archive": "Archiv",
        "settings": "Einstellungen",
        "admin": "Administrator",
        "menu": "Menü",
        "tools": "Werkzeuge",
        "configurations": "Konfigurationen",
        "myProfile": "Mein Profil",
        "logout": "Abmelden",
        "loggedInAs": "Angemeldet als: {{email}}"
      },
      "buttons": {
        "upload": "Hochladen",
        "download": "Herunterladen",
        "save": "Speichern",
        "cancel": "Abbrechen",
        "delete": "Löschen",
        "edit": "Bearbeiten",
        "submit": "Einreichen",
        "close": "Schließen",
        "next": "Weiter",
        "previous": "Zurück",
        "confirm": "Bestätigen",
        "back": "Zurück"
      },
      "forms": {
        "firstName": "Vorname",
        "lastName": "Nachname",
        "email": "E-Mail",
        "password": "Passwort",
        "confirmPassword": "Passwort bestätigen",
        "currentPassword": "Aktuelles Passwort",
        "newPassword": "Neues Passwort",
        "required": "Erforderlich",
        "optional": "Optional",
        "emailPlaceholder": "Geben Sie Ihre E-Mail-Adresse ein",
        "passwordPlaceholder": "Geben Sie Ihr Passwort ein"
      },
      "chatbot": {
        "placeholder": "Schreiben Sie hier Ihre Nachricht...",
        "send": "Senden",
        "newChat": "Neuer Chat",
        "clearHistory": "Verlauf löschen",
        "typing": "KI tippt...",
        "error": "Entschuldigung, etwas ist schief gelaufen. Bitte versuchen Sie es erneut.",
        "welcome": "Hallo! Wie kann ich Ihnen heute helfen?"
      },
      "settings": {
        "title": "Einstellungen",
        "account": "Konto",
        "language": "Sprache",
        "dangerZone": "Gefahrenbereich",
        "preferredLanguage": "Bevorzugte Sprache",
        "saveLanguagePreference": "Spracheinstellung speichern",
        "deleteAccount": "Konto löschen",
        "deleteAccountWarning": "Diese Aktion kann nicht rückgängig gemacht werden.",
        "profile": "Profil",
        "security": "Sicherheit",
        "changePassword": "Passwort ändern",
        "appearance": "Darstellung"
      },
      "errors": {
        "somethingWentWrong": "Etwas ist schief gelaufen",
        "tryAgain": "Bitte versuchen Sie es erneut",
        "invalidEmail": "Ungültige E-Mail-Adresse",
        "passwordTooShort": "Passwort ist zu kurz",
        "passwordsDoNotMatch": "Passwörter stimmen nicht überein",
        "networkError": "Netzwerkfehler. Bitte überprüfen Sie Ihre Verbindung.",
        "unauthorized": "Sie sind nicht berechtigt, diese Aktion durchzuführen.",
        "notFound": "Die angeforderte Ressource wurde nicht gefunden."
      },
      "common": {
        "loading": "Laden...",
        "noData": "Keine Daten verfügbar",
        "success": "Erfolg!",
        "failed": "Fehlgeschlagen",
        "welcome": "Willkommen",
        "goodbye": "Auf Wiedersehen",
        "yes": "Ja",
        "no": "Nein",
        "ok": "OK",
        "search": "Suchen",
        "filter": "Filter",
        "sort": "Sortieren",
        "view": "Ansicht",
        "copy": "Kopieren",
        "paste": "Einfügen",
        "cut": "Ausschneiden"
      }
    }
  }

  // Italian
  resources.it = {
    common: {
      "navigation": {
        "dashboard": "Dashboard",
        "review": "Rivedi",
        "generate": "Genera",
        "compare": "Confronta",
        "match": "Abbina",
        "modelSelection": "Selezione Modello",
        "knowledgeBases": "Basi di Conoscenza",
        "archive": "Archivio",
        "settings": "Impostazioni",
        "admin": "Amministratore",
        "menu": "Menu",
        "tools": "Strumenti",
        "configurations": "Configurazioni",
        "myProfile": "Il Mio Profilo",
        "logout": "Disconnetti",
        "loggedInAs": "Connesso come: {{email}}"
      },
      "buttons": {
        "upload": "Carica",
        "download": "Scarica",
        "save": "Salva",
        "cancel": "Annulla",
        "delete": "Elimina",
        "edit": "Modifica",
        "submit": "Invia",
        "close": "Chiudi",
        "next": "Avanti",
        "previous": "Precedente",
        "confirm": "Conferma",
        "back": "Indietro"
      },
      "forms": {
        "firstName": "Nome",
        "lastName": "Cognome",
        "email": "Email",
        "password": "Password",
        "confirmPassword": "Conferma Password",
        "currentPassword": "Password Attuale",
        "newPassword": "Nuova Password",
        "required": "Obbligatorio",
        "optional": "Opzionale",
        "emailPlaceholder": "Inserisci il tuo indirizzo email",
        "passwordPlaceholder": "Inserisci la tua password"
      },
      "chatbot": {
        "placeholder": "Scrivi il tuo messaggio qui...",
        "send": "Invia",
        "newChat": "Nuova Chat",
        "clearHistory": "Cancella Cronologia",
        "typing": "L'IA sta scrivendo...",
        "error": "Spiacente, qualcosa è andato storto. Riprova.",
        "welcome": "Ciao! Come posso aiutarti oggi?"
      },
      "settings": {
        "title": "Impostazioni",
        "account": "Account",
        "language": "Lingua",
        "dangerZone": "Zona di Pericolo",
        "preferredLanguage": "Lingua Preferita",
        "saveLanguagePreference": "Salva Preferenza Lingua",
        "deleteAccount": "Elimina Account",
        "deleteAccountWarning": "Questa azione non può essere annullata.",
        "profile": "Profilo",
        "security": "Sicurezza",
        "changePassword": "Cambia Password",
        "appearance": "Aspetto"
      },
      "errors": {
        "somethingWentWrong": "Qualcosa è andato storto",
        "tryAgain": "Riprova",
        "invalidEmail": "Indirizzo email non valido",
        "passwordTooShort": "Password troppo corta",
        "passwordsDoNotMatch": "Le password non corrispondono",
        "networkError": "Errore di rete. Controlla la tua connessione.",
        "unauthorized": "Non sei autorizzato a eseguire questa azione.",
        "notFound": "La risorsa richiesta non è stata trovata."
      },
      "common": {
        "loading": "Caricamento...",
        "noData": "Nessun dato disponibile",
        "success": "Successo!",
        "failed": "Fallito",
        "welcome": "Benvenuto",
        "goodbye": "Arrivederci",
        "yes": "Sì",
        "no": "No",
        "ok": "OK",
        "search": "Cerca",
        "filter": "Filtro",
        "sort": "Ordina",
        "view": "Visualizza",
        "copy": "Copia",
        "paste": "Incolla",
        "cut": "Taglia"
      }
    }
  }

  // Portuguese
  resources.pt = {
    common: {
      "navigation": {
        "dashboard": "Painel",
        "review": "Revisar",
        "generate": "Gerar",
        "compare": "Comparar",
        "match": "Corresponder",
        "modelSelection": "Seleção de Modelo",
        "knowledgeBases": "Bases de Conhecimento",
        "archive": "Arquivo",
        "settings": "Configurações",
        "admin": "Administrador",
        "menu": "Menu",
        "tools": "Ferramentas",
        "configurations": "Configurações",
        "myProfile": "Meu Perfil",
        "logout": "Sair",
        "loggedInAs": "Conectado como: {{email}}"
      },
      "buttons": {
        "upload": "Carregar",
        "download": "Baixar",
        "save": "Salvar",
        "cancel": "Cancelar",
        "delete": "Excluir",
        "edit": "Editar",
        "submit": "Enviar",
        "close": "Fechar",
        "next": "Próximo",
        "previous": "Anterior",
        "confirm": "Confirmar",
        "back": "Voltar"
      },
      "forms": {
        "firstName": "Nome",
        "lastName": "Sobrenome",
        "email": "Email",
        "password": "Senha",
        "confirmPassword": "Confirmar Senha",
        "currentPassword": "Senha Atual",
        "newPassword": "Nova Senha",
        "required": "Obrigatório",
        "optional": "Opcional",
        "emailPlaceholder": "Digite seu endereço de email",
        "passwordPlaceholder": "Digite sua senha"
      },
      "chatbot": {
        "placeholder": "Digite sua mensagem aqui...",
        "send": "Enviar",
        "newChat": "Novo Chat",
        "clearHistory": "Limpar Histórico",
        "typing": "IA está digitando...",
        "error": "Desculpe, algo deu errado. Tente novamente.",
        "welcome": "Olá! Como posso ajudá-lo hoje?"
      },
      "settings": {
        "title": "Configurações",
        "account": "Conta",
        "language": "Idioma",
        "dangerZone": "Zona de Perigo",
        "preferredLanguage": "Idioma Preferido",
        "saveLanguagePreference": "Salvar Preferência de Idioma",
        "deleteAccount": "Excluir Conta",
        "deleteAccountWarning": "Esta ação não pode ser desfeita.",
        "profile": "Perfil",
        "security": "Segurança",
        "changePassword": "Alterar Senha",
        "appearance": "Aparência"
      },
      "errors": {
        "somethingWentWrong": "Algo deu errado",
        "tryAgain": "Tente novamente",
        "invalidEmail": "Endereço de email inválido",
        "passwordTooShort": "Senha muito curta",
        "passwordsDoNotMatch": "Senhas não coincidem",
        "networkError": "Erro de rede. Verifique sua conexão.",
        "unauthorized": "Você não está autorizado a realizar esta ação.",
        "notFound": "O recurso solicitado não foi encontrado."
      },
      "common": {
        "loading": "Carregando...",
        "noData": "Nenhum dado disponível",
        "success": "Sucesso!",
        "failed": "Falhou",
        "welcome": "Bem-vindo",
        "goodbye": "Tchau",
        "yes": "Sim",
        "no": "Não",
        "ok": "OK",
        "search": "Pesquisar",
        "filter": "Filtrar",
        "sort": "Classificar",
        "view": "Visualizar",
        "copy": "Copiar",
        "paste": "Colar",
        "cut": "Cortar"
      }
    }
  }

  // Russian
  resources.ru = {
    common: {
      "navigation": {
        "dashboard": "Панель управления",
        "review": "Обзор",
        "generate": "Генерировать",
        "compare": "Сравнить",
        "match": "Сопоставить",
        "modelSelection": "Выбор модели",
        "knowledgeBases": "Базы знаний",
        "archive": "Архив",
        "settings": "Настройки",
        "admin": "Администратор",
        "menu": "Меню",
        "tools": "Инструменты",
        "configurations": "Конфигурации",
        "myProfile": "Мой профиль",
        "logout": "Выйти",
        "loggedInAs": "Вошел как: {{email}}"
      },
      "buttons": {
        "upload": "Загрузить",
        "download": "Скачать",
        "save": "Сохранить",
        "cancel": "Отмена",
        "delete": "Удалить",
        "edit": "Редактировать",
        "submit": "Отправить",
        "close": "Закрыть",
        "next": "Далее",
        "previous": "Назад",
        "confirm": "Подтвердить",
        "back": "Назад"
      },
      "forms": {
        "firstName": "Имя",
        "lastName": "Фамилия",
        "email": "Электронная почта",
        "password": "Пароль",
        "confirmPassword": "Подтвердить пароль",
        "currentPassword": "Текущий пароль",
        "newPassword": "Новый пароль",
        "required": "Обязательно",
        "optional": "Необязательно",
        "emailPlaceholder": "Введите ваш адрес электронной почты",
        "passwordPlaceholder": "Введите ваш пароль"
      },
      "chatbot": {
        "placeholder": "Введите ваше сообщение здесь...",
        "send": "Отправить",
        "newChat": "Новый чат",
        "clearHistory": "Очистить историю",
        "typing": "ИИ печатает...",
        "error": "Извините, что-то пошло не так. Попробуйте еще раз.",
        "welcome": "Привет! Как я могу помочь вам сегодня?"
      },
      "settings": {
        "title": "Настройки",
        "account": "Аккаунт",
        "language": "Язык",
        "dangerZone": "Опасная зона",
        "preferredLanguage": "Предпочитаемый язык",
        "saveLanguagePreference": "Сохранить языковые настройки",
        "deleteAccount": "Удалить аккаунт",
        "deleteAccountWarning": "Это действие нельзя отменить.",
        "profile": "Профиль",
        "security": "Безопасность",
        "changePassword": "Изменить пароль",
        "appearance": "Внешний вид"
      },
      "errors": {
        "somethingWentWrong": "Что-то пошло не так",
        "tryAgain": "Попробуйте еще раз",
        "invalidEmail": "Неверный адрес электронной почты",
        "passwordTooShort": "Пароль слишком короткий",
        "passwordsDoNotMatch": "Пароли не совпадают",
        "networkError": "Ошибка сети. Проверьте соединение.",
        "unauthorized": "У вас нет разрешения на выполнение этого действия.",
        "notFound": "Запрашиваемый ресурс не найден."
      },
      "common": {
        "loading": "Загрузка...",
        "noData": "Нет доступных данных",
        "success": "Успех!",
        "failed": "Неудача",
        "welcome": "Добро пожаловать",
        "goodbye": "До свидания",
        "yes": "Да",
        "no": "Нет",
        "ok": "ОК",
        "search": "Поиск",
        "filter": "Фильтр",
        "sort": "Сортировка",
        "view": "Просмотр",
        "copy": "Копировать",
        "paste": "Вставить",
        "cut": "Вырезать"
      }
    }
  }

  // Continue with more languages...
  // I'll add a few more key languages to demonstrate the pattern

  // Chinese (Simplified)
  resources.zh = {
    common: {
      "navigation": {
        "dashboard": "仪表板",
        "review": "审查",
        "generate": "生成",
        "compare": "比较",
        "match": "匹配",
        "modelSelection": "模型选择",
        "knowledgeBases": "知识库",
        "archive": "档案",
        "settings": "设置",
        "admin": "管理员",
        "menu": "菜单",
        "tools": "工具",
        "configurations": "配置",
        "myProfile": "我的资料",
        "logout": "登出",
        "loggedInAs": "登录为：{{email}}"
      },
      "buttons": {
        "upload": "上传",
        "download": "下载",
        "save": "保存",
        "cancel": "取消",
        "delete": "删除",
        "edit": "编辑",
        "submit": "提交",
        "close": "关闭",
        "next": "下一个",
        "previous": "上一个",
        "confirm": "确认",
        "back": "返回"
      },
      "forms": {
        "firstName": "名字",
        "lastName": "姓氏",
        "email": "电子邮件",
        "password": "密码",
        "confirmPassword": "确认密码",
        "currentPassword": "当前密码",
        "newPassword": "新密码",
        "required": "必需",
        "optional": "可选",
        "emailPlaceholder": "输入您的电子邮件地址",
        "passwordPlaceholder": "输入您的密码"
      },
      "chatbot": {
        "placeholder": "在此输入您的消息...",
        "send": "发送",
        "newChat": "新聊天",
        "clearHistory": "清除历史",
        "typing": "AI正在输入...",
        "error": "抱歉，出了点问题。请再试一次。",
        "welcome": "您好！我今天能为您做些什么？"
      },
      "settings": {
        "title": "设置",
        "account": "账户",
        "language": "语言",
        "dangerZone": "危险区域",
        "preferredLanguage": "首选语言",
        "saveLanguagePreference": "保存语言偏好",
        "deleteAccount": "删除账户",
        "deleteAccountWarning": "此操作无法撤销。",
        "profile": "资料",
        "security": "安全",
        "changePassword": "更改密码",
        "appearance": "外观"
      },
      "errors": {
        "somethingWentWrong": "出了点问题",
        "tryAgain": "请再试一次",
        "invalidEmail": "无效的电子邮件地址",
        "passwordTooShort": "密码太短",
        "passwordsDoNotMatch": "密码不匹配",
        "networkError": "网络错误。请检查您的连接。",
        "unauthorized": "您无权执行此操作。",
        "notFound": "未找到请求的资源。"
      },
      "common": {
        "loading": "加载中...",
        "noData": "无可用数据",
        "success": "成功！",
        "failed": "失败",
        "welcome": "欢迎",
        "goodbye": "再见",
        "yes": "是",
        "no": "否",
        "ok": "确定",
        "search": "搜索",
        "filter": "筛选",
        "sort": "排序",
        "view": "查看",
        "copy": "复制",
        "paste": "粘贴",
        "cut": "剪切"
      }
    }
  }

  // Japanese
  resources.ja = {
    common: {
      "navigation": {
        "dashboard": "ダッシュボード",
        "review": "レビュー",
        "generate": "生成",
        "compare": "比較",
        "match": "マッチ",
        "modelSelection": "モデル選択",
        "knowledgeBases": "ナレッジベース",
        "archive": "アーカイブ",
        "settings": "設定",
        "admin": "管理者",
        "menu": "メニュー",
        "tools": "ツール",
        "configurations": "設定",
        "myProfile": "マイプロフィール",
        "logout": "ログアウト",
        "loggedInAs": "ログイン中：{{email}}"
      },
      "buttons": {
        "upload": "アップロード",
        "download": "ダウンロード",
        "save": "保存",
        "cancel": "キャンセル",
        "delete": "削除",
        "edit": "編集",
        "submit": "送信",
        "close": "閉じる",
        "next": "次へ",
        "previous": "前へ",
        "confirm": "確認",
        "back": "戻る"
      },
      "forms": {
        "firstName": "名",
        "lastName": "姓",
        "email": "メール",
        "password": "パスワード",
        "confirmPassword": "パスワード確認",
        "currentPassword": "現在のパスワード",
        "newPassword": "新しいパスワード",
        "required": "必須",
        "optional": "任意",
        "emailPlaceholder": "メールアドレスを入力",
        "passwordPlaceholder": "パスワードを入力"
      },
      "chatbot": {
        "placeholder": "メッセージをここに入力...",
        "send": "送信",
        "newChat": "新しいチャット",
        "clearHistory": "履歴をクリア",
        "typing": "AIが入力中...",
        "error": "申し訳ございませんが、エラーが発生しました。もう一度お試しください。",
        "welcome": "こんにちは！今日はどのようにお手伝いできますか？"
      },
      "settings": {
        "title": "設定",
        "account": "アカウント",
        "language": "言語",
        "dangerZone": "危険ゾーン",
        "preferredLanguage": "優先言語",
        "saveLanguagePreference": "言語設定を保存",
        "deleteAccount": "アカウント削除",
        "deleteAccountWarning": "この操作は元に戻せません。",
        "profile": "プロフィール",
        "security": "セキュリティ",
        "changePassword": "パスワード変更",
        "appearance": "外観"
      },
      "errors": {
        "somethingWentWrong": "何かが間違っています",
        "tryAgain": "もう一度お試しください",
        "invalidEmail": "無効なメールアドレス",
        "passwordTooShort": "パスワードが短すぎます",
        "passwordsDoNotMatch": "パスワードが一致しません",
        "networkError": "ネットワークエラー。接続を確認してください。",
        "unauthorized": "この操作を実行する権限がありません。",
        "notFound": "要求されたリソースが見つかりません。"
      },
      "common": {
        "loading": "読み込み中...",
        "noData": "利用可能なデータがありません",
        "success": "成功！",
        "failed": "失敗",
        "welcome": "ようこそ",
        "goodbye": "さようなら",
        "yes": "はい",
        "no": "いいえ",
        "ok": "OK",
        "search": "検索",
        "filter": "フィルタ",
        "sort": "ソート",
        "view": "表示",
        "copy": "コピー",
        "paste": "貼り付け",
        "cut": "切り取り"
      }
    }
  }

  // Ukrainian
  resources.uk = {
    common: {
      "navigation": {
        "dashboard": "Панель керування", "review": "Огляд", "generate": "Генерувати", "compare": "Порівняти",
        "match": "Співставити", "modelSelection": "Вибір моделі", "knowledgeBases": "Бази знань",
        "archive": "Архів", "settings": "Налаштування", "admin": "Адміністратор", "menu": "Меню",
        "tools": "Інструменти", "configurations": "Конфігурації", "myProfile": "Мій профіль",
        "logout": "Вийти", "loggedInAs": "Увійшов як: {{email}}"
      },
      "buttons": {
        "upload": "Завантажити", "download": "Скачати", "save": "Зберегти", "cancel": "Скасувати",
        "delete": "Видалити", "edit": "Редагувати", "submit": "Надіслати", "close": "Закрити",
        "next": "Далі", "previous": "Назад", "confirm": "Підтвердити", "back": "Назад"
      },
      "forms": {
        "firstName": "Ім'я", "lastName": "Прізвище", "email": "Електронна пошта", "password": "Пароль",
        "confirmPassword": "Підтвердити пароль", "currentPassword": "Поточний пароль", "newPassword": "Новий пароль",
        "required": "Обов'язково", "optional": "Необов'язково", "emailPlaceholder": "Введіть адресу електронної пошти",
        "passwordPlaceholder": "Введіть пароль"
      },
      "chatbot": {
        "placeholder": "Введіть повідомлення тут...", "send": "Надіслати", "newChat": "Новий чат",
        "clearHistory": "Очистити історію", "typing": "ШІ друкує...", "error": "Вибачте, щось пішло не так. Спробуйте ще раз.",
        "welcome": "Привіт! Як я можу допомогти вам сьогодні?"
      },
      "settings": {
        "title": "Налаштування",
        "account": "Акаунт",
        "language": "Мова",
        "dangerZone": "Небезпечна зона",
        "preferredLanguage": "Бажана мова",
        "saveLanguagePreference": "Зберегти мовні налаштування",
        "deleteAccount": "Видалити акаунт",
        "deleteAccountWarning": "Цю дію неможливо скасувати.",
        "profile": "Профіль",
        "security": "Безпека",
        "changePassword": "Змінити пароль",
        "appearance": "Зовнішній вигляд"
      },
      "errors": {
        "somethingWentWrong": "Щось пішло не так", "tryAgain": "Спробуйте ще раз", "invalidEmail": "Неправильна адреса електронної пошти",
        "passwordTooShort": "Пароль занадто короткий", "passwordsDoNotMatch": "Паролі не збігаються",
        "networkError": "Помилка мережі. Перевірте з'єднання.", "unauthorized": "У вас немає дозволу на виконання цієї дії.",
        "notFound": "Запитуваний ресурс не знайдено."
      },
      "common": {
        "loading": "Завантаження...", "noData": "Немає доступних даних", "success": "Успіх!", "failed": "Невдача",
        "welcome": "Ласкаво просимо", "goodbye": "До побачення", "yes": "Так", "no": "Ні", "ok": "ОК",
        "search": "Пошук", "filter": "Фільтр", "sort": "Сортування", "view": "Перегляд",
        "copy": "Копіювати", "paste": "Вставити", "cut": "Вирізати"
      }
    }
  }

  // Polish
  resources.pl = {
    common: {
      "navigation": {
        "dashboard": "Panel kontrolny", "review": "Przegląd", "generate": "Generuj", "compare": "Porównaj",
        "match": "Dopasuj", "modelSelection": "Wybór modelu", "knowledgeBases": "Bazy wiedzy",
        "archive": "Archiwum", "settings": "Ustawienia", "admin": "Administrator", "menu": "Menu",
        "tools": "Narzędzia", "configurations": "Konfiguracje", "myProfile": "Mój profil",
        "logout": "Wyloguj", "loggedInAs": "Zalogowany jako: {{email}}"
      },
      "buttons": {
        "upload": "Prześlij", "download": "Pobierz", "save": "Zapisz", "cancel": "Anuluj",
        "delete": "Usuń", "edit": "Edytuj", "submit": "Wyślij", "close": "Zamknij",
        "next": "Dalej", "previous": "Wstecz", "confirm": "Potwierdź", "back": "Wstecz"
      },
      "forms": {
        "firstName": "Imię", "lastName": "Nazwisko", "email": "Email", "password": "Hasło",
        "confirmPassword": "Potwierdź hasło", "currentPassword": "Obecne hasło", "newPassword": "Nowe hasło",
        "required": "Wymagane", "optional": "Opcjonalne", "emailPlaceholder": "Wprowadź adres email",
        "passwordPlaceholder": "Wprowadź hasło"
      },
      "chatbot": {
        "placeholder": "Wpisz wiadomość tutaj...", "send": "Wyślij", "newChat": "Nowy czat",
        "clearHistory": "Wyczyść historię", "typing": "AI pisze...", "error": "Przepraszamy, coś poszło nie tak. Spróbuj ponownie.",
        "welcome": "Cześć! Jak mogę ci dzisiaj pomóc?"
      },
      "settings": {
        "title": "Ustawienia",
        "account": "Konto",
        "language": "Język",
        "dangerZone": "Strefa niebezpieczna",
        "preferredLanguage": "Preferowany język",
        "saveLanguagePreference": "Zapisz preferencje języka",
        "deleteAccount": "Usuń konto",
        "deleteAccountWarning": "Ta akcja nie może być cofnięta.",
        "profile": "Profil",
        "security": "Bezpieczeństwo",
        "changePassword": "Zmień hasło",
        "appearance": "Wygląd"
      },
      "errors": {
        "somethingWentWrong": "Coś poszło nie tak", "tryAgain": "Spróbuj ponownie", "invalidEmail": "Nieprawidłowy adres email",
        "passwordTooShort": "Hasło jest za krótkie", "passwordsDoNotMatch": "Hasła nie pasują",
        "networkError": "Błąd sieci. Sprawdź połączenie.", "unauthorized": "Nie masz uprawnień do wykonania tej akcji.",
        "notFound": "Żądany zasób nie został znaleziony."
      },
      "common": {
        "loading": "Ładowanie...", "noData": "Brak dostępnych danych", "success": "Sukces!", "failed": "Nieudane",
        "welcome": "Witamy", "goodbye": "Do widzenia", "yes": "Tak", "no": "Nie", "ok": "OK",
        "search": "Szukaj", "filter": "Filtr", "sort": "Sortuj", "view": "Widok",
        "copy": "Kopiuj", "paste": "Wklej", "cut": "Wytnij"
      }
    }
  }

  // Dutch
  resources.nl = {
    common: {
      "navigation": {
        "dashboard": "Dashboard", "review": "Beoordelen", "generate": "Genereren", "compare": "Vergelijken",
        "match": "Matchen", "modelSelection": "Modelselectie", "knowledgeBases": "Kennisbanken",
        "archive": "Archief", "settings": "Instellingen", "admin": "Beheerder", "menu": "Menu",
        "tools": "Hulpmiddelen", "configurations": "Configuraties", "myProfile": "Mijn Profiel",
        "logout": "Uitloggen", "loggedInAs": "Ingelogd als: {{email}}"
      },
      "buttons": {
        "upload": "Uploaden", "download": "Downloaden", "save": "Opslaan", "cancel": "Annuleren",
        "delete": "Verwijderen", "edit": "Bewerken", "submit": "Verzenden", "close": "Sluiten",
        "next": "Volgende", "previous": "Vorige", "confirm": "Bevestigen", "back": "Terug"
      },
      "forms": {
        "firstName": "Voornaam", "lastName": "Achternaam", "email": "E-mail", "password": "Wachtwoord",
        "confirmPassword": "Wachtwoord bevestigen", "currentPassword": "Huidige wachtwoord", "newPassword": "Nieuw wachtwoord",
        "required": "Verplicht", "optional": "Optioneel", "emailPlaceholder": "Voer uw e-mailadres in",
        "passwordPlaceholder": "Voer uw wachtwoord in"
      },
      "chatbot": {
        "placeholder": "Typ hier uw bericht...", "send": "Verzenden", "newChat": "Nieuwe Chat",
        "clearHistory": "Geschiedenis wissen", "typing": "AI is aan het typen...", "error": "Sorry, er is iets misgegaan. Probeer het opnieuw.",
        "welcome": "Hallo! Hoe kan ik u vandaag helpen?"
      },
      "settings": {
        "title": "Instellingen",
        "account": "Account",
        "language": "Taal",
        "dangerZone": "Gevarenzone",
        "preferredLanguage": "Voorkeurstaal",
        "saveLanguagePreference": "Taalvoorkeur opslaan",
        "deleteAccount": "Account verwijderen",
        "deleteAccountWarning": "Deze actie kan niet ongedaan worden gemaakt.",
        "profile": "Profiel",
        "security": "Beveiliging",
        "changePassword": "Wachtwoord wijzigen",
        "appearance": "Uiterlijk"
      },
      "errors": {
        "somethingWentWrong": "Er is iets misgegaan", "tryAgain": "Probeer het opnieuw", "invalidEmail": "Ongeldig e-mailadres",
        "passwordTooShort": "Wachtwoord is te kort", "passwordsDoNotMatch": "Wachtwoorden komen niet overeen",
        "networkError": "Netwerkfout. Controleer uw verbinding.", "unauthorized": "U bent niet geautoriseerd om deze actie uit te voeren.",
        "notFound": "De gevraagde bron is niet gevonden."
      },
      "common": {
        "loading": "Laden...", "noData": "Geen gegevens beschikbaar", "success": "Succes!", "failed": "Mislukt",
        "welcome": "Welkom", "goodbye": "Tot ziens", "yes": "Ja", "no": "Nee", "ok": "OK",
        "search": "Zoeken", "filter": "Filter", "sort": "Sorteren", "view": "Bekijken",
        "copy": "Kopiëren", "paste": "Plakken", "cut": "Knippen"
      }
    }
  }

  // Korean
  resources.ko = {
    common: {
      "navigation": {
        "dashboard": "대시보드", "review": "검토", "generate": "생성", "compare": "비교",
        "match": "매치", "modelSelection": "모델 선택", "knowledgeBases": "지식 베이스",
        "archive": "아카이브", "settings": "설정", "admin": "관리자", "menu": "메뉴",
        "tools": "도구", "configurations": "구성", "myProfile": "내 프로필",
        "logout": "로그아웃", "loggedInAs": "로그인됨: {{email}}"
      },
      "buttons": {
        "upload": "업로드", "download": "다운로드", "save": "저장", "cancel": "취소",
        "delete": "삭제", "edit": "편집", "submit": "제출", "close": "닫기",
        "next": "다음", "previous": "이전", "confirm": "확인", "back": "뒤로"
      },
      "forms": {
        "firstName": "이름", "lastName": "성", "email": "이메일", "password": "비밀번호",
        "confirmPassword": "비밀번호 확인", "currentPassword": "현재 비밀번호", "newPassword": "새 비밀번호",
        "required": "필수", "optional": "선택사항", "emailPlaceholder": "이메일 주소를 입력하세요",
        "passwordPlaceholder": "비밀번호를 입력하세요"
      },
      "chatbot": {
        "placeholder": "여기에 메시지를 입력하세요...", "send": "보내기", "newChat": "새 채팅",
        "clearHistory": "기록 지우기", "typing": "AI가 입력 중입니다...", "error": "죄송합니다. 문제가 발생했습니다. 다시 시도해 주세요.",
        "welcome": "안녕하세요! 오늘 어떻게 도와드릴까요?"
      },
      "settings": {
        "title": "설정",
        "account": "계정",
        "language": "언어",
        "dangerZone": "위험 구역",
        "preferredLanguage": "선호 언어",
        "saveLanguagePreference": "언어 설정 저장",
        "deleteAccount": "계정 삭제",
        "deleteAccountWarning": "이 작업은 되돌릴 수 없습니다.",
        "profile": "프로필",
        "security": "보안",
        "changePassword": "비밀번호 변경",
        "appearance": "외관"
      },
      "errors": {
        "somethingWentWrong": "문제가 발생했습니다", "tryAgain": "다시 시도해 주세요", "invalidEmail": "유효하지 않은 이메일 주소",
        "passwordTooShort": "비밀번호가 너무 짧습니다", "passwordsDoNotMatch": "비밀번호가 일치하지 않습니다",
        "networkError": "네트워크 오류입니다. 연결을 확인해 주세요.", "unauthorized": "이 작업을 수행할 권한이 없습니다.",
        "notFound": "요청한 리소스를 찾을 수 없습니다."
      },
      "common": {
        "loading": "로딩 중...", "noData": "사용 가능한 데이터가 없습니다", "success": "성공!", "failed": "실패",
        "welcome": "환영합니다", "goodbye": "안녕히 가세요", "yes": "예", "no": "아니오", "ok": "확인",
        "search": "검색", "filter": "필터", "sort": "정렬", "view": "보기",
        "copy": "복사", "paste": "붙여넣기", "cut": "잘라내기"
      }
    }
  }

  // Arabic
  resources.ar = {
    common: {
      "navigation": {
        "dashboard": "لوحة التحكم", "review": "مراجعة", "generate": "إنشاء", "compare": "مقارنة",
        "match": "مطابقة", "modelSelection": "اختيار النموذج", "knowledgeBases": "قواعد المعرفة",
        "archive": "الأرشيف", "settings": "الإعدادات", "admin": "المدير", "menu": "القائمة",
        "tools": "الأدوات", "configurations": "التكوينات", "myProfile": "ملفي الشخصي",
        "logout": "تسجيل الخروج", "loggedInAs": "مسجل الدخول كـ: {{email}}"
      },
      "buttons": {
        "upload": "رفع", "download": "تحميل", "save": "حفظ", "cancel": "إلغاء",
        "delete": "حذف", "edit": "تعديل", "submit": "إرسال", "close": "إغلاق",
        "next": "التالي", "previous": "السابق", "confirm": "تأكيد", "back": "رجوع"
      },
      "forms": {
        "firstName": "الاسم الأول", "lastName": "اسم العائلة", "email": "البريد الإلكتروني", "password": "كلمة المرور",
        "confirmPassword": "تأكيد كلمة المرور", "currentPassword": "كلمة المرور الحالية", "newPassword": "كلمة المرور الجديدة",
        "required": "مطلوب", "optional": "اختياري", "emailPlaceholder": "أدخل عنوان بريدك الإلكتروني",
        "passwordPlaceholder": "أدخل كلمة المرور"
      },
      "chatbot": {
        "placeholder": "اكتب رسالتك هنا...", "send": "إرسال", "newChat": "محادثة جديدة",
        "clearHistory": "مسح التاريخ", "typing": "الذكاء الاصطناعي يكتب...", "error": "عذراً، حدث خطأ ما. يرجى المحاولة مرة أخرى.",
        "welcome": "مرحباً! كيف يمكنني مساعدتك اليوم؟"
      },
      "settings": {
        "title": "الإعدادات",
        "account": "الحساب",
        "language": "اللغة",
        "dangerZone": "منطقة الخطر",
        "preferredLanguage": "اللغة المفضلة",
        "saveLanguagePreference": "حفظ تفضيل اللغة",
        "deleteAccount": "حذف الحساب",
        "deleteAccountWarning": "لا يمكن التراجع عن هذا الإجراء.",
        "profile": "الملف الشخصي",
        "security": "الأمان",
        "changePassword": "تغيير كلمة المرور",
        "appearance": "المظهر"
      },
      "errors": {
        "somethingWentWrong": "حدث خطأ ما", "tryAgain": "يرجى المحاولة مرة أخرى", "invalidEmail": "عنوان بريد إلكتروني غير صالح",
        "passwordTooShort": "كلمة المرور قصيرة جداً", "passwordsDoNotMatch": "كلمات المرور غير متطابقة",
        "networkError": "خطأ في الشبكة. يرجى التحقق من اتصالك.", "unauthorized": "لست مخولاً لتنفيذ هذا الإجراء.",
        "notFound": "المورد المطلوب غير موجود."
      },
      "common": {
        "loading": "جارٍ التحميل...", "noData": "لا توجد بيانات متاحة", "success": "نجح!", "failed": "فشل",
        "welcome": "مرحباً", "goodbye": "وداعاً", "yes": "نعم", "no": "لا", "ok": "موافق",
        "search": "بحث", "filter": "تصفية", "sort": "ترتيب", "view": "عرض",
        "copy": "نسخ", "paste": "لصق", "cut": "قص"
      }
    }
  }

  // Hindi
  resources.hi = {
    common: {
      "navigation": {
        "dashboard": "डैशबोर्ड", "review": "समीक्षा", "generate": "उत्पन्न करें", "compare": "तुलना करें",
        "match": "मैच", "modelSelection": "मॉडल चयन", "knowledgeBases": "ज्ञान आधार",
        "archive": "संग्रह", "settings": "सेटिंग्स", "admin": "व्यवस्थापक", "menu": "मेनू",
        "tools": "उपकरण", "configurations": "कॉन्फ़िगरेशन", "myProfile": "मेरी प्रोफ़ाइल",
        "logout": "लॉग आउट", "loggedInAs": "लॉग इन किया गया: {{email}}"
      },
      "buttons": {
        "upload": "अपलोड", "download": "डाउनलोड", "save": "सहेजें", "cancel": "रद्द करें",
        "delete": "हटाएं", "edit": "संपादित करें", "submit": "जमा करें", "close": "बंद करें",
        "next": "अगला", "previous": "पिछला", "confirm": "पुष्टि करें", "back": "वापस"
      },
      "forms": {
        "firstName": "पहला नाम", "lastName": "अंतिम नाम", "email": "ईमेल", "password": "पासवर्ड",
        "confirmPassword": "पासवर्ड की पुष्टि करें", "currentPassword": "वर्तमान पासवर्ड", "newPassword": "नया पासवर्ड",
        "required": "आवश्यक", "optional": "वैकल्पिक", "emailPlaceholder": "अपना ईमेल पता दर्ज करें",
        "passwordPlaceholder": "अपना पासवर्ड दर्ज करें"
      },
      "chatbot": {
        "placeholder": "यहाँ अपना संदेश टाइप करें...", "send": "भेजें", "newChat": "नई चैट",
        "clearHistory": "इतिहास साफ़ करें", "typing": "AI टाइप कर रहा है...", "error": "क्षमा करें, कुछ गलत हुआ। कृपया फिर से कोशिश करें।",
        "welcome": "नमस्ते! आज मैं आपकी कैसे सहायता कर सकता हूँ?"
      },
      "settings": {
        "title": "सेटिंग्स",
        "account": "खाता",
        "language": "भाषा",
        "dangerZone": "खतरा क्षेत्र",
        "preferredLanguage": "पसंदीदा भाषा",
        "saveLanguagePreference": "भाषा वरीयता सहेजें",
        "deleteAccount": "खाता हटाएं",
        "deleteAccountWarning": "इस क्रिया को पूर्ववत नहीं किया जा सकता।",
        "profile": "प्रोफ़ाइल",
        "security": "सुरक्षा",
        "changePassword": "पासवर्ड बदलें",
        "appearance": "दिखावट"
      },
      "errors": {
        "somethingWentWrong": "कुछ गलत हुआ", "tryAgain": "कृपया फिर से कोशिश करें", "invalidEmail": "अमान्य ईमेल पता",
        "passwordTooShort": "पासवर्ड बहुत छोटा है", "passwordsDoNotMatch": "पासवर्ड मेल नहीं खाते",
        "networkError": "नेटवर्क त्रुटि। कृपया अपना कनेक्शन जांचें।", "unauthorized": "आप इस क्रिया को करने के लिए अधिकृत नहीं हैं।",
        "notFound": "अनुरोधित संसाधन नहीं मिला।"
      },
      "common": {
        "loading": "लोड हो रहा है...", "noData": "कोई डेटा उपलब्ध नहीं", "success": "सफलता!", "failed": "असफल",
        "welcome": "स्वागत है", "goodbye": "अलविदा", "yes": "हाँ", "no": "नहीं", "ok": "ठीक है",
        "search": "खोजें", "filter": "फ़िल्टर", "sort": "क्रमबद्ध करें", "view": "देखें",
        "copy": "कॉपी करें", "paste": "पेस्ट करें", "cut": "काटें"
      }
    }
  }

  // Add additional language translations
  addNordicTranslations(resources)
  addCentralEuropeanTranslations(resources)
  addBalticEasternEuropeanTranslations(resources)
  addAsianTranslations(resources)
  addMiddleEasternOtherTranslations(resources)

  // For all remaining languages, use a fallback with English
  const allLanguages = {
    "en": "English", "es": "Spanish (Europe)", "fr": "French", "de": "German", "it": "Italian",
    "pt": "Portuguese", "ru": "Russian", "uk": "Ukrainian", "pl": "Polish", "nl": "Dutch",
    "sv": "Swedish", "no": "Norwegian", "da": "Danish", "fi": "Finnish", "cs": "Czech",
    "sk": "Slovak", "hu": "Hungarian", "ro": "Romanian", "bg": "Bulgarian", "hr": "Croatian",
    "sr": "Serbian", "sl": "Slovenian", "et": "Estonian", "lv": "Latvian", "lt": "Lithuanian",
    "el": "Greek", "zh": "Chinese (Simplified)", "zh-TW": "Chinese (Traditional)", "ja": "Japanese",
    "ko": "Korean", "hi": "Hindi", "th": "Thai", "vi": "Vietnamese", "id": "Indonesian",
    "ms": "Malay", "tl": "Filipino", "ar": "Arabic", "he": "Hebrew", "fa": "Persian (Farsi)",
    "tr": "Turkish", "sw": "Swahili", "pt-BR": "Portuguese (Brazil)", "es-LATAM": "Spanish (Latin America)"
  }

  // Add English fallback for languages not explicitly translated above
  for (const [code] of Object.entries(allLanguages)) {
    if (!resources[code]) {
      resources[code] = { common: resources.en.common }
    }
  }

  return resources
}

// Generate resources for all languages
const resources = generateAllLanguageResources()

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    
    // Language detection options
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },

    interpolation: {
      escapeValue: false, // not needed for react as it escapes by default
    },

    // Default namespace
    defaultNS: 'common',
    ns: ['common'],
  })

export default i18n
