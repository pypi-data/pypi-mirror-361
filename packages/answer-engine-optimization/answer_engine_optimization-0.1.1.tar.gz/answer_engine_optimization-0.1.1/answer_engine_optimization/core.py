
import json
from bs4 import BeautifulSoup

class AEOEngine:
    def __init__(self):
        self.faqs = []

    def add_faq(self, question, answer):
        self.faqs.append({"question": question.strip(), "answer": answer.strip()})

    def get_faqs(self):
        return self.faqs

    def generate_faq_schema(self):
        if not self.faqs:
            return json.dumps({"error": "No FAQs available. Add FAQs first."}, indent=2)
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq["answer"]
                    }
                }
                for faq in self.faqs
            ]
        }
        return json.dumps(schema, indent=2)

    def generate_quick_answer(self, text):
        return f"<div class='quick-answer'><strong>Quick Answer:</strong> {text}</div>"

    def check_aeo_friendly(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        checks = {
            "title_present": bool(soup.title),
            "faq_schema_present": '"@type": "FAQPage"' in html_content,
            "quick_answer_present": "quick-answer" in html_content
        }
        score = sum(checks.values())
        checks["score"] = f"{score}/3"
        return checks
