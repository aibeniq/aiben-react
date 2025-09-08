// Asian Languages Translations
// Chinese Traditional (zh-TW), Thai (th), Vietnamese (vi), Indonesian (id), Malay (ms), Filipino (tl)

export const addAsianTranslations = (resources: any) => {
  // Chinese Traditional
  resources['zh-TW'] = {
    common: {
      "navigation": {
        "dashboard": "儀表板",
        "review": "檢閱",
        "generate": "生成",
        "compare": "比較",
        "match": "匹配",
        "modelSelection": "模型選擇",
        "knowledgeBases": "知識庫",
        "archive": "檔案庫",
        "settings": "設定",
        "admin": "管理員",
        "menu": "選單",
        "tools": "工具",
        "configurations": "配置",
        "myProfile": "我的個人資料",
        "logout": "登出",
        "loggedInAs": "登入身份：{{email}}"
      },
      "buttons": {
        "upload": "上傳",
        "download": "下載",
        "save": "儲存",
        "cancel": "取消",
        "delete": "刪除",
        "edit": "編輯",
        "submit": "提交",
        "close": "關閉",
        "next": "下一個",
        "previous": "上一個",
        "confirm": "確認",
        "back": "返回"
      },
      "forms": {
        "firstName": "名字",
        "lastName": "姓氏",
        "email": "電子郵件",
        "password": "密碼",
        "confirmPassword": "確認密碼",
        "currentPassword": "目前密碼",
        "newPassword": "新密碼",
        "required": "必填",
        "optional": "選填",
        "emailPlaceholder": "輸入您的電子郵件地址",
        "passwordPlaceholder": "輸入您的密碼"
      },
      "chatbot": {
        "placeholder": "在此輸入您的訊息...",
        "send": "發送",
        "newChat": "新聊天",
        "clearHistory": "清除歷史記錄",
        "typing": "AI 正在輸入...",
        "error": "抱歉，發生錯誤。請重試。",
        "welcome": "您好！今天我可以如何協助您？"
      },
      "settings": {
        "title": "設定",
        "account": "帳戶",
        "language": "語言",
        "dangerZone": "危險區域",
        "preferredLanguage": "偏好語言",
        "saveLanguagePreference": "儲存語言偏好",
        "deleteAccount": "刪除帳戶",
        "deleteAccountWarning": "此操作無法撤銷。",
        "profile": "個人資料",
        "security": "安全性",
        "changePassword": "更改密碼",
        "appearance": "外觀"
      },
      "errors": {
        "somethingWentWrong": "發生錯誤",
        "tryAgain": "請重試",
        "invalidEmail": "無效的電子郵件地址",
        "passwordTooShort": "密碼太短",
        "passwordsDoNotMatch": "密碼不匹配",
        "networkError": "網路錯誤。請檢查您的連線。",
        "unauthorized": "您沒有執行此操作的權限。",
        "notFound": "找不到請求的資源。"
      },
      "common": {
        "loading": "載入中...",
        "noData": "無可用資料",
        "success": "成功！",
        "failed": "失敗",
        "welcome": "歡迎",
        "goodbye": "再見",
        "yes": "是",
        "no": "否",
        "ok": "確定",
        "search": "搜尋",
        "filter": "篩選",
        "sort": "排序",
        "view": "檢視",
        "copy": "複製",
        "paste": "貼上",
        "cut": "剪下"
      }
    }
  }

  // Thai
  resources.th = {
    common: {
      "navigation": {
        "dashboard": "แดชบอร์ด",
        "review": "ตรวจสอบ",
        "generate": "สร้าง",
        "compare": "เปรียบเทียบ",
        "match": "จับคู่",
        "modelSelection": "การเลือกโมเดล",
        "knowledgeBases": "ฐานความรู้",
        "archive": "เก็บเอกสาร",
        "settings": "การตั้งค่า",
        "admin": "ผู้ดูแลระบบ",
        "menu": "เมนู",
        "tools": "เครื่องมือ",
        "configurations": "การกำหนดค่า",
        "myProfile": "โปรไฟล์ของฉัน",
        "logout": "ออกจากระบบ",
        "loggedInAs": "เข้าสู่ระบบในฐานะ: {{email}}"
      },
      "buttons": {
        "upload": "อัปโหลด",
        "download": "ดาวน์โหลด",
        "save": "บันทึก",
        "cancel": "ยกเลิก",
        "delete": "ลบ",
        "edit": "แก้ไข",
        "submit": "ส่ง",
        "close": "ปิด",
        "next": "ถัดไป",
        "previous": "ก่อนหน้า",
        "confirm": "ยืนยัน",
        "back": "กลับ"
      },
      "forms": {
        "firstName": "ชื่อ",
        "lastName": "นามสกุล",
        "email": "อีเมล",
        "password": "รหัสผ่าน",
        "confirmPassword": "ยืนยันรหัสผ่าน",
        "currentPassword": "รหัสผ่านปัจจุบัน",
        "newPassword": "รหัสผ่านใหม่",
        "required": "จำเป็น",
        "optional": "ทางเลือก",
        "emailPlaceholder": "ใส่ที่อยู่อีเมลของคุณ",
        "passwordPlaceholder": "ใส่รหัสผ่านของคุณ"
      },
      "chatbot": {
        "placeholder": "พิมพ์ข้อความของคุณที่นี่...",
        "send": "ส่ง",
        "newChat": "แชทใหม่",
        "clearHistory": "ล้างประวัติ",
        "typing": "AI กำลังพิมพ์...",
        "error": "ขออภัย มีบางอย่างผิดพลาด โปรดลองอีกครั้ง",
        "welcome": "สวัสดี! วันนี้ฉันช่วยคุณอย่างไร?"
      },
      "settings": {
        "title": "การตั้งค่า",
        "account": "บัญชี",
        "language": "ภาษา",
        "dangerZone": "โซนอันตราย",
        "preferredLanguage": "ภาษาที่ต้องการ",
        "saveLanguagePreference": "บันทึกการตั้งค่าภาษา",
        "deleteAccount": "ลบบัญชี",
        "deleteAccountWarning": "การกระทำนี้ไม่สามารถเลิกทำได้",
        "profile": "โปรไฟล์",
        "security": "ความปลอดภัย",
        "changePassword": "เปลี่ยนรหัสผ่าน",
        "appearance": "รูปลักษณ์"
      },
      "errors": {
        "somethingWentWrong": "มีบางอย่างผิดพลาด",
        "tryAgain": "โปรดลองอีกครั้ง",
        "invalidEmail": "ที่อยู่อีเมลไม่ถูกต้อง",
        "passwordTooShort": "รหัสผ่านสั้นเกินไป",
        "passwordsDoNotMatch": "รหัสผ่านไม่ตรงกัน",
        "networkError": "ข้อผิดพลาดเครือข่าย โปรดตรวจสอบการเชื่อมต่อ",
        "unauthorized": "คุณไม่ได้รับอนุญาตให้ทำการกระทำนี้",
        "notFound": "ไม่พบทรัพยากรที่ร้องขอ"
      },
      "common": {
        "loading": "กำลังโหลด...",
        "noData": "ไม่มีข้อมูลที่พร้อมใช้งาน",
        "success": "สำเร็จ!",
        "failed": "ล้มเหลว",
        "welcome": "ยินดีต้อนรับ",
        "goodbye": "ลาก่อน",
        "yes": "ใช่",
        "no": "ไม่",
        "ok": "ตกลง",
        "search": "ค้นหา",
        "filter": "กรอง",
        "sort": "เรียง",
        "view": "ดู",
        "copy": "คัดลอก",
        "paste": "วาง",
        "cut": "ตัด"
      }
    }
  }

  // Vietnamese
  resources.vi = {
    common: {
      "navigation": {
        "dashboard": "Bảng điều khiển",
        "review": "Xem xét",
        "generate": "Tạo",
        "compare": "So sánh",
        "match": "Khớp",
        "modelSelection": "Lựa chọn mô hình",
        "knowledgeBases": "Cơ sở tri thức",
        "archive": "Lưu trữ",
        "settings": "Cài đặt",
        "admin": "Quản trị",
        "menu": "Menu",
        "tools": "Công cụ",
        "configurations": "Cấu hình",
        "myProfile": "Hồ sơ của tôi",
        "logout": "Đăng xuất",
        "loggedInAs": "Đã đăng nhập với: {{email}}"
      },
      "buttons": {
        "upload": "Tải lên",
        "download": "Tải xuống",
        "save": "Lưu",
        "cancel": "Hủy",
        "delete": "Xóa",
        "edit": "Chỉnh sửa",
        "submit": "Gửi",
        "close": "Đóng",
        "next": "Tiếp theo",
        "previous": "Trước đó",
        "confirm": "Xác nhận",
        "back": "Quay lại"
      },
      "forms": {
        "firstName": "Tên",
        "lastName": "Họ",
        "email": "Email",
        "password": "Mật khẩu",
        "confirmPassword": "Xác nhận mật khẩu",
        "currentPassword": "Mật khẩu hiện tại",
        "newPassword": "Mật khẩu mới",
        "required": "Bắt buộc",
        "optional": "Tùy chọn",
        "emailPlaceholder": "Nhập địa chỉ email của bạn",
        "passwordPlaceholder": "Nhập mật khẩu của bạn"
      },
      "chatbot": {
        "placeholder": "Nhập tin nhắn của bạn ở đây...",
        "send": "Gửi",
        "newChat": "Cuộc trò chuyện mới",
        "clearHistory": "Xóa lịch sử",
        "typing": "AI đang gõ...",
        "error": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
        "welcome": "Xin chào! Hôm nay tôi có thể giúp gì cho bạn?"
      },
      "settings": {
        "title": "Cài đặt",
        "account": "Tài khoản",
        "language": "Ngôn ngữ",
        "dangerZone": "Vùng nguy hiểm",
        "preferredLanguage": "Ngôn ngữ ưa thích",
        "saveLanguagePreference": "Lưu tùy chọn ngôn ngữ",
        "deleteAccount": "Xóa tài khoản",
        "deleteAccountWarning": "Hành động này không thể hoàn tác.",
        "profile": "Hồ sơ",
        "security": "Bảo mật",
        "changePassword": "Đổi mật khẩu",
        "appearance": "Giao diện"
      },
      "errors": {
        "somethingWentWrong": "Có lỗi xảy ra",
        "tryAgain": "Vui lòng thử lại",
        "invalidEmail": "Địa chỉ email không hợp lệ",
        "passwordTooShort": "Mật khẩu quá ngắn",
        "passwordsDoNotMatch": "Mật khẩu không khớp",
        "networkError": "Lỗi mạng. Vui lòng kiểm tra kết nối.",
        "unauthorized": "Bạn không có quyền thực hiện hành động này.",
        "notFound": "Không tìm thấy tài nguyên được yêu cầu."
      },
      "common": {
        "loading": "Đang tải...",
        "noData": "Không có dữ liệu",
        "success": "Thành công!",
        "failed": "Thất bại",
        "welcome": "Chào mừng",
        "goodbye": "Tạm biệt",
        "yes": "Có",
        "no": "Không",
        "ok": "OK",
        "search": "Tìm kiếm",
        "filter": "Lọc",
        "sort": "Sắp xếp",
        "view": "Xem",
        "copy": "Sao chép",
        "paste": "Dán",
        "cut": "Cắt"
      }
    }
  }

  // Indonesian
  resources.id = {
    common: {
      "navigation": {
        "dashboard": "Dasbor",
        "review": "Tinjauan",
        "generate": "Buat",
        "compare": "Bandingkan",
        "match": "Cocokkan",
        "modelSelection": "Pilihan Model",
        "knowledgeBases": "Basis Pengetahuan",
        "archive": "Arsip",
        "settings": "Pengaturan",
        "admin": "Admin",
        "menu": "Menu",
        "tools": "Alat",
        "configurations": "Konfigurasi",
        "myProfile": "Profil Saya",
        "logout": "Keluar",
        "loggedInAs": "Masuk sebagai: {{email}}"
      },
      "buttons": {
        "upload": "Unggah",
        "download": "Unduh",
        "save": "Simpan",
        "cancel": "Batal",
        "delete": "Hapus",
        "edit": "Edit",
        "submit": "Kirim",
        "close": "Tutup",
        "next": "Selanjutnya",
        "previous": "Sebelumnya",
        "confirm": "Konfirmasi",
        "back": "Kembali"
      },
      "forms": {
        "firstName": "Nama Depan",
        "lastName": "Nama Belakang",
        "email": "Email",
        "password": "Kata Sandi",
        "confirmPassword": "Konfirmasi Kata Sandi",
        "currentPassword": "Kata Sandi Saat Ini",
        "newPassword": "Kata Sandi Baru",
        "required": "Wajib",
        "optional": "Opsional",
        "emailPlaceholder": "Masukkan alamat email Anda",
        "passwordPlaceholder": "Masukkan kata sandi Anda"
      },
      "chatbot": {
        "placeholder": "Ketik pesan Anda di sini...",
        "send": "Kirim",
        "newChat": "Obrolan Baru",
        "clearHistory": "Hapus Riwayat",
        "typing": "AI sedang mengetik...",
        "error": "Maaf, terjadi kesalahan. Silakan coba lagi.",
        "welcome": "Halo! Bagaimana saya bisa membantu Anda hari ini?"
      },
      "settings": {
        "title": "Pengaturan",
        "account": "Akun",
        "language": "Bahasa",
        "dangerZone": "Zona Bahaya",
        "preferredLanguage": "Bahasa Pilihan",
        "saveLanguagePreference": "Simpan Preferensi Bahasa",
        "deleteAccount": "Hapus Akun",
        "deleteAccountWarning": "Tindakan ini tidak dapat dibatalkan.",
        "profile": "Profil",
        "security": "Keamanan",
        "changePassword": "Ubah Kata Sandi",
        "appearance": "Tampilan"
      },
      "errors": {
        "somethingWentWrong": "Terjadi kesalahan",
        "tryAgain": "Silakan coba lagi",
        "invalidEmail": "Alamat email tidak valid",
        "passwordTooShort": "Kata sandi terlalu pendek",
        "passwordsDoNotMatch": "Kata sandi tidak cocok",
        "networkError": "Kesalahan jaringan. Periksa koneksi Anda.",
        "unauthorized": "Anda tidak berwenang untuk melakukan tindakan ini.",
        "notFound": "Sumber daya yang diminta tidak ditemukan."
      },
      "common": {
        "loading": "Memuat...",
        "noData": "Tidak ada data tersedia",
        "success": "Berhasil!",
        "failed": "Gagal",
        "welcome": "Selamat datang",
        "goodbye": "Selamat tinggal",
        "yes": "Ya",
        "no": "Tidak",
        "ok": "OK",
        "search": "Cari",
        "filter": "Filter",
        "sort": "Urutkan",
        "view": "Lihat",
        "copy": "Salin",
        "paste": "Tempel",
        "cut": "Potong"
      }
    }
  }

  // Malay
  resources.ms = {
    common: {
      "navigation": {
        "dashboard": "Papan Pemuka",
        "review": "Semakan",
        "generate": "Jana",
        "compare": "Bandingkan",
        "match": "Padankan",
        "modelSelection": "Pemilihan Model",
        "knowledgeBases": "Pangkalan Pengetahuan",
        "archive": "Arkib",
        "settings": "Tetapan",
        "admin": "Pentadbir",
        "menu": "Menu",
        "tools": "Alatan",
        "configurations": "Konfigurasi",
        "myProfile": "Profil Saya",
        "logout": "Log Keluar",
        "loggedInAs": "Log masuk sebagai: {{email}}"
      },
      "buttons": {
        "upload": "Muat Naik",
        "download": "Muat Turun",
        "save": "Simpan",
        "cancel": "Batal",
        "delete": "Padam",
        "edit": "Edit",
        "submit": "Hantar",
        "close": "Tutup",
        "next": "Seterusnya",
        "previous": "Sebelumnya",
        "confirm": "Sahkan",
        "back": "Kembali"
      },
      "forms": {
        "firstName": "Nama Pertama",
        "lastName": "Nama Keluarga",
        "email": "E-mel",
        "password": "Kata Laluan",
        "confirmPassword": "Sahkan Kata Laluan",
        "currentPassword": "Kata Laluan Semasa",
        "newPassword": "Kata Laluan Baru",
        "required": "Wajib",
        "optional": "Pilihan",
        "emailPlaceholder": "Masukkan alamat e-mel anda",
        "passwordPlaceholder": "Masukkan kata laluan anda"
      },
      "chatbot": {
        "placeholder": "Taip mesej anda di sini...",
        "send": "Hantar",
        "newChat": "Sembang Baru",
        "clearHistory": "Padam Sejarah",
        "typing": "AI sedang menaip...",
        "error": "Maaf, ada yang tidak kena. Sila cuba lagi.",
        "welcome": "Hai! Bagaimana saya boleh membantu anda hari ini?"
      },
      "settings": {
        "title": "Tetapan",
        "account": "Akaun",
        "language": "Bahasa",
        "dangerZone": "Zon Bahaya",
        "preferredLanguage": "Bahasa Pilihan",
        "saveLanguagePreference": "Simpan Pilihan Bahasa",
        "deleteAccount": "Padam Akaun",
        "deleteAccountWarning": "Tindakan ini tidak boleh dibatalkan.",
        "profile": "Profil",
        "security": "Keselamatan",
        "changePassword": "Tukar Kata Laluan",
        "appearance": "Penampilan"
      },
      "errors": {
        "somethingWentWrong": "Ada yang tidak kena",
        "tryAgain": "Sila cuba lagi",
        "invalidEmail": "Alamat e-mel tidak sah",
        "passwordTooShort": "Kata laluan terlalu pendek",
        "passwordsDoNotMatch": "Kata laluan tidak sepadan",
        "networkError": "Ralat rangkaian. Semak sambungan anda.",
        "unauthorized": "Anda tidak diberi kuasa untuk tindakan ini.",
        "notFound": "Sumber yang diminta tidak dijumpai."
      },
      "common": {
        "loading": "Memuatkan...",
        "noData": "Tiada data tersedia",
        "success": "Berjaya!",
        "failed": "Gagal",
        "welcome": "Selamat datang",
        "goodbye": "Selamat tinggal",
        "yes": "Ya",
        "no": "Tidak",
        "ok": "OK",
        "search": "Cari",
        "filter": "Penapis",
        "sort": "Susun",
        "view": "Lihat",
        "copy": "Salin",
        "paste": "Tampal",
        "cut": "Potong"
      }
    }
  }

  // Filipino (Tagalog)
  resources.tl = {
    common: {
      "navigation": {
        "dashboard": "Dashboard",
        "review": "Pagsusuri",
        "generate": "Likhain",
        "compare": "Ikumpara",
        "match": "Tumugma",
        "modelSelection": "Pagpili ng Modelo",
        "knowledgeBases": "Mga Base ng Kaalaman",
        "archive": "Archive",
        "settings": "Mga Setting",
        "admin": "Admin",
        "menu": "Menu",
        "tools": "Mga Kasangkapan",
        "configurations": "Mga Konpigurasyon",
        "myProfile": "Aking Profile",
        "logout": "Mag-logout",
        "loggedInAs": "Naka-login bilang: {{email}}"
      },
      "buttons": {
        "upload": "I-upload",
        "download": "I-download",
        "save": "I-save",
        "cancel": "Kanselahin",
        "delete": "Tanggalin",
        "edit": "I-edit",
        "submit": "Ipasa",
        "close": "Isara",
        "next": "Susunod",
        "previous": "Nakaraan",
        "confirm": "Kumpirmahin",
        "back": "Bumalik"
      },
      "forms": {
        "firstName": "Unang Pangalan",
        "lastName": "Huling Pangalan",
        "email": "Email",
        "password": "Password",
        "confirmPassword": "Kumpirmahin ang Password",
        "currentPassword": "Kasalukuyang Password",
        "newPassword": "Bagong Password",
        "required": "Kinakailangan",
        "optional": "Opsyonal",
        "emailPlaceholder": "Ilagay ang inyong email address",
        "passwordPlaceholder": "Ilagay ang inyong password"
      },
      "chatbot": {
        "placeholder": "Mag-type ng inyong mensahe dito...",
        "send": "Ipadala",
        "newChat": "Bagong Chat",
        "clearHistory": "Tanggalin ang Kasaysayan",
        "typing": "Nag-ta-type ang AI...",
        "error": "Pasensya na, may nangyaring mali. Subukan muli.",
        "welcome": "Kumusta! Paano kita matutulungan ngayon?"
      },
      "settings": {
        "title": "Mga Setting",
        "account": "Account",
        "language": "Wika",
        "dangerZone": "Delikadong Lugar",
        "preferredLanguage": "Ginustong Wika",
        "saveLanguagePreference": "I-save ang Preference sa Wika",
        "deleteAccount": "Tanggalin ang Account",
        "deleteAccountWarning": "Hindi na mababawi ang aksyong ito.",
        "profile": "Profile",
        "security": "Seguridad",
        "changePassword": "Baguhin ang Password",
        "appearance": "Hitsura"
      },
      "errors": {
        "somethingWentWrong": "May nangyaring mali",
        "tryAgain": "Subukan muli",
        "invalidEmail": "Hindi wastong email address",
        "passwordTooShort": "Masyadong maikli ang password",
        "passwordsDoNotMatch": "Hindi nagtugma ang mga password",
        "networkError": "Error sa network. Suriin ang inyong koneksyon.",
        "unauthorized": "Walang pahintulot para sa aksyong ito.",
        "notFound": "Hindi natagpuan ang hiniling na resource."
      },
      "common": {
        "loading": "Naglo-load...",
        "noData": "Walang available na data",
        "success": "Tagumpay!",
        "failed": "Nabigo",
        "welcome": "Maligayang pagdating",
        "goodbye": "Paalam",
        "yes": "Oo",
        "no": "Hindi",
        "ok": "OK",
        "search": "Maghanap",
        "filter": "Filter",
        "sort": "Ayusin",
        "view": "Tingnan",
        "copy": "Kopyahin",
        "paste": "I-paste",
        "cut": "Putulin"
      }
    }
  }
}
