#!/usr/bin/env bash
# Copyright (c) 2021-2022 José Manuel Barroso Galindo <theypsilon@gmail.com>

set -euo pipefail

git add dont_download.sh
git commit -m "BOT: New dont_download.sh" > /dev/null 2>&1 || true
git fetch origin main

set +e
CHANGES="$(git diff main:dont_download.sh origin/main:dont_download.sh | sed '/^[+-]export COMMIT/d' | sed '/^+++/d' | sed '/^---/d' | grep '^[+-]' | wc -l)"
set -e

if [ ${CHANGES} -ge 1 ] ; then
  echo "There are changes to push."
  echo
  git push origin main
  gh release create latest_release || true
  gh release upload latest_release dont_download.zip --clobber
  echo
  echo "New dont_download.sh can be used."
  echo "::set-output name=NEW_RELEASE::yes"
else
  echo "Nothing to be updated."
  echo "::set-output name=NEW_RELEASE::no"
fi
