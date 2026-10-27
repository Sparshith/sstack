#!/bin/sh
# Show a page. In Chrome on macOS: reload the tab that already has it and close duplicates.
# Anywhere else: open it with the default browser.
# usage: show.sh path/to/index.html
f="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
if [ "$(uname)" != Darwin ] || ! pgrep -xq "Google Chrome"; then
  case "$(uname)" in Darwin) open "$f" ;; *) xdg-open "$f" >/dev/null 2>&1 & ;; esac
  exit 0
fi
found=$(osascript - "$f" <<'OSA'
on run argv
  set target to item 1 of argv
  tell application "Google Chrome"
    set kept to false
    repeat with w in windows
      set i to (count of tabs of w)
      repeat while i ≥ 1
        set t to tab i of w
        if (URL of t) contains target then
          if kept then
            close t
          else
            set kept to true
            tell t to reload
          end if
        end if
        set i to i - 1
      end repeat
    end repeat
    return kept
  end tell
end run
OSA
)
[ "$found" = "true" ] || open -a "Google Chrome" "$f"
