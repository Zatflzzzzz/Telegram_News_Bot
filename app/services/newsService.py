from fastapi import requests
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import requests

from app.config.config import settings
from app.entities.model import User, NewsLog

def json_response(
        success: bool,
        message: str,
        data=None):

    return {
        "success": success,
        "message": message,
        "data": data
    }

def get_news(category: str):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={settings.NEWS_API_KEY}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_last_news():
    url = f"https://newsapi.org/v2/everything?q=apple&from=2025-02-13&to=2025-02-13&sortBy=popularity&apiKey={settings.NEWS_API_KEY}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def add_news_log(
        db: Session,
        author: str,
        title: str,
        urlToImage: str,
        category: str,
        user_id: int):

    try:
        news_log = NewsLog(author=author, title=title, urlToImage=urlToImage, category=category, user_id=user_id)

        db.add(news_log)
        db.commit()
        db.refresh(news_log)

        return json_response(True, "News log added", {"id": news_log.id, "title": news_log.title})
    except SQLAlchemyError as e:

        db.rollback()
        return json_response(False, "Database error", str(e))