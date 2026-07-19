import argparse
import sys
from generator import MilkLabCaptionGenerator

def main():
    parser = argparse.ArgumentParser(
        description="🥛 MilkLab° Caption Generator CLI Tool"
    )
    
    # กำหนด Arguments ตามตัวอย่างท้ายภาพใบงาน
    parser.add_argument(
        "--captions", 
        type=str, 
        required=True, 
        help="ระบุหัวข้อ เมนู หรือโปรโมชันที่ต้องการคิดแคปชัน"
    )
    
    parser.add_argument(
        "--vibe-good", 
        action="store_true", 
        help="เปิดใช้งานโหมดมู้ดดี พลังบวก อบอุ่น"
    )

    args = parser.parse_args()

    print("\n" + "="*50)
    print("🥛  WELCOME TO MILKLAB° CAPTION GENERATOR  🥛")
    print("="*50)
    print(f"⏳ AI กำลังเจนแคปชันหัวข้อ: '{args.captions}'...")
    print("-"*50)

    try:
        bot = MilkLabCaptionGenerator()
        caption_result = bot.generate(topic=args.captions, vibe_good=args.vibe_good)
        print(caption_result)
        print("="*50)
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()