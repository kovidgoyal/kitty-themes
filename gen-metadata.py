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


def parse_theme(fname, raw):
    in_blurb = False
    lines = raw.splitlines()
    conf = parse_config(lines)
    bg = conf.get('background', Color())
    is_dark = max(bg) < 115
    ans = {'blurb': '', 'name': theme_name_from_file_name(fname)}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.startswith('## '):
            break
        line = line[3:]
        if in_blurb:
            ans['blurb'] += line
            continue
        key, val = line.split(':', 1)
        key = key.strip().lower()
        val = val.strip()
        if val:
            ans[key] = val
    if not ans['blurb']:
        del ans['blurb']
    if is_dark:
        ans['is_dark'] = True
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
