from llm_setup import gemini_llm

def calculate_risk_score(text: str):

    prompt = f"""
Analyze this contract and give risk scores (0-100):

Return ONLY JSON:
{{
  "legal": number,
  "finance": number,
  "compliance": number
}}

Contract:
{text[:2000]}
"""

    try:
        response = gemini_llm.invoke(prompt).content

        import json, re
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if match:
            data = json.loads(match.group())
            return (
                data.get("legal", 50),
                data.get("finance", 50),
                data.get("compliance", 50)
            )

    except:
        pass

    # fallback
    return 50, 50, 50