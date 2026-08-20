import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv
from sales_logger import log_sale

load_dotenv()

def parse_command_with_llm(user_cmd: str):
    api_key = os.getenv("GEMINI_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = """คุณคือ AI Agent แปลงคำสั่งภาษาไทยเป็น Tool Call 
ให้อ่านคำสั่งแล้วตอบกลับเป็น JSON รูปแบบนี้เท่านั้น ห้ามมีข้อความอื่น:
{
    "tool": "log_sale",
    "args": {
        "menu": "ชื่อเมนู",
        "qty": จำนวนที่เป็นตัวเลข integer,
        "price": ราคาต่อชิ้นที่เป็นตัวเลข float
    }
}"""

    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_cmd}
        ],
        "temperature": 0.0
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    res_json = response.json()
    content = res_json['choices'][0]['message']['content']
    
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
        
    return json.loads(content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmd", type=str, required=True)
    args = parser.parse_args()
    
    user_cmd = args.cmd
    
    # [user]
    print(f"[user] {user_cmd}")
    
    try:
        tool_call = parse_command_with_llm(user_cmd)
        
        # [llm]
        tool_name = tool_call.get("tool")
        tool_args = tool_call.get("args", {})
        menu = tool_args.get("menu")
        qty = int(tool_args.get("qty", 0))
        price = float(tool_args.get("price", 0))
        
        print(f'[llm] tool_call: {tool_name}(menu="{menu}", qty={qty}, price={int(price) if price.is_integer() else price})')
        
        # [tool] & [assistant]
        try:
            result = log_sale(menu=menu, qty=qty, price=price)
            print(f"[tool] return: {result}")
            print(f"[assistant] {result}")
        except Exception as exc:
            print(f"[tool] error: {type(exc).__name__}: {exc}")
            print(f"[assistant] ขออภัยค่ะ ทำรายการไม่สำเร็จ รอสักครู่แล้วลองอีกครั้งนะคะ")
            sys.exit(1)
            
    except Exception as exc:
        print(f"[tool] error: {type(exc).__name__}: {exc}")
        print(f"[assistant] ขออภัยค่ะ ไม่สามารถเข้าใจคำสั่งได้")
        sys.exit(1)

if __name__ == "__main__":
    main()