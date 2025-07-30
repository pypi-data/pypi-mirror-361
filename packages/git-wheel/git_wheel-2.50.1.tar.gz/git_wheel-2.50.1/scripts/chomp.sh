#!/usr/bin/env bash
for file in "$1"/*; do
  if ! [[ -f "$file" && "$(head -c2 "$file")" == '#!' ]]; then
    rm -rf "$file"
  fi
done
