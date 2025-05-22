import telebot
from telebot.types import Message, ReactionTypeEmoji
import logging


class AutoReactBot:
    """
    Simple bot that automatically reacts to specific stickers in any group it's added to.
    """

    def __init__(self, token: str, target_sticker_ids: list[str], reaction_emoji: str = "👎"):
        """
        Initialize the auto-react bot.

        Args:
            token: Bot token from @BotFather
            target_sticker_ids: List of file_unique_id values of stickers to react to
            reaction_emoji: Emoji to use as reaction (default: 👎)
        """
        self.bot = telebot.TeleBot(token, parse_mode=None)
        self.target_sticker_ids = target_sticker_ids
        self.reaction_emoji = reaction_emoji

        # Setup basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Register handlers
        self._setup_handlers()

        # Log bot info
        try:
            bot_info = self.bot.get_me()
            self.logger.info(f"Bot started: @{bot_info.username}")
            self.logger.info(f"Watching for sticker IDs: {self.target_sticker_ids}")
            self.logger.info(f"Will react with: {self.reaction_emoji}")
        except Exception as e:
            self.logger.error(f"Failed to get bot info: {e}")

    def _setup_handlers(self):
        """Setup the sticker message handler."""

        @self.bot.message_handler(content_types=['sticker'])
        def handle_sticker(message: Message):
            """Automatically react to target stickers."""
            sticker = message.sticker

            if sticker.file_unique_id in self.target_sticker_ids:
                self.logger.info(f"Target sticker detected in chat {message.chat.id}")
                self._add_reaction(message.chat.id, message.message_id)

    def _add_reaction(self, chat_id: int, message_id: int):
        """Add reaction to the message and send follow-up text."""
        try:
            reaction = ReactionTypeEmoji(self.reaction_emoji)

            self.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[reaction],
                is_big=False
            )

            self.logger.info(f"✅ Reaction added successfully: {self.reaction_emoji}")

            # Send follow-up message
            self.bot.send_message(chat_id, "Хейтер обнаружен! Атакую!", reply_to_message_id=message_id)

        except telebot.apihelper.ApiTelegramException as e:
            error_msg = str(e)
            if "Forbidden" in error_msg:
                self.logger.warning("Bot lacks permission to add reactions or send messages in this chat")
            elif "REACTION_INVALID" in error_msg:
                self.logger.warning(f"Emoji {self.reaction_emoji} not supported for reactions")
            elif "message not found" in error_msg:
                self.logger.warning("Message too old or deleted")
            else:
                self.logger.error(f"Failed to add reaction or send message: {error_msg}")
        except Exception as e:
            self.logger.error(f"Unexpected error adding reaction or sending message: {e}")

    def start(self):
        """Start the bot with polling."""
        self.logger.info("🚀 Auto-react bot is running...")
        self.logger.info("Add me to groups and I'll automatically react to your target stickers!")

        try:
            self.bot.polling(
                timeout=20,
                long_polling_timeout=20,
                skip_pending=True,
                none_stop=True
            )
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Bot error: {e}")
            raise


def main():
    """
    Main function to run the auto-react bot.
    Configure your settings here.
    """

    # ⚙️ CONFIGURATION - Update these values:
    BOT_TOKEN = "8136388260:AAEUOrx4F4JsOXztuoiZV1II6AevSgIcw1Q"
    TARGET_STICKER_IDS = [
        "AgADZwADuRtZCw",    # Replace with your actual sticker file_unique_id
        "AgADLXUAAkw0aEk",
        "AgADtnYAAuLomUs"
    ]
    REACTION_EMOJI = "👎"

    # Create and start the bot
    bot = AutoReactBot(
        token=BOT_TOKEN,
        target_sticker_ids=TARGET_STICKER_IDS,
        reaction_emoji=REACTION_EMOJI
    )

    bot.start()


if __name__ == "__main__":
    main()
