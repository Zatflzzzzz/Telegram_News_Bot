from fastapi import FastAPI, Depends, HTTPException, status

from app.config import dependencies
from app.entities.model import Base
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import dependencies
from app.dto.dto import UserDto, TokenDto, NewsDto
from app.entities.model import User
from app.factories.factory import UserFactory, TokenFactory, NewsFactory
from app.services import authService, newsService

import logging

from app.services.newsService import get_last_news

app = FastAPI()

Base.metadata.create_all(bind=dependencies.engine)

@app.post("/register", response_model=UserDto)
async def register_user(
        username: str,
        password: str,
        db: Session = Depends(dependencies.get_db)):

    logging.debug(f"Received registration request for username: {username, password}")

    result = authService.create_user(db, username, password)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return UserFactory.create_user_dto(username, password)

@app.post("/login", response_model=TokenDto)
async def login(
        username: str,
        password: str,
        db: Session = Depends(dependencies.get_db)):

    user = authService.authenticate_user(db, username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = authService.create_access_token(data={"sub": user.username})

    return TokenFactory.create_token_dto(access_token, "bearer")

@app.get("/get_news_by_category", response_model=List[NewsDto])
async def get_news_by_category(
        category: str,
        current_user: User = Depends(authService.get_current_user),
        db: Session = Depends(dependencies.get_db)):

    news_data = newsService.get_news(category)

    if not news_data or news_data.get("status") != "ok":
        raise HTTPException(status_code=400, detail="Failed to fetch news from NewsApi")

    articles = news_data.get("articles", [])[:3]

    news_list = []

    for article in articles:
        news_dto = NewsFactory.create_news_dto({
            "author": article.get("author"),
            "title": article.get("title"),
            "urlToImage": article.get("urlToImage"),
            "category": category,
            "user_id": current_user.id

        })

        news_list.append(news_dto)

        newsService.add_news_log(
            db,
            author=article.get("author"),
            title=article.get("title"),
            urlToImage=article.get("urlToImage"),
            category=category,
            user_id=current_user.id
        )

    return news_list

@app.get("/get_last_popular_news", response_model=List[NewsDto])
def get_last_popular_news(
        current_user: User = Depends(authService.get_current_user),
        db: Session = Depends(dependencies.get_db)):

    news_data = get_last_news()

    if not news_data or news_data.get("status") != "ok":
        raise HTTPException(status_code=400, detail="Failed to fetch news from NewsApi")

    articles = news_data.get("articles", [])[:3]

    news_list = []

    for article in articles:
        news_dto = NewsFactory.create_news_dto({
            "author": article.get("author"),
            "title": article.get("title"),
            "urlToImage": article.get("urlToImage"),
            "category": "",
            "user_id": current_user.id

        })

        news_list.append(news_dto)

        newsService.add_news_log(
            db,
            author=article.get("author"),
            title=article.get("title"),
            urlToImage=article.get("urlToImage"),
            category="",
            user_id=current_user.id
        )

    return news_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)