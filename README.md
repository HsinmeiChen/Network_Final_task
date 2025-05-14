# Network_Final_task

執行步驟：
1. 安裝套件：pip install -r requirements.txt
2. 設定 OpenAI 金鑰：建立 config.ini 檔案或直接在 settings.py 中編輯
3. 啟動伺服器：python manage.py runserver
4. 打開瀏覽器
5. 輸入帳號密碼(任意)


教案設計格式（.docx）：在 config.ini 中"doc = sample1.docx"
可支援【圖片】與【HTML 標籤】，系統會自動嵌入呈現
✅ 答案正確時進入下一步，錯誤時觸發 Guide 引導流程


GPT 模式說明：
後端設定選擇 Assistant 模式
OpenAI_Completion：單題互動模式，無上下文、快速回應、格式清楚(例如：系統中的遊戲情境)
OpenAI_Assistant：多輪對話模式，有上下文記憶、適合逐步引導

系統流程：
使用者輸入 → views.py 處理輸入 → 呼叫 ask_chatgpt() → Service_Assistant 根據模式選擇 Assistant
 → OpenAI_Completion → OpenAI 回應 JSON → 顯示在 chat.html 前端畫面
 → OpenAI_Assistant  → Assistant API 回應串
