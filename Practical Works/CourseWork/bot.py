import os
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp
import xml.etree.ElementTree as ET
from yt_work import YtHelper


class ConfigManager:
    """Класс для управления конфигурацией"""

    def __init__(self, config_path):
        self.config_path = config_path
        self.tree = ET.parse(config_path)
        self.root = self.tree.getroot()

    def get_token(self):
        return self.root.find('Token').text

    def get_bot_username(self):
        return self.root.find('BotUsername').text


class YouTubeBot:
    """Основной класс бота"""

    def __init__(self, token, download_dir='downloads'):
        self.token = token
        self.download_dir = download_dir
        self.yt_helper = YtHelper()
        os.makedirs(self.download_dir, exist_ok=True)
        self.app = Application.builder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Настройка обработчиков"""
        self.app.add_handler(CommandHandler('start', self.start_command))
        self.app.add_handler(CommandHandler('help', self.help_command))
        self.app.add_handler(CommandHandler('find', self.find_command))
        self.app.add_handler(CallbackQueryHandler(self.video_chosen, pattern='^video_'))
        self.app.add_handler(CallbackQueryHandler(self.download_video_with_resolution, pattern='^res_'))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_error_handler(self.error_handler)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'Привет {update.effective_user.first_name}. '
                                        f'Отправь ссылку на видео с YouTube или используй команду /find (название) для поиска')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            'Отправь ссылку на видео с YouTube или используй команду /find (название) для поиска')

    async def find_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_query = update.message.text.replace("/find", "").strip()
        if not user_query:
            await update.message.reply_text('Введите название видео, которое вы хотите найти.')
            return

        context.user_data['query'] = user_query  # Сохранить ссылку для последующего использования
        message = await update.message.reply_text('Подождите немного. Идёт поиск...')
        await self.choose_video(update, context, message)

    async def choose_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, search_message):
        user_query = context.user_data.get('query')
        videos = self.yt_helper.search_youtube_videos(user_query, max_results=5)

        # Случай, если мы не нашли ни 1 видео
        if len(videos) == 0:
            await search_message.edit_text("Не удалось найти видео по вашему запросу( Попробуйте еще раз.")
            return

        keyboard = [
            [InlineKeyboardButton(f'{video[0]}, {video[1]}', callback_data=f"video_{video[2]}")]
            for video in videos
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await search_message.edit_text('Выберите нужное видео:', reply_markup=reply_markup)

    async def video_chosen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        url = query.data.replace("video_", "")
        context.user_data['url'] = url
        print(f"User choose url - {url}")

        # Так как у video_chosen нет доступа к сообщению, наш update = query
        await self.choose_resolution(query, context, url)

    async def choose_resolution(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url=None):
        if url:
            context.user_data['url'] = url
        keyboard = [
            [InlineKeyboardButton(res, callback_data=f'res_{res}')]
            for res in ['1080', '720', '480', '360', 'mp3']
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if isinstance(update, Update):
            await update.message.reply_text('Выберите разрешение:', reply_markup=reply_markup)
        else:
            await update.edit_message_text('Выберите разрешение:', reply_markup=reply_markup)

    async def download_video_with_resolution(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        resolution = query.data.replace("res_", "")  # Получить выбранное разрешение
        url = context.user_data.get('url')  # Получить сохранённую ссылку

        if not url:
            await query.edit_message_text('Ошибка: ссылка не найдена.')
            return

        ydl_opts = self._get_download_options(resolution)
        if "mp3" in resolution:
            message = await query.edit_message_text(f'Скачивание аудио, подождите немного...')
        else:
            message = await query.edit_message_text(
                f'Скачивание видео в разрешении {resolution}p, подождите немного...')
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if 'mp3' in resolution:
                    file_path = file_path.rsplit('.', 1)[0] + '.mp3'  # Меняем расширение для mp3

                # Отправить файл пользователю
                if 'mp3' in resolution:
                    with open(file_path, 'rb') as audio:
                        await query.message.reply_audio(audio, caption=f'Ваше аудио: {info["title"]}')
                else:
                    with open(file_path, 'rb') as video:
                        await query.message.reply_video(video, caption=f'Ваше видео: {info["title"]}')

                await message.delete()

        except Exception as e:
            print(f'Error: {e}')
            await query.message.reply_text('Произошла ошибка при скачивании.')
        finally:
            # Удалить файл после отправки
            os.remove(file_path)

    def _get_download_options(self, resolution):
        if 'mp3' in resolution:
            return {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'{self.download_dir}/%(title)s.%(ext)s',
            }
        return {
            'outtmpl': f'{self.download_dir}/%(title)s_{resolution}p.%(ext)s',
            'format': f'bestvideo[height<={resolution}]+bestaudio/best[ext=mp4]',
            'merge_output_format': 'mp4',
        }

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        print(f"User: @{update.effective_user.first_name}({update.effective_user.id}): {update.message.text}")
        if 'youtube.com' in text or 'youtu.be' in text:
            await self.choose_resolution(update, context, text)
        else:
            await update.message.reply_text('Отправьте ссылку на видео с YouTube или используйте /find (название).')

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f'Update {update} caused error {context.error}')

    def run(self):
        print('Starting bot...')
        print("Polling...")
        self.app.run_polling(poll_interval=3)


if __name__ == '__main__':
    config = ConfigManager('config.xml')
    bot = YouTubeBot(token=config.get_token())
    bot.run()
