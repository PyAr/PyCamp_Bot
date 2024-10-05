import os
import subprocess
import sys

from telegram.ext import CommandHandler

from pycamp_bot.constants import SENTRY_DATA_SOURCE_NAME_ENVVAR
from pycamp_bot.utils import escape_markdown


async def show_version(update, context):
    """Let people see the details about what is being run and how"""

    git_rev_parse = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, check=True)
    commit = git_rev_parse.stdout.decode().rstrip()

    git_log = subprocess.run(['git', 'log', '--max-count=1', '--pretty=format:%ai'], capture_output=True, check=True)
    author_date = git_log.stdout.decode().rstrip()

    git_diff = subprocess.run(['git', 'diff', '--quiet'], capture_output=True)
    if git_diff.returncode == 0:
        clean_worktree = '🟢'
    else:
        clean_worktree = '🔴'

    python_version = '.'.join(str(component) for component in sys.version_info[:3])

    pip_freeze = subprocess.run(['pip', 'freeze', '--exclude', 'PyCamp_Bot'], capture_output=True, check=True)
    dependencies = []
    for pip_line in pip_freeze.stdout.decode().splitlines():
        dependencies.append(escape_markdown(pip_line))

    if SENTRY_DATA_SOURCE_NAME_ENVVAR in os.environ:
        sentry_envvar_set = '🟢'
    else:
        sentry_envvar_set = '🔴'

    lines = [
        f'Commit deployado: `{commit}`',
        f'Fecha del commit \\(author date\\): `{escape_markdown(author_date)}`',
        f'Clean worktree: {clean_worktree}',
        f'Versión de Python: `{python_version}`',
        'Dependencias:',
        '```',
        *dependencies,
        '```',
        f'Variable de entorno de Sentry definida: {sentry_envvar_set}',
    ]

    await update.message.reply_text('\n'.join(lines), parse_mode='MarkdownV2')


def set_handlers(application):
    application.add_handler(CommandHandler('mostrar_version', show_version))
