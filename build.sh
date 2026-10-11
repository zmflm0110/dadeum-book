#!/bin/sh
# chapters/*.md -> 다듬-완전정복.pdf  (pandoc -> HTML -> headless Chrome)
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
pandoc chapters/*.md -f markdown -t html5 -s --toc --toc-depth=2 \
  --metadata title="다듬(DaDeum) 완전정복" --metadata lang=ko \
  -H style.html -o build.html
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="다듬-완전정복.pdf" "file://$PWD/build.html" 2>/dev/null
ls -la 다듬-완전정복.pdf
