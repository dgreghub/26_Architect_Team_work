from chatbot.core import chat


def test_chat_returns_default_response_with_empty_history():
    user_message = "하이 안녕"
    history = []

    textbox_value, new_history = chat(user_message, history)

    assert textbox_value == ""
    assert new_history == [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": "안녕하세요 8팀 봇입니다."}
    ]


def test_chat_appends_to_existing_history():
    user_message = "안녕"
    history = [
        {"role": "user", "content": "처음입니다."},
        {"role": "assistant", "content": "안녕하세요!"}
    ]

    textbox_value, new_history = chat(user_message, history)

    assert textbox_value == ""
    assert new_history[-2:] == [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": "안녕하세요 8팀 봇입니다."}
    ]
