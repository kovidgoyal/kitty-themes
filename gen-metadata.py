#! kitty +launch
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2021, Kovid Goyal <kovid at kovidgoyal.net>

import glob
import json
import os
from operator import itemgetter

from kittens.themes.collection import parse_theme


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
