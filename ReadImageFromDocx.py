from docx import Document

# 載入教案
def load_teaching_plan(docx_path):
    doc = Document(docx_path)
    teaching_plan = []
    step_data = {"step": "", "content": []}

    for paragraph in doc.paragraphs:
        # 檢查是否包含 "step" 關鍵字來開始新的步驟
        if "step" in paragraph.text.lower():
            # 如果已經有內容，則先添加到教案中
            if step_data["step"] or step_data["content"]:
                teaching_plan.append(step_data)
            
            # 新的步驟段落
            step_data = {"step": paragraph.text.strip(), "content": []}
        
        # 讀取 paragraph 中的每個 run
        for run in paragraph.runs:
            # 檢查是否有圖片
            drawing_elements = run._element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
            
            if drawing_elements:
                # 處理圖片
                for drawing in drawing_elements:
                    image_id = drawing.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                    
                    if image_id:
                        image_part = doc.part.related_parts[image_id]
                        image_data = image_part.blob
                        
                        # 將圖片的二進位數據直接加入內容
                        step_data["content"].append({"type": "image", "value": image_data})
            
            # 若為文字，直接加入內容
            elif run.text.strip():
                step_data["content"].append({"type": "text", "value": run.text.strip()})
    
    # 將最後的步驟添加到教案中
    if step_data["step"] or step_data["content"]:
        teaching_plan.append(step_data)

    return teaching_plan

# 使用範例
docx_path = "組裝實作PPT.docx"
teaching_plan = load_teaching_plan(docx_path)

# 顯示結果
for step in teaching_plan:
    print("步驟:", step["step"])
    for item in step["content"]:
        if item["type"] == "text":
            print( item["value"])
        elif item["type"] == "image":
            print("圖片二進位數據:", item["value"][:10], "...")  # 只顯示前10位資料以便確認
