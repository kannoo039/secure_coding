from app import create_app, socketio

# 애플리케이션 객체 생성
app = create_app()

# 서버 실행 (호스트를 0.0.0.0으로 설정해 외부 접속 가능)
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

