import logging
import time

from pyrogram import Client, filters, types
from pyrogram.types import Message

from bot import Bot
from bot.enums import LogTopics
from bot.errors import BotError
from bot.filters import executor_required
from bot.functions import get_chat_link, get_target, msg_auto_clean
from bot.plugins import COMMAND_PREFIXES
from bot.validation import NameRule, UserValidator
from core.decorator import event_log
from core.log import event_logger, main_logger
from database.models.blacklist import FullNameBlacklist

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("add_name_rule", prefixes=COMMAND_PREFIXES)
    & executor_required
    & filters.group
    & ~filters.forwarded
)
@event_log()
async def add_username_rule(cli: Bot, msg: Message) -> None:
    # noinspection DuplicatedCode
    await msg.delete()

    start_time: float = time.perf_counter()
    exec_info: str = (
        f"執行者：{msg.from_user.mention} (<code>{msg.from_user.id}</code>)\n"
        f"執行位置：{get_chat_link(msg.chat)} (<code>{msg.chat.id}</code>)\n"
        f"執行：<b><u>新增使用者名稱檢查</u></b>"
    )

    if len(msg.command) == 3:
        match_time: str = msg.command[2]

        try:
            match_time: int = int(match_time)
        except ValueError:
            await cli.send_log_message(
                "❌ #add_name_rule\n"
                f"{exec_info}\n"
                f"使用者名稱長度不足\n"
                f"輸入的內容：<code>{msg.text}</code>\n",
                LogTopics.error,
            )
            await msg_auto_clean(
                await cli.send_message(
                    msg.chat.id,
                    f"輸入的次數不是數字，請輸入數字",
                )
            )
            return

    elif len(msg.command) == 2:
        match_time: int = 0

    else:
        await cli.send_log_message(
            "❌ #add_name_rule\n"
            f"{exec_info}\n"
            f"指令格式錯誤\n"
            f"輸入的內容：<code>{msg.text}</code>\n",
            LogTopics.error,
        )
        await msg_auto_clean(await cli.send_message(msg.chat.id, "指令格式錯誤"))
        return

    new_word: str = msg.command[1]

    if len(new_word) < 3:
        await cli.send_log_message(
            "❌ #add_name_rule \n"
            f"{exec_info}\n"
            f"使用者名稱長度不足\n"
            f"輸入的內容：<code>{msg.text}</code>\n",
            LogTopics.error,
        )
        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                f"輸入的內容太短，請輸入至少 3 個字元",
            )
        )
        return

    FullNameBlacklist.create(new_word, match_time, msg.from_user.id)

    await cli.send_log_message(
        "✅ #add_name_rule\n"
        f"{exec_info}\n"
        f"新增使用者名稱檢查\n"
        f"新增的內容：<code>{new_word}</code>\n"
        f"新增的次數：<code>{match_time}</code>\n"
        f"執行時間：<code>{time.perf_counter() - start_time:.3f}</code> 秒",
        LogTopics.action,
    )
    await msg_auto_clean(
        await cli.send_message(
            msg.chat.id,
            "操作成功",
        )
    )


@Client.on_message(
    filters.command("delete_name_rule", prefixes=COMMAND_PREFIXES)
    & executor_required
    & filters.group
    & ~filters.forwarded
)
async def delete_name_rule(cli: Bot, msg: Message) -> None:
    # noinspection DuplicatedCode
    await msg.delete()

    start_time: float = time.perf_counter()
    exec_info: str = (
        f"執行者：{msg.from_user.mention} (<code>{msg.from_user.id}</code>)\n"
        f"執行位置：{get_chat_link(msg.chat)} (<code>{msg.chat.id}</code>)\n"
        f"執行：<b><u>全域解除封鎖</u></b>"
    )

    if len(msg.command) != 2:
        await cli.send_log_message(
            "❌ #delete_name_rule\n"
            f"{exec_info}\n"
            f"指令格式錯誤\n"
            f"輸入的內容：<code>{msg.text}</code>\n",
            LogTopics.error,
        )
        await msg_auto_clean(await cli.send_message(msg.chat.id, "指令格式錯誤"))
        return

    delete_word: str = msg.command[1]

    w: FullNameBlacklist | None = FullNameBlacklist.get(delete_word)
    if not w:
        await cli.send_log_message(
            "❌ #delete_name_rule\n"
            f"{exec_info}\n"
            f"規則不存在\n"
            f"輸入的內容：<code>{msg.text}</code>\n",
            LogTopics.error,
        )
        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                f"操作失敗",
            )
        )
        return

    w.delete()

    await cli.send_log_message(
        "✅ #delete_name_rule\n"
        f"{exec_info}\n"
        f"刪除使用者名稱檢查\n"
        f"刪除的內容：<code>{delete_word}</code>\n"
        f"執行時間：<code>{time.perf_counter() - start_time:.3f}</code> 秒",
        LogTopics.action,
    )
    await msg_auto_clean(
        await cli.send_message(
            msg.chat.id,
            "操作成功",
        )
    )


@Client.on_message(
    filters.command("check_name_rule", prefixes=COMMAND_PREFIXES)
    & executor_required
    & filters.group
    & ~filters.forwarded
)
async def check_name_rule(cli: Bot, msg: Message) -> None:
    # noinspection DuplicatedCode
    await msg.delete()

    exec_info: str = (
        f"執行者：{msg.from_user.mention} (<code>{msg.from_user.id}</code>)\n"
        f"執行位置：{get_chat_link(msg.chat)} (<code>{msg.chat.id}</code>)\n"
        f"執行：<b><u>全域解除封鎖</u></b>"
    )

    try:
        target: types.User | types.Chat = await get_target(cli, msg)

    except BotError as e:
        await cli.send_log_message(
            f"❌ #check_name_rule\n{exec_info}\n{e.message}", LogTopics.error
        )
        await msg_auto_clean(await cli.send_message(msg.chat.id, f"操作錯誤"))
        return

    if not isinstance(target, types.User):
        await cli.send_log_message(
            f"❌ #check_name_rule\n{exec_info}\n目標不能被檢查", LogTopics.error
        )
        await msg_auto_clean(await cli.send_message(msg.chat.id, f"操作錯誤"))
        return

    uv: UserValidator = UserValidator(target, [NameRule])
    uv.validate()

    if not uv.errors:
        await cli.send_log_message(
            f"✅ #check_name_rule\n{exec_info}\n名字未符合封鎖條件", LogTopics.action
        )
        await msg_auto_clean(await cli.send_message(msg.chat.id, f"操作成功"))
        return

    await cli.send_log_message(
        f"❌ #check_name_rule\n"
        f"{exec_info}\n"
        f"名字符合封鎖條件\n"
        f"<code>{uv.error_messages}</code>\n",
        LogTopics.action,
    )
    await msg_auto_clean(await cli.send_message(msg.chat.id, f"操作成功"))
