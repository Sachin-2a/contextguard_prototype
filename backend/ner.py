from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()

def detect_entities(text: str) -> list:
    # Detects names, locations, organizations, phone numbers[cite: 4]
    results = analyzer.analyze(text=text, language='en')
    findings = []
    for r in results:
        findings.append({
            "type": r.entity_type,
            "span": (r.start, r.end),
            "value": text[r.start:r.end]
        })
    return findings
