import os
import json
import re
from bs4 import BeautifulSoup

def extract_questions_from_html(file_path, start_index):
    """ 解析 HTML 並回傳題目 JSON 格式 """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    questions = []

    for idx, question_div in enumerate(soup.find_all("div", class_="ExExam"), start=start_index):
        # 題目
        question_text = ""
        question_title = question_div.find("div", class_="ExTit")
        if question_title:
            question_text = question_title.get_text(strip=True)
            # 移除開頭的數字與可能的標點符號 (e.g., "1. "、"2) ")
            question_text = re.sub(r"^\d+[\.\s\)]*", "", question_text)

        # 選項
        options = {}
        option_divs = question_div.find("div", class_="ExSel1")
        if option_divs:
            for option_div in option_divs.find_all("div", recursive=False):
                bold_tag = option_div.find("b")  # 找到 <b> 標籤
                if bold_tag:
                    option_key = bold_tag.get_text(strip=True)[0]  # 取 "A", "B", "C", "D"
                    option_value = option_div.get_text(strip=True).replace(bold_tag.get_text(strip=True), "", 1).strip()
                    options[option_key] = option_value

        # Debug 訊息 (確認選項是否成功提取)
        if not options:
            print(f"[DEBUG] 選項解析失敗 - 檔案: {file_path}, 題目: {question_text}")
            print(f"[DEBUG] ExSel1 內部 HTML: {option_divs}")

        # 正確答案
        correct_answers = []
        answer_div = question_div.find("div", class_="ExSel2")
        if answer_div:
            match = re.search(r"正確解答為：\s*([A-D]+)", answer_div.get_text())
            if match:
                correct_answers = list(match.group(1))  # 可能是單選或多選

        # 儲存題目
        questions.append({
            "question_number": idx,
            "question": question_text,
            "options": options,
            "correct_answer": correct_answers
        })

    return questions

def scan_folder_for_html(folder_path):
    """ 遞迴掃描資料夾內所有 HTML 檔案，解析所有題目並合併成一個 JSON """
    all_questions = []
    question_index = 1  # 初始題號

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                print(f"[INFO] 解析檔案：{file_path}")

                # 讀取 HTML 檔案
                questions = extract_questions_from_html(file_path, question_index)
                
                # 更新題號 (確保不重複)
                question_index += len(questions)

                all_questions.extend(questions)

    # 輸出合併後的 JSON
    output_file = os.path.join(folder_path, "questions.json")
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(all_questions, json_file, ensure_ascii=False, indent=4)

    print(f"✅ 轉換完成！共 {len(all_questions)} 題，JSON 檔案已儲存至 {output_file}")


# 設定掃描的資料夾路徑
folder_path = "Z:\gihub desktop\multiple_choice_training\multiple_choice\extracting\html_src_cloud"  # 修改為你的 HTML 檔案資料夾
scan_folder_for_html(folder_path)
