"""
эвристики для оценки риска объявления (0-100, чем выше — тем подозрительнее).
Логика простая легко читать легко добавить новое правило,
легко покрыть тестами (см. tests/test_fraud_detector.py).
"""
 
import re
from useme_scout.scraper import Job
 
 
SUSPICIOUS_PHRASES = [
    "напишите в телеграм",
    "пишите в телеграмм",
    "write on telegram",
    "contact via whatsapp",
    "оплата вне платформы",
    "payment outside",
    "переведите предоплату",
    "send advance payment",
]
 
VAGUE_DESCRIPTION_MIN_LEN = 40  # символов — короче этого считаем "мало деталей"
 
 
def score_job(job: Job) -> tuple[int, list[str]]:
    """
    Возвращает (score, причины).
    score: 0-100, где 100 — максимально подозрительно.
    """
    score = 0
    reasons: list[str] = []
 
    text = f"{job.title} {job.description}".lower()
 
    # Правило 1 - подозрительные фразы про оплату вне платформы
    for phrase in SUSPICIOUS_PHRASES:
        if phrase in text:
            score += 40
            reasons.append(f"Найдена подозрительная фраза: «{phrase}»")
            break  # не начисляем за каждую фразу отдельно, чтобы не раздувать score
 
    # Правило 2 - слишком короткое/расплывчатое описание
    if len(job.description.strip()) < VAGUE_DESCRIPTION_MIN_LEN:
        score += 20
        reasons.append("Очень короткое описание задачи — мало деталей")
 
    # Правило 3 - бюджет указан, но выглядит нереалистично (пустой/0/не указан явно)
    if job.budget is None or job.budget.strip() in ("", "0"):
        score += 15
        reasons.append("Бюджет не указан или равен нулю")
 
    # Правило 4 - в описании просят контакт напрямую (email/телефон в открытую)
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
        score += 10
        reasons.append("В описании явно указан email — возможен обход платформы")
 
    if re.search(r"(\+?\d[\d\s\-()]{7,}\d)", text):
        score += 10
        reasons.append("В описании явно указан номер телефона")
 
    return min(score, 100), reasons
 
 
def is_risky(job: Job, threshold: int = 50) -> bool:
    score, _ = score_job(job)
    return score >= threshold
 