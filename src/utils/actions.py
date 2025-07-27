# -*- coding: utf-8 -*-
"""
botのDiscordに対しての動作を規定
"""
import asyncio
import logging
import os

import discord

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class Bot:
    def __init__(self, client, guild_id, vc_id):
        self.client = client
        self.guild_id = int(guild_id)
        self.vc_id = int(vc_id)
        self.guild = self.client.get_guild(self.guild_id)
        self.voice_channel = self.find_voice_chat()
        self.voice_client = None

    def find_voice_chat(self):
        voice_channels = self.guild.voice_channels
        logger.info(f"指定されたVCの探索を開始します。")
        logger.debug(f"REGISTERED_VOICE_CHANNEL_ID: {self.vc_id}")
        for vc in voice_channels:
            logger.debug(f"PUBLIC_VOICE_CHANNEL_ID:{vc.id} PUBLIC_CHANNEL_NAME:{vc.name}")
            if self.vc_id == vc.id:
                logger.info(f"一致するVOICE_CHANNEL_IDが見つかりました。")
                return vc
        # TODO voice_channelが見つからない場合の対処
        logger.critical(f"一致するVOICE_CHANNEL_IDが見つかりませんでした。")
        return None


    async def join_vc(self):
        if not self.voice_client or not self.voice_client.is_connected():
            logger.debug(f"{self.voice_channel.name}に参加を試みます。")
            self.voice_client = await self.voice_channel.connect()
            logger.info(f"{self.voice_channel.name}に参加しました。")

    async def leave_vc(self):
        if self.voice_client and self.voice_client.is_connected():
            logger.debug(f"{self.voice_channel.name}から退出を試みます。")
            await self.voice_client.disconnect()
            logger.info(f"{self.voice_channel.name}から退出しました。")

    async def play_audio(self, f_name):
        """
        botが音声ファイルを再生する

        Note: VoiceClientのplayメソッドは再生を別のスレッドに引き渡す
        afterでコールバックを受け取れるのでコールバック内にさらにevent loopを入れて
        コールバックが返ってくるまで待機出来るようにしている
        """

        # 再生終了を待つ空のループ
        audio_finished_event = asyncio.Event()
        def after_playing(error):
            if error:
                logger.error(f"音声再生中にエラーが発生しました: {error}")
            # 再生終了を伝える
            # 別のスレッドから実行される可能性を考慮しメインイベントループに対して行う
            self.client.loop.call_soon_threadsafe(audio_finished_event.set)

        logger.debug("音声ファイルの再生を試みます。")
        # 音声ファイルのパスを構築
        audio_path = os.path.join("audio", f_name)
        logger.debug(f"FILE_PATH: {audio_path}")

        # ボイスチャンネルに接続していない場合は接続
        if not self.voice_client or not self.voice_client.is_connected():
            logger.warning(f"{self.voice_channel.name}に参加出来ていません。")
            self.voice_client = await self.voice_channel.connect()
            logger.info(f"{self.voice_channel.name}に参加しました。")

        # 既に音声を再生中の場合は停止
        if self.voice_client.is_playing():
            logger.warning(f"前回の音声ファイルがまだ再生中です。")
            self.voice_client.stop()
            logger.info(f"前回の音声ファイルの再生を停止しました。")

        # 音声ファイルを再生
        logger.debug("音声ファイルを再生します。")
        self.voice_client.play(discord.FFmpegPCMAudio(audio_path),after=after_playing)
        # 再生が終了されるのを待つ
        await audio_finished_event.wait()
        logger.info(f"音声ファイルの再生が完了しました。")

    async def send_message(self, msg):
        logger.debug(f"テキストチャンネルにメッセージを送信: {msg}")
        await self.voice_channel.send(msg)
        logger.info(f"メッセージの送信が完了しました。")
