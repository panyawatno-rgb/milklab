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
        style_description = (
            "ฟีลดี พลังบวก อบอุ่น ละมุนหัวใจ ละเอียดอ่อน และเข้าถึงง่าย" 
            if vibe_good else 
            "สนุกสนาน กวน ๆ วัยรุ่น ตลก และอินเทรนด์"
        )

        prompt = f"""
        คุณเป็น Social Media Manager และ Content Creator ประจำร้าน "MilkLab°" 
        ซึ่งเป็นคาเฟ่นมสดและเครื่องดื่มสุดพรีเมียมของคนรุ่นใหม่ 
        
        โจทย์: ช่วยคิดแคปชันสำหรับโพสต์โปรโมตบน Social Media (Facebook/Instagram/TikTok)
        หัวข้อ/เนื้อหาโพสต์: "{topic}"
        โทนเสียงและอารมณ์ (Mood & Tone): {style_description}
        
        ข้อกำหนดในการเขียน:
        1. เขียนเป็นภาษาไทยที่ลื่นไหล น่าอ่าน มีการใช้ Emoji ที่เข้ากับเนื้อหา
        2. มีคำเชิญชวน (Call to Action) ให้มาลองที่ร้าน MilkLab°
        3. แปะแฮชแท็กท้ายโพสต์ เช่น #MilkLab #คาเฟ่นมสด
        4. นำเสนอผลลัพธ์เป็นทางเลือกให้ผู้ใช้ 3 แบบ (แบบสั้น, แบบยาวเน้นสตอรี่, แบบสั้นกระชับสำหรับ TikTok)
        """

        # ยิงเข้า Gateway ของ OpenRouter เพื่อเรียกใช้งานโมเดล Gemini 1.5 Flash ของ Google
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
            "temperature": 0.7,
            "max_tokens": 1000  # เพิ่มบรรทัดนี้เพื่อจำกัดการใช้เครดิตให้พอดี
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
