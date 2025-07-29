import sys
import google.generativeai as genai

def main():
    # إعداد المفتاح مباشرة في الكود
    api_key = "AIzaSyAwrjZJBcNHS0mRnSkJgzhUm4ulFI1Q8tc"
    genai.configure(api_key=api_key)

    # تهيئة الموديل
    model = genai.GenerativeModel("gemini-2.5-flash")

    print("مرحبًا في Zynapse10! اكتب سؤالك، أو 'exit' للخروج.")
    while True:
        prompt = input("Zynapse10> ").strip()
        if prompt.lower() in ("exit", "quit"):
            print("إلى اللقاء!")
            break
        try:
            response = model.generate_content(prompt)
            print(response.text)
        except Exception as e:
            print(f"حدث خطأ أثناء الاتصال بـ Gemini: {e}")

if __name__ == "__main__":
    main()
