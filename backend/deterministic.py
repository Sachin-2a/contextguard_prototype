import re

# Verhoeff algorithm tables for structured identification checksum validation
d = [[0,1,2,3,4,5,6,7,8,9], [1,2,3,4,0,6,7,8,9,5], [2,3,4,0,1,7,8,9,5,6], [3,4,0,1,2,8,9,5,6,7], [4,0,1,2,3,9,5,6,7,8], [5,9,8,7,6,0,4,3,2,1], [6,5,9,8,7,1,0,4,3,2], [7,6,5,9,8,2,1,0,4,3], [8,7,6,5,9,3,2,1,0,4], [9,8,7,6,5,4,3,2,1,0]]
p = [[0,1,2,3,4,5,6,7,8,9], [1,5,7,6,2,8,3,0,9,4], [5,8,0,3,7,9,6,1,4,2], [8,9,1,6,0,4,3,5,2,7], [9,4,5,3,1,2,6,8,7,0], [4,2,8,6,5,7,3,9,0,1], [2,7,9,3,8,0,6,4,1,5], [7,0,4,6,9,1,3,2,5,8]]

def validate_verhoeff(num_str: str) -> bool:
    c = 0
    reversed_num = [int(ch) for ch in reversed(num_str)]
    for i, n in enumerate(reversed_num):
        c = d[c][p[i % 8][n]]
    return c == 0

def detect_structured_ids(text: str) -> list:
    findings = []
    
    # PAN Card Regex pattern matching
    pan_matches = re.finditer(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text)
    for m in pan_matches:
        findings.append({"type": "PAN_CARD", "span": m.span(), "value": m.group()})
        
    return findings
