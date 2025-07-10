import os
import discord
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID"))

# ===== ログ設定 =====
logger = logging.getLogger(__name__)

# ===== Discord設定 =====
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = discord.Client(intents=intents)
vc_connection: discord.VoiceClient = None


# ===== Botログイン・ログアウト =====
async def login_bot():
    logger.info("Botログイン処理を開始します。")
    asyncio.create_task(bot.start(TOKEN))
    await wait_until_ready()
    logger.info("Botが準備完了しました。")


async def logout_bot():
    global vc_connection
    if vc_connection and vc_connection.is_connected():
        logger.info("ボイスチャンネルから切断します。")
        await vc_connection.disconnect()
    logger.info("Botログアウトします。")
    await bot.close()


async def wait_until_ready():
    while not bot.is_ready():
        await asyncio.sleep(0.5)


# ===== チャンネル取得 =====
def get_guild():
    return bot.get_guild(GUILD_ID)


def get_voice_channel():
    guild = get_guild()
    return guild.get_channel(VC_CHANNEL_ID)


def get_text_channel():
    vc = get_voice_channel()
    return vc.guild.system_channel or vc  # fallback


# ===== 音声再生 =====
async def play_audio(audio_file):
    global vc_connection
    voice_channel = get_voice_channel()

    if not vc_connection or not vc_connection.is_connected():
        logger.info(f"ボイスチャンネルに接続します。({voice_channel.name})")
        vc_connection = await voice_channel.connect()

    if vc_connection.is_playing():
        logger.info("再生中の音声を停止します。")
        vc_connection.stop()

    logger.info(f"音声ファイルを再生します: {audio_file}")
    event = asyncio.Event()

    vc_connection.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: event.set())

    await event.wait()
    logger.info("音声再生が完了しました。")


# ===== テキスト + 音声通知 =====
async def send_text_and_audio(message, audio_file):
    text_channel = get_text_channel()
    if text_channel:
        logger.info(f"テキストチャンネルにメッセージ送信: {message}")
        await text_channel.send(message)
    await play_audio(audio_file)


# ===== 通知関数群 =====
async def notify_attendance():
    logger.info("出勤通知 (9:00)")
    await send_text_and_audio("おはようございます。本日も頑張りましょう。", "attendance.wav")


async def notify_start(hour: int):
    logger.info(f"{hour}:00 通知")
    await send_text_and_audio(f"{hour}時になりました。開始してください。", "start.wav")


async def notify_stop(hour: int):
    logger.info(f"{hour}:50 通知")
    await send_text_and_audio(f"{hour}時50分になりました。時間になりました。お疲れ様です。", "stop.wav")


async def notify_lunch():
    logger.info("昼休憩通知 (12:00)")
    await send_text_and_audio("お疲れ様です。お昼になりました。", "lunch.wav")


async def notify_leaving():
    global vc_connection
    logger.info("退勤通知 (18:00)")
    await send_text_and_audio("本日もお疲れ様でした。", "leaving.wav")
    await asyncio.sleep(1.0)
    if vc_connection and vc_connection.is_connected():
        logger.info("ボイスチャンネルから退出します。")
        await vc_connection.disconnect()
        vc_connection = None
