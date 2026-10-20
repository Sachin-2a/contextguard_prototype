# backend/policy.py
import uuid
from vault import save_to_vault

POLICY_MATRIX = {
    "NATIONAL_ID": {"default": "Redact"},
    "PAN_CARD": {"default": "Pseudonymize"},
    "Health Data": {"default": "Redact"},
    "HR Salary": {
        "HR_to_Employee": "Allow", #[cite: 2]
        "External_API": "Redact"
    }
}

def apply_policy(text: str, findings: list, context: dict):
    # Sort in reverse to prevent offset shifting during replacements
    findings.sort(key=lambda x: x.get("span", (0,0))[0] if "span" in x else 0, reverse=True)
    
    final_text = text
    actions_taken = []
    
    for f in findings:
        entity_type = f["type"]
        original_value = f["value"]
        
        # Look up policy
        rules = POLICY_MATRIX.get(entity_type, {"default": "Redact"})
        action = rules.get(context["destination"], rules["default"])
        
        if action == "Allow":
            actions_taken.append({"entity": entity_type, "action": "Allow"})
            continue
            
        elif action == "Redact":
            final_text = final_text.replace(original_value, f"[REDACTED {entity_type}]") #[cite: 3]
            actions_taken.append({"entity": entity_type, "action": "Redact"})
            
        elif action == "Pseudonymize":
            token = f"[PERSON_{str(uuid.uuid4())[:4]}]"
            save_to_vault(token, original_value)
            final_text = final_text.replace(original_value, token) #[cite: 4]
            actions_taken.append({"entity": entity_type, "action": "Pseudonymize"})
            
    return final_text, actions_taken
