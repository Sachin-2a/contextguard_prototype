import json
import os
import google.generativeai as genai

def analyze_context(text: str, context: dict) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    
    prompt = f"""
    Analyze the following text based on the provided context envelope. 
    Identify if the text contains sensitive information given who is asking and where it is going.
    Text: "{text}"
    Context: {json.dumps(context)}
    
    Return ONLY a valid JSON object with:
    - category: The type of sensitive data (e.g., "Health Data", "HR Salary", "None")
    - risk_level: "High", "Medium", "Low", or "None"
    - reason: Why it is or isn't sensitive in this context.
    - findings: A list of dicts with "type", and "value" of the exact sensitive substring.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except Exception as e:
        # Fallback response if API key isn't set or network fails during local testing
        return {
            "category": "General Text",
            "risk_level": "Low",
            "reason": "Fallback mode active (Check GEMINI_API_KEY configuration).",
            "findings": []
        }
