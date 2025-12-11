# Celestial Radio & Music Bot Playbook

Source: Discord broadcast planning chat (Celestial Radio, Hydra vs. FredBoat).

## Celestial Radio Structure
- **Category:** `🌌 The Celestial Radio` (broadcast + stream hub).
- **Channels:**
  - `🎙️ the-station` — live talks, Q&As, meditations, or open forum broadcasts.
  - `🎧 vibe-stream` — music-focused voice/text hybrid for lo-fi, ambient, or Irie playlists.
  - `💬 radio-chat` — linked text channel for song requests, reactions, questions during broadcasts.
  - Optional: `🎵 dj-booth` (community DJ takeovers) and `📅 show-schedule` (announce upcoming sets).
- **Pinned Intro (drop in #radio-chat):**
  ```
  Welcome to The Celestial Radio 🌌🎶
  Where airwaves melt into mindfulness and music becomes medicine.

  🎙️ Tune in via the-station for live talks + celestial convos.
  🎧 Vibe out in vibe-stream and drop song requests below.
  💬 React, share feels, or ask questions right here in radio-chat.

  Honor the vibe, keep lyrics mindful, and treat silence as sacred.
  ```

## Hydra vs. FredBoat (2025 snapshot)

| Feature | Hydra Bot | FredBoat |
| --- | --- | --- |
| Music status | Previously full-featured but removed premium music features (per Feb 2023 update); functionality may be limited or disabled entirely. | Continues to stream music from YouTube/SoundCloud/playlists using classic commands. |
| Interfaces | Slash commands, dashboards, Spotify integration (when enabled); may no longer function for audio. | Text commands with `;;` prefix; simple and reliable. |
| Always-on stream | Requires premium + stable music support (no longer officially available). | Supports long queues but no native 24/7 mode; works as long as voice channel is active. |
| Best use now | Utility/moderation features if music removed. | Primary music bot for Celestial Radio. |

**Recommendation:** Use FredBoat as the main music bot. Keep Hydra only if you need its non-music features or in case music playback is restored.

## FredBoat Installation Guide

1. **Invite Bot:** Visit `https://fredboat.com/invite`, select the Irie Igloo server, and authorize with Connect, Speak, Read Messages, Send Messages, and Use Slash Commands.
2. **Voice Channel:** Use `🎧 vibe-stream` (or whichever Celestial Radio voice channel you want) before issuing commands.
3. **Core Commands (double semicolons):**
   - `;;play <song name or URL>` — queue a track/playlist.
   - `;;queue` — display upcoming songs.
   - `;;skip` — skip current track.
   - `;;stop` — clear queue + make bot leave.
   - `;;pause` / `;;resume` — control playback.
   - `;;shuffle` — shuffle queue.
   - `;;help` — show command list.
4. **Song Request Channel:** Create/pin instructions in `#radio-chat` or `#song-requests`. Example:
   ```
   🎶 Request Flow
   1. Join 🎧 vibe-stream.
   2. Type ;;play <song/link>.
   3. DJs manage skips — request politely.
   4. Keep lyrics + energy aligned with portal vibes.
   ```
5. **DJ Role:**  
   - Create `🎵 DJ` role (Server Settings → Roles).  
   - Enable Connect, Speak, and Use Slash Commands.  
   - Assign to trusted curators so only they can run moderation commands (`;;skip`, `;;stop`).  
   - Adjust Integrations → FredBoat to restrict command usage to DJ role if desired.
6. **Maintenance Tips:**  
   - Run `;;stop` after long sessions to prevent queue ghosts.  
   - If bot ignores commands, check channel permissions (it must read/send messages).  
   - Clear laggy queues by stopping and re-adding songs.  
   - Encourage DJs to use playlists to keep transitions smooth.

## Optional Secondary Bots
- **Lofi Radio / Chillout bots:** Keep continuous lo-fi in a secondary voice channel if you want 24/7 ambiance without manual queues.
- **Jockey / Green-burst alternatives:** Use if you need volume controls, EQ filters, or multi-bot rotation.

## Broadcast Ritual Template
Leverage this for weekly Celestial Radio events:
1. **Opening (5 min):** Host introduces theme, sets intention.
2. **Vibe Stream (15–20 min):** Curated music or guided breath to settle the room.
3. **Circle Dialogue (20 min):** Open floor or featured guest conversation via `🎙️ the-station`.
4. **Community Share (10 min):** Invite questions via `💬 radio-chat`.
5. **Closing Ground (5 min):** Breath cue, affirmation, or sonic send-off.

Use the template as a run-of-show when hosting Velvet Evenings recaps, Bound & Beyond debriefs, or nutrition spotlights inside Celestial Radio.
