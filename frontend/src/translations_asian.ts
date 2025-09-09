// Asian Languages Translations
// Chinese Traditional (zh-TW), Thai (th), Vietnamese (vi), Indonesian (id), Malay (ms), Filipino (tl)

export const addAsianTranslations = (resources: any) => {
  // Chinese Traditional
  resources["zh-TW"] = {
    common: {
      navigation: {
        dashboard: "儀表板",
        review: "檢閱",
        generate: "生成",
        compare: "比較",
        match: "匹配",
        modelSelection: "模型選擇",
        knowledgeBases: "知識庫",
        archive: "檔案庫",
        settings: "設定",
        admin: "管理員",
        menu: "選單",
        tools: "工具",
        configurations: "配置",
        myProfile: "我的個人資料",
        logout: "登出",
        loggedInAs: "登入身份：{{email}}",
      },
      buttons: {
        upload: "上傳",
        download: "下載",
        save: "儲存",
        cancel: "取消",
        delete: "刪除",
        edit: "編輯",
        submit: "提交",
        close: "關閉",
        next: "下一個",
        previous: "上一個",
        confirm: "確認",
        back: "返回",
      },
      forms: {
        firstName: "名字",
        lastName: "姓氏",
        email: "電子郵件",
        password: "密碼",
        confirmPassword: "確認密碼",
        currentPassword: "目前密碼",
        newPassword: "新密碼",
        required: "必填",
        optional: "選填",
        emailPlaceholder: "輸入您的電子郵件地址",
        passwordPlaceholder: "輸入您的密碼",
      },
      chatbot: {
        placeholder: "在此輸入您的訊息...",
        send: "發送",
        newChat: "新聊天",
        clearHistory: "清除歷史記錄",
        typing: "AI 正在輸入...",
        error: "抱歉，發生錯誤。請重試。",
        welcome: "您好！今天我可以如何協助您？",
      },
      settings: {
        title: "設定",
        account: "帳戶",
        language: "語言",
        dangerZone: "危險區域",
        preferredLanguage: "偏好語言",
        saveLanguagePreference: "儲存語言偏好",
        deleteAccount: "刪除帳戶",
        deleteAccountWarning: "此操作無法撤銷。",
        profile: "個人資料",
        security: "安全性",
        changePassword: "更改密碼",
        appearance: "外觀",
      },
      errors: {
        somethingWentWrong: "發生錯誤",
        tryAgain: "請重試",
        invalidEmail: "無效的電子郵件地址",
        passwordTooShort: "密碼太短",
        passwordsDoNotMatch: "密碼不匹配",
        networkError: "網路錯誤。請檢查您的連線。",
        unauthorized: "您沒有執行此操作的權限。",
        notFound: "找不到請求的資源。",
      },
      common: {
        loading: "載入中...",
        noData: "無可用資料",
        success: "成功！",
        failed: "失敗",
        welcome: "歡迎",
        goodbye: "再見",
        yes: "是",
        no: "否",
        ok: "確定",
        search: "搜尋",
        filter: "篩選",
        sort: "排序",
        view: "檢視",
        copy: "複製",
        paste: "貼上",
        cut: "剪下",
      },
      review: {
        pageTitle: "檢閱文件",
        pageDescription: "基於用戶定義的檢查清單和政策資料庫檢閱文件。",
        knowledgeBaseTitle: "知識庫",
        knowledgeBaseDescription: "點擊選擇",
        checklistTitle: "檢查清單",
        checklistDescription: "點擊選擇",
        customInstructionsTitle: "自訂指示（選填）",
        customInstructionsPlaceholder: "輸入在回答檢查清單問題時應考慮的附加指示...",
        customInstructionsHelp: "{count}/2000 字符。這些指示將在處理過程中添加到每個問題中。",
        searchModeHelp: "向量搜尋提供快速、有針對性的結果。完整文件分析檢查知識庫的所有內容。",
        processingFile: "正在處理文件...",
        processingFiles: "正在處理文件...",
        selectKnowledgeBaseTitle: "選擇知識庫",
        selectChecklistTitle: "選擇檢查清單",
        noResults: "暫無結果",
        uploadDocuments: "上傳一個或多個文件以根據您選擇的檢查清單進行檢閱",
        results: "結果",
        downloadReport: "下載報告",
        downloadCsv: "下載CSV",
        clearResults: "清除結果",
        copyReport: "複製報告",
        reportCopied: "報告已複製到剪貼板！",
        reviewButton: "檢閱",
        consultDocuments: "諮詢文件",
        noChecklistsAvailable: "沒有可用的檢查清單。創建您的第一個檢查清單以開始。",
        createChecklist: "創建檢查清單",
        editChecklist: "編輯檢查清單",
        checklistName: "檢查清單名稱",
        checklistNamePlaceholder: "輸入檢查清單名稱...",
        checklistDescriptionLabel: "描述",
        checklistDescriptionPlaceholder: "輸入檢查清單描述以獲取自動問題建議（最少10個字符）...",
        questions: "問題",
        suggest: "建議",
        suggesting: "正在建議...",
        optimize: "最佳化",
        optimizeTooltip: "必須選擇知識庫才能啟用最佳化功能",
        optimizeTooltipEnabled: "基於選定的知識庫最佳化問題",
        uploadFiles: "上傳文件",
        knowledgeBase: "知識庫",
        referenceDocuments: "參考文件（選填）",
        selectKnowledgeBasePlaceholder: "選擇知識庫...",
        noKnowledgeBasesAvailable: "沒有可用的知識庫。請先創建一個以使用此功能。",
        copyQuestions: "複製問題",
        questionsCopied: "問題已複製到剪貼板",
        noQuestionsToCopy: "沒有問題可複製",
        failedToCopyQuestions: "複製問題到剪貼板失敗",
        saveChecklist: "保存檢查清單",
        cancel: "取消",
        deleteChecklist: "刪除檢查清單"
      },
    },
  }

  // Thai
  resources.th = {
    common: {
      navigation: {
        dashboard: "แดชบอร์ด",
        review: "ตรวจสอบ",
        generate: "สร้าง",
        compare: "เปรียบเทียบ",
        match: "จับคู่",
        modelSelection: "การเลือกโมเดล",
        knowledgeBases: "ฐานความรู้",
        archive: "เก็บเอกสาร",
        settings: "การตั้งค่า",
        admin: "ผู้ดูแลระบบ",
        menu: "เมนู",
        tools: "เครื่องมือ",
        configurations: "การกำหนดค่า",
        myProfile: "โปรไฟล์ของฉัน",
        logout: "ออกจากระบบ",
        loggedInAs: "เข้าสู่ระบบในฐานะ: {{email}}",
      },
      buttons: {
        upload: "อัปโหลด",
        download: "ดาวน์โหลด",
        save: "บันทึก",
        cancel: "ยกเลิก",
        delete: "ลบ",
        edit: "แก้ไข",
        submit: "ส่ง",
        close: "ปิด",
        next: "ถัดไป",
        previous: "ก่อนหน้า",
        confirm: "ยืนยัน",
        back: "กลับ",
      },
      forms: {
        firstName: "ชื่อ",
        lastName: "นามสกุล",
        email: "อีเมล",
        password: "รหัสผ่าน",
        confirmPassword: "ยืนยันรหัสผ่าน",
        currentPassword: "รหัสผ่านปัจจุบัน",
        newPassword: "รหัสผ่านใหม่",
        required: "จำเป็น",
        optional: "ทางเลือก",
        emailPlaceholder: "ใส่ที่อยู่อีเมลของคุณ",
        passwordPlaceholder: "ใส่รหัสผ่านของคุณ",
      },
      chatbot: {
        placeholder: "พิมพ์ข้อความของคุณที่นี่...",
        send: "ส่ง",
        newChat: "แชทใหม่",
        clearHistory: "ล้างประวัติ",
        typing: "AI กำลังพิมพ์...",
        error: "ขออภัย มีบางอย่างผิดพลาด โปรดลองอีกครั้ง",
        welcome: "สวัสดี! วันนี้ฉันช่วยคุณอย่างไร?",
      },
      settings: {
        title: "การตั้งค่า",
        account: "บัญชี",
        language: "ภาษา",
        dangerZone: "โซนอันตราย",
        preferredLanguage: "ภาษาที่ต้องการ",
        saveLanguagePreference: "บันทึกการตั้งค่าภาษา",
        deleteAccount: "ลบบัญชี",
        deleteAccountWarning: "การกระทำนี้ไม่สามารถเลิกทำได้",
        profile: "โปรไฟล์",
        security: "ความปลอดภัย",
        changePassword: "เปลี่ยนรหัสผ่าน",
        appearance: "รูปลักษณ์",
      },
      errors: {
        somethingWentWrong: "มีบางอย่างผิดพลาด",
        tryAgain: "โปรดลองอีกครั้ง",
        invalidEmail: "ที่อยู่อีเมลไม่ถูกต้อง",
        passwordTooShort: "รหัสผ่านสั้นเกินไป",
        passwordsDoNotMatch: "รหัสผ่านไม่ตรงกัน",
        networkError: "ข้อผิดพลาดเครือข่าย โปรดตรวจสอบการเชื่อมต่อ",
        unauthorized: "คุณไม่ได้รับอนุญาตให้ทำการกระทำนี้",
        notFound: "ไม่พบทรัพยากรที่ร้องขอ",
      },
      common: {
        loading: "กำลังโหลด...",
        noData: "ไม่มีข้อมูลที่พร้อมใช้งาน",
        success: "สำเร็จ!",
        failed: "ล้มเหลว",
        welcome: "ยินดีต้อนรับ",
        goodbye: "ลาก่อน",
        yes: "ใช่",
        no: "ไม่",
        ok: "ตกลง",
        search: "ค้นหา",
        filter: "กรอง",
        sort: "เรียง",
        view: "ดู",
        copy: "คัดลอก",
        paste: "วาง",
        cut: "ตัด",
      },
      review: {
        pageTitle: "ตรวจสอบเอกสาร",
        pageDescription: "ตรวจสอบเอกสารตามรายการตรวจสอบและฐานข้อมูลนีติกรรมที่ผู้ใช้กำหนด",
        knowledgeBaseTitle: "ฐานความรู้",
        knowledgeBaseDescription: "คลิกเพื่อเลือก",
        checklistTitle: "รายการตรวจสอบ",
        checklistDescription: "คลิกเพื่อเลือก",
        customInstructionsTitle: "คำแนะนำเฉพาะ (ทางเลือก)",
        customInstructionsPlaceholder: "ใส่คำแนะนำเพิ่มเติมที่ควรพิจารณาเมื่อตอบคำถามในรายการตรวจสอบ...",
        customInstructionsHelp: "{count}/2000 ตัวอักษร คำแนะนำเหล่านี้จะถูกเพิ่มเข้าไปในทุกคำถามระหว่างการประมวลผล",
        searchModeHelp: "การค้นหาแบบเวกเตอร์ให้ผลลัพธ์ที่รวดเร็วและตรงเป้าหมาย การวิเคราะห์เอกสารแบบเต็มจะตรวจสอบเนื้อหาทั้งหมดในฐานความรู้",
        processingFile: "กำลังประมวลผลไฟล์...",
        processingFiles: "กำลังประมวลผลไฟล์...",
        selectKnowledgeBaseTitle: "เลือกฐานความรู้",
        selectChecklistTitle: "เลือกรายการตรวจสอบ",
        noResults: "ยังไม่มีผลลัพธ์",
        uploadDocuments: "อัปโหลดเอกสารหนึ่งไฟล์หรือมากกว่าเพื่อตรวจสอบกับรายการตรวจสอบที่คุณเลือก",
        results: "ผลลัพธ์",
        downloadReport: "ดาวน์โหลดรายงาน",
        downloadCsv: "ดาวน์โหลด CSV",
        clearResults: "ล้างผลลัพธ์",
        copyReport: "คัดลอกรายงาน",
        reportCopied: "คัดลอกรายงานไปยังคลิปบอร์ดแล้ว!",
        reviewButton: "ตรวจสอบ",
        consultDocuments: "ปรึกษาเอกสาร",
        noChecklistsAvailable: "ไม่มีรายการตรวจสอบที่ใช้ได้ สร้างรายการตรวจสอบแรกของคุณเพื่อเริ่มต้น",
        createChecklist: "สร้างรายการตรวจสอบ",
        editChecklist: "แก้ไขรายการตรวจสอบ",
        checklistName: "ชื่อรายการตรวจสอบ",
        checklistNamePlaceholder: "ใส่ชื่อรายการตรวจสอบ...",
        checklistDescriptionLabel: "คำอธิบาย",
        checklistDescriptionPlaceholder: "ใส่คำอธิบายรายการตรวจสอบสำหรับข้อเสนอแนะคำถามอัตโนมัติ (อย่างน้อย 10 ตัวอักษร)...",
        questions: "คำถาม",
        suggest: "แนะนำ",
        suggesting: "กำลังแนะนำ...",
        optimize: "ปรับให้เหมาะสม",
        optimizeTooltip: "ต้องเลือกฐานความรู้เพื่อเปิดใช้งานฟังก์ชันปรับให้เหมาะสม",
        optimizeTooltipEnabled: "ปรับคำถามให้เหมาะสมตามฐานความรู้ที่เลือก",
        uploadFiles: "อัปโหลดไฟล์",
        knowledgeBase: "ฐานความรู้",
        referenceDocuments: "เอกสารอ้างอิง (ทางเลือก)",
        selectKnowledgeBasePlaceholder: "เลือกฐานความรู้...",
        noKnowledgeBasesAvailable: "ไม่มีฐานความรู้ที่ใช้ได้ สร้างฐานความรู้ก่อนเพื่อใช้ฟังก์ชันนี้",
        copyQuestions: "คัดลอกคำถาม",
        questionsCopied: "คัดลอกคำถามไปยังคลิปบอร์ดแล้ว",
        noQuestionsToCopy: "ไม่มีคำถามให้คัดลอก",
        failedToCopyQuestions: "ไม่สามารถคัดลอกคำถามไปยังคลิปบอร์ดได้",
        saveChecklist: "บันทึกรายการตรวจสอบ",
        cancel: "ยกเลิก",
        deleteChecklist: "ลบรายการตรวจสอบ"
      },
    },
  }

  // Vietnamese
  resources.vi = {
    common: {
      navigation: {
        dashboard: "Bảng điều khiển",
        review: "Xem xét",
        generate: "Tạo",
        compare: "So sánh",
        match: "Khớp",
        modelSelection: "Lựa chọn mô hình",
        knowledgeBases: "Cơ sở tri thức",
        archive: "Lưu trữ",
        settings: "Cài đặt",
        admin: "Quản trị",
        menu: "Menu",
        tools: "Công cụ",
        configurations: "Cấu hình",
        myProfile: "Hồ sơ của tôi",
        logout: "Đăng xuất",
        loggedInAs: "Đã đăng nhập với: {{email}}",
      },
      buttons: {
        upload: "Tải lên",
        download: "Tải xuống",
        save: "Lưu",
        cancel: "Hủy",
        delete: "Xóa",
        edit: "Chỉnh sửa",
        submit: "Gửi",
        close: "Đóng",
        next: "Tiếp theo",
        previous: "Trước đó",
        confirm: "Xác nhận",
        back: "Quay lại",
      },
      forms: {
        firstName: "Tên",
        lastName: "Họ",
        email: "Email",
        password: "Mật khẩu",
        confirmPassword: "Xác nhận mật khẩu",
        currentPassword: "Mật khẩu hiện tại",
        newPassword: "Mật khẩu mới",
        required: "Bắt buộc",
        optional: "Tùy chọn",
        emailPlaceholder: "Nhập địa chỉ email của bạn",
        passwordPlaceholder: "Nhập mật khẩu của bạn",
      },
      chatbot: {
        placeholder: "Nhập tin nhắn của bạn ở đây...",
        send: "Gửi",
        newChat: "Cuộc trò chuyện mới",
        clearHistory: "Xóa lịch sử",
        typing: "AI đang gõ...",
        error: "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
        welcome: "Xin chào! Hôm nay tôi có thể giúp gì cho bạn?",
      },
      settings: {
        title: "Cài đặt",
        account: "Tài khoản",
        language: "Ngôn ngữ",
        dangerZone: "Vùng nguy hiểm",
        preferredLanguage: "Ngôn ngữ ưa thích",
        saveLanguagePreference: "Lưu tùy chọn ngôn ngữ",
        deleteAccount: "Xóa tài khoản",
        deleteAccountWarning: "Hành động này không thể hoàn tác.",
        profile: "Hồ sơ",
        security: "Bảo mật",
        changePassword: "Đổi mật khẩu",
        appearance: "Giao diện",
      },
      errors: {
        somethingWentWrong: "Có lỗi xảy ra",
        tryAgain: "Vui lòng thử lại",
        invalidEmail: "Địa chỉ email không hợp lệ",
        passwordTooShort: "Mật khẩu quá ngắn",
        passwordsDoNotMatch: "Mật khẩu không khớp",
        networkError: "Lỗi mạng. Vui lòng kiểm tra kết nối.",
        unauthorized: "Bạn không có quyền thực hiện hành động này.",
        notFound: "Không tìm thấy tài nguyên được yêu cầu.",
      },
      common: {
        loading: "Đang tải...",
        noData: "Không có dữ liệu",
        success: "Thành công!",
        failed: "Thất bại",
        welcome: "Chào mừng",
        goodbye: "Tạm biệt",
        yes: "Có",
        no: "Không",
        ok: "OK",
        search: "Tìm kiếm",
        filter: "Lọc",
        sort: "Sắp xếp",
        view: "Xem",
        copy: "Sao chép",
        paste: "Dán",
        cut: "Cắt",
      },
      review: {
        pageTitle: "Xem xét tài liệu",
        pageDescription: "Xem xét tài liệu dựa trên danh sách kiểm tra do người dùng định nghĩa và cơ sở dữ liệu chính sách.",
        knowledgeBaseTitle: "Cơ sở tri thức",
        knowledgeBaseDescription: "Nhấp để chọn",
        checklistTitle: "Danh sách kiểm tra",
        checklistDescription: "Nhấp để chọn",
        customInstructionsTitle: "Hướng dẫn tùy chỉnh (tùy chọn)",
        customInstructionsPlaceholder: "Nhập hướng dẫn bổ sung cần xem xét khi trả lời các câu hỏi danh sách kiểm tra...",
        customInstructionsHelp: "{count}/2000 ký tự. Những hướng dẫn này sẽ được thêm vào mỗi câu hỏi trong quá trình xử lý.",
        searchModeHelp: "Tìm kiếm vector cung cấp kết quả nhanh, có mục tiêu. Phân tích tài liệu đầy đủ kiểm tra toàn bộ nội dung cơ sở tri thức.",
        processingFile: "Đang xử lý tệp...",
        processingFiles: "Đang xử lý các tệp...",
        selectKnowledgeBaseTitle: "Chọn cơ sở tri thức",
        selectChecklistTitle: "Chọn danh sách kiểm tra",
        noResults: "Chưa có kết quả",
        uploadDocuments: "Tải lên một hoặc nhiều tài liệu để xem xét theo danh sách kiểm tra đã chọn",
        results: "Kết quả",
        downloadReport: "Tải xuống báo cáo",
        downloadCsv: "Tải xuống CSV",
        clearResults: "Xóa kết quả",
        copyReport: "Sao chép báo cáo",
        reportCopied: "Báo cáo đã được sao chép vào clipboard!",
        reviewButton: "Xem xét",
        consultDocuments: "Tham khảo tài liệu",
        noChecklistsAvailable: "Không có danh sách kiểm tra nào. Tạo danh sách kiểm tra đầu tiên để bắt đầu.",
        createChecklist: "Tạo danh sách kiểm tra",
        editChecklist: "Chỉnh sửa danh sách kiểm tra",
        checklistName: "Tên danh sách kiểm tra",
        checklistNamePlaceholder: "Nhập tên danh sách kiểm tra...",
        checklistDescriptionLabel: "Mô tả",
        checklistDescriptionPlaceholder: "Nhập mô tả danh sách kiểm tra cho các đề xuất câu hỏi tự động (tối thiểu 10 ký tự)...",
        questions: "Câu hỏi",
        suggest: "Đề xuất",
        suggesting: "Đang đề xuất...",
        optimize: "Tối ưu hóa",
        optimizeTooltip: "Cần chọn cơ sở tri thức để bật tính năng tối ưu hóa",
        optimizeTooltipEnabled: "Tối ưu hóa câu hỏi dựa trên cơ sở tri thức đã chọn",
        uploadFiles: "Tải lên tệp",
        knowledgeBase: "Cơ sở tri thức",
        referenceDocuments: "Tài liệu tham khảo (tùy chọn)",
        selectKnowledgeBasePlaceholder: "Chọn cơ sở tri thức...",
        noKnowledgeBasesAvailable: "Không có cơ sở tri thức nào. Tạo một cái trước để sử dụng tính năng này.",
        copyQuestions: "Sao chép câu hỏi",
        questionsCopied: "Câu hỏi đã được sao chép vào clipboard",
        noQuestionsToCopy: "Không có câu hỏi để sao chép",
        failedToCopyQuestions: "Không thể sao chép câu hỏi vào clipboard",
        saveChecklist: "Lưu danh sách kiểm tra",
        cancel: "Hủy",
        deleteChecklist: "Xóa danh sách kiểm tra"
      },
    },
  }

  // Indonesian
  resources.id = {
    common: {
      navigation: {
        dashboard: "Dasbor",
        review: "Tinjauan",
        generate: "Buat",
        compare: "Bandingkan",
        match: "Cocokkan",
        modelSelection: "Pilihan Model",
        knowledgeBases: "Basis Pengetahuan",
        archive: "Arsip",
        settings: "Pengaturan",
        admin: "Admin",
        menu: "Menu",
        tools: "Alat",
        configurations: "Konfigurasi",
        myProfile: "Profil Saya",
        logout: "Keluar",
        loggedInAs: "Masuk sebagai: {{email}}",
      },
      buttons: {
        upload: "Unggah",
        download: "Unduh",
        save: "Simpan",
        cancel: "Batal",
        delete: "Hapus",
        edit: "Edit",
        submit: "Kirim",
        close: "Tutup",
        next: "Selanjutnya",
        previous: "Sebelumnya",
        confirm: "Konfirmasi",
        back: "Kembali",
      },
      forms: {
        firstName: "Nama Depan",
        lastName: "Nama Belakang",
        email: "Email",
        password: "Kata Sandi",
        confirmPassword: "Konfirmasi Kata Sandi",
        currentPassword: "Kata Sandi Saat Ini",
        newPassword: "Kata Sandi Baru",
        required: "Wajib",
        optional: "Opsional",
        emailPlaceholder: "Masukkan alamat email Anda",
        passwordPlaceholder: "Masukkan kata sandi Anda",
      },
      chatbot: {
        placeholder: "Ketik pesan Anda di sini...",
        send: "Kirim",
        newChat: "Obrolan Baru",
        clearHistory: "Hapus Riwayat",
        typing: "AI sedang mengetik...",
        error: "Maaf, terjadi kesalahan. Silakan coba lagi.",
        welcome: "Halo! Bagaimana saya bisa membantu Anda hari ini?",
      },
      settings: {
        title: "Pengaturan",
        account: "Akun",
        language: "Bahasa",
        dangerZone: "Zona Bahaya",
        preferredLanguage: "Bahasa Pilihan",
        saveLanguagePreference: "Simpan Preferensi Bahasa",
        deleteAccount: "Hapus Akun",
        deleteAccountWarning: "Tindakan ini tidak dapat dibatalkan.",
        profile: "Profil",
        security: "Keamanan",
        changePassword: "Ubah Kata Sandi",
        appearance: "Tampilan",
      },
      errors: {
        somethingWentWrong: "Terjadi kesalahan",
        tryAgain: "Silakan coba lagi",
        invalidEmail: "Alamat email tidak valid",
        passwordTooShort: "Kata sandi terlalu pendek",
        passwordsDoNotMatch: "Kata sandi tidak cocok",
        networkError: "Kesalahan jaringan. Periksa koneksi Anda.",
        unauthorized: "Anda tidak berwenang untuk melakukan tindakan ini.",
        notFound: "Sumber daya yang diminta tidak ditemukan.",
      },
      common: {
        loading: "Memuat...",
        noData: "Tidak ada data tersedia",
        success: "Berhasil!",
        failed: "Gagal",
        welcome: "Selamat datang",
        goodbye: "Selamat tinggal",
        yes: "Ya",
        no: "Tidak",
        ok: "OK",
        search: "Cari",
        filter: "Filter",
        sort: "Urutkan",
        view: "Lihat",
        copy: "Salin",
        paste: "Tempel",
        cut: "Potong",
      },
      review: {
        pageTitle: "Tinjau Dokumen",
        pageDescription: "Tinjau dokumen berdasarkan daftar periksa yang ditentukan pengguna dan database kebijakan.",
        knowledgeBaseTitle: "Basis Pengetahuan",
        knowledgeBaseDescription: "Klik untuk memilih",
        checklistTitle: "Daftar Periksa",
        checklistDescription: "Klik untuk memilih",
        customInstructionsTitle: "Instruksi Kustom (Opsional)",
        customInstructionsPlaceholder: "Masukkan instruksi tambahan yang perlu dipertimbangkan saat menjawab pertanyaan daftar periksa...",
        customInstructionsHelp: "{count}/2000 karakter. Instruksi ini akan ditambahkan ke setiap pertanyaan selama pemrosesan.",
        searchModeHelp: "Pencarian vektor memberikan hasil yang cepat dan terarah. Analisis dokumen penuh memeriksa semua konten basis pengetahuan.",
        processingFile: "Memproses file...",
        processingFiles: "Memproses file...",
        selectKnowledgeBaseTitle: "Pilih Basis Pengetahuan",
        selectChecklistTitle: "Pilih Daftar Periksa",
        noResults: "Belum ada hasil",
        uploadDocuments: "Unggah satu atau lebih dokumen untuk ditinjau terhadap daftar periksa yang dipilih",
        results: "Hasil",
        downloadReport: "Unduh Laporan",
        downloadCsv: "Unduh CSV",
        clearResults: "Hapus Hasil",
        copyReport: "Salin Laporan",
        reportCopied: "Laporan disalin ke clipboard!",
        reviewButton: "Tinjau",
        consultDocuments: "Konsultasi Dokumen",
        noChecklistsAvailable: "Tidak ada daftar periksa yang tersedia. Buat daftar periksa pertama Anda untuk memulai.",
        createChecklist: "Buat Daftar Periksa",
        editChecklist: "Edit Daftar Periksa",
        checklistName: "Nama Daftar Periksa",
        checklistNamePlaceholder: "Masukkan nama daftar periksa...",
        checklistDescriptionLabel: "Deskripsi",
        checklistDescriptionPlaceholder: "Masukkan deskripsi daftar periksa untuk saran pertanyaan otomatis (minimal 10 karakter)...",
        questions: "Pertanyaan",
        suggest: "Sarankan",
        suggesting: "Menyarankan...",
        optimize: "Optimalkan",
        optimizeTooltip: "Basis pengetahuan harus dipilih untuk mengaktifkan fitur optimisasi",
        optimizeTooltipEnabled: "Optimalkan pertanyaan berdasarkan basis pengetahuan yang dipilih",
        uploadFiles: "Unggah File",
        knowledgeBase: "Basis Pengetahuan",
        referenceDocuments: "Dokumen Referensi (Opsional)",
        selectKnowledgeBasePlaceholder: "Pilih basis pengetahuan...",
        noKnowledgeBasesAvailable: "Tidak ada basis pengetahuan yang tersedia. Buat satu terlebih dahulu untuk menggunakan fitur ini.",
        copyQuestions: "Salin Pertanyaan",
        questionsCopied: "Pertanyaan disalin ke clipboard",
        noQuestionsToCopy: "Tidak ada pertanyaan untuk disalin",
        failedToCopyQuestions: "Gagal menyalin pertanyaan ke clipboard",
        saveChecklist: "Simpan Daftar Periksa",
        cancel: "Batal",
        deleteChecklist: "Hapus Daftar Periksa"
      },
    },
  }

  // Malay
  resources.ms = {
    common: {
      navigation: {
        dashboard: "Papan Pemuka",
        review: "Semakan",
        generate: "Jana",
        compare: "Bandingkan",
        match: "Padankan",
        modelSelection: "Pemilihan Model",
        knowledgeBases: "Pangkalan Pengetahuan",
        archive: "Arkib",
        settings: "Tetapan",
        admin: "Pentadbir",
        menu: "Menu",
        tools: "Alatan",
        configurations: "Konfigurasi",
        myProfile: "Profil Saya",
        logout: "Log Keluar",
        loggedInAs: "Log masuk sebagai: {{email}}",
      },
      buttons: {
        upload: "Muat Naik",
        download: "Muat Turun",
        save: "Simpan",
        cancel: "Batal",
        delete: "Padam",
        edit: "Edit",
        submit: "Hantar",
        close: "Tutup",
        next: "Seterusnya",
        previous: "Sebelumnya",
        confirm: "Sahkan",
        back: "Kembali",
      },
      forms: {
        firstName: "Nama Pertama",
        lastName: "Nama Keluarga",
        email: "E-mel",
        password: "Kata Laluan",
        confirmPassword: "Sahkan Kata Laluan",
        currentPassword: "Kata Laluan Semasa",
        newPassword: "Kata Laluan Baru",
        required: "Wajib",
        optional: "Pilihan",
        emailPlaceholder: "Masukkan alamat e-mel anda",
        passwordPlaceholder: "Masukkan kata laluan anda",
      },
      chatbot: {
        placeholder: "Taip mesej anda di sini...",
        send: "Hantar",
        newChat: "Sembang Baru",
        clearHistory: "Padam Sejarah",
        typing: "AI sedang menaip...",
        error: "Maaf, ada yang tidak kena. Sila cuba lagi.",
        welcome: "Hai! Bagaimana saya boleh membantu anda hari ini?",
      },
      settings: {
        title: "Tetapan",
        account: "Akaun",
        language: "Bahasa",
        dangerZone: "Zon Bahaya",
        preferredLanguage: "Bahasa Pilihan",
        saveLanguagePreference: "Simpan Pilihan Bahasa",
        deleteAccount: "Padam Akaun",
        deleteAccountWarning: "Tindakan ini tidak boleh dibatalkan.",
        profile: "Profil",
        security: "Keselamatan",
        changePassword: "Tukar Kata Laluan",
        appearance: "Penampilan",
      },
      errors: {
        somethingWentWrong: "Ada yang tidak kena",
        tryAgain: "Sila cuba lagi",
        invalidEmail: "Alamat e-mel tidak sah",
        passwordTooShort: "Kata laluan terlalu pendek",
        passwordsDoNotMatch: "Kata laluan tidak sepadan",
        networkError: "Ralat rangkaian. Semak sambungan anda.",
        unauthorized: "Anda tidak diberi kuasa untuk tindakan ini.",
        notFound: "Sumber yang diminta tidak dijumpai.",
      },
      common: {
        loading: "Memuatkan...",
        noData: "Tiada data tersedia",
        success: "Berjaya!",
        failed: "Gagal",
        welcome: "Selamat datang",
        goodbye: "Selamat tinggal",
        yes: "Ya",
        no: "Tidak",
        ok: "OK",
        search: "Cari",
        filter: "Penapis",
        sort: "Susun",
        view: "Lihat",
        copy: "Salin",
        paste: "Tampal",
        cut: "Potong",
      },
      review: {
        pageTitle: "Semak Dokumen",
        pageDescription: "Semak dokumen berdasarkan senarai semak yang ditentukan pengguna dan pangkalan data dasar.",
        knowledgeBaseTitle: "Pangkalan Pengetahuan",
        knowledgeBaseDescription: "Klik untuk memilih",
        checklistTitle: "Senarai Semak",
        checklistDescription: "Klik untuk memilih",
        customInstructionsTitle: "Arahan Khas (Pilihan)",
        customInstructionsPlaceholder: "Masukkan arahan tambahan yang perlu dipertimbangkan semasa menjawab soalan senarai semak...",
        customInstructionsHelp: "{count}/2000 aksara. Arahan ini akan ditambah kepada setiap soalan semasa pemprosesan.",
        searchModeHelp: "Carian vektor memberikan hasil yang pantas dan terarah. Analisis dokumen penuh memeriksa semua kandungan pangkalan pengetahuan.",
        processingFile: "Memproses fail...",
        processingFiles: "Memproses fail...",
        selectKnowledgeBaseTitle: "Pilih Pangkalan Pengetahuan",
        selectChecklistTitle: "Pilih Senarai Semak",
        noResults: "Belum ada keputusan",
        uploadDocuments: "Muat naik satu atau lebih dokumen untuk disemak terhadap senarai semak yang dipilih",
        results: "Keputusan",
        downloadReport: "Muat Turun Laporan",
        downloadCsv: "Muat Turun CSV",
        clearResults: "Kosongkan Keputusan",
        copyReport: "Salin Laporan",
        reportCopied: "Laporan disalin ke papan keratan!",
        reviewButton: "Semak",
        consultDocuments: "Rujuk Dokumen",
        noChecklistsAvailable: "Tiada senarai semak tersedia. Cipta senarai semak pertama anda untuk bermula.",
        createChecklist: "Cipta Senarai Semak",
        editChecklist: "Edit Senarai Semak",
        checklistName: "Nama Senarai Semak",
        checklistNamePlaceholder: "Masukkan nama senarai semak...",
        checklistDescriptionLabel: "Penerangan",
        checklistDescriptionPlaceholder: "Masukkan penerangan senarai semak untuk cadangan soalan automatik (sekurang-kurangnya 10 aksara)...",
        questions: "Soalan",
        suggest: "Cadangkan",
        suggesting: "Mencadangkan...",
        optimize: "Optimumkan",
        optimizeTooltip: "Pangkalan pengetahuan mesti dipilih untuk membolehkan ciri pengoptimuman",
        optimizeTooltipEnabled: "Optimumkan soalan berdasarkan pangkalan pengetahuan yang dipilih",
        uploadFiles: "Muat Naik Fail",
        knowledgeBase: "Pangkalan Pengetahuan",
        referenceDocuments: "Dokumen Rujukan (Pilihan)",
        selectKnowledgeBasePlaceholder: "Pilih pangkalan pengetahuan...",
        noKnowledgeBasesAvailable: "Tiada pangkalan pengetahuan tersedia. Cipta satu dahulu untuk menggunakan ciri ini.",
        copyQuestions: "Salin Soalan",
        questionsCopied: "Soalan disalin ke papan keratan",
        noQuestionsToCopy: "Tiada soalan untuk disalin",
        failedToCopyQuestions: "Gagal menyalin soalan ke papan keratan",
        saveChecklist: "Simpan Senarai Semak",
        cancel: "Batal",
        deleteChecklist: "Padam Senarai Semak"
      },
    },
  }

  // Filipino (Tagalog)
  resources.tl = {
    common: {
      navigation: {
        dashboard: "Dashboard",
        review: "Pagsusuri",
        generate: "Likhain",
        compare: "Ikumpara",
        match: "Tumugma",
        modelSelection: "Pagpili ng Modelo",
        knowledgeBases: "Mga Base ng Kaalaman",
        archive: "Archive",
        settings: "Mga Setting",
        admin: "Admin",
        menu: "Menu",
        tools: "Mga Kasangkapan",
        configurations: "Mga Konpigurasyon",
        myProfile: "Aking Profile",
        logout: "Mag-logout",
        loggedInAs: "Naka-login bilang: {{email}}",
      },
      buttons: {
        upload: "I-upload",
        download: "I-download",
        save: "I-save",
        cancel: "Kanselahin",
        delete: "Tanggalin",
        edit: "I-edit",
        submit: "Ipasa",
        close: "Isara",
        next: "Susunod",
        previous: "Nakaraan",
        confirm: "Kumpirmahin",
        back: "Bumalik",
      },
      forms: {
        firstName: "Unang Pangalan",
        lastName: "Huling Pangalan",
        email: "Email",
        password: "Password",
        confirmPassword: "Kumpirmahin ang Password",
        currentPassword: "Kasalukuyang Password",
        newPassword: "Bagong Password",
        required: "Kinakailangan",
        optional: "Opsyonal",
        emailPlaceholder: "Ilagay ang inyong email address",
        passwordPlaceholder: "Ilagay ang inyong password",
      },
      chatbot: {
        placeholder: "Mag-type ng inyong mensahe dito...",
        send: "Ipadala",
        newChat: "Bagong Chat",
        clearHistory: "Tanggalin ang Kasaysayan",
        typing: "Nag-ta-type ang AI...",
        error: "Pasensya na, may nangyaring mali. Subukan muli.",
        welcome: "Kumusta! Paano kita matutulungan ngayon?",
      },
      settings: {
        title: "Mga Setting",
        account: "Account",
        language: "Wika",
        dangerZone: "Delikadong Lugar",
        preferredLanguage: "Ginustong Wika",
        saveLanguagePreference: "I-save ang Preference sa Wika",
        deleteAccount: "Tanggalin ang Account",
        deleteAccountWarning: "Hindi na mababawi ang aksyong ito.",
        profile: "Profile",
        security: "Seguridad",
        changePassword: "Baguhin ang Password",
        appearance: "Hitsura",
      },
      errors: {
        somethingWentWrong: "May nangyaring mali",
        tryAgain: "Subukan muli",
        invalidEmail: "Hindi wastong email address",
        passwordTooShort: "Masyadong maikli ang password",
        passwordsDoNotMatch: "Hindi nagtugma ang mga password",
        networkError: "Error sa network. Suriin ang inyong koneksyon.",
        unauthorized: "Walang pahintulot para sa aksyong ito.",
        notFound: "Hindi natagpuan ang hiniling na resource.",
      },
      common: {
        loading: "Naglo-load...",
        noData: "Walang available na data",
        success: "Tagumpay!",
        failed: "Nabigo",
        welcome: "Maligayang pagdating",
        goodbye: "Paalam",
        yes: "Oo",
        no: "Hindi",
        ok: "OK",
        search: "Maghanap",
        filter: "Filter",
        sort: "Ayusin",
        view: "Tingnan",
        copy: "Kopyahin",
        paste: "I-paste",
        cut: "Putulin",
      },
      review: {
        pageTitle: "Pagsusuri ng mga Dokumento",
        pageDescription: "Suriin ang dokumento batay sa checklist na tinukoy ng user at database ng patakaran.",
        knowledgeBaseTitle: "Base ng Kaalaman",
        knowledgeBaseDescription: "I-click para pumili",
        checklistTitle: "Checklist",
        checklistDescription: "I-click para pumili",
        customInstructionsTitle: "Custom na mga Tagubilin (Opsyonal)",
        customInstructionsPlaceholder: "Maglagay ng karagdagang mga tagubilin na dapat isaalang-alang sa pagsagot sa mga tanong sa checklist...",
        customInstructionsHelp: "{count}/2000 character. Ang mga tagubiling ito ay idadagdag sa bawat tanong sa panahon ng pagproseso.",
        searchModeHelp: "Ang vector search ay nagbibigay ng mabilis, nakatuon na mga resulta. Ang buong pagsusuri ng dokumento ay sinusuri ang lahat ng nilalaman ng base ng kaalaman.",
        processingFile: "Pinoproseso ang file...",
        processingFiles: "Pinoproseso ang mga file...",
        selectKnowledgeBaseTitle: "Pumili ng Base ng Kaalaman",
        selectChecklistTitle: "Pumili ng Checklist",
        noResults: "Wala pang mga resulta",
        uploadDocuments: "Mag-upload ng isa o higit pang mga dokumento para sa pagsusuri laban sa napiling checklist",
        results: "Mga Resulta",
        downloadReport: "I-download ang Ulat",
        downloadCsv: "I-download ang CSV",
        clearResults: "I-clear ang mga Resulta",
        copyReport: "Kopyahin ang Ulat",
        reportCopied: "Nakopya na ang ulat sa clipboard!",
        reviewButton: "Pagsusuri",
        consultDocuments: "Kumunsulta sa mga Dokumento",
        noChecklistsAvailable: "Walang available na mga checklist. Lumikha ng inyong unang checklist para magsimula.",
        createChecklist: "Lumikha ng Checklist",
        editChecklist: "I-edit ang Checklist",
        checklistName: "Pangalan ng Checklist",
        checklistNamePlaceholder: "Ilagay ang pangalan ng checklist...",
        checklistDescriptionLabel: "Paglalarawan",
        checklistDescriptionPlaceholder: "Ilagay ang paglalarawan ng checklist para sa awtomatikong mga mungkahi ng tanong (hindi kukulangin sa 10 character)...",
        questions: "Mga Tanong",
        suggest: "Magmungkahi",
        suggesting: "Nagmumungkahi...",
        optimize: "I-optimize",
        optimizeTooltip: "Dapat piliin ang base ng kaalaman para ma-enable ang optimize feature",
        optimizeTooltipEnabled: "I-optimize ang mga tanong batay sa napiling base ng kaalaman",
        uploadFiles: "Mag-upload ng mga File",
        knowledgeBase: "Base ng Kaalaman",
        referenceDocuments: "Mga Reference Document (Opsyonal)",
        selectKnowledgeBasePlaceholder: "Pumili ng base ng kaalaman...",
        noKnowledgeBasesAvailable: "Walang available na mga base ng kaalaman. Lumikha muna ng isa para magamit ang feature na ito.",
        copyQuestions: "Kopyahin ang mga Tanong",
        questionsCopied: "Nakopya na ang mga tanong sa clipboard",
        noQuestionsToCopy: "Walang mga tanong na kokopyahin",
        failedToCopyQuestions: "Nabigo sa pagkopya ng mga tanong sa clipboard",
        saveChecklist: "I-save ang Checklist",
        cancel: "Kanselahin",
        deleteChecklist: "Tanggalin ang Checklist"
      },
    },
  }

  // Add Model Selection translations to Chinese Traditional
  resources['zh-TW'].common.modelSelection = {
    llmManagement: "LLM 管理",
    llmDescription: "配置和管理用於生成文本回應的LLM。預設模型將用於所有操作。",
    addNewLlm: "新增LLM",
    noLlmsConfigured: "沒有配置LLM",
    addNewLlmToGetStarted: "新增LLM開始使用",
    embeddingModelManagement: "嵌入模型管理",
    embeddingDescription: "配置和管理用於知識庫索引和檢索的嵌入模型。預設模型將在創建新知識庫時使用，但每個知識庫將繼續使用其原始嵌入模型，即使預設值之後發生變化。",
    addEmbeddingModel: "新增嵌入模型",
    noEmbeddingModelsConfigured: "沒有配置嵌入模型",
    addNewEmbeddingModelToGetStarted: "新增嵌入模型開始使用",
    tableHeaders: {
      name: "名稱",
      modelId: "模型ID",
      provider: "提供者",
      description: "說明",
      status: "狀態",
      actions: "操作"
    },
    status: {
      default: "預設",
      available: "可用"
    },
    actions: {
      setAsDefault: "設為預設",
      delete: "刪除",
      validate: "驗證",
      validating: "驗證中"
    },
    dialog: {
      addNewLlm: "新增LLM",
      addEmbeddingModel: "新增嵌入模型",
      displayName: "顯示名稱",
      provider: "提供者",
      modelId: "模型ID",
      description: "說明",
      cancel: "取消",
      addModel: "新增模型"
    },
    placeholders: {
      customModel: "例如：我的自定義模型",
      embeddingModelId: "例如：sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "描述模型、其特性以及何時使用它"
    },
    validation: {
      pleaseEnterModelId: "請輸入模型ID"
    }
  }

  // Add Model Selection translations to Thai
  resources.th.common.modelSelection = {
    llmManagement: "การจัดการ LLM",
    llmDescription: "กำหนดค่าและจัดการ LLM ที่ใช้สำหรับสร้างการตอบสนองข้อความ โมเดลเริ่มต้นจะถูกใช้สำหรับการดำเนินการทั้งหมด",
    addNewLlm: "เพิ่ม LLM ใหม่",
    noLlmsConfigured: "ไม่มี LLM ที่กำหนดค่า",
    addNewLlmToGetStarted: "เพิ่ม LLM ใหม่เพื่อเริ่มต้น",
    embeddingModelManagement: "การจัดการโมเดลฝัง",
    embeddingDescription: "กำหนดค่าและจัดการโมเดลฝังที่ใช้สำหรับการสร้างดัชนีและการดึงข้อมูลฐานความรู้ โมเดลเริ่มต้นจะถูกใช้เมื่อสร้างฐานความรู้ใหม่ แต่ฐานความรู้แต่ละแห่งจะยังคงใช้โมเดลฝังเดิมต่อไป แม้ว่าค่าเริ่มต้นจะเปลี่ยนภายหลัง",
    addEmbeddingModel: "เพิ่มโมเดลฝัง",
    noEmbeddingModelsConfigured: "ไม่มีโมเดลฝังที่กำหนดค่า",
    addNewEmbeddingModelToGetStarted: "เพิ่มโมเดลฝังใหม่เพื่อเริ่มต้น",
    tableHeaders: {
      name: "ชื่อ",
      modelId: "ID โมเดล",
      provider: "ผู้ให้บริการ",
      description: "คำอธิบาย",
      status: "สถานะ",
      actions: "การดำเนินการ"
    },
    status: {
      default: "เริ่มต้น",
      available: "พร้อมใช้งาน"
    },
    actions: {
      setAsDefault: "ตั้งเป็นค่าเริ่มต้น",
      delete: "ลบ",
      validate: "ตรวจสอบ",
      validating: "กำลังตรวจสอบ"
    },
    dialog: {
      addNewLlm: "เพิ่ม LLM ใหม่",
      addEmbeddingModel: "เพิ่มโมเดลฝัง",
      displayName: "ชื่อที่แสดง",
      provider: "ผู้ให้บริการ",
      modelId: "ID โมเดล",
      description: "คำอธิบาย",
      cancel: "ยกเลิก",
      addModel: "เพิ่มโมเดล"
    },
    placeholders: {
      customModel: "เช่น โมเดลที่กำหนดเองของฉัน",
      embeddingModelId: "เช่น sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "อธิบายโมเดล ลักษณะเฉพาะ และเมื่อใดควรใช้"
    },
    validation: {
      pleaseEnterModelId: "โปรดป้อน ID โมเดล"
    }
  }

  // Add Model Selection translations to Vietnamese
  resources.vi.common.modelSelection = {
    llmManagement: "Quản lý LLM",
    llmDescription: "Cấu hình và quản lý các LLM được sử dụng để tạo phản hồi văn bản. Mô hình mặc định sẽ được sử dụng cho tất cả các hoạt động.",
    addNewLlm: "Thêm LLM mới",
    noLlmsConfigured: "Không có LLM nào được cấu hình",
    addNewLlmToGetStarted: "Thêm LLM mới để bắt đầu",
    embeddingModelManagement: "Quản lý mô hình nhúng",
    embeddingDescription: "Cấu hình và quản lý các mô hình nhúng được sử dụng để lập chỉ mục và truy xuất cơ sở tri thức. Mô hình mặc định sẽ được sử dụng khi tạo cơ sở tri thức mới, nhưng mỗi cơ sở tri thức sẽ tiếp tục sử dụng mô hình nhúng gốc của nó ngay cả khi mặc định thay đổi sau này.",
    addEmbeddingModel: "Thêm mô hình nhúng",
    noEmbeddingModelsConfigured: "Không có mô hình nhúng nào được cấu hình",
    addNewEmbeddingModelToGetStarted: "Thêm mô hình nhúng mới để bắt đầu",
    tableHeaders: {
      name: "Tên",
      modelId: "ID Mô hình",
      provider: "Nhà cung cấp",
      description: "Mô tả",
      status: "Trạng thái",
      actions: "Hành động"
    },
    status: {
      default: "Mặc định",
      available: "Có sẵn"
    },
    actions: {
      setAsDefault: "Đặt làm mặc định",
      delete: "Xóa",
      validate: "Xác thực",
      validating: "Đang xác thực"
    },
    dialog: {
      addNewLlm: "Thêm LLM mới",
      addEmbeddingModel: "Thêm mô hình nhúng",
      displayName: "Tên hiển thị",
      provider: "Nhà cung cấp",
      modelId: "ID Mô hình",
      description: "Mô tả",
      cancel: "Hủy",
      addModel: "Thêm mô hình"
    },
    placeholders: {
      customModel: "ví dụ: Mô hình tùy chỉnh của tôi",
      embeddingModelId: "ví dụ: sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Mô tả mô hình, đặc điểm của nó và khi nào sử dụng nó"
    },
    validation: {
      pleaseEnterModelId: "Vui lòng nhập ID mô hình"
    }
  }

  // Add Model Selection translations to Indonesian
  resources.id.common.modelSelection = {
    llmManagement: "Manajemen LLM",
    llmDescription: "Konfigurasi dan kelola LLM yang digunakan untuk menghasilkan respons teks. Model default akan digunakan untuk semua operasi.",
    addNewLlm: "Tambah LLM Baru",
    noLlmsConfigured: "Tidak ada LLM yang dikonfigurasi",
    addNewLlmToGetStarted: "Tambahkan LLM baru untuk memulai",
    embeddingModelManagement: "Manajemen Model Embedding",
    embeddingDescription: "Konfigurasi dan kelola model embedding yang digunakan untuk pengindeksan dan pengambilan basis pengetahuan. Model default akan digunakan saat membuat basis pengetahuan baru, tetapi setiap basis pengetahuan akan terus menggunakan model embedding aslinya meskipun default berubah nanti.",
    addEmbeddingModel: "Tambah Model Embedding",
    noEmbeddingModelsConfigured: "Tidak ada model embedding yang dikonfigurasi",
    addNewEmbeddingModelToGetStarted: "Tambahkan model embedding baru untuk memulai",
    tableHeaders: {
      name: "Nama",
      modelId: "ID Model",
      provider: "Penyedia",
      description: "Deskripsi",
      status: "Status",
      actions: "Aksi"
    },
    status: {
      default: "Default",
      available: "Tersedia"
    },
    actions: {
      setAsDefault: "Atur sebagai Default",
      delete: "Hapus",
      validate: "Validasi",
      validating: "Memvalidasi"
    },
    dialog: {
      addNewLlm: "Tambah LLM Baru",
      addEmbeddingModel: "Tambah Model Embedding",
      displayName: "Nama Tampilan",
      provider: "Penyedia",
      modelId: "ID Model",
      description: "Deskripsi",
      cancel: "Batal",
      addModel: "Tambah Model"
    },
    placeholders: {
      customModel: "misal, Model Kustom Saya",
      embeddingModelId: "misal, sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Jelaskan model, karakteristiknya, dan kapan menggunakannya"
    },
    validation: {
      pleaseEnterModelId: "Silakan masukkan ID model"
    }
  }

  // Add Model Selection translations to Malay
  resources.ms.common.modelSelection = {
    llmManagement: "Pengurusan LLM",
    llmDescription: "Konfigurasikan dan urus LLM yang digunakan untuk menjana respons teks. Model lalai akan digunakan untuk semua operasi.",
    addNewLlm: "Tambah LLM Baru",
    noLlmsConfigured: "Tiada LLM dikonfigurasikan",
    addNewLlmToGetStarted: "Tambahkan LLM baru untuk bermula",
    embeddingModelManagement: "Pengurusan Model Embedding",
    embeddingDescription: "Konfigurasikan dan urus model embedding yang digunakan untuk pengindeksan dan perolehan pangkalan pengetahuan. Model lalai akan digunakan semasa mencipta pangkalan pengetahuan baru, tetapi setiap pangkalan pengetahuan akan terus menggunakan model embedding asalnya walaupun lalai berubah kemudian.",
    addEmbeddingModel: "Tambah Model Embedding",
    noEmbeddingModelsConfigured: "Tiada model embedding dikonfigurasikan",
    addNewEmbeddingModelToGetStarted: "Tambahkan model embedding baru untuk bermula",
    tableHeaders: {
      name: "Nama",
      modelId: "ID Model",
      provider: "Penyedia",
      description: "Penerangan",
      status: "Status",
      actions: "Tindakan"
    },
    status: {
      default: "Lalai",
      available: "Tersedia"
    },
    actions: {
      setAsDefault: "Tetapkan sebagai Lalai",
      delete: "Padam",
      validate: "Sahkan",
      validating: "Mengesahkan"
    },
    dialog: {
      addNewLlm: "Tambah LLM Baru",
      addEmbeddingModel: "Tambah Model Embedding",
      displayName: "Nama Paparan",
      provider: "Penyedia",
      modelId: "ID Model",
      description: "Penerangan",
      cancel: "Batal",
      addModel: "Tambah Model"
    },
    placeholders: {
      customModel: "cth., Model Tersuai Saya",
      embeddingModelId: "cth., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Terangkan model, ciri-cirinya, dan bila menggunakannya"
    },
    validation: {
      pleaseEnterModelId: "Sila masukkan ID model"
    }
  }

  // Add Model Selection translations to Filipino/Tagalog
  resources.tl.common.modelSelection = {
    llmManagement: "Pamamahala ng LLM",
    llmDescription: "I-configure at pamahalaan ang mga LLM na ginagamit para sa paglikha ng mga text response. Ang default na model ay gagamitin para sa lahat ng mga operasyon.",
    addNewLlm: "Magdagdag ng Bagong LLM",
    noLlmsConfigured: "Walang naka-configure na LLM",
    addNewLlmToGetStarted: "Magdagdag ng bagong LLM para magsimula",
    embeddingModelManagement: "Pamamahala ng Embedding Model",
    embeddingDescription: "I-configure at pamahalaan ang mga embedding model na ginagamit para sa pag-index at pagkuha ng knowledge base. Ang default na model ay gagamitin kapag lumilikha ng mga bagong knowledge base, ngunit ang bawat knowledge base ay patuloy na gagamitin ang kanyang orihinal na embedding model kahit na mag-iba ang default sa hinaharap.",
    addEmbeddingModel: "Magdagdag ng Embedding Model",
    noEmbeddingModelsConfigured: "Walang naka-configure na embedding model",
    addNewEmbeddingModelToGetStarted: "Magdagdag ng bagong embedding model para magsimula",
    tableHeaders: {
      name: "Pangalan",
      modelId: "Model ID",
      provider: "Provider",
      description: "Paglalarawan",
      status: "Status",
      actions: "Mga Aksyon"
    },
    status: {
      default: "Default",
      available: "Available"
    },
    actions: {
      setAsDefault: "Itakda bilang Default",
      delete: "Tanggalin",
      validate: "I-validate",
      validating: "Nag-va-validate"
    },
    dialog: {
      addNewLlm: "Magdagdag ng Bagong LLM",
      addEmbeddingModel: "Magdagdag ng Embedding Model",
      displayName: "Display Name",
      provider: "Provider",
      modelId: "Model ID",
      description: "Paglalarawan",
      cancel: "Kanselahin",
      addModel: "Magdagdag ng Model"
    },
    placeholders: {
      customModel: "hal., Aking Custom Model",
      embeddingModelId: "hal., sentence-transformers/all-MiniLM-L6-v2",
      describeModel: "Ilarawan ang model, mga katangian nito, at kailan ito gagamitin"
    },
    validation: {
      pleaseEnterModelId: "Pakilagay ang model ID"
    }
  }

  // Add Knowledge Bases translations for Asian languages
  
  // Chinese Traditional
  if (!resources["zh-TW"].common.knowledgeBases) {
    resources["zh-TW"].common.knowledgeBases = {
      title: "知識庫",
      description: "管理和組織您的文件到知識庫中，以實現高效的AI輔助互動。",
      createNew: "建立新知識庫",
      noKnowledgeBases: "尚未建立任何知識庫",
      getStarted: "建立您的第一個知識庫以開始使用",
      tableHeaders: {
        name: "名稱",
        description: "描述",
        documents: "文件",
        createdAt: "建立時間",
        actions: "操作"
      },
      actions: {
        view: "查看",
        edit: "編輯",
        delete: "刪除",
        configure: "配置"
      },
      dialog: {
        createNew: "建立新知識庫",
        editKnowledgeBase: "編輯知識庫",
        name: "名稱",
        description: "描述",
        cancel: "取消",
        create: "建立",
        save: "儲存"
      },
      placeholders: {
        knowledgeBaseName: "例如：公司政策",
        knowledgeBaseDescription: "描述此知識庫包含的內容及其目的"
      },
      validation: {
        pleaseEnterName: "請輸入知識庫名稱"
      }
    }
  }

  // Thai
  if (!resources.th.common.knowledgeBases) {
    resources.th.common.knowledgeBases = {
      title: "ฐานความรู้",
      description: "จัดการและจัดระเบียบเอกสารของคุณในฐานความรู้เพื่อการโต้ตอบที่มีประสิทธิภาพด้วย AI",
      createNew: "สร้างฐานความรู้ใหม่",
      noKnowledgeBases: "ยังไม่มีฐานความรู้ที่สร้างขึ้น",
      getStarted: "สร้างฐานความรู้แรกของคุณเพื่อเริ่มต้น",
      tableHeaders: {
        name: "ชื่อ",
        description: "คำอธิบาย",
        documents: "เอกสาร",
        createdAt: "สร้างเมื่อ",
        actions: "การดำเนินการ"
      },
      actions: {
        view: "ดู",
        edit: "แก้ไข",
        delete: "ลบ",
        configure: "กำหนดค่า"
      },
      dialog: {
        createNew: "สร้างฐานความรู้ใหม่",
        editKnowledgeBase: "แก้ไขฐานความรู้",
        name: "ชื่อ",
        description: "คำอธิบาย",
        cancel: "ยกเลิก",
        create: "สร้าง",
        save: "บันทึก"
      },
      placeholders: {
        knowledgeBaseName: "เช่น นโยบายบริษัท",
        knowledgeBaseDescription: "อธิบายสิ่งที่ฐานความรู้นี้มีและวัตถุประสงค์"
      },
      validation: {
        pleaseEnterName: "กรุณาป้อนชื่อสำหรับฐานความรู้"
      }
    }
  }

  // Vietnamese
  if (!resources.vi.common.knowledgeBases) {
    resources.vi.common.knowledgeBases = {
      title: "Cơ sở tri thức",
      description: "Quản lý và tổ chức tài liệu của bạn trong các cơ sở tri thức để tương tác hiệu quả được hỗ trợ bởi AI.",
      createNew: "Tạo cơ sở tri thức mới",
      noKnowledgeBases: "Chưa có cơ sở tri thức nào được tạo",
      getStarted: "Tạo cơ sở tri thức đầu tiên của bạn để bắt đầu",
      tableHeaders: {
        name: "Tên",
        description: "Mô tả",
        documents: "Tài liệu",
        createdAt: "Được tạo",
        actions: "Hành động"
      },
      actions: {
        view: "Xem",
        edit: "Chỉnh sửa",
        delete: "Xóa",
        configure: "Cấu hình"
      },
      dialog: {
        createNew: "Tạo cơ sở tri thức mới",
        editKnowledgeBase: "Chỉnh sửa cơ sở tri thức",
        name: "Tên",
        description: "Mô tả",
        cancel: "Hủy",
        create: "Tạo",
        save: "Lưu"
      },
      placeholders: {
        knowledgeBaseName: "ví dụ: Chính sách công ty",
        knowledgeBaseDescription: "Mô tả nội dung của cơ sở tri thức này và mục đích của nó"
      },
      validation: {
        pleaseEnterName: "Vui lòng nhập tên cho cơ sở tri thức"
      }
    }
  }

  // Indonesian
  if (!resources.id.common.knowledgeBases) {
    resources.id.common.knowledgeBases = {
      title: "Basis Pengetahuan",
      description: "Kelola dan atur dokumen Anda dalam basis pengetahuan untuk interaksi yang efisien dengan dukungan AI.",
      createNew: "Buat basis pengetahuan baru",
      noKnowledgeBases: "Belum ada basis pengetahuan yang dibuat",
      getStarted: "Buat basis pengetahuan pertama Anda untuk memulai",
      tableHeaders: {
        name: "Nama",
        description: "Deskripsi",
        documents: "Dokumen",
        createdAt: "Dibuat",
        actions: "Tindakan"
      },
      actions: {
        view: "Lihat",
        edit: "Edit",
        delete: "Hapus",
        configure: "Konfigurasi"
      },
      dialog: {
        createNew: "Buat basis pengetahuan baru",
        editKnowledgeBase: "Edit basis pengetahuan",
        name: "Nama",
        description: "Deskripsi",
        cancel: "Batal",
        create: "Buat",
        save: "Simpan"
      },
      placeholders: {
        knowledgeBaseName: "mis., Kebijakan Perusahaan",
        knowledgeBaseDescription: "Jelaskan apa yang dikandung basis pengetahuan ini dan tujuannya"
      },
      validation: {
        pleaseEnterName: "Harap masukkan nama untuk basis pengetahuan"
      }
    }
  }

  // Malay
  if (!resources.ms.common.knowledgeBases) {
    resources.ms.common.knowledgeBases = {
      title: "Pangkalan Pengetahuan",
      description: "Urus dan atur dokumen anda dalam pangkalan pengetahuan untuk interaksi berkesan yang disokong AI.",
      createNew: "Cipta pangkalan pengetahuan baharu",
      noKnowledgeBases: "Tiada pangkalan pengetahuan telah dicipta lagi",
      getStarted: "Cipta pangkalan pengetahuan pertama anda untuk bermula",
      tableHeaders: {
        name: "Nama",
        description: "Penerangan",
        documents: "Dokumen",
        createdAt: "Dicipta",
        actions: "Tindakan"
      },
      actions: {
        view: "Lihat",
        edit: "Edit",
        delete: "Padam",
        configure: "Konfigur"
      },
      dialog: {
        createNew: "Cipta pangkalan pengetahuan baharu",
        editKnowledgeBase: "Edit pangkalan pengetahuan",
        name: "Nama",
        description: "Penerangan",
        cancel: "Batal",
        create: "Cipta",
        save: "Simpan"
      },
      placeholders: {
        knowledgeBaseName: "cth., Dasar Syarikat",
        knowledgeBaseDescription: "Terangkan apa yang terkandung dalam pangkalan pengetahuan ini dan tujuannya"
      },
      validation: {
        pleaseEnterName: "Sila masukkan nama untuk pangkalan pengetahuan"
      }
    }
  }

  // Filipino
  if (!resources.tl.common.knowledgeBases) {
    resources.tl.common.knowledgeBases = {
      title: "Mga Base ng Kaalaman",
      description: "Pamahalaan at ayusin ang inyong mga dokumento sa mga base ng kaalaman para sa epektibong pakikipag-ugnayan na suportado ng AI.",
      createNew: "Lumikha ng bagong base ng kaalaman",
      noKnowledgeBases: "Wala pang nalikha na mga base ng kaalaman",
      getStarted: "Lumikha ng inyong unang base ng kaalaman para magsimula",
      tableHeaders: {
        name: "Pangalan",
        description: "Paglalarawan",
        documents: "Mga Dokumento",
        createdAt: "Nalikha",
        actions: "Mga Aksyon"
      },
      actions: {
        view: "Tingnan",
        edit: "I-edit",
        delete: "Tanggalin",
        configure: "I-configure"
      },
      dialog: {
        createNew: "Lumikha ng bagong base ng kaalaman",
        editKnowledgeBase: "I-edit ang base ng kaalaman",
        name: "Pangalan",
        description: "Paglalarawan",
        cancel: "Kanselahin",
        create: "Lumikha",
        save: "I-save"
      },
      placeholders: {
        knowledgeBaseName: "hal., Mga Patakaran ng Kumpanya",
        knowledgeBaseDescription: "Ilarawan kung ano ang nilalaman ng base ng kaalaman na ito at ang layunin nito"
      },
      validation: {
        pleaseEnterName: "Pakilagay ang pangalan para sa base ng kaalaman"
      }
    }
  }
}
