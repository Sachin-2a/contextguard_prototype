import json
import os
import google.generativeai as genai

# Configure your Gemini API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def analyze_context(text: str, context: dict) -> dict:
    prompt = f"""
    Analyze the following text based on the provided context envelope. 
    Identify if the text contains sensitive information given who is asking and where it is going.
    Text: "{text}"
    Context: {json.dumps(context)}
    
    Return ONLY a JSON object with:
    - category: The type of sensitive data (e.g., "Health Data", "HR Salary", "None")
    - risk_level: "High", "Medium", "Low", or "None"
    - reason: Why it is or isn't sensitive in this context.
    - findings: A list of dicts with "type", and "value" of the exact sensitive substring.
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    try:
        # Strip markdown formatting from LLM response if present
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json) # Structured JSON output[cite: 4]
    except:
        return {"category": "Error", "risk_level": "High", "reason": "LLM Parsing Failed", "findings": []}
