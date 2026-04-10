import google.generativeai as genai
from django.conf import settings
from core.models import SystemSettings
import os

class GeminiAdvisor:
    def __init__(self):
        # 1. Try environment variable first
        api_key = os.getenv('GOOGLE_API_KEY')
        
        # 2. If not found, try Database
        if not api_key:
            try:
                settings_obj = SystemSettings.load()
                api_key = settings_obj.gemini_api_key
            except Exception:
                pass

        if not api_key:
            print("WARNING: GOOGLE_API_KEY not found in environment or database.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def generate_solution(self, object_type, severity):
        """
        Generates a maintenance suggestion for a specific hazard.
        """
        if not self.model:
            return "Error: Gemini API Key not configured."

        prompt = f"""
        Act as an airport safety expert. 
        A hazard has been detected on the runway:
        - Type: {object_type}
        - Risk Level: {severity}

        Provide a concise, immediate action plan (1-2 sentences max) for the maintenance crew to resolve this specific issue safely.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error connecting to Gemini: {str(e)}"
