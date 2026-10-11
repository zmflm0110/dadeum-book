#!/bin/sh
# README.md -> 다듬-README.pdf (용어·기술 목록 포함, 단독으로 읽을 수 있음)
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
pandoc README.md -f markdown -t html5 -s --metadata pagetitle="다듬 README" --metadata lang=ko -H style-easy.html -o build-readme.html
"$CHROME" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="다듬-README.pdf" "file://$PWD/build-readme.html" 2>/dev/null
ls -la 다듬-README.pdf
