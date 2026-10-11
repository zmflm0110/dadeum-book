#!/bin/sh
# qa/*.md -> 다듬-질의응답.pdf
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
pandoc qa/*.md -f markdown -t html5 -s --toc --toc-depth=1 --metadata pagetitle="다듬 질의응답 대비서" --metadata lang=ko \
  -H style.html -o build-qa.html
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="다듬-질의응답.pdf" "file://$PWD/build-qa.html" 2>/dev/null
ls -la 다듬-질의응답.pdf
