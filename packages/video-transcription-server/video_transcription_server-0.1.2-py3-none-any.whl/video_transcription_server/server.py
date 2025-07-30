import asyncio
import json
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
import whisper
import yt_dlp
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from dotenv import load_dotenv
import requests
import tempfile


load_dotenv()

# Configuração de logging para stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

# Cache para modelos Whisper
whisper_models = {}


def baixar_cookie_blob(blob_url: str) -> str:
    """
    Baixa um arquivo cookies.txt de um blob storage e salva localmente em arquivo temporário.
    Retorna o caminho do arquivo temporário salvo.
    """
    resp = requests.get(blob_url)
    resp.raise_for_status()
    # Cria arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as tf:
        tf.write(resp.text)
        return tf.name


def get_whisper_model(model_size: str = "base"):
    """Carrega e retorna o modelo Whisper especificado"""
    if model_size not in whisper_models:
        logger.info(f"Carregando modelo Whisper: {model_size}")
        whisper_models[model_size] = whisper.load_model(model_size)
    return whisper_models[model_size]


async def download_video(
    url: str, output_path: str, cookies_blob_url: str = None
) -> str:
    """Download com suporte a cookies do navegador"""
    logger.info(f"Iniciando Download de {url}")

    # Detectar se ffmpeg está disponível
    ffmpeg_locations = [
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
        "ffmpeg",
    ]

    ffmpeg_path = None
    for path in ffmpeg_locations:
        if os.path.exists(path) or shutil.which(path):
            ffmpeg_path = path
            break

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": f"{output_path}/%(id)s.%(ext)s",
        "noplaylist": True,
        "quiet": False,
        "restrictfilenames": True,
        "nopart": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "headers": {
            "Accept-Language": "en-US,en;q=0.9",
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
    }

    # Adicionar cookies se especificado
    if cookies_blob_url:
        cookiefile_local = baixar_cookie_blob(cookies_blob_url)
        ydl_opts["cookiefile"] = cookiefile_local
        logger.info(f"Usando cookiefile baixado de blob: {cookiefile_local}")

    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path

    try:

        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                for file in os.listdir(output_path):
                    logger.info(f"Arquivo baixado: {file}")
                    if file.endswith((".mp3", ".m4a", ".wav", ".opus")):
                        return os.path.join(output_path, file)
            raise Exception("Arquivo não encontrado após download")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, download)
        return result

    finally:
        # Limpa o arquivo temporário (se foi criado)
        if cookiefile_local and os.path.exists(cookiefile_local):
            os.unlink(cookiefile_local)


async def convert_to_audio_ffmpeg(video_path: str, audio_path: str) -> str:
    """Conversão com ffmpeg assíncrona"""
    try:
        # Se já é áudio MP3, apenas copiar
        if video_path.endswith(".mp3") and video_path != audio_path:
            shutil.copy2(video_path, audio_path)
            return audio_path

        # Se já é o arquivo de destino, retornar direto
        if video_path == audio_path:
            return audio_path

        # Buscar ffmpeg
        ffmpeg_cmd = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"

        # Conversão com ffmpeg
        cmd = [
            ffmpeg_cmd,
            "-i",
            video_path,
            "-vn",  # Sem vídeo
            "-ar",
            "16000",  # Sample rate baixo para Whisper
            "-ac",
            "1",  # Mono
            "-b:a",
            "64k",  # Bitrate razoável
            "-y",  # Sobrescrever
            audio_path,
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)

        if process.returncode != 0:
            logger.error(f"Erro ffmpeg: {stderr.decode()}")
            raise Exception(f"FFmpeg falhou com código {process.returncode}")

        return audio_path

    except Exception as e:
        logger.error(f"Erro na conversão com ffmpeg: {e}")
        # Se a conversão falhar mas já temos um arquivo de áudio, usar ele mesmo
        if video_path.endswith((".mp3", ".m4a", ".wav", ".opus")):
            return video_path
        raise


async def transcribe_audio_async(
    audio_path: str, model_size: str = "base", language: str = "auto"
) -> dict:
    """Transcreve áudio usando Whisper de forma assíncrona"""
    try:

        def transcribe():
            model = get_whisper_model(model_size)
            language_param = None if language == "auto" else language
            result = model.transcribe(audio_path, language=language_param, fp16=False)
            return {
                "text": result["text"].strip(),
                "language": result["language"],
                "duration": result.get("duration", 0),
            }

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, transcribe)

    except Exception as e:
        raise Exception(f"Erro na transcrição: {str(e)}")


# Criar instância do servidor MCP
server = Server("video-transcription-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Lista as ferramentas disponíveis no servidor MCP"""
    return [
        types.Tool(
            name="transcribe_video",
            description="Baixa um vídeo, converte para áudio e transcreve o conteúdo",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL do vídeo para transcrever",
                    },
                    "language": {
                        "type": "string",
                        "description": "Idioma do áudio (auto para detecção automática)",
                        "default": "auto",
                    },
                    "model_size": {
                        "type": "string",
                        "description": "Tamanho do modelo Whisper (tiny, base, small, medium, large)",
                        "enum": ["tiny", "base", "small", "medium", "large"],
                        "default": "base",
                    },
                    "cookies_from": {
                        "type": "string",
                        "description": "Navegador para extrair cookies (chrome, firefox, safari, edge)",
                        "enum": [
                            "chrome",
                            "firefox",
                            "safari",
                            "edge",
                            "chromium",
                            "brave",
                        ],
                        "default": None,
                    },
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="list_whisper_models",
            description="Lista os modelos Whisper disponíveis",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Manipula chamadas de ferramentas"""

    if name == "transcribe_video":
        logger.info(f"Iniciando ferramenta: {name}")
        try:
            url = arguments.get("url")
            language = arguments.get("language", "auto")
            model_size = arguments.get("model_size", "base")
            cookies_blob_url = arguments.get("cookies_blob_url", None)

            if not url:
                return {
                    "content": [{"type": "text", "text": "Erro: URL é obrigatória"}],
                    "isError": True,
                }

            with tempfile.TemporaryDirectory() as temp_dir:
                logger.info(f"Iniciando transcrição do vídeo: {url}")

                # Download
                video_path = await download_video(
                    url, temp_dir, cookies_blob_url=cookies_blob_url
                )
                logger.info(f"Download concluído: {video_path}")

                # Conversão para áudio (se necessário)
                audio_path = os.path.join(temp_dir, "audio.mp3")
                if not video_path.endswith(".mp3"):
                    await convert_to_audio_ffmpeg(video_path, audio_path)
                    logger.info("Conversão concluída")
                else:
                    audio_path = video_path

                # Transcrição
                transcription_result = await transcribe_audio_async(
                    audio_path, model_size, language
                )
                logger.info("Transcrição concluída")

                result = {
                    "text": transcription_result["text"],
                    "language": transcription_result["language"],
                    "duration": transcription_result["duration"],
                    "model_used": model_size,
                    "success": True,
                }

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False),
                        }
                    ]
                }

        except Exception as e:
            logger.error(f"Erro na transcrição: {str(e)}")
            return {
                "content": [{"type": "text", "text": f"Erro na transcrição: {str(e)}"}],
                "isError": True,
            }

    elif name == "list_whisper_models":
        models = ["tiny", "base", "small", "medium", "large"]
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "available_models": models,
                            "loaded_models": list(whisper_models.keys()),
                        },
                        indent=2,
                    ),
                }
            ]
        }

    else:
        return {
            "content": [
                {"type": "text", "text": f"Ferramenta '{name}' não encontrada"}
            ],
            "isError": True,
        }


async def async_main():
    """Função principal assíncrona"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        try:
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="video-transcription-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
        except Exception as e:
            logger.error(f"Erro ao executar servidor: {e}")
            raise


def main():
    """Entry point for the package"""
    anyio.run(async_main)


if __name__ == "__main__":
    main()
