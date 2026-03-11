from flask import current_app
import os
from google import genai


class GeminiService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            print("⚠ GEMINI API key missing")
            self.client = None
            return

        try:
            # Initialize Gemini client
            self.client = genai.Client(api_key=api_key)

        except Exception as e:
            print(f"Gemini initialization error: {e}")
            self.client = None


    def get_response(self, prompt):

        if not self.client:
            return "Gemini AI service is not configured."

        try:

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if response and response.text:
                return response.text

            return "No response from AI."

        except Exception as e:
            return f"AI Error: {str(e)}"


    def get_disease_info(self, disease_name):

        prompt = f"""
You are an agricultural expert.

Explain the plant disease: {disease_name}

Provide:
1. Simple explanation
2. Cause
3. Treatment
4. Prevention

Keep it short and farmer-friendly.
"""

        return self.get_response(prompt)


    def get_farming_advice(self, weather_data):

        prompt = f"""
Weather conditions:

{weather_data}

Give practical farming advice for farmers based on this weather.
"""

        return self.get_response(prompt)


    def get_market_advice(self, crop_name, predictions):

        prompt = f"""
Crop: {crop_name}

Predicted market prices for next months:
{predictions}

Advise the farmer:

- Should they sell now or wait?
- Why?

Keep the advice simple and practical.
"""

        return self.get_response(prompt)


    def translate_and_chat(self, query, language):

        prompt = f"""
You are an agricultural expert chatbot.

Answer the following farmer question in {language} language.

Question:
{query}

Give a clear and simple answer.
"""

        return self.get_response(prompt)
