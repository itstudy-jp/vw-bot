from discord.ext import tasks
from datetime import datetime

# 音声ファイルのパス（同じディレクトリにあると仮定）
MORNING_START = {
    "09:00": ("おはようございます。本日も頑張りましょう。", "attendance.wav"),
}

STOP_WORKING = {
    "12:00": ("お疲れ様です。お昼になりました。", "lunch.wav"),
    "18:00": ("本日もお疲れ様でした。", "leaving.wav"),
}

async def users_mute(voice_channel: discord.VoiceChannel):
    for member in voice_channel.members:
        if not member.bot:
            try:
                await member.edit(mute=True)
            except Exception as e:
                print(f"[MUTE失敗] {member.display_name}: {e}")

async def users_nmute(voice_channel: discord.VoiceChannel):
    for member in voice_channel.members:
        if not member.bot:
            try:
                await member.edit(mute=False)
            except Exception as e:
                print(f"[UNMUTE失敗] {member.display_name}: {e}")

@tasks.loop(seconds=30)
async def scheduled_notifications():
    now = datetime.now().strftime("%H:%M")
    hour = datetime.now().hour
    minute = datetime.now().minute

    channel = bot.get_channel(TEXT_CHANNEL_ID)
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)

    # 時刻ベースの通知
    if now in MORNING_START:
        message, audio_file = MORNING_START[now]
        await users_mute(voice_channel)
    if now in STOP_WORKING:
        message, audio_file = STOP_WORKING[now]
        await users_unmute(voice_channel)
    elif minute == 0:
        message = f"{hour}時になりました。開始してください。"
        audio_file = "start.wav"
        await users_mute(voice_channel)
    elif minute == 50 and hour not in [11, 17]:
        message = f"お疲れ様です。50分になりました。"
        audio_file = "stop.wav"
        await users_unmute(voice_channel)
    else:
        return

    # VCに接続
    if voice_channel:
        vc = await voice_channel.connect()
        await channel.send(message)
        vc.play(discord.FFmpegPCMAudio(audio_file))
        while vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect()
    else:
        await channel.send("⚠️ ボイスチャンネルが見つかりません。")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Discord'))
    channel = bot.get_channel(TEXT_CHANNEL_ID)
    await channel.send('定時通知BOTが起動しました。')
    scheduled_notifications.start()
