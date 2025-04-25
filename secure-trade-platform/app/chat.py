from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import User
from flask_socketio import emit, join_room
from app import socketio

chat_bp = Blueprint('chat_bp', __name__)

# 채팅방 접속 라우트
@chat_bp.route("/chat/<int:receiver_id>")
@login_required
def chat(receiver_id):
    receiver = User.query.get_or_404(receiver_id)

    # 방 이름은 두 사용자 ID를 정렬해서 구성 (예: room_2_5)
    sorted_ids = sorted([current_user.id, receiver.id])
    room = f"room_{sorted_ids[0]}_{sorted_ids[1]}"
    return render_template("chat.html", receiver=receiver, room=room)

# 클라이언트가 방에 접속할 때
@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f"{data['username']} joined the chat."}, room=room)

# 메시지를 보냈을 때
@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    emit('receive_message', {
        'username': data['username'],
        'message': data['message']
    }, room=room)

# 공용 채팅방 라우트
@chat_bp.route('/chat/public', methods=['GET'])
@login_required
def public_chat():
    return render_template('public_chat.html', username=current_user.username)


@socketio.on('public_message')
@login_required
def handle_public_message(data):
    username = current_user.username
    message = data.get('message', '').strip()
    if message:
        emit('public_message', {
            'username': username,
            'message': message
        }, broadcast=True)

