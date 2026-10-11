#!/bin/sh
# easy/01 -> 다듬-쉽게읽기.pdf (한 주제 한 쪽), easy/02 -> 다듬-5단계설명.pdf
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mk() { # md pdf title
  pandoc "$1" -f markdown -t html5 -s --metadata pagetitle="$3" --metadata lang=ko -H style-easy.html -o build-easy.html
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$2" "file://$PWD/build-easy.html" 2>/dev/null
  ls -la "$2"
}
mk easy/01-쉽게읽는다듬.md 다듬-쉽게읽기.pdf "쉽게 읽는 다듬"
mk easy/02-5단계설명.md 다듬-5단계설명.pdf "다듬 5단계 설명"
