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
        welcomeMessageWithSource: "選擇知識庫或上傳檔案，然後提出問題。",
        welcomeMessageGeneral: "請隨意提問！如需搜尋知識庫，請先選擇知識庫。",
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
        customInstructionsHelp: "{{count}}/2000 字符。這些指示將在處理過程中添加到每個問題中。",
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
        allUsersToggleTooltip: "在僅查看您的歷史記錄或所有用戶的歷史記錄之間切換",
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
      compare: {
        title: "文件比較",
        subtitle: "比較兩個文件，查看它們在用戶定義的主題列表方面的差異。",
        selectFirstDocument: "選擇第一個文件",
        selectSecondDocument: "選擇第二個文件",
        pleaseSelect: "請選擇...",
        documentA: "文件 A",
        documentB: "文件 B",
        compareDocuments: "比較文件",
        comparison: "比較",
        noDocumentsFound: "未找到文件",
        selectTwoDocuments: "請選擇兩個文件進行比較",
        loadingComparison: "正在載入比較...",
        topicList: "主題清單",
        clickToBrowse: "點擊瀏覽或拖放到此處",
        supportedFormats: "支援格式：PDF、TXT、DOCX",
        analysisType: "分析類型",
        quickAnalysis: "快速分析",
        detailedAnalysis: "詳細分析",
        comprehensiveAnalysis: "全面分析",
        analysisDepth: "分析深度",
        surfaceLevel: "表面層次",
        moderate: "中等",
        deep: "深入",
        veryDeep: "非常深入",
        editTopicList: "編輯主題列表"
      },
      match: {
        title: "文件匹配",
        subtitle: "確保字段條目在不同格式的文件之間匹配。",
        selectDocument: "選擇文件以尋找匹配",
        pleaseSelect: "請選擇文件...",
        sourceDocument: "源文件",
        matchingDocuments: "匹配文件",
        findMatches: "尋找匹配",
        similarityScore: "相似度分數",
        noDocumentsFound: "未找到文件",
        selectDocumentToMatch: "請選擇文件以尋找匹配",
        loadingMatches: "正在搜尋匹配...",
        noMatchesFound: "未找到相似文件",
        matchResults: "匹配結果",
        similarity: "相似度",
        matchingCriteria: "匹配條件",
        semanticSimilarity: "語義相似度",
        keywordMatching: "關鍵字匹配",
        structuralSimilarity: "結構相似度",
        threshold: "閾值",
        minimumSimilarity: "最小相似度",
        searchDepth: "搜尋深度",
        maxResults: "最大結果數",
        editFormTemplate: "編輯表單範本"
      },
      knowledgeBases: {
        title: "知識庫管理",
        addKnowledgeBase: "新增知識庫",
        emptyStateTitle: "您還沒有知識庫",
        emptyStateDescription: "新增一個新的知識庫以開始",
        tableHeaders: {
          title: "標題",
          description: "描述",
          numberOfSources: "來源數量",
          embeddingModel: "嵌入模型",
          dateCreated: "建立日期",
          dateModified: "修改日期",
          actions: "動作"
        },
        status: {
          default: "預設",
          na: "不適用"
        },
        actions: {
          view: "檢視",
          edit: "編輯",
          delete: "刪除",
          configure: "設定"
        },
        deleteModal: {
          title: "刪除知識庫",
          buttonText: "刪除知識庫",
          description: "此知識庫將被永久刪除。您確定嗎？您將無法撤銷此操作。",
          confirmButton: "刪除",
          cancelButton: "取消",
          successMessage: "知識庫已成功刪除",
          errorMessage: "刪除知識庫時發生錯誤"
        },
        modals: {
          add: {
            title: "新增知識庫",
            description: "通過提供詳細資訊並在下方上傳文件來建立新的知識庫。",
            fields: {
              title: "標題",
              titlePlaceholder: "標題",
              titleRequired: "標題為必填",
              description: "描述",
              descriptionPlaceholder: "描述",
            },
            fileUpload: {
              dragAndDrop: "將檔案拖放到此處或點擊瀏覽",
              dropFiles: "將檔案拖放到此處...",
              selectedFiles: "已選擇的檔案：",
              removeFile: "移除檔案",
            },
            buttons: {
              cancel: "取消",
              save: "儲存",
              creating: "建立中...",
            },
            validation: {
              atLeastOneFile: "至少需要一個檔案。",
            },
            success: "知識庫已成功建立。",
          },
          edit: {
            title: "編輯知識庫",
            description: "在下方更新知識庫詳細資訊。",
            fields: {
              title: "標題",
              titlePlaceholder: "標題",
              titleRequired: "標題為必填",
              description: "描述",
              descriptionPlaceholder: "描述",
            },
            fileUpload: {
              currentFiles: "目前檔案：",
              dragAndDrop: "將檔案拖放到此處或點擊瀏覽",
              dropFiles: "將檔案拖放到此處...",
              selectedFiles: "已選擇的檔案：",
              removeFile: "移除檔案",
            },
            buttons: {
              cancel: "取消",
              save: "儲存",
              saving: "儲存中...",
            },
            success: "知識庫已成功更新。",
          },
          editFormTemplateModal: {
            title: "編輯表單範本",
            formTemplateName: "表單範本名稱",
            formTemplateDescription: "表單範本描述",
            descriptionPlaceholder: "輸入表單範本描述...",
            referenceDocuments: "參考文件（可選）",
            uploadFiles: "上傳檔案",
            knowledgeBase: "知識庫",
            formFields: "表單欄位",
            suggest: "建議",
            fieldPlaceholder: "新增欄位名稱...",
            cancel: "取消",
            updateFormTemplate: "更新表單範本"
          },
        },
        editCustom: {
          title: "編輯自訂指示",
          currentInstructions: "目前指示：",
          save: "儲存",
          cancel: "取消",
        },
      },
      optimizeChecklistModal: {
        title: "優化檢查清單",
        customInstructionsLabel: "自訂指示（選擇性）",
        customInstructionsHelperText: "輸入在回答檢查清單問題時應考慮的額外指示",
        analyzing: "分析中...",
        analyzeButton: "分析檢查清單",
        analyzingMessage: "正在分析您的檢查清單以尋找優化機會...",
        cancelAnalysis: "取消分析",
        downloading: "下載中...",
        downloadCsv: "下載 CSV",
        questionsNeedingOptimization: "需要優化的問題",
        questionsAlreadyOptimized: "已優化的問題",
        selected: "已選擇",
        select: "選擇",
        original: "原始",
        suggestedImprovement: "建議改進",
        policyContext: "政策背景",
        currentAnswer: "目前答案",
        showLess: "顯示較少",
        showMore: "顯示更多",
        optimizationsSelectedText: "項優化已選擇用於應用",
        applying: "應用中...",
        applySelectedOptimizations: "應用選擇的優化",
        uploadDocumentsTitle: "上傳檢查清單應接受的文件 *",
        uploadDocumentsHelperText: "上傳應符合所有檢查清單要求的文件，以幫助識別可能過於嚴格的問題",
        customInstructionsPlaceholder: "例如，在評估與年齡相關的要求時，考慮這是一項兒科研究，此協議用於低風險干預等。"
      },
      optimizeOutlineModal: {
        title: "優化大綱",
        description: "上傳一個參考文件，代表您想要生成的報告類型的高品質範例。系統將使用您目前的大綱和知識庫生成報告，將其與參考進行比較，並建議大綱部分的改進。",
        groundTruthDocument: "參考文件",
        customInstructionsLabel: "自訂指示（選擇性）",
        customInstructionsHelperText: "為優化過程提供額外指導",
        customInstructionsPlaceholder: "例如，專注於改進技術深度，確保符合特定標準等。",
        characters: "字元",
        analyzingOutline: "正在分析大綱並生成優化...",
        cancelAnalysis: "取消分析",
        optimizationResults: "優化結果",
        sectionsNeedOptimization: "個部分需要優化",
        downloadCsv: "下載 CSV",
        section: "部分",
        accepted: "已接受",
        accept: "接受",
        originalSectionDescription: "原始部分描述",
        suggestedSectionDescription: "建議部分描述",
        generatedContent: "生成的內容（使用目前描述）",
        groundTruthReference: "參考引用",
        showLess: "顯示較少",
        showMore: "顯示更多",
        close: "關閉",
        cancel: "取消",
        optimizing: "優化中...",
        optimizeOutline: "優化大綱",
        applyOptimizations: "應用 {{count}} 項優化"
      }
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
        welcomeMessageWithSource: "เลือกฐานความรู้หรืออัปโหลดไฟล์ แล้วถามคำถาม",
        welcomeMessageGeneral: "ถามฉันอะไรก็ได้! สำหรับการค้นหาในฐานความรู้ ให้เลือกฐานความรู้ก่อน",
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
        customInstructionsHelp: "{{count}}/2000 ตัวอักษร คำแนะนำเหล่านี้จะถูกเพิ่มเข้าไปในทุกคำถามระหว่างการประมวลผล",
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
        allUsersToggleTooltip: "สลับระหว่างการดูเฉพาะประวัติของคุณหรือประวัติของผู้ใช้ทั้งหมด",
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
      compare: {
        title: "เปรียบเทียบเอกสาร",
        subtitle: "เปรียบเทียบเอกสารสองฉบับเพื่อดูความแตกต่างตามรายการหัวข้อที่ผู้ใช้กำหนด",
        selectFirstDocument: "เลือกเอกสารฉบับแรก",
        selectSecondDocument: "เลือกเอกสารฉบับที่สอง",
        pleaseSelect: "กรุณาเลือก...",
        documentA: "เอกสาร A",
        documentB: "เอกสาร B",
        compareDocuments: "เปรียบเทียบเอกสาร",
        comparison: "การเปรียบเทียบ",
        noDocumentsFound: "ไม่พบเอกสาร",
        selectTwoDocuments: "กรุณาเลือกเอกสารสองฉบับเพื่อเปรียบเทียบ",
        loadingComparison: "กำลังโหลดการเปรียบเทียบ...",
        topicList: "รายการหัวข้อ",
        clickToBrowse: "คลิกเพื่อเรียกดูหรือลากมาที่นี่",
        supportedFormats: "รูปแบบที่รองรับ: PDF, TXT, DOCX",
        analysisType: "ประเภทการวิเคราะห์",
        quickAnalysis: "การวิเคราะห์อย่างรวดเร็ว",
        detailedAnalysis: "การวิเคราะห์อย่างละเอียด",
        comprehensiveAnalysis: "การวิเคราะห์อย่างครอบคลุม",
        analysisDepth: "ความลึกของการวิเคราะห์",
        surfaceLevel: "ระดับผิวเผิน",
        moderate: "ปานกลาง",
        deep: "ลึก",
        veryDeep: "ลึกมาก",
        editTopicList: "แก้ไขรายการหัวข้อ"
      },
      match: {
        title: "การจับคู่เอกสาร",
        subtitle: "ตรวจสอบให้แน่ใจว่าข้อมูลในฟิลด์ตรงกันระหว่างเอกสารที่มีรูปแบบต่างกัน",
        selectDocument: "เลือกเอกสารเพื่อค้นหาการจับคู่",
        pleaseSelect: "กรุณาเลือกเอกสาร...",
        sourceDocument: "เอกสารต้นฉบับ",
        matchingDocuments: "เอกสารที่จับคู่",
        findMatches: "ค้นหาการจับคู่",
        similarityScore: "คะแนนความคล้ายคลึง",
        noDocumentsFound: "ไม่พบเอกสาร",
        selectDocumentToMatch: "กรุณาเลือกเอกสารเพื่อค้นหาการจับคู่",
        loadingMatches: "กำลังค้นหาการจับคู่...",
        noMatchesFound: "ไม่พบเอกสารที่คล้ายกัน",
        matchResults: "ผลการจับคู่",
        similarity: "ความคล้ายคลึง",
        matchingCriteria: "เกณฑ์การจับคู่",
        semanticSimilarity: "ความคล้ายคลึงทางความหมาย",
        keywordMatching: "การจับคู่คำสำคัญ",
        structuralSimilarity: "ความคล้ายคลึงทางโครงสร้าง",
        threshold: "เกณฑ์",
        minimumSimilarity: "ความคล้ายคลึงขั้นต่ำ",
        searchDepth: "ความลึกการค้นหา",
        maxResults: "จำนวนผลลัพธ์สูงสุด",
        editFormTemplate: "แก้ไขแม่แบบฟอร์ม"
      },
      knowledgeBases: {
        title: "การจัดการฐานความรู้",
        addKnowledgeBase: "เพิ่มฐานความรู้",
        emptyStateTitle: "คุณยังไม่มีฐานความรู้",
        emptyStateDescription: "เพิ่มฐานความรู้ใหม่เพื่อเริ่มต้น",
        tableHeaders: {
          title: "ชื่อเรื่อง",
          description: "คำอธิบาย",
          numberOfSources: "จำนวนแหล่งข้อมูล",
          embeddingModel: "โมเดลการฝัง",
          dateCreated: "วันที่สร้าง",
          dateModified: "วันที่แก้ไข",
          actions: "การดำเนินการ"
        },
        status: {
          default: "ค่าเริ่มต้น",
          na: "ไม่มี"
        },
        actions: {
          view: "ดู",
          edit: "แก้ไข",
          delete: "ลบ",
          configure: "กำหนดค่า"
        },
        deleteModal: {
          title: "ลบฐานความรู้",
          buttonText: "ลบฐานความรู้",
          description: "ฐานความรู้นี้จะถูกลบอย่างถาวร คุณแน่ใจหรือไม่? คุณจะไม่สามารถยกเลิกการดำเนินการนี้ได้",
          confirmButton: "ลบ",
          cancelButton: "ยกเลิก",
          successMessage: "ลบฐานความรู้สำเร็จแล้ว",
          errorMessage: "เกิดข้อผิดพลาดในการลบฐานความรู้"
        },
        modals: {
          add: {
            title: "เพิ่มฐานความรู้",
            description: "สร้างฐานความรู้ใหม่โดยการให้รายละเอียดและอัปโหลดเอกสารด้านล่าง",
            fields: {
              title: "ชื่อเรื่อง",
              titlePlaceholder: "ชื่อเรื่อง",
              titleRequired: "จำเป็นต้องมีชื่อเรื่อง",
              description: "คำอธิบาย",
              descriptionPlaceholder: "คำอธิบาย",
            },
            fileUpload: {
              dragAndDrop: "ลากไฟล์มาที่นี่หรือคลิกเพื่อเรียกดู",
              dropFiles: "วางไฟล์ที่นี่...",
              selectedFiles: "ไฟล์ที่เลือก:",
              removeFile: "ลบไฟล์",
            },
            buttons: {
              cancel: "ยกเลิก",
              save: "บันทึก",
              creating: "กำลังสร้าง...",
            },
            validation: {
              atLeastOneFile: "จำเป็นต้องมีไฟล์อย่างน้อยหนึ่งไฟล์",
            },
            success: "สร้างฐานความรู้สำเร็จแล้ว",
          },
          edit: {
            title: "แก้ไขฐานความรู้",
            description: "อัปเดตรายละเอียดฐานความรู้ด้านล่าง",
            fields: {
              title: "ชื่อเรื่อง",
              titlePlaceholder: "ชื่อเรื่อง",
              titleRequired: "จำเป็นต้องมีชื่อเรื่อง",
              description: "คำอธิบาย",
              descriptionPlaceholder: "คำอธิบาย",
            },
            fileUpload: {
              currentFiles: "ไฟล์ปัจจุบัน:",
              dragAndDrop: "ลากไฟล์มาที่นี่หรือคลิกเพื่อเรียกดู",
              dropFiles: "วางไฟล์ที่นี่...",
              selectedFiles: "ไฟล์ที่เลือก:",
              removeFile: "ลบไฟล์",
            },
            buttons: {
              cancel: "ยกเลิก",
              save: "บันทึก",
              saving: "กำลังบันทึก...",
            },
            success: "อัปเดตฐานความรู้สำเร็จแล้ว",
          },
          editFormTemplateModal: {
            title: "แก้ไขเทมเพลตฟอร์ม",
            formTemplateName: "ชื่อเทมเพลตฟอร์ม",
            formTemplateDescription: "คำอธิบายเทมเพลตฟอร์ม",
            descriptionPlaceholder: "ใส่คำอธิบายเทมเพลตฟอร์ม...",
            referenceDocuments: "เอกสารอ้างอิง (ไม่บังคับ)",
            uploadFiles: "อัปโหลดไฟล์",
            knowledgeBase: "ฐานความรู้",
            formFields: "ฟิลด์ฟอร์ม",
            suggest: "แนะนำ",
            fieldPlaceholder: "เพิ่มชื่อฟิลด์...",
            cancel: "ยกเลิก",
            updateFormTemplate: "อัปเดตเทมเพลตฟอร์ม"
          },
        },
        editCustom: {
          title: "แก้ไขคำแนะนำที่กำหนดเอง",
          currentInstructions: "คำแนะนำปัจจุบัน:",
          save: "บันทึก",
          cancel: "ยกเลิก",
        },
      },
      optimizeChecklistModal: {
        title: "ปรับปรุงรายการตรวจสอบ",
        customInstructionsLabel: "คำแนะนำที่กำหนดเอง (ไม่บังคับ)",
        customInstructionsHelperText: "ป้อนคำแนะนำเพิ่มเติมที่ควรพิจารณาเมื่อตอบคำถามในรายการตรวจสอบ",
        analyzing: "กำลังวิเคราะห์...",
        analyzeButton: "วิเคราะห์รายการตรวจสอบ",
        analyzingMessage: "กำลังวิเคราะห์รายการตรวจสอบของคุณเพื่อหาโอกาสในการปรับปรุง...",
        cancelAnalysis: "ยกเลิกการวิเคราะห์",
        downloading: "กำลังดาวน์โหลด...",
        downloadCsv: "ดาวน์โหลด CSV",
        questionsNeedingOptimization: "คำถามที่ต้องการการปรับปรุง",
        questionsAlreadyOptimized: "คำถามที่ปรับปรุงแล้ว",
        selected: "เลือกแล้ว",
        select: "เลือก",
        original: "ต้นฉบับ",
        suggestedImprovement: "การปรับปรุงที่แนะนำ",
        policyContext: "บริบทนโยบาย",
        currentAnswer: "คำตอบปัจจุบัน",
        showLess: "แสดงน้อยลง",
        showMore: "แสดงเพิ่มเติม",
        optimizationsSelectedText: "การปรับปรุงที่เลือกสำหรับการใช้งาน",
        applying: "กำลังใช้งาน...",
        applySelectedOptimizations: "ใช้การปรับปรุงที่เลือก",
        uploadDocumentsTitle: "อัปโหลดเอกสารที่รายการตรวจสอบควรยอมรับ *",
        uploadDocumentsHelperText: "อัปโหลดเอกสารที่ควรตรงตามข้อกำหนดทั้งหมดของรายการตรวจสอบเพื่อช่วยระบุคำถามที่อาจเข้มงวดเกินไป",
        customInstructionsPlaceholder: "เช่น พิจารณาว่านี่เป็นการศึกษาในเด็กเมื่อประเมินข้อกำหนดที่เกี่ยวข้องกับอายุ โปรโตคอลนี้สำหรับการแทรกแซงความเสี่ยงต่ำ ฯลฯ"
      },
      optimizeOutlineModal: {
        title: "ปรับปรุงโครงร่าง",
        description: "อัปโหลดเอกสารอ้างอิงที่แสดงตัวอย่างคุณภาพสูงของรายงานประเภทที่คุณต้องการสร้าง ระบบจะสร้างรายงานโดยใช้โครงร่างและฐานความรู้ปัจจุบันของคุณ เปรียบเทียบกับเอกสารอ้างอิง และแนะนำการปรับปรุงสำหรับส่วนต่างๆ ของโครงร่าง",
        groundTruthDocument: "เอกสารอ้างอิง",
        customInstructionsLabel: "คำแนะนำที่กำหนดเอง (ไม่บังคับ)",
        customInstructionsHelperText: "ให้คำแนะนำเพิ่มเติมสำหรับกระบวนการปรับปรุง",
        customInstructionsPlaceholder: "เช่น มุ่งเน้นไปที่การปรับปรุงความลึกทางเทคนิค ให้แน่ใจว่าสอดคล้องกับมาตรฐานเฉพาะ ฯลฯ",
        characters: "อักขระ",
        analyzingOutline: "กำลังวิเคราะห์โครงร่างและสร้างการปรับปรุง...",
        cancelAnalysis: "ยกเลิกการวิเคราะห์",
        optimizationResults: "ผลการปรับปรุง",
        sectionsNeedOptimization: "ส่วนที่ต้องการปรับปรุง",
        downloadCsv: "ดาวน์โหลด CSV",
        section: "ส่วน",
        accepted: "ยอมรับแล้ว",
        accept: "ยอมรับ",
        originalSectionDescription: "คำอธิบายส่วนต้นฉบับ",
        suggestedSectionDescription: "คำอธิบายส่วนที่แนะนำ",
        generatedContent: "เนื้อหาที่สร้างขึ้น (ด้วยคำอธิบายปัจจุบัน)",
        groundTruthReference: "การอ้างอิงเอกสารอ้างอิง",
        showLess: "แสดงน้อยลง",
        showMore: "แสดงเพิ่มเติม",
        close: "ปิด",
        cancel: "ยกเลิก",
        optimizing: "กำลังปรับปรุง...",
        optimizeOutline: "ปรับปรุงโครงร่าง",
        applyOptimizations: "ใช้การปรับปรุง {{count}} รายการ"
      }
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
        welcomeMessageWithSource: "Chọn cơ sở tri thức hoặc tải lên tệp, sau đó đặt câu hỏi.",
        welcomeMessageGeneral: "Hỏi tôi bất cứ điều gì! Để tìm kiếm cơ sở tri thức, hãy chọn cơ sở tri thức trước.",
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
        customInstructionsHelp: "{{count}}/2000 ký tự. Những hướng dẫn này sẽ được thêm vào mỗi câu hỏi trong quá trình xử lý.",
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
        allUsersToggleTooltip: "Chuyển đổi giữa xem chỉ lịch sử của bạn hoặc lịch sử của tất cả người dùng",
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
      compare: {
        title: "So sánh tài liệu",
        subtitle: "So sánh hai tài liệu để xem chúng khác nhau như thế nào đối với danh sách chủ đề do người dùng định nghĩa.",
        selectFirstDocument: "Chọn tài liệu đầu tiên",
        selectSecondDocument: "Chọn tài liệu thứ hai",
        pleaseSelect: "Vui lòng chọn...",
        documentA: "Tài liệu A",
        documentB: "Tài liệu B",
        compareDocuments: "So sánh tài liệu",
        comparison: "So sánh",
        noDocumentsFound: "Không tìm thấy tài liệu",
        selectTwoDocuments: "Vui lòng chọn hai tài liệu để so sánh",
        loadingComparison: "Đang tải so sánh...",
        topicList: "Danh sách chủ đề",
        clickToBrowse: "Nhấp để duyệt hoặc kéo thả vào đây",
        supportedFormats: "Định dạng hỗ trợ: PDF, TXT, DOCX",
        analysisType: "Loại phân tích",
        quickAnalysis: "Phân tích nhanh",
        detailedAnalysis: "Phân tích chi tiết",
        comprehensiveAnalysis: "Phân tích toàn diện",
        analysisDepth: "Độ sâu phân tích",
        surfaceLevel: "Mức độ bề mặt",
        moderate: "Vừa phải",
        deep: "Sâu",
        veryDeep: "Rất sâu",
        editTopicList: "Chỉnh sửa danh sách chủ đề"
      },
      match: {
        title: "Khớp tài liệu",
        subtitle: "Đảm bảo rằng các mục nhập trường khớp nhau giữa các tài liệu có định dạng khác nhau.",
        selectDocument: "Chọn tài liệu để tìm kết quả khớp",
        pleaseSelect: "Vui lòng chọn tài liệu...",
        sourceDocument: "Tài liệu nguồn",
        matchingDocuments: "Tài liệu khớp",
        findMatches: "Tìm kết quả khớp",
        similarityScore: "Điểm tương tự",
        noDocumentsFound: "Không tìm thấy tài liệu",
        selectDocumentToMatch: "Vui lòng chọn tài liệu để tìm kết quả khớp",
        loadingMatches: "Đang tìm kết quả khớp...",
        noMatchesFound: "Không tìm thấy tài liệu tương tự",
        matchResults: "Kết quả khớp",
        similarity: "Tương tự",
        matchingCriteria: "Tiêu chí khớp",
        semanticSimilarity: "Tương tự ngữ nghĩa",
        keywordMatching: "Khớp từ khóa",
        structuralSimilarity: "Tương tự cấu trúc",
        threshold: "Ngưỡng",
        minimumSimilarity: "Tương tự tối thiểu",
        searchDepth: "Độ sâu tìm kiếm",
        maxResults: "Số kết quả tối đa",
        editFormTemplate: "Chỉnh sửa mẫu biểu mẫu"
      },
      knowledgeBases: {
        title: "Quản lý cơ sở tri thức",
        addKnowledgeBase: "Thêm cơ sở tri thức",
        emptyStateTitle: "Bạn chưa có cơ sở tri thức nào",
        emptyStateDescription: "Thêm cơ sở tri thức mới để bắt đầu",
        tableHeaders: {
          title: "Tiêu đề",
          description: "Mô tả",
          numberOfSources: "Số lượng nguồn",
          embeddingModel: "Mô hình nhúng",
          dateCreated: "Ngày tạo",
          dateModified: "Ngày sửa đổi",
          actions: "Hành động"
        },
        status: {
          default: "Mặc định",
          na: "Không có"
        },
        actions: {
          view: "Xem",
          edit: "Chỉnh sửa",
          delete: "Xóa",
          configure: "Cấu hình"
        },
        deleteModal: {
          title: "Xóa cơ sở tri thức",
          buttonText: "Xóa cơ sở tri thức",
          description: "Cơ sở tri thức này sẽ bị xóa vĩnh viễn. Bạn có chắc chắn không? Bạn sẽ không thể hoàn tác hành động này.",
          confirmButton: "Xóa",
          cancelButton: "Hủy",
          successMessage: "Cơ sở tri thức đã được xóa thành công",
          errorMessage: "Đã xảy ra lỗi khi xóa cơ sở tri thức"
        },
        modals: {
          add: {
            title: "Thêm cơ sở tri thức",
            description: "Tạo cơ sở tri thức mới bằng cách cung cấp chi tiết và tải lên tài liệu bên dưới.",
            fields: {
              title: "Tiêu đề",
              titlePlaceholder: "Tiêu đề",
              titleRequired: "Tiêu đề là bắt buộc",
              description: "Mô tả",
              descriptionPlaceholder: "Mô tả",
            },
            fileUpload: {
              dragAndDrop: "Kéo thả tệp vào đây hoặc nhấp để duyệt",
              dropFiles: "Thả tệp vào đây...",
              selectedFiles: "Tệp đã chọn:",
              removeFile: "Xóa tệp",
            },
            buttons: {
              cancel: "Hủy",
              save: "Lưu",
              creating: "Đang tạo...",
            },
            validation: {
              atLeastOneFile: "Cần ít nhất một tệp.",
            },
            success: "Cơ sở tri thức đã được tạo thành công.",
          },
          edit: {
            title: "Chỉnh sửa cơ sở tri thức",
            description: "Cập nhật chi tiết cơ sở tri thức bên dưới.",
            fields: {
              title: "Tiêu đề",
              titlePlaceholder: "Tiêu đề",
              titleRequired: "Tiêu đề là bắt buộc",
              description: "Mô tả",
              descriptionPlaceholder: "Mô tả",
            },
            fileUpload: {
              currentFiles: "Tệp hiện tại:",
              dragAndDrop: "Kéo thả tệp vào đây hoặc nhấp để duyệt",
              dropFiles: "Thả tệp vào đây...",
              selectedFiles: "Tệp đã chọn:",
              removeFile: "Xóa tệp",
            },
            buttons: {
              cancel: "Hủy",
              save: "Lưu",
              saving: "Đang lưu...",
            },
            success: "Cơ sở tri thức đã được cập nhật thành công.",
          },
          editFormTemplateModal: {
            title: "Chỉnh Sửa Mẫu Biểu Mẫu",
            formTemplateName: "Tên Mẫu Biểu Mẫu",
            formTemplateDescription: "Mô Tả Mẫu Biểu Mẫu",
            descriptionPlaceholder: "Nhập mô tả mẫu biểu mẫu...",
            referenceDocuments: "Tài Liệu Tham Khảo (Tùy Chọn)",
            uploadFiles: "Tải Lên Tệp",
            knowledgeBase: "Cơ Sở Tri Thức",
            formFields: "Trường Biểu Mẫu",
            suggest: "Đề Xuất",
            fieldPlaceholder: "Thêm tên trường...",
            cancel: "Hủy",
            updateFormTemplate: "Cập Nhật Mẫu Biểu Mẫu"
          },
        },
        editCustom: {
          title: "Chỉnh sửa hướng dẫn tùy chỉnh",
          currentInstructions: "Hướng dẫn hiện tại:",
          save: "Lưu",
          cancel: "Hủy",
        },
      },
      optimizeChecklistModal: {
        title: "Tối ưu hóa Danh sách Kiểm tra",
        customInstructionsLabel: "Hướng dẫn Tùy chỉnh (Tùy chọn)",
        customInstructionsHelperText: "Nhập hướng dẫn bổ sung cần được xem xét khi trả lời các câu hỏi danh sách kiểm tra",
        analyzing: "Đang phân tích...",
        analyzeButton: "Phân tích Danh sách Kiểm tra",
        analyzingMessage: "Đang phân tích danh sách kiểm tra của bạn để tìm cơ hội tối ưu hóa...",
        cancelAnalysis: "Hủy Phân tích",
        downloading: "Đang tải xuống...",
        downloadCsv: "Tải xuống CSV",
        questionsNeedingOptimization: "Câu hỏi Cần Tối ưu hóa",
        questionsAlreadyOptimized: "Câu hỏi Đã Tối ưu hóa",
        selected: "Đã chọn",
        select: "Chọn",
        original: "Gốc",
        suggestedImprovement: "Cải tiến Được Đề xuất",
        policyContext: "Bối cảnh Chính sách",
        currentAnswer: "Câu trả lời Hiện tại",
        showLess: "Hiển thị Ít hơn",
        showMore: "Hiển thị Nhiều hơn",
        optimizationsSelectedText: "tối ưu hóa được chọn để áp dụng",
        applying: "Đang áp dụng...",
        applySelectedOptimizations: "Áp dụng Tối ưu hóa Đã chọn",
        uploadDocumentsTitle: "Tải lên tài liệu mà danh sách kiểm tra nên chấp nhận *",
        uploadDocumentsHelperText: "Tải lên các tài liệu nên đáp ứng tất cả yêu cầu của danh sách kiểm tra để giúp xác định các câu hỏi có thể quá nghiêm ngặt",
        customInstructionsPlaceholder: "ví dụ: Xem xét đây là nghiên cứu nhi khoa khi đánh giá các yêu cầu liên quan đến tuổi, Giao thức này dành cho can thiệp rủi ro thấp, v.v."
      },
      optimizeOutlineModal: {
        title: "Tối ưu hóa Dàn bài",
        description: "Tải lên tài liệu tham chiếu đại diện cho ví dụ chất lượng cao về loại báo cáo bạn muốn tạo. Hệ thống sẽ tạo báo cáo sử dụng dàn bài và cơ sở kiến thức hiện tại của bạn, so sánh với tham chiếu và đề xuất cải tiến cho các phần của dàn bài.",
        groundTruthDocument: "Tài liệu Tham chiếu",
        customInstructionsLabel: "Hướng dẫn Tùy chỉnh (Tùy chọn)",
        customInstructionsHelperText: "Cung cấp hướng dẫn bổ sung cho quá trình tối ưu hóa",
        customInstructionsPlaceholder: "ví dụ: Tập trung vào cải thiện độ sâu kỹ thuật, đảm bảo tuân thủ các tiêu chuẩn cụ thể, v.v.",
        characters: "ký tự",
        analyzingOutline: "Đang phân tích dàn bài và tạo tối ưu hóa...",
        cancelAnalysis: "Hủy Phân tích",
        optimizationResults: "Kết quả Tối ưu hóa",
        sectionsNeedOptimization: "phần cần tối ưu hóa",
        downloadCsv: "Tải xuống CSV",
        section: "Phần",
        accepted: "Đã chấp nhận",
        accept: "Chấp nhận",
        originalSectionDescription: "Mô tả Phần Gốc",
        suggestedSectionDescription: "Mô tả Phần Được Đề xuất",
        generatedContent: "Nội dung Được Tạo (với mô tả hiện tại)",
        groundTruthReference: "Tham chiếu Chuẩn",
        showLess: "Hiển thị Ít hơn",
        showMore: "Hiển thị Nhiều hơn",
        close: "Đóng",
        cancel: "Hủy",
        optimizing: "Đang tối ưu hóa...",
        optimizeOutline: "Tối ưu hóa Dàn bài",
        applyOptimizations: "Áp dụng {{count}} Tối ưu hóa"
      }
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
        welcomeMessageWithSource: "Pilih basis pengetahuan atau unggah file, lalu ajukan pertanyaan.",
        welcomeMessageGeneral: "Tanyakan apa saja kepada saya! Untuk pencarian basis pengetahuan, pilih basis pengetahuan terlebih dahulu.",
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
        customInstructionsHelp: "{{count}}/2000 karakter. Instruksi ini akan ditambahkan ke setiap pertanyaan selama pemrosesan.",
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
        allUsersToggleTooltip: "Beralih antara melihat hanya riwayat Anda atau riwayat semua pengguna",
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
      compare: {
        title: "Bandingkan Dokumen",
        subtitle: "Bandingkan dua dokumen untuk melihat bagaimana perbedaannya terkait daftar topik yang ditentukan pengguna.",
        selectFirstDocument: "Pilih dokumen pertama",
        selectSecondDocument: "Pilih dokumen kedua",
        pleaseSelect: "Silakan pilih...",
        documentA: "Dokumen A",
        documentB: "Dokumen B",
        compareDocuments: "Bandingkan Dokumen",
        comparison: "Perbandingan",
        noDocumentsFound: "Tidak ada dokumen ditemukan",
        selectTwoDocuments: "Silakan pilih dua dokumen untuk dibandingkan",
        loadingComparison: "Memuat perbandingan...",
        topicList: "Daftar Topik",
        clickToBrowse: "Klik untuk menelusuri atau seret ke sini",
        supportedFormats: "Format yang didukung: PDF, TXT, DOCX",
        analysisType: "Jenis Analisis",
        quickAnalysis: "Analisis Cepat",
        detailedAnalysis: "Analisis Terperinci",
        comprehensiveAnalysis: "Analisis Komprehensif",
        analysisDepth: "Kedalaman Analisis",
        surfaceLevel: "Tingkat Permukaan",
        moderate: "Sedang",
        deep: "Dalam",
        veryDeep: "Sangat Dalam",
        editTopicList: "Edit Daftar Topik"
      },
      match: {
        title: "Pencocokan Dokumen",
        subtitle: "Pastikan entri bidang cocok di antara dokumen dengan format berbeda.",
        selectDocument: "Pilih dokumen untuk mencari kecocokan",
        pleaseSelect: "Silakan pilih dokumen...",
        sourceDocument: "Dokumen Sumber",
        matchingDocuments: "Dokumen yang Cocok",
        findMatches: "Temukan Kecocokan",
        similarityScore: "Skor Kemiripan",
        noDocumentsFound: "Tidak ada dokumen ditemukan",
        selectDocumentToMatch: "Silakan pilih dokumen untuk mencari kecocokan",
        loadingMatches: "Mencari kecocokan...",
        noMatchesFound: "Tidak ada dokumen serupa ditemukan",
        matchResults: "Hasil Pencocokan",
        similarity: "Kemiripan",
        matchingCriteria: "Kriteria Pencocokan",
        semanticSimilarity: "Kemiripan Semantik",
        keywordMatching: "Pencocokan Kata Kunci",
        structuralSimilarity: "Kemiripan Struktural",
        threshold: "Ambang Batas",
        minimumSimilarity: "Kemiripan Minimum",
        searchDepth: "Kedalaman Pencarian",
        maxResults: "Hasil Maksimum",
        editFormTemplate: "Edit Template Formulir"
      },
      knowledgeBases: {
        title: "Kelola Basis Pengetahuan",
        addKnowledgeBase: "Tambah Basis Pengetahuan",
        emptyStateTitle: "Anda belum memiliki basis pengetahuan",
        emptyStateDescription: "Tambahkan basis pengetahuan baru untuk memulai",
        tableHeaders: {
          title: "Judul",
          description: "Deskripsi",
          numberOfSources: "Jumlah Sumber",
          embeddingModel: "Model Embedding",
          dateCreated: "Tanggal Dibuat",
          dateModified: "Tanggal Dimodifikasi",
          actions: "Tindakan"
        },
        status: {
          default: "Default",
          na: "Tidak Tersedia"
        },
        actions: {
          view: "Lihat",
          edit: "Edit",
          delete: "Hapus",
          configure: "Konfigurasi"
        },
        deleteModal: {
          title: "Hapus Basis Pengetahuan",
          buttonText: "Hapus Basis Pengetahuan",
          description: "Basis pengetahuan ini akan dihapus secara permanen. Apakah Anda yakin? Anda tidak akan dapat membatalkan tindakan ini.",
          confirmButton: "Hapus",
          cancelButton: "Batal",
          successMessage: "Basis pengetahuan berhasil dihapus",
          errorMessage: "Terjadi kesalahan saat menghapus basis pengetahuan"
        },
        modals: {
          add: {
            title: "Tambah Basis Pengetahuan",
            description: "Buat basis pengetahuan baru dengan memberikan detail dan mengunggah dokumen di bawah ini.",
            fields: {
              title: "Judul",
              titlePlaceholder: "Judul",
              titleRequired: "Judul diperlukan",
              description: "Deskripsi",
              descriptionPlaceholder: "Deskripsi",
            },
            fileUpload: {
              dragAndDrop: "Seret file ke sini atau klik untuk menelusuri",
              dropFiles: "Letakkan file di sini...",
              selectedFiles: "File yang Dipilih:",
              removeFile: "Hapus File",
            },
            buttons: {
              cancel: "Batal",
              save: "Simpan",
              creating: "Membuat...",
            },
            validation: {
              atLeastOneFile: "Setidaknya satu file diperlukan.",
            },
            success: "Basis pengetahuan berhasil dibuat.",
          },
          edit: {
            title: "Edit Basis Pengetahuan",
            description: "Perbarui detail basis pengetahuan di bawah ini.",
            fields: {
              title: "Judul",
              titlePlaceholder: "Judul",
              titleRequired: "Judul diperlukan",
              description: "Deskripsi",
              descriptionPlaceholder: "Deskripsi",
            },
            fileUpload: {
              currentFiles: "File Saat Ini:",
              dragAndDrop: "Seret file ke sini atau klik untuk menelusuri",
              dropFiles: "Letakkan file di sini...",
              selectedFiles: "File yang Dipilih:",
              removeFile: "Hapus File",
            },
            buttons: {
              cancel: "Batal",
              save: "Simpan",
              saving: "Menyimpan...",
            },
            success: "Basis pengetahuan berhasil diperbarui.",
          },
          editFormTemplateModal: {
            title: "Edit Template Form",
            formTemplateName: "Nama Template Form",
            formTemplateDescription: "Deskripsi Template Form",
            descriptionPlaceholder: "Masukkan deskripsi template form...",
            referenceDocuments: "Dokumen Referensi (Opsional)",
            uploadFiles: "Unggah File",
            knowledgeBase: "Basis Pengetahuan",
            formFields: "Bidang Form",
            suggest: "Sarankan",
            fieldPlaceholder: "Tambahkan nama bidang...",
            cancel: "Batal",
            updateFormTemplate: "Perbarui Template Form"
          },
        },
        editCustom: {
          title: "Edit Instruksi Kustom",
          currentInstructions: "Instruksi Saat Ini:",
          save: "Simpan",
          cancel: "Batal",
        },
      },
      optimizeChecklistModal: {
        title: "Optimalkan Daftar Periksa",
        customInstructionsLabel: "Instruksi Kustom (Opsional)",
        customInstructionsHelperText: "Masukkan instruksi tambahan yang harus dipertimbangkan saat menjawab pertanyaan daftar periksa",
        analyzing: "Menganalisis...",
        analyzeButton: "Analisis Daftar Periksa",
        analyzingMessage: "Menganalisis daftar periksa Anda untuk peluang optimalisasi...",
        cancelAnalysis: "Batalkan Analisis",
        downloading: "Mengunduh...",
        downloadCsv: "Unduh CSV",
        questionsNeedingOptimization: "Pertanyaan yang Memerlukan Optimalisasi",
        questionsAlreadyOptimized: "Pertanyaan yang Sudah Dioptimalkan",
        selected: "Dipilih",
        select: "Pilih",
        original: "Asli",
        suggestedImprovement: "Perbaikan yang Disarankan",
        policyContext: "Konteks Kebijakan",
        currentAnswer: "Jawaban Saat Ini",
        showLess: "Tampilkan Lebih Sedikit",
        showMore: "Tampilkan Lebih Banyak",
        optimizationsSelectedText: "optimalisasi dipilih untuk diterapkan",
        applying: "Menerapkan...",
        applySelectedOptimizations: "Terapkan Optimalisasi yang Dipilih",
        uploadDocumentsTitle: "Unggah dokumen yang harus diterima oleh daftar periksa *",
        uploadDocumentsHelperText: "Unggah dokumen yang harus memenuhi semua persyaratan daftar periksa untuk membantu mengidentifikasi pertanyaan yang mungkin terlalu ketat",
        customInstructionsPlaceholder: "mis., Pertimbangkan ini adalah studi pediatrik saat mengevaluasi persyaratan terkait usia, Protokol ini untuk intervensi risiko rendah, dll."
      },
      optimizeOutlineModal: {
        title: "Optimalkan Garis Besar",
        description: "Unggah dokumen referensi yang mewakili contoh berkualitas tinggi dari jenis laporan yang ingin Anda buat. Sistem akan membuat laporan menggunakan garis besar dan basis pengetahuan Anda saat ini, membandingkannya dengan referensi, dan menyarankan perbaikan untuk bagian garis besar.",
        groundTruthDocument: "Dokumen Referensi",
        customInstructionsLabel: "Instruksi Kustom (Opsional)",
        customInstructionsHelperText: "Berikan panduan tambahan untuk proses optimalisasi",
        customInstructionsPlaceholder: "mis., Fokus pada peningkatan kedalaman teknis, pastikan kepatuhan terhadap standar spesifik, dll.",
        characters: "karakter",
        analyzingOutline: "Menganalisis garis besar dan menghasilkan optimalisasi...",
        cancelAnalysis: "Batalkan Analisis",
        optimizationResults: "Hasil Optimalisasi",
        sectionsNeedOptimization: "bagian memerlukan optimalisasi",
        downloadCsv: "Unduh CSV",
        section: "Bagian",
        accepted: "Diterima",
        accept: "Terima",
        originalSectionDescription: "Deskripsi Bagian Asli",
        suggestedSectionDescription: "Deskripsi Bagian yang Disarankan",
        generatedContent: "Konten yang Dihasilkan (dengan deskripsi saat ini)",
        groundTruthReference: "Referensi Kebenaran Dasar",
        showLess: "Tampilkan Lebih Sedikit",
        showMore: "Tampilkan Lebih Banyak",
        close: "Tutup",
        cancel: "Batal",
        optimizing: "Mengoptimalkan...",
        optimizeOutline: "Optimalkan Garis Besar",
        applyOptimizations: "Terapkan {{count}} Optimalisasi"
      }
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
        welcomeMessageWithSource: "Pilih pangkalan pengetahuan atau muat naik fail, kemudian tanya soalan.",
        welcomeMessageGeneral: "Tanya saya apa sahaja! Untuk carian pangkalan pengetahuan, pilih pangkalan pengetahuan dahulu.",
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
        customInstructionsHelp: "{{count}}/2000 aksara. Arahan ini akan ditambah kepada setiap soalan semasa pemprosesan.",
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
        allUsersToggleTooltip: "Tukar antara melihat hanya sejarah anda atau sejarah semua pengguna",
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
      compare: {
        title: "Bandingkan Dokumen",
        subtitle: "Pilih dua dokumen untuk dibandingkan",
        selectFirstDocument: "Pilih dokumen pertama",
        selectSecondDocument: "Pilih dokumen kedua",
        pleaseSelect: "Sila pilih...",
        documentA: "Dokumen A",
        documentB: "Dokumen B",
        compareDocuments: "Bandingkan Dokumen",
        comparison: "Perbandingan",
        noDocumentsFound: "Tiada dokumen ditemui",
        selectTwoDocuments: "Sila pilih dua dokumen untuk dibandingkan",
        loadingComparison: "Memuatkan perbandingan...",
        topicList: "Senarai Topik",
        clickToBrowse: "Klik untuk semak imbas atau seret ke sini",
        supportedFormats: "Format yang disokong: PDF, TXT, DOCX",
        analysisType: "Jenis Analisis",
        quickAnalysis: "Analisis Pantas",
        detailedAnalysis: "Analisis Terperinci",
        comprehensiveAnalysis: "Analisis Komprehensif",
        analysisDepth: "Kedalaman Analisis",
        surfaceLevel: "Tahap Permukaan",
        moderate: "Sederhana",
        deep: "Mendalam",
        veryDeep: "Sangat Mendalam",
        editTopicList: "Edit Senarai Topik"
      },
      match: {
        title: "Padanan Dokumen",
        subtitle: "Cari dokumen serupa berdasarkan kandungan",
        selectDocument: "Pilih dokumen untuk mencari padanan",
        pleaseSelect: "Sila pilih dokumen...",
        sourceDocument: "Dokumen Sumber",
        matchingDocuments: "Dokumen yang Sepadan",
        findMatches: "Cari Padanan",
        similarityScore: "Skor Kesamaan",
        noDocumentsFound: "Tiada dokumen ditemui",
        selectDocumentToMatch: "Sila pilih dokumen untuk mencari padanan",
        loadingMatches: "Mencari padanan...",
        noMatchesFound: "Tiada dokumen serupa ditemui",
        matchResults: "Hasil Padanan",
        similarity: "Kesamaan",
        matchingCriteria: "Kriteria Padanan",
        semanticSimilarity: "Kesamaan Semantik",
        keywordMatching: "Padanan Kata Kunci",
        structuralSimilarity: "Kesamaan Struktur",
        threshold: "Ambang",
        minimumSimilarity: "Kesamaan Minimum",
        searchDepth: "Kedalaman Carian",
        maxResults: "Hasil Maksimum",
        editFormTemplate: "Edit Templat Borang"
      },
      knowledgeBases: {
        title: "Pengurusan Pangkalan Pengetahuan",
        addKnowledgeBase: "Tambah Pangkalan Pengetahuan",
        emptyStateTitle: "Anda belum mempunyai pangkalan pengetahuan",
        emptyStateDescription: "Tambahkan pangkalan pengetahuan baru untuk bermula",
        tableHeaders: {
          title: "Tajuk",
          description: "Penerangan",
          numberOfSources: "Bilangan Sumber",
          embeddingModel: "Model Pembenaman",
          dateCreated: "Tarikh Dicipta",
          dateModified: "Tarikh Diubah Suai",
          actions: "Tindakan"
        },
        status: {
          default: "Lalai",
          na: "Tidak Tersedia"
        },
        actions: {
          view: "Lihat",
          edit: "Edit",
          delete: "Padam",
          configure: "Konfigurasi"
        },
        deleteModal: {
          title: "Padam Pangkalan Pengetahuan",
          buttonText: "Padam Pangkalan Pengetahuan",
          description: "Pangkalan pengetahuan ini akan dipadamkan secara kekal. Adakah anda pasti? Anda tidak akan dapat membatalkan tindakan ini.",
          confirmButton: "Padam",
          cancelButton: "Batal",
          successMessage: "Pangkalan pengetahuan berjaya dipadamkan",
          errorMessage: "Ralat berlaku semasa memadamkan pangkalan pengetahuan"
        },
        modals: {
          add: {
            title: "Tambah Pangkalan Pengetahuan",
            description: "Cipta pangkalan pengetahuan baharu dengan memberikan butiran dan memuat naik dokumen di bawah.",
            fields: {
              title: "Tajuk",
              titlePlaceholder: "Tajuk",
              titleRequired: "Tajuk diperlukan",
              description: "Penerangan",
              descriptionPlaceholder: "Penerangan",
            },
            fileUpload: {
              dragAndDrop: "Seret fail ke sini atau klik untuk semak imbas",
              dropFiles: "Letakkan fail di sini...",
              selectedFiles: "Fail yang Dipilih:",
              removeFile: "Buang Fail",
            },
            buttons: {
              cancel: "Batal",
              save: "Simpan",
              creating: "Mencipta...",
            },
            validation: {
              atLeastOneFile: "Sekurang-kurangnya satu fail diperlukan.",
            },
            success: "Pangkalan pengetahuan berjaya dicipta.",
          },
          edit: {
            title: "Edit Pangkalan Pengetahuan",
            description: "Kemas kini butiran pangkalan pengetahuan di bawah.",
            fields: {
              title: "Tajuk",
              titlePlaceholder: "Tajuk",
              titleRequired: "Tajuk diperlukan",
              description: "Penerangan",
              descriptionPlaceholder: "Penerangan",
            },
            fileUpload: {
              currentFiles: "Fail Semasa:",
              dragAndDrop: "Seret fail ke sini atau klik untuk semak imbas",
              dropFiles: "Letakkan fail di sini...",
              selectedFiles: "Fail yang Dipilih:",
              removeFile: "Buang Fail",
            },
            buttons: {
              cancel: "Batal",
              save: "Simpan",
              saving: "Menyimpan...",
            },
            success: "Pangkalan pengetahuan berjaya dikemas kini.",
          },
          editFormTemplateModal: {
            title: "Edit Templat Borang",
            formTemplateName: "Nama Templat Borang",
            formTemplateDescription: "Penerangan Templat Borang",
            descriptionPlaceholder: "Masukkan penerangan templat borang...",
            referenceDocuments: "Dokumen Rujukan (Pilihan)",
            uploadFiles: "Muat Naik Fail",
            knowledgeBase: "Pangkalan Pengetahuan",
            formFields: "Medan Borang",
            suggest: "Cadangkan",
            fieldPlaceholder: "Tambah nama medan...",
            cancel: "Batal",
            updateFormTemplate: "Kemas Kini Templat Borang"
          },
        },
        editCustom: {
          title: "Edit Arahan Tersuai",
          currentInstructions: "Arahan Semasa:",
          save: "Simpan",
          cancel: "Batal",
        },
      },
      optimizeChecklistModal: {
        title: "Optimumkan Senarai Semak",
        customInstructionsLabel: "Arahan Tersuai (Pilihan)",
        customInstructionsHelperText: "Masukkan arahan tambahan yang perlu dipertimbangkan semasa menjawab soalan senarai semak",
        analyzing: "Menganalisis...",
        analyzeButton: "Analisis Senarai Semak",
        analyzingMessage: "Menganalisis senarai semak anda untuk peluang pengoptimuman...",
        cancelAnalysis: "Batalkan Analisis",
        downloading: "Memuat turun...",
        downloadCsv: "Muat turun CSV",
        questionsNeedingOptimization: "Soalan yang Memerlukan Pengoptimuman",
        questionsAlreadyOptimized: "Soalan yang Sudah Dioptimumkan",
        selected: "Dipilih",
        select: "Pilih",
        original: "Asal",
        suggestedImprovement: "Penambahbaikan yang Dicadangkan",
        policyContext: "Konteks Dasar",
        currentAnswer: "Jawapan Semasa",
        showLess: "Tunjukkan Kurang",
        showMore: "Tunjukkan Lebih",
        optimizationsSelectedText: "pengoptimuman dipilih untuk digunakan",
        applying: "Menggunakan...",
        applySelectedOptimizations: "Gunakan Pengoptimuman yang Dipilih",
        uploadDocumentsTitle: "Muat naik dokumen yang patut diterima oleh senarai semak *",
        uploadDocumentsHelperText: "Muat naik dokumen yang patut memenuhi semua keperluan senarai semak untuk membantu mengenal pasti soalan yang mungkin terlalu ketat",
        customInstructionsPlaceholder: "cth., Pertimbangkan ini adalah kajian pediatrik semasa menilai keperluan berkaitan umur, Protokol ini untuk campur tangan berisiko rendah, dll."
      },
      optimizeOutlineModal: {
        title: "Optimumkan Garis Panduan",
        description: "Muat naik dokumen rujukan yang mewakili contoh berkualiti tinggi bagi jenis laporan yang anda ingin hasilkan. Sistem akan menghasilkan laporan menggunakan garis panduan dan pangkalan pengetahuan semasa anda, membandingkannya dengan rujukan, dan mencadangkan penambahbaikan untuk bahagian garis panduan.",
        groundTruthDocument: "Dokumen Rujukan",
        customInstructionsLabel: "Arahan Tersuai (Pilihan)",
        customInstructionsHelperText: "Berikan panduan tambahan untuk proses pengoptimuman",
        customInstructionsPlaceholder: "cth., Fokus pada penambahbaikan kedalaman teknikal, pastikan pematuhan kepada piawaian khusus, dll.",
        characters: "aksara",
        analyzingOutline: "Menganalisis garis panduan dan menghasilkan pengoptimuman...",
        cancelAnalysis: "Batalkan Analisis",
        optimizationResults: "Keputusan Pengoptimuman",
        sectionsNeedOptimization: "bahagian memerlukan pengoptimuman",
        downloadCsv: "Muat turun CSV",
        section: "Bahagian",
        accepted: "Diterima",
        accept: "Terima",
        originalSectionDescription: "Penerangan Bahagian Asal",
        suggestedSectionDescription: "Penerangan Bahagian yang Dicadangkan",
        generatedContent: "Kandungan yang Dihasilkan (dengan penerangan semasa)",
        groundTruthReference: "Rujukan Kebenaran Asas",
        showLess: "Tunjukkan Kurang",
        showMore: "Tunjukkan Lebih",
        close: "Tutup",
        cancel: "Batal",
        optimizing: "Mengoptimumkan...",
        optimizeOutline: "Optimumkan Garis Panduan",
        applyOptimizations: "Gunakan {{count}} Pengoptimuman"
      }
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
        welcomeMessageWithSource: "Pumili ng knowledge base o mag-upload ng mga file, pagkatapos magtanong.",
        welcomeMessageGeneral: "Tanungin mo ako ng kahit ano! Para sa paghahanap sa knowledge base, pumili muna ng knowledge base.",
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
        customInstructionsHelp: "{{count}}/2000 character. Ang mga tagubiling ito ay idadagdag sa bawat tanong sa panahon ng pagproseso.",
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
        allUsersToggleTooltip: "Lumipat sa pagitan ng pagtingin lamang sa inyong kasaysayan o kasaysayan ng lahat ng mga user",
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
      compare: {
        title: "Ihambing ang mga Dokumento",
        subtitle: "Pumili ng dalawang dokumento upang ihambing",
        selectFirstDocument: "Pumili ng unang dokumento",
        selectSecondDocument: "Pumili ng pangalawang dokumento",
        pleaseSelect: "Pakiselect...",
        documentA: "Dokumento A",
        documentB: "Dokumento B",
        compareDocuments: "Ihambing ang mga Dokumento",
        comparison: "Paghahambing",
        noDocumentsFound: "Walang nahanap na dokumento",
        selectTwoDocuments: "Pakipili ng dalawang dokumento upang ihambing",
        loadingComparison: "Naglo-load ng paghahambing...",
        topicList: "Listahan ng mga Paksa",
        clickToBrowse: "I-click upang mag-browse o i-drag dito",
        supportedFormats: "Mga suportadong format: PDF, TXT, DOCX",
        analysisType: "Uri ng Pagsusuri",
        quickAnalysis: "Mabilis na Pagsusuri",
        detailedAnalysis: "Detalyadong Pagsusuri",
        comprehensiveAnalysis: "Komprehensibong Pagsusuri",
        analysisDepth: "Lalim ng Pagsusuri",
        surfaceLevel: "Surface Level",
        moderate: "Katamtaman",
        deep: "Malalim",
        veryDeep: "Napaka-lalim",
        editTopicList: "I-edit ang Listahan ng Paksa"
      },
      match: {
        title: "Pagtugma ng Dokumento",
        subtitle: "Maghanap ng mga katulad na dokumento batay sa nilalaman",
        selectDocument: "Pumili ng dokumento upang maghanap ng mga tumugma",
        pleaseSelect: "Pakiselect ang dokumento...",
        sourceDocument: "Source Document",
        matchingDocuments: "Mga Tumugmang Dokumento",
        findMatches: "Maghanap ng mga Tugma",
        similarityScore: "Similarity Score",
        noDocumentsFound: "Walang nahanap na dokumento",
        selectDocumentToMatch: "Pakipili ng dokumento upang maghanap ng mga tugma",
        loadingMatches: "Naghahanap ng mga tugma...",
        noMatchesFound: "Walang nahanap na katulad na dokumento",
        matchResults: "Mga Resulta ng Pagtugma",
        similarity: "Pagkakatulad",
        matchingCriteria: "Mga Pamantayan sa Pagtugma",
        semanticSimilarity: "Semantic na Pagkakatulad",
        keywordMatching: "Keyword Matching",
        structuralSimilarity: "Structural na Pagkakatulad",
        threshold: "Threshold",
        minimumSimilarity: "Pinakamababang Pagkakatulad",
        searchDepth: "Lalim ng Paghahanap",
        maxResults: "Pinakamataas na Resulta",
        editFormTemplate: "I-edit ang Template ng Form"
      },
      knowledgeBases: {
        title: "Pamamahala ng Knowledge Base",
        addKnowledgeBase: "Magdagdag ng Knowledge Base",
        emptyStateTitle: "Wala ka pang mga knowledge base",
        emptyStateDescription: "Magdagdag ng bagong knowledge base upang magsimula",
        tableHeaders: {
          title: "Pamagat",
          description: "Paglalarawan",
          numberOfSources: "Bilang ng mga Source",
          embeddingModel: "Embedding Model",
          dateCreated: "Petsa ng Paglikha",
          dateModified: "Petsa ng Pagbabago",
          actions: "Mga Aksyon"
        },
        status: {
          default: "Default",
          na: "Hindi Available"
        },
        actions: {
          view: "Tingnan",
          edit: "I-edit",
          delete: "Tanggalin",
          configure: "I-configure"
        },
        deleteModal: {
          title: "Tanggalin ang Knowledge Base",
          buttonText: "Tanggalin ang Knowledge Base",
          description: "Ang knowledge base na ito ay permanenteng matatanggal. Sigurado ka ba? Hindi mo na ito mababalik.",
          confirmButton: "Tanggalin",
          cancelButton: "Kanselahin",
          successMessage: "Matagumpay na natanggal ang knowledge base",
          errorMessage: "May error na nangyari habang tinatanggal ang knowledge base"
        },
        modals: {
          add: {
            title: "Magdagdag ng Knowledge Base",
            description: "Lumikha ng bagong knowledge base sa pamamagitan ng pagbibigay ng mga detalye at pag-upload ng mga dokumento sa ibaba.",
            fields: {
              title: "Pamagat",
              titlePlaceholder: "Pamagat",
              titleRequired: "Kailangan ang pamagat",
              description: "Paglalarawan",
              descriptionPlaceholder: "Paglalarawan",
            },
            fileUpload: {
              dragAndDrop: "I-drag ang mga file dito o i-click upang mag-browse",
              dropFiles: "I-drop ang mga file dito...",
              selectedFiles: "Mga Napiling File:",
              removeFile: "Tanggalin ang File",
            },
            buttons: {
              cancel: "Kanselahin",
              save: "I-save",
              creating: "Ginagawa...",
            },
            validation: {
              atLeastOneFile: "Kailangan ng hindi bababa sa isang file.",
            },
            success: "Matagumpay na nalikha ang knowledge base.",
          },
          edit: {
            title: "I-edit ang Knowledge Base",
            description: "I-update ang mga detalye ng knowledge base sa ibaba.",
            fields: {
              title: "Pamagat",
              titlePlaceholder: "Pamagat",
              titleRequired: "Kailangan ang pamagat",
              description: "Paglalarawan",
              descriptionPlaceholder: "Paglalarawan",
            },
            fileUpload: {
              currentFiles: "Kasalukuyang mga File:",
              dragAndDrop: "I-drag ang mga file dito o i-click upang mag-browse",
              dropFiles: "I-drop ang mga file dito...",
              selectedFiles: "Mga Napiling File:",
              removeFile: "Tanggalin ang File",
            },
            buttons: {
              cancel: "Kanselahin",
              save: "I-save",
              saving: "Sine-save...",
            },
            success: "Matagumpay na na-update ang knowledge base.",
          },
          editFormTemplateModal: {
            title: "I-edit ang Form Template",
            formTemplateName: "Pangalan ng Form Template",
            formTemplateDescription: "Paglalarawan ng Form Template",
            descriptionPlaceholder: "Ilagay ang paglalarawan ng form template...",
            referenceDocuments: "Mga Reference Document (Optional)",
            uploadFiles: "Mag-upload ng mga File",
            knowledgeBase: "Knowledge Base",
            formFields: "Mga Field ng Form",
            suggest: "Mag-suggest",
            fieldPlaceholder: "Magdagdag ng field name...",
            cancel: "Kanselahin",
            updateFormTemplate: "I-update ang Form Template"
          },
        },
        editCustom: {
          title: "I-edit ang Custom na mga Tagubilin",
          currentInstructions: "Kasalukuyang mga Tagubilin:",
          save: "I-save",
          cancel: "Kanselahin",
        },
      },
      optimizeChecklistModal: {
        title: "I-optimize ang Checklist",
        customInstructionsLabel: "Mga Custom na Tagubilin (Opsyonal)",
        customInstructionsHelperText: "Maglagay ng karagdagang mga tagubilin na dapat isaalang-alang kapag sumasagot sa mga tanong sa checklist",
        analyzing: "Nag-aanalisa...",
        analyzeButton: "Suriin ang Checklist",
        analyzingMessage: "Sinusuri ang inyong checklist para sa mga pagkakataong ma-optimize...",
        cancelAnalysis: "Kanselahin ang Pagsusuri",
        downloading: "Nag-dodownload...",
        downloadCsv: "I-download ang CSV",
        questionsNeedingOptimization: "Mga Tanong na Kailangan ng Optimization",
        questionsAlreadyOptimized: "Mga Tanong na Na-optimize Na",
        selected: "Napili",
        select: "Piliin",
        original: "Orihinal",
        suggestedImprovement: "Mungkahing Pagpapabuti",
        policyContext: "Konteksto ng Patakaran",
        currentAnswer: "Kasalukuyang Sagot",
        showLess: "Magpakita ng Mas Kaunti",
        showMore: "Magpakita ng Higit Pa",
        optimizationsSelectedText: "mga optimization na napili para sa paggamit",
        applying: "Ginagamit...",
        applySelectedOptimizations: "Gamitin ang Mga Napiking Optimization",
        uploadDocumentsTitle: "Mag-upload ng mga dokumento na dapat tanggapin ng checklist *",
        uploadDocumentsHelperText: "Mag-upload ng mga dokumento na dapat matugunan ang lahat ng mga requirement ng checklist upang makatulong sa pagkilala ng mga tanong na maaaring masyadong mahigpit",
        customInstructionsPlaceholder: "hal., Isaalang-alang na ito ay pediatric study kapag sinusuri ang mga requirement na may kaugnayan sa edad, Ang protocol na ito ay para sa low-risk intervention, atbp."
      },
      optimizeOutlineModal: {
        title: "I-optimize ang Outline",
        description: "Mag-upload ng reference document na kumakatawan sa mataas na kalidad na halimbawa ng uri ng ulat na gusto ninyong makabuo. Ang sistema ay gagawa ng ulat gamit ang inyong kasalukuyang outline at knowledge base, ikukumpara ito sa reference, at magmumungkahi ng mga pagpapabuti para sa mga seksyon ng outline.",
        groundTruthDocument: "Reference Document",
        customInstructionsLabel: "Mga Custom na Tagubilin (Opsyonal)",
        customInstructionsHelperText: "Magbigay ng karagdagang gabay para sa proseso ng optimization",
        customInstructionsPlaceholder: "hal., Tumuon sa pagpapabuti ng technical depth, tiyakin ang pagsunod sa mga tukoy na pamantayan, atbp.",
        characters: "mga karakter",
        analyzingOutline: "Sinusuri ang outline at bumubuo ng mga optimization...",
        cancelAnalysis: "Kanselahin ang Pagsusuri",
        optimizationResults: "Mga Resulta ng Optimization",
        sectionsNeedOptimization: "mga seksyon ay nangangailangan ng optimization",
        downloadCsv: "I-download ang CSV",
        section: "Seksyon",
        accepted: "Tinanggap",
        accept: "Tanggapin",
        originalSectionDescription: "Orihinal na Paglalarawan ng Seksyon",
        suggestedSectionDescription: "Mungkahing Paglalarawan ng Seksyon",
        generatedContent: "Nabuong Nilalaman (sa kasalukuyang paglalarawan)",
        groundTruthReference: "Ground-Truth Reference",
        showLess: "Magpakita ng Mas Kaunti",
        showMore: "Magpakita ng Higit Pa",
        close: "Isara",
        cancel: "Kanselahin",
        optimizing: "Nag-o-optimize...",
        optimizeOutline: "I-optimize ang Outline",
        applyOptimizations: "Gamitin ang {{count}} Optimization"
      }
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
      addKnowledgeBase: "新增知識庫",
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
      addKnowledgeBase: "เพิ่มฐานความรู้",
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
      addKnowledgeBase: "Thêm cơ sở tri thức",
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
      addKnowledgeBase: "Tambah basis pengetahuan",
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
      addKnowledgeBase: "Tambah pangkalan pengetahuan",
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
      addKnowledgeBase: "Magdagdag ng base ng kaalaman",
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

  // Add Archive translations for Asian languages
  if (!resources.zh.common.archive) {
    resources.zh.common.archive = {
      tabs: {
        review: "审查",
        generate: "生成",
        compare: "比较",
        match: "匹配"
      },
      metadata: {
        questions: "个问题",
        questions_one: "个问题",
        fields: "个字段",
        fields_one: "个字段",
        documents: "个文档",
        documents_one: "个文档",
        digitized: "数字化",
        handwritten: "手写"
      },
      feedback: {
        positive: "为此结果提供正面反馈",
        negative: "为此结果提供负面反馈",
        hasFeedback: "此结果有反馈"
      },
      emptyMessages: {
        review: "暂无审查历史",
        generate: "暂无生成历史",
        compare: "暂无比较历史",
        match: "暂无匹配历史"
      },
      deleteConfirmation: "您确定要删除此项目吗？",
      history: "历史",
      allUsers: "所有用户"
    }
  }

  if (!resources.ja.common.archive) {
    resources.ja.common.archive = {
      tabs: {
        review: "レビュー",
        generate: "生成",
        compare: "比較",
        match: "マッチ"
      },
      metadata: {
        questions: "個の質問",
        questions_one: "個の質問",
        fields: "個のフィールド",
        fields_one: "個のフィールド",
        documents: "個のドキュメント",
        documents_one: "個のドキュメント",
        digitized: "デジタル化済み",
        handwritten: "手書き"
      },
      feedback: {
        positive: "この結果に対してポジティブなフィードバックを提供する",
        negative: "この結果に対してネガティブなフィードバックを提供する",
        hasFeedback: "この結果にはフィードバックがあります"
      },
      emptyMessages: {
        review: "レビュー履歴はまだありません",
        generate: "生成履歴はまだありません",
        compare: "比較履歴はまだありません",
        match: "マッチ履歴はまだありません"
      },
      deleteConfirmation: "このアイテムを削除してもよろしいですか？",
      history: "履歴",
      allUsers: "すべてのユーザー"
    }
  }

  if (!resources.hi.common.archive) {
    resources.hi.common.archive = {
      tabs: {
        review: "समीक्षा",
        generate: "उत्पन्न करें",
        compare: "तुलना करें",
        match: "मैच करें"
      },
      metadata: {
        questions: "प्रश्न",
        questions_one: "प्रश्न",
        fields: "फ़ील्ड",
        fields_one: "फ़ील्ड",
        documents: "दस्तावेज़",
        documents_one: "दस्तावेज़",
        digitized: "डिजिटलीकृत",
        handwritten: "हस्तलिखित"
      },
      feedback: {
        positive: "इस परिणाम के लिए सकारात्मक फीडबैक दें",
        negative: "इस परिणाम के लिए नकारात्मक फीडबैक दें",
        hasFeedback: "इस परिणाम में फीडबैक है"
      },
      emptyMessages: {
        review: "अभी तक कोई समीक्षा इतिहास नहीं",
        generate: "अभी तक कोई उत्पादन इतिहास नहीं",
        compare: "अभी तक कोई तुलना इतिहास नहीं",
        match: "अभी तक कोई मैच इतिहास नहीं"
      },
      deleteConfirmation: "क्या आप वाकई इस आइटम को हटाना चाहते हैं?",
      history: "इतिहास",
      allUsers: "सभी उपयोगकर्ता"
    }
  }

  if (!resources.th.common.archive) {
    resources.th.common.archive = {
      tabs: {
        review: "ตรวจสอบ",
        generate: "สร้าง",
        compare: "เปรียบเทียบ",
        match: "จับคู่"
      },
      metadata: {
        questions: "คำถาม",
        questions_one: "คำถาม",
        fields: "ฟิลด์",
        fields_one: "ฟิลด์",
        documents: "เอกสาร",
        documents_one: "เอกสาร",
        digitized: "ดิจิทัล",
        handwritten: "เขียนด้วยมือ"
      },
      feedback: {
        positive: "ให้ข้อเสนอแนะเชิงบวกสำหรับผลลัพธ์นี้",
        negative: "ให้ข้อเสนอแนะเชิงลบสำหรับผลลัพธ์นี้",
        hasFeedback: "ผลลัพธ์นี้มีข้อเสนอแนะ"
      },
      emptyMessages: {
        review: "ยังไม่มีประวัติการตรวจสอบ",
        generate: "ยังไม่มีประวัติการสร้าง",
        compare: "ยังไม่มีประวัติการเปรียบเทียบ",
        match: "ยังไม่มีประวัติการจับคู่"
      },
      deleteConfirmation: "คุณแน่ใจหรือไม่ว่าต้องการลบรายการนี้?",
      history: "ประวัติ",
      allUsers: "ผู้ใช้ทั้งหมด"
    }
  }

  if (!resources.vi.common.archive) {
    resources.vi.common.archive = {
      tabs: {
        review: "Xem xét",
        generate: "Tạo",
        compare: "So sánh",
        match: "Khớp"
      },
      metadata: {
        questions: "câu hỏi",
        questions_one: "câu hỏi",
        fields: "trường",
        fields_one: "trường",
        documents: "tài liệu",
        documents_one: "tài liệu",
        digitized: "số hóa",
        handwritten: "viết tay"
      },
      feedback: {
        positive: "Cung cấp phản hồi tích cực cho kết quả này",
        negative: "Cung cấp phản hồi tiêu cực cho kết quả này",
        hasFeedback: "Kết quả này có phản hồi"
      },
      emptyMessages: {
        review: "Chưa có lịch sử xem xét",
        generate: "Chưa có lịch sử tạo",
        compare: "Chưa có lịch sử so sánh",
        match: "Chưa có lịch sử khớp"
      },
      deleteConfirmation: "Bạn có chắc chắn muốn xóa mục này?",
      history: "Lịch sử",
      allUsers: "Tất cả người dùng"
    }
  }

  if (!resources.id.common.archive) {
    resources.id.common.archive = {
      tabs: {
        review: "Tinjau",
        generate: "Hasilkan",
        compare: "Bandingkan",
        match: "Cocokkan"
      },
      metadata: {
        questions: "pertanyaan",
        questions_one: "pertanyaan",
        fields: "bidang",
        fields_one: "bidang",
        documents: "dokumen",
        documents_one: "dokumen",
        digitized: "didigitalkan",
        handwritten: "tulisan tangan"
      },
      feedback: {
        positive: "Berikan umpan balik positif untuk hasil ini",
        negative: "Berikan umpan balik negatif untuk hasil ini",
        hasFeedback: "Hasil ini memiliki umpan balik"
      },
      emptyMessages: {
        review: "Belum ada riwayat tinjauan",
        generate: "Belum ada riwayat pembuatan",
        compare: "Belum ada riwayat perbandingan",
        match: "Belum ada riwayat pencocokan"
      },
      deleteConfirmation: "Apakah Anda yakin ingin menghapus item ini?",
      history: "Riwayat",
      allUsers: "Semua pengguna"
    }
  }

  if (!resources.ms.common.archive) {
    resources.ms.common.archive = {
      tabs: {
        review: "Semak",
        generate: "Jana",
        compare: "Bandingkan",
        match: "Padankan"
      },
      metadata: {
        questions: "soalan",
        questions_one: "soalan",
        fields: "medan",
        fields_one: "medan",
        documents: "dokumen",
        documents_one: "dokumen",
        digitized: "didigitalkan",
        handwritten: "tulisan tangan"
      },
      feedback: {
        positive: "Berikan maklum balas positif untuk hasil ini",
        negative: "Berikan maklum balas negatif untuk hasil ini",
        hasFeedback: "Hasil ini mempunyai maklum balas"
      },
      emptyMessages: {
        review: "Belum ada sejarah semakan",
        generate: "Belum ada sejarah penjanaan",
        compare: "Belum ada sejarah perbandingan",
        match: "Belum ada sejarah pemadanan"
      },
      deleteConfirmation: "Adakah anda pasti mahu memadam item ini?",
      history: "Sejarah",
      allUsers: "Semua pengguna"
    }
  }

  if (!resources.tl.common.archive) {
    resources.tl.common.archive = {
      tabs: {
        review: "Suriin",
        generate: "Bumuo",
        compare: "Ihambing",
        match: "Itugma"
      },
      metadata: {
        questions: "mga tanong",
        questions_one: "tanong",
        fields: "mga field",
        fields_one: "field",
        documents: "mga dokumento",
        documents_one: "dokumento",
        digitized: "na-digitize",
        handwritten: "nakasulat sa kamay"
      },
      feedback: {
        positive: "Magbigay ng positibong feedback para sa resultang ito",
        negative: "Magbigay ng negatibong feedback para sa resultang ito",
        hasFeedback: "May feedback ang resultang ito"
      },
      emptyMessages: {
        review: "Walang kasaysayan ng pagsusuri pa",
        generate: "Walang kasaysayan ng pagbubuo pa",
        compare: "Walang kasaysayan ng paghahambing pa",
        match: "Walang kasaysayan ng pagtutugma pa"
      },
      deleteConfirmation: "Sigurado ka bang gusto mong tanggalin ang item na ito?",
      history: "Kasaysayan",
      allUsers: "Lahat ng mga user"
    }
  }

  // Add Settings extensions for Asian languages
  if (resources.zh.common.settings) {
    Object.assign(resources.zh.common.settings, {
      currentPassword: "当前密码",
      newPassword: "新密码",
      confirmPassword: "确认密码",
      save: "保存",
      system: "系统",
      lightMode: "浅色模式",
      darkMode: "深色模式",
      deleteAccountDescription: "永久删除您的数据和与您账户相关的所有内容。",
      delete: "删除"
    })
  }

  if (resources.ja.common.settings) {
    Object.assign(resources.ja.common.settings, {
      currentPassword: "現在のパスワード",
      newPassword: "新しいパスワード",
      confirmPassword: "パスワードを確認",
      save: "保存",
      system: "システム",
      lightMode: "ライトモード",
      darkMode: "ダークモード",
      deleteAccountDescription: "あなたのデータとアカウントに関連するすべてを永久に削除します。",
      delete: "削除"
    })
  }

  if (resources.hi.common.settings) {
    Object.assign(resources.hi.common.settings, {
      currentPassword: "वर्तमान पासवर्ड",
      newPassword: "नया पासवर्ड",
      confirmPassword: "पासवर्ड की पुष्टि करें",
      save: "सेव करें",
      system: "सिस्टम",
      lightMode: "लाइट मोड",
      darkMode: "डार्क मोड",
      deleteAccountDescription: "अपना डेटा और अपने खाते से जुड़ी हर चीज़ को स्थायी रूप से हटा दें।",
      delete: "हटाएं"
    })
  }

  if (resources.th.common.settings) {
    Object.assign(resources.th.common.settings, {
      currentPassword: "รหัสผ่านปัจจุบัน",
      newPassword: "รหัสผ่านใหม่",
      confirmPassword: "ยืนยันรหัสผ่าน",
      save: "บันทึก",
      system: "ระบบ",
      lightMode: "โหมดสว่าง",
      darkMode: "โหมดมืด",
      deleteAccountDescription: "ลบข้อมูลของคุณและทุกสิ่งที่เกี่ยวข้องกับบัญชีของคุณอย่างถาวร",
      delete: "ลบ"
    })
  }

  if (resources.vi.common.settings) {
    Object.assign(resources.vi.common.settings, {
      currentPassword: "Mật khẩu hiện tại",
      newPassword: "Mật khẩu mới",
      confirmPassword: "Xác nhận mật khẩu",
      save: "Lưu",
      system: "Hệ thống",
      lightMode: "Chế độ sáng",
      darkMode: "Chế độ tối",
      deleteAccountDescription: "Xóa vĩnh viễn dữ liệu của bạn và mọi thứ liên quan đến tài khoản của bạn.",
      delete: "Xóa"
    })
  }

  if (resources.id.common.settings) {
    Object.assign(resources.id.common.settings, {
      currentPassword: "Kata Sandi Saat Ini",
      newPassword: "Kata Sandi Baru",
      confirmPassword: "Konfirmasi Kata Sandi",
      save: "Simpan",
      system: "Sistem",
      lightMode: "Mode Terang",
      darkMode: "Mode Gelap",
      deleteAccountDescription: "Hapus data Anda dan semua yang terkait dengan akun Anda secara permanen.",
      delete: "Hapus"
    })
  }

  if (resources.ms.common.settings) {
    Object.assign(resources.ms.common.settings, {
      currentPassword: "Kata Laluan Semasa",
      newPassword: "Kata Laluan Baru",
      confirmPassword: "Sahkan Kata Laluan",
      save: "Simpan",
      system: "Sistem",
      lightMode: "Mod Terang",
      darkMode: "Mod Gelap",
      deleteAccountDescription: "Padam data anda dan segala yang berkaitan dengan akaun anda secara kekal.",
      delete: "Padam"
    })
  }

  if (resources.tl.common.settings) {
    Object.assign(resources.tl.common.settings, {
      currentPassword: "Kasalukuyang Password",
      newPassword: "Bagong Password",
      confirmPassword: "Kumpirmahin ang Password",
      save: "I-save",
      system: "Sistema",
      lightMode: "Light Mode",
      darkMode: "Dark Mode",
      deleteAccountDescription: "Permanenteng burahin ang inyong data at lahat ng nauugnay sa inyong account.",
      delete: "Burahin"
    })
  }
}
