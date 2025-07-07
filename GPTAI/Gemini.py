import google.generativeai as genai
import settings

class Gemini:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)

    def return_answer(self, query_type, question_value):
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(question_value)
        return response.text, []
