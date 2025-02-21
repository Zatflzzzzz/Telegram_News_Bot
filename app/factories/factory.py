from app.dto.dto import UserDto, TokenDto, NewsDto


class UserFactory:
    @staticmethod
    def create_user_dto(username, password):
        return UserDto(username=username, password=password)

class TokenFactory:
    @staticmethod
    def create_token_dto(access_token, token_type):
        return TokenDto(access_token=access_token, token_type=token_type)

class NewsFactory:
    @staticmethod
    def create_news_dto(news_data):
        return NewsDto(
            author=news_data.get("author"),
            title=news_data.get("title"),
            urlToImage=news_data.get("urlToImage"),
            category=news_data.get("category"),
            user_id=news_data.get("user_id")
        )