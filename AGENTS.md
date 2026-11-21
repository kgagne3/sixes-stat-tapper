# Sixes Stat Tapper: project rules

## Overview

`index.html` is the whole app: CSS and JavaScript are inline. There is no build step and no framework.
Two data and feed files sit next to it:

- `data/pointbench.js` sets `window.POINTBENCH` (teams, rosters, games). Regenerate it with `tools/pull_pointbench.py`. Do not hand-edit.
- `sw.js` and `manifest.webmanifest` make the app installable and offline. Icons are `icon.svg`, `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`.

## Single-file constraint

- Keep `index.html` self-contained. No new `<link>`, `<img>` or `@import` to other hosts, no bundler, no npm.
- Allowed external calls: the external broadcast lookup, and the scoreboard WebSocket. Both are read-only. Do not add any other network request, analytics or account.
- After any change, check that the app runs both from `file://` and from a local server.

## Before editing

- Save a pre-edit copy: `cp index.html backup/index.pre-<change-name>.html`. The `backup/` folder is git-ignored.
- Read the code you are about to change. Keep the change to what was asked.

## Testing

- Test every change in a browser. Use a phone width of 375 px, and a tablet width of 768 px.
- Check the console for zero errors.
- Exercise the flows you touched: setup, goal, save, penalty, goalie prompt, CSV export.
- Use simulated scoreboard readings for live-clock work. Do not rely on the field reader being online.

## Behaviour to keep

- New events are saved as they are tapped. Log entries are in tap order, oldest first.
- Every entry keeps its game time and its tap time. The CSV keeps `game_time`, `board_clock` and `tapped_at`.
- Penalty durations are 30 sec, 1 min and 2 min.
- Team colours come from Setup. Home defaults to white. Away defaults to its flag colour.
- Light and dark theme use CSS variables.

## Privacy

- No personal details in code, commits or screenshots.
- The external socket and broadcast addresses are private to the integration team. Do not paste them into other public places, and say so before adding a new public copy.

## Workflow

- Commit with a clear message and the Co-Authored-By trailer.
- After pushing to `main`, check that GitHub Pages serves the new version before reporting done.
- Keep answers short. Say what changed, what was tested, and what was not tested.
