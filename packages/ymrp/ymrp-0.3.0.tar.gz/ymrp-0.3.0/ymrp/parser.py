from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .constants import (
    BIG_TIMEOUT,
    MEDIUM_TIMEOUT,
    MONTHS,
    REVIEW,
    REVIEW_VIEW_EXPAND,
    REVIEWS_CONTAINER,
    SMALL_TIMEOUT,
    VERY_SMALL_TIMEOUT,
)


class Parser:
    def get_reviews_html_content(self, url: str) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            reviews_container = page.locator(REVIEWS_CONTAINER)
            page.wait_for_selector(REVIEWS_CONTAINER, timeout=BIG_TIMEOUT, state='visible')

            reviews_container.click(button='left')

            last_review = None
            prev_review_count, review_count = 0, 0

            while True:
                page.wait_for_timeout(MEDIUM_TIMEOUT)

                last_review = page.locator(REVIEW)
                review_count = last_review.count()
                last_review = last_review.last

                last_review.click(button='left')

                if prev_review_count == review_count:
                    break

                prev_review_count = review_count

            more_buttons = page.locator(REVIEW_VIEW_EXPAND).all()
            iterations = 0
            while iterations < 10 or len(more_buttons) != 0:
                more_buttons = page.locator(REVIEW_VIEW_EXPAND).all()
                for button in more_buttons:
                    try:
                        button.click(button='left', timeout=VERY_SMALL_TIMEOUT)
                    except Exception:
                        pass
                iterations += 1

            page.wait_for_timeout(SMALL_TIMEOUT)

            reviews_container = page.locator(REVIEWS_CONTAINER)
            return reviews_container.inner_html()

    def convert_date(self, date_str: str) -> str:
        parts = date_str.split()
        if len(parts) == 3:
            day, month_name, year = parts
        else:
            day, month_name = parts
            year = str(datetime.now().year)
        month = MONTHS.get(month_name, '01')
        return f'{year}-{month}-{day.zfill(2)}'

    def parse_yandex_review(
        self,
        review: BeautifulSoup,
    ) -> dict[str, Any]:
        review_data = {}

        name = review.find('span', itemprop='name')
        if name:
            review_data['name'] = name.text.strip()

        rating = review.find('meta', itemprop='ratingValue')
        if rating:
            review_data['rating'] = int(float(rating['content']))

        review_text = review.find(
            'span',
            class_='spoiler-view__text-container',
        )
        if review_text:
            review_data['text'] = review_text.text.strip()

        date = review.find(
            'span',
            class_='business-review-view__date',
        )
        if date:
            review_data['date'] = self.convert_date(date.text.strip())

        return review_data

    def parse_yandex_reviews(
        self,
        html_content: str = '',
    ) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        review_cards = soup.find_all(
            'div',
            class_='business-reviews-card-view__review',
        )
        reviews: list[dict[str, Any]] = []
        for review in review_cards:
            try:
                reviews.append(self.parse_yandex_review(review))
            except Exception:
                pass
        return reviews

    def get_yandex_reviews(self, url: str) -> list[dict[str, Any]]:
        return self.parse_yandex_reviews(
            html_content=self.get_reviews_html_content(url)
        )
