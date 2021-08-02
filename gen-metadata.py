#! kitty +launch
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2021, Kovid Goyal <kovid at kovidgoyal.net>

import glob
import json
import os
import re
from operator import itemgetter

from kitty.config import parse_config
from kitty.rgb import Color


def theme_name_from_file_name(fname):
    ans = fname.rsplit('.', 1)[0]
    ans = ans.replace('_', ' ')

    def camel_case(m):
        return m.group(1) + ' ' + m.group(2)

    ans = re.sub(r'([a-z])([A-Z])', camel_case, ans)
    return ' '.join(x.capitalize() for x in filter(None, ans.split()))


class LineParser:

    def __init__(self):
        self.in_metadata = False
        self.in_blurb = False
        self.keep_going = True

    def __call__(self, line, ans):
        is_block = line.startswith('## ')
        if self.in_metadata and not is_block:
            self.keep_going = False
            return
        if not self.in_metadata and is_block:
            self.in_metadata = True
        if not self.in_metadata:
            return
        line = line[3:]
        if self.in_blurb:
            ans['blurb'] += line
            return
        try:
            key, val = line.split(':', 1)
        except Exception:
            self.keep_going = False
            return
        key = key.strip().lower()
        val = val.strip()
        if val:
            ans[key] = val


def parse_theme(fname, raw):
    lines = raw.splitlines()
    conf = parse_config(lines)
    bg = conf.get('background', Color())
    is_dark = max(bg) < 115
    ans = {'blurb': '', 'name': theme_name_from_file_name(fname)}
    parser = LineParser()
    for i, line in enumerate(raw.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            parser(line, ans)
        except Exception as e:
            raise SystemExit(
                f'Failed to parse {fname} line {i+1} with error: {e}')
        if not parser.keep_going:
            break
    if not ans['blurb']:
        del ans['blurb']
    if is_dark:
        ans['is_dark'] = True
    ans['num_settings'] = len(conf)
    return ans


def main():
    themes = []
    seen = {}
    for theme in glob.glob('themes/*.conf'):
        name = os.path.basename(theme)
        with open(theme) as f:
            text = f.read()
        td = parse_theme(name, text)
        td['file'] = theme
        if td['name'] in seen:
            raise SystemExit(
                f'The theme {td["name"]} is defined multiple times')
        seen[td['name']] = theme
        themes.append(td)

    themes.sort(key=itemgetter('name'))
    with open('themes.json', 'w') as f:
        json.dump(themes, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
