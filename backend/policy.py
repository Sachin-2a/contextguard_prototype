import uuid
from backend.vault import save_to_vault

POLICY_MATRIX = {
    "PAN_CARD": {"default": "Pseudonymize"},
    "HR Salary": {
        "HR_to_Employee": "Allow",
        "External_API": "Redact"
    },
    "Health Data": {"default": "Redact"},
    "PERSON": {"default": "Pseudonymize"}
}

def apply_policy(text: str, findings: list, context: dict):
    # Sort findings in reverse to preserve string indices during updates
    valid_findings = [f for f in findings if "span" in f or "value" in f]
    valid_findings.sort(key=lambda x: x.get("span", (0,0))[0], reverse=True)
    
    final_text = text
    actions_taken = []
    
    for f in valid_findings:
        entity_type = f.get("type", "UNKNOWN")
        original_value = f.get("value", "")
        
        if not original_value:
            continue
            
        rules = POLICY_MATRIX.get(entity_type, {"default": "Redact"})
        destination = context.get("destination", "External_API")
        action = rules.get(destination, rules.get("default", "Redact"))
        
        if action == "Allow":
            actions_taken.append({"entity": entity_type, "action": "Allow"})
            continue
            
        elif action == "Redact":
            final_text = final_text.replace(original_value, f"[REDACTED {entity_type}]")
            actions_taken.append({"entity": entity_type, "action": "Redact"})
            
        elif action == "Pseudonymize":
            token = f"[{entity_type}_{str(uuid.uuid4())[:4]}]"
            save_to_vault(token, original_value)
            final_text = final_text.replace(original_value, token)
            actions_taken.append({"entity": entity_type, "action": "Pseudonymize"})
            
    return final_text, actions_taken
