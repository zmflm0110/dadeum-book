#!/bin/sh
# brief/다듬-소개서.md -> 다듬-소개서.pdf
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
pandoc brief/다듬-소개서.md -f markdown -t html5 -s --metadata pagetitle="다듬(DaDeum) 소개서" --metadata lang=ko \
  -H style.html -o build-brief.html
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="다듬-소개서.pdf" "file://$PWD/build-brief.html" 2>/dev/null
ls -la 다듬-소개서.pdf
