#!/usr/bin/env python3
"""
Главный CLI модуль для litellm-gigachat.
"""

import click
import logging
import sys
from datetime import datetime
from importlib import metadata

from .commands.start import start
from .commands.test import test
from .commands.token_info import token_info
from .commands.refresh_token import refresh_token
from .commands.examples import examples
from .commands.version import version_cmd
from .utils import setup_logging, get_package_version


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show the version and exit.')
@click.option('-v', '--verbose', is_flag=True, help='Включить подробный вывод')
@click.option('-d', '--debug', is_flag=True, help='Включить режим отладки')
@click.pass_context
def cli(ctx, version, verbose, debug):
    """LiteLLM прокси-сервер для GigaChat API."""
    
    # Создаем контекст для передачи параметров в подкоманды
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug
    
    # Настройка логирования
    setup_logging(verbose, debug)
    
    if version:
        click.echo(f"litellm-gigachat {get_package_version()}")
        ctx.exit()
    
    # Если команда не указана, показываем help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Добавляем команды
cli.add_command(start)
cli.add_command(test)
cli.add_command(token_info)
cli.add_command(refresh_token)
cli.add_command(examples)
cli.add_command(version_cmd, name='version')


def main():
    """Точка входа для CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⚠️  Прервано пользователем", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
