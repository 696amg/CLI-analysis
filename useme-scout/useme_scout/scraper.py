from dataclasses import dataclass, asdict
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
 
 
BASE_URL = "https://useme.com"
LISTING_URL = "https://useme.com/pl/jobs/"  # подставь реальный урл раздела, который парсишь
 
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
 
 
@dataclass
class Job:
    title: str
    description: str
    budget: str | None
    client_name: str | None
    url: str
    scraped_at: str
 
    def to_dict(self) -> dict:
        return asdict(self)
 
 
def fetch_page(url: str) -> str:
    """Скачивает HTML страницы."""
    with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
 
 
def parse_jobs(html: str) -> list[Job]:
    """
    Парсит HTML и возвращает список заказов.
 
    TODO: замени селекторы ".job-card", ".job-title" и т.д. на реальные,
    посмотрев структуру страницы через DevTools (F12 -> Elements).
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[Job] = []
 
    cards = soup.select(".job-card")  # <-- заменить на реальный селектор карточки заказа
 
    for card in cards:
        title_el = card.select_one(".job-title")
        desc_el = card.select_one(".job-description")
        budget_el = card.select_one(".job-budget")
        client_el = card.select_one(".job-client-name")
        link_el = card.select_one("a")
 
        if not title_el or not link_el:
            continue
 
        href = link_el.get("href", "")
        full_url = href if href.startswith("http") else BASE_URL + href
 
        jobs.append(
            Job(
                title=title_el.get_text(strip=True),
                description=desc_el.get_text(strip=True) if desc_el else "",
                budget=budget_el.get_text(strip=True) if budget_el else None,
                client_name=client_el.get_text(strip=True) if client_el else None,
                url=full_url,
                scraped_at=datetime.now().isoformat(timespec="seconds"),
            )
        )
 
    return jobs
 
 
def scan(url: str = LISTING_URL) -> list[Job]:
    """Главная функция: скачать + распарсить."""
    html = fetch_page(url)
    return parse_jobs(html)
 
 
if __name__ == "__main__":
    # Быстрый ручной тест: python -m useme_scout.scraper
    results = scan()
    print(f"Найдено объявлений: {len(results)}")
    for job in results[:5]:
        print(f"- {job.title} | {job.budget}")