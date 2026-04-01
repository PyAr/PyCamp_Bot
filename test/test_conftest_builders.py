"""Tests de los builders de conftest: garantizan la interfaz que usan los handlers.

Si PTB o los handlers cambian de atributos, estos tests fallan y evitan
regresiones silenciosas en los tests de handlers.
"""
import pytest

from test.conftest import (
    make_user,
    make_chat,
    make_message,
    make_update,
    make_callback_update,
    make_context,
)


class TestMakeUser:
    def test_exposes_username_id_first_name(self):
        u = make_user(username="pepe", user_id=999, first_name="Pepe")
        assert u.username == "pepe"
        assert u.id == 999
        assert u.first_name == "Pepe"
        assert u.is_bot is False

    def test_accepts_username_none(self):
        u = make_user(username=None)
        assert u.username is None


class TestMakeChat:
    def test_exposes_id_and_type(self):
        c = make_chat(chat_id=111, chat_type="private")
        assert c.id == 111
        assert c.type == "private"


class TestMakeMessage:
    def test_exposes_text_chat_id_from_user_reply_text(self):
        msg = make_message(text="/start", username="u1", chat_id=222)
        assert msg.text == "/start"
        assert msg.chat_id == 222
        assert msg.from_user.username == "u1"
        assert msg.chat.id == 222
        assert callable(msg.reply_text)

    def test_reply_text_is_awaitable(self):
        msg = make_message()
        import asyncio
        asyncio.get_event_loop().run_until_complete(msg.reply_text("hi"))


class TestMakeUpdate:
    def test_exposes_message_with_same_interface(self):
        up = make_update(text="/cmd", username="alice", chat_id=333)
        assert up.message.text == "/cmd"
        assert up.message.chat_id == 333
        assert up.message.from_user.username == "alice"
        assert callable(up.message.reply_text)

    def test_update_id_set(self):
        up = make_update(update_id=42)
        assert up.update_id == 42


class TestMakeCallbackUpdate:
    def test_exposes_callback_query_data_and_message(self):
        up = make_callback_update(
            data="vote:si",
            username="voter",
            message_text="ProyectoX",
            chat_id=444,
        )
        assert up.callback_query.data == "vote:si"
        assert up.callback_query.from_user.username == "voter"
        assert up.callback_query.message.text == "ProyectoX"
        assert up.callback_query.message.chat_id == 444
        assert up.callback_query.message.chat.id == 444
        assert callable(up.callback_query.answer)

    def test_answer_is_awaitable(self):
        up = make_callback_update()
        import asyncio
        asyncio.get_event_loop().run_until_complete(up.callback_query.answer())


class TestMakeContext:
    def test_exposes_bot_send_message_and_edit_message_text(self):
        ctx = make_context()
        assert ctx.bot is not None
        assert callable(ctx.bot.send_message)
        assert callable(ctx.bot.edit_message_text)
