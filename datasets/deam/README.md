---
abstract: "DEAM local layout. Audio and annotations are gitignored. Canonical source is cvml.unige.ch, not mirdata."
---

# DEAM (local)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Canonical files: https://cvml.unige.ch/databases/DEAM/

- `DEAM_Annotations.zip` — 2 Hz averaged arousal/valence
- `DEAM_audio.zip` — `MEMD_audio/{song_id}.mp3`
- `metadata.zip`

**Not loaded via mirdata.** There is no `mirdata.initialize("deam")`.

Licence: CC-licensed source audio; commercial status **UNKNOWN** (pages mix BY-NC). Research use with PLOS ONE citation.

Do not commit the zip/mp3 trees.
