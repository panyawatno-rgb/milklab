import os
import requests
from dotenv import load_dotenv

load_dotenv()

class MilkLabCaptionGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ ไม่พบ GEMINI_API_KEY ในไฟล์ .env")

    def generate(self, topic: str, vibe_good: bool = False) -> str:
        prompt = f"""
        ช่วยคิดแคปชันสำหรับโพสต์โปรโมตเมนู "{topic}" ของร้าน MilkLab° โดยแบ่งออกเป็น 3 รูปแบบตามข้อกำหนดดังนี้ (ห้ามใช้ภาษาอังกฤษในการเขียนแคปชัน ให้ใช้ภาษาไทยทั้งหมด):
        
        1. รูปแบบ Cute: ใช้หัวข้อคำว่า [label style='color: #FFB61C;']Section 1: Cute Output (Sparkle Mode)[/label] เขียนฟีลน่ารัก อบอุ่น ละมุน มีความสดใส มี positive energy
        2. รูปแบบ Minimal: ใช้หัวข้อคำว่า [label style='color: #87CEFA;']Section 2: Minimal Output[/label] เขียนแบบสั้น เรียบง่าย กระชับ ตรงประเด็น น้อยแต่มาก
        3. รูปแบบ Gen-Z: ใช้หัวข้อคำว่า [label style='color: #FDFD96;']Section 3: Gen-Z Output (Slang-ish)[/label] เป็นหัวข้อ ใช้ภาษาวัยรุ่น ตัวมารดา อินเทรนด์ เช่น ฟีล, ตัวแม่, no cap, แบบฉ่ำ
        
        ข้อกำหนดการแสดงผล:
        - ให้ขึ้นต้นแต่ละ Section ด้วยเครื่องหมาย *** คั่นระหว่างกัน
        - เขียนคำตอบของแต่ละสไตล์เป็นภาษาไทยที่เข้ากับมู้ดนั้นๆ มี Emoji และ Hashtag ให้เหมาะสม
        """

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "google/gemini-2.5-flash",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 1000
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            res_json = response.json()
            
            if response.status_code == 200:
                return res_json['choices'][0]['message']['content']
            else:
                return f"❌ ข้อผิดพลาดจากเซิร์ฟเวอร์ ({response.status_code}): {res_json.get('error', {}).get('message', 'Unknown Error')}"
        except Exception as e:
            return f"❌ เกิดข้อผิดพลาดในระบบเน็ตเวิร์ก: {str(e)}"