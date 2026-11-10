#!/usr/bin/env python3
"""Read sidebar metadata using the legacy helpers, without calling legacy Herdr."""
import argparse
import json
import os
from pathlib import Path
import runpy
import subprocess


def load(name):
    return runpy.run_path(str((Path.home() / '.local/bin' / name).resolve()))


def title(directory):
    helper = load('herdr-linear-titles')
    def git(*args):
        result = subprocess.run(['git', *args], cwd=directory, text=True,
                                capture_output=True, timeout=3)
        return result.stdout.strip() if result.returncode == 0 else ''
    branch = git('symbolic-ref', '--quiet', '--short', 'HEAD')
    ticket = helper['ticket_id'](branch)
    result = {'ticket': ticket, 'title': None, 'branch': branch}
    if ticket:
        scope = git('rev-parse', '--path-format=absolute', '--git-common-dir') or directory
        if scope.endswith('/.git'):
            scope = scope[:-5]
        cache = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))) / 'herdr-linear-titles'
        result['title'] = helper['lookup_title'](ticket, directory, scope, cache)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--cwd')
    group.add_argument('--stacks', action='store_true')
    args = parser.parse_args()
    try:
        result = load('dev-stack-status')['snapshot']() if args.stacks else title(args.cwd)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        result = {'error': str(error), 'projects': []} if args.stacks else {'error': str(error)}
    print(json.dumps(result))
