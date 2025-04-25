import os

class Config:
    # .env 파일에서 SECRET_KEY 환경 변수 불러오기
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-default-secret-key')  # 환경변수가 없으면 기본 키 사용
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')  # DB 연결 문자열
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 성능 개선을 위한 설정

