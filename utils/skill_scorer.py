import re
from collections import Counter


# 🔹 Normalize common skill variations
SKILL_SYNONYMS = {
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "llm": "large language models",
    "js": "javascript"
}


def normalize_text(text):
    text = text.lower()

    for short, full in SKILL_SYNONYMS.items():
        text = re.sub(rf"\b{short}\b", full, text)

    return text


def extract_keywords(text):
    """
    Extract only meaningful technical keywords
    """

    text = normalize_text(text)

    # 🔥 Only keep technical words
    allowed_keywords = {
        "python", "java", "c++", "javascript",
        "machine learning", "deep learning", "nlp",
        "tensorflow", "pytorch", "scikit-learn",
        "fastapi", "flask", "django",
        "docker", "redis", "aws",
        "react", "node", "api",
        "data structures", "algorithms",
        "dbms", "operating systems"
    }

    found = set()

    for skill in allowed_keywords:
        if skill in text:
            found.add(skill)

    return Counter(found)


def extract_skill_phrases(text):
    """
    Extract multi-word skill phrases like 'machine learning'
    """
    text = normalize_text(text)

    phrases = re.findall(r"\b[a-z]+(?:\s[a-z]+){1,2}\b", text)

    return set(phrases)


def compute_match_score(resume_text, job_text):
    """
    Advanced scoring using:
    - keyword overlap
    - phrase matching
    - importance weighting
    """

    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_text)

    resume_phrases = extract_skill_phrases(resume_text)
    job_phrases = extract_skill_phrases(job_text)

    # 🔹 Keyword overlap score
    common_keywords = set(resume_keywords.keys()) & set(job_keywords.keys())

    keyword_score = sum(min(resume_keywords[k], job_keywords[k]) for k in common_keywords)

    total_job_keywords = sum(job_keywords.values()) or 1

    keyword_match_ratio = keyword_score / total_job_keywords

    # 🔹 Phrase overlap score (more important)
    common_phrases = resume_phrases & job_phrases
    phrase_match_ratio = len(common_phrases) / (len(job_phrases) or 1)

    # 🔹 Weighted scoring
    score = int((0.6 * keyword_match_ratio + 0.4 * phrase_match_ratio) * 100)

    # 🔹 Missing important terms
    missing_keywords = set(job_keywords.keys()) - set(resume_keywords.keys())

    # 🔹 Strong areas
    strong_areas = list(common_keywords)[:10]

    return {
        "score": min(score, 100),
        "matched_keywords": list(common_keywords),
        "matched_phrases": list(common_phrases),
        "missing_keywords": list(missing_keywords)[:10],
        "strong_areas": strong_areas
    }


def get_priority(score):
    """
    Smarter decision logic
    """
    if score >= 85:
        return "🔥 HIGH APPLY (Strong Fit)"
    elif score >= 70:
        return "⚡ APPLY (Good Fit)"
    elif score >= 50:
        return "🧠 PREPARE & APPLY"
    elif score >= 30:
        return "📚 UPSKILL BEFORE APPLYING"
    else:
        return "❌ LOW MATCH"


def generate_action_plan(score, missing_skills):
    """
    Intelligent action guidance
    """

    if score >= 80:
        return "Focus on applying immediately and preparing for interviews."

    if not missing_skills:
        return "Strengthen your core concepts and apply confidently."

    top_skills = missing_skills[:3]

    return (
        f"Learn and practice: {', '.join(top_skills)}. "
        "Build at least 1 strong project and reapply."
    )