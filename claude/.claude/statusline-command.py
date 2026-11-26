#!/usr/bin/env python3
"""Claude status line matching the shared Codex footer; JSON arrives on stdin."""
import json
import math
import os
from pathlib import Path
import re
import sys


def clean(value):
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(value))


def percentage(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return max(0, min(100, value))
    return None


def render(data, color=True):
    def field(key):
        value = data.get(key)
        return value if isinstance(value, dict) else {}

    parts = []
    def add(value, code):
        if value:
            value = clean(value)
            parts.append(f'\033[{code}m{value}\033[0m' if color else value)

    model = field('model').get('display_name', '')
    effort = field('effort').get('level')
    add(f'{model} ({effort})' if model and effort else model, '36')
    cwd = field('workspace').get('current_dir') or data.get('cwd')
    if cwd:
        path = str(cwd)
        home = str(Path.home())
        if path == home or path.startswith(home + '/'):
            path = '~' + path[len(home):]
        components = path.split('/')
        if len(components) > 3:
            path = '…/' + '/'.join(components[-3:])
        add(path, '35')
    context = field('context_window')
    remaining = percentage(context.get('remaining_percentage'))
    used = percentage(context.get('used_percentage'))
    if remaining is None and used is not None:
        remaining = 100 - used
    if remaining is not None:
        add(f'ctx {remaining:.0f}% left', '31' if remaining < 20 else '37')
    if used is not None:
        add(f'{used:.0f}% used', '37')
    limit = field('rate_limits').get('five_hour') or {}
    consumed = percentage(limit.get('used_percentage')) if isinstance(limit, dict) else None
    if consumed is not None:
        left = 100 - consumed
        add(f'5h {left:.0f}% left', '31' if left < 20 else '34')
    return ' | '.join(parts)


if __name__ == '__main__':
    try:
        payload = json.load(sys.stdin)
        if isinstance(payload, dict):
            print(render(payload, color='NO_COLOR' not in os.environ))
    except (ValueError, TypeError):
        pass
