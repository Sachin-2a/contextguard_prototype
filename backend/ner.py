from presidio_analyzer import AnalyzerEngine
import spacy
import subprocess

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

analyzer = AnalyzerEngine()

def detect_entities(text: str) -> list:
    results = analyzer.analyze(text=text, language='en')
    findings = []
    for r in results:
        findings.append({
            "type": r.entity_type,
            "span": (r.start, r.end),
            "value": text[r.start:r.end]
        })
    return findings
