# Photo Story Creator v2.0 desktop architecture

## Checkpoint 1: Electron foundation

Photo Story Creator v1.9.1 remains the stable browser release. The
`v2.0-desktop` branch starts from the exact v1.9.1 commit and initially loads the
unchanged browser application as its Electron renderer. This keeps all current
storyboard, preview, timing, caption, transition, motion, transform, audio,
recovery, and render-script behavior available while desktop capabilities are
introduced behind a controlled boundary.

## Source layout

| Path | Responsibility |
| --- | --- |
| `index.html` | Unchanged v1.9.1 browser renderer and compatibility baseline |
| `desktop/main/` | Electron lifecycle, window policy, dialogs, and IPC registration |
| `desktop/preload/` | Small renderer-facing desktop API |
| `desktop/services/` | Project files, FFmpeg discovery, and platform adapters |
| `shared/project-format/` | Compatibility and future migration policy |
| `tests/desktop/` | Desktop security and `.pscproj` compatibility checks |

## Security boundary

The renderer has no Node.js integration. Context isolation, Chromium sandboxing,
and web security remain enabled. The preload exposes named operations only; it
does not expose `ipcRenderer`, filesystem modules, shell execution, or arbitrary
paths. New windows are denied, remote navigation is blocked, and HTTPS links may
only be handed to the operating system browser.

## `.pscproj` compatibility

The desktop service accepts the existing format marker, requires a version, and
requires `images` to be an array when present. Unknown fields are retained.
Legacy fixtures from v1.2 through v1.7 are exercised by the Node test suite, while
the unchanged browser loader continues to supply current defaults and normalize
image IDs. No v2-only project schema is introduced at this checkpoint.

Before a future schema change:

1. Add real v1.8 and v1.9.1 fixtures without source media.
2. Extract browser defaulting into a shared pure module.
3. Define explicit, one-way in-memory migrations with fixture tests.
4. Decide whether desktop-only data belongs beside the project rather than in it.
5. Retain an explicit browser-compatible save option while v1.9.1 is supported.

## Linux-first, cross-platform design

Linux is the first packaging and acceptance target (`AppImage` and `deb`). Main
process services use Node APIs that also work on Windows and macOS. Platform
differences stay behind service modules. Paths are passed as values rather than
embedded shell fragments; future FFmpeg execution should use argument arrays and
`spawn`, never construct a shell command from project data.

## Planned checkpoints

### Checkpoint 2: desktop-aware project workflow

- Route Open and Save through native dialogs when `photoStoryDesktop` exists.
- Keep browser download/file-input behavior as the fallback.
- Track the current project path and update the window title.
- Add dirty-state confirmation before desktop window close.
- Add v1.8 and v1.9.1 compatibility fixtures.

### Checkpoint 3: native media access

- Select image and audio folders with native dialogs.
- Store portable relative paths where possible.
- Reuse the existing thumbnail and relinking behavior.
- Add recent projects without storing media bytes.

### Checkpoint 4: managed FFmpeg rendering

- Detect and validate FFmpeg/FFprobe.
- Move render planning out of the HTML application into testable shared code.
- Run FFmpeg directly with argument arrays and stream progress to the UI.
- Preserve generated Linux and Windows scripts as an exportable advanced option.
- Retain resumable clip fingerprints and never overwrite source media.

### Checkpoint 5: Linux preview package

- Add application icons and desktop metadata.
- Build unpacked Linux output first, then AppImage and Debian packages.
- Test on Linux Mint with projects opened from local and Synology-mounted paths.
- Verify clean interruption, relinking, audio resolution, and render resumption.

## Non-goals for the initial checkpoint

- Rewriting the interface in a JavaScript framework.
- Changing the `.pscproj` schema version.
- Bundling FFmpeg before licensing and update behavior are decided.
- Removing browser operation or generated render scripts.
- Making filesystem changes outside a user-selected project or output location.
