from typing import Optional

import click

from . import get_model, models


@click.group()
@click.version_option()
def cli():
    """
    mstt: A command-line interface (CLI) tool for performing speech-to-text (STT)
    transcription using various ASR models.
    """


@cli.command()
@click.argument("audio_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-m",
    "--model",
    default="hf/whisper-tiny",
    help="The model to use for transcription.",
)
@click.option("--key", help="API key to use for this request.")
def transcribe(
    audio_path: str,
    model: str = "hf/whisper-tiny",
    key: Optional[str] = None,
):
    """
    Transcribes an audio file using the specified ASR model.

    Args:
        audio_path (str): The path to the audio file to transcribe.
        model (str, optional): The ID of the ASR model to use for transcription.
                               Defaults to "hf/whisper-tiny".
        key (Optional[str], optional): An optional API key for models that require authentication.
                                       Defaults to None.

    Example:
        $ mstt transcribe my_audio.wav -m openai/whisper-base
    """
    try:
        asr_model = get_model(model)
        result = asr_model.transcribe(audio_path)
        click.echo(result)
        # 还可以添加 --json 输出完整结果
    except Exception as e:
        raise click.ClickException(str(e)) from e


@cli.command(name="models")
def list_models():
    """
    Lists all ASR models currently available through installed plugins and dynamic loaders.

    This command helps users discover which models they can use for transcription.

    Example:
        $ mstt models
    """
    click.echo("Available models:")
    for model_name in models():
        click.echo(f"- {model_name}")
