from ai_engine.gemini_service import GeminiAdvisor
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rvms_backend.settings")
django.setup()

def test_gemini():
    advisor = GeminiAdvisor()
    if not advisor.model:
        print("Skipping test: No API Key found.")
        return

    print("Testing Gemini API...")
    suggestion = advisor.generate_solution(object_type="FOD (Metal Object)", severity="HIGH")
    print(f"\n[Scenario]: High Risk FOD Detected")
    print(f"[Gemini Suggestion]: {suggestion}")

if __name__ == '__main__':
    test_gemini()
