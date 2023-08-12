#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from typing import Dict

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_TECH, TYPING_TYPE = range(4)

reply_keyboard = [
    ["Age", "Favourite colour"],
    ["Number of siblings", "Something else..."],
    ["Done"],
]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation, display any stored data and ask user for input."""
    reply_text = "Please send me the list of group by format: group name | group id"
    await update.message.reply_text(reply_text)

    return TYPING_REPLY


async def tech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation, display any stored data and ask user for input."""
    reply_text = "Please send me the group id of your technician group"
    await update.message.reply_text(reply_text)

    return TYPING_TECH


async def get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation, display any stored data and ask user for input."""
    await update.message.reply_text(f"Your group id is:  {update.message.chat.id}")


async def chooseType(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation, display any stored data and ask user for input."""
    await update.message.reply_text(f"Please choose your group type\n 1: Tech\n 2: Customer")

    return TYPING_TYPE


async def group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation, display any stored data and ask user for input."""
    await update.message.reply_text('Please choose group!',
                                    reply_markup=ReplyKeyboardMarkup([context.chat_data['group']],
                                                                     one_time_keyboard=True))

    return CHOOSING


async def group_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    group_name = text.split("| ")[0]
    group_id = text.split("| ")[1]
    context.chat_data['group_id'] = group_id
    await update.message.reply_text(f"You have changed group to {group_name}")

    return ConversationHandler.END


async def received_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    text = update.message.text
    context.chat_data["type"] = text
    await update.message.reply_text("Add type group done!")
    return ConversationHandler.END


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    text = update.message.text
    context.chat_data['group'] = text.splitlines()
    await update.message.reply_text("Add group done!")
    return ConversationHandler.END


async def received_tech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    text = update.message.text
    context.chat_data['tech_id'] = text
    await update.message.reply_text("Add tech group done!")
    return ConversationHandler.END


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    await update.message.reply_text("Good bye!")
    return ConversationHandler.END


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""

    try:
        match context.chat_data["type"]:
            case '1':
                if 'context.chat_data["group_id"]' is not None:
                    try:
                        await context.bot.send_message(context.chat_data['group_id'],
                                                       f"<b>Message from {update.message.chat.title}:</b>\n{update.message.text}",
                                                       parse_mode="HTML")
                    except:
                        await update.message.reply_text("Your group id is not existed!")

                else:
                    await update.message.reply_text(f"Please choose customer group!")
            case '2':
                if 'context.chat_data["tech_id"]' is not None:
                    try:
                        await context.bot.send_message(context.chat_data["tech_id"],
                                                       f"<b>Message from {update.message.chat.title}:</b>\n{update.message.text}",
                                                       parse_mode="HTML")
                    except:
                        await update.message.reply_text("Your tech id is not existed!")
            case _:
                await update.message.reply_text(f"Please choose your group type!")

    except:
        await update.message.reply_text(f"Please choose your group type!")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token("6320128129:AAF8VPvuWsTjRVQNuObROcuUaL_uAWsgQ2I").persistence(
        persistence).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("type", chooseType), CommandHandler("add", add), CommandHandler("tech", tech), CommandHandler("group", group)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.TEXT & ~(filters.Regex("^Done$")), group_choice
                ),
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_information,
                )
            ],
            TYPING_TECH: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_tech,
                )
            ],
            TYPING_TYPE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_type,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
        name="my_conversation",
        persistent=True,
    )

    application.add_handler(conv_handler)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(echo_handler)
    get_group_handler = CommandHandler("get", get)
    application.add_handler(get_group_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
