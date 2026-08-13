# Desktop development checkpoint

## Prerequisites

- Node.js 24 or newer
- npm 11 or newer
- FFmpeg and FFprobe on `PATH` for the full rendering regression suite

## Install and test

From the repository root on the `v2.0-desktop` branch:

```bash
npm install
npm test
```

## Start the desktop application

```bash
npm start
```

This checkpoint displays the unchanged v1.9.1 browser application in a secured
Electron window. Native Open and Save services are present behind the preload
bridge but are intentionally not wired into the renderer controls until the next
checkpoint. The browser's existing file-input and download behavior therefore
remains the active project workflow.

## Linux package experiments

Create an unpacked directory first:

```bash
npm run pack:linux
```

After that succeeds, create AppImage and Debian packages:

```bash
npm run dist:linux
```

Build output belongs in `dist/`, which is ignored by Git. Do not commit generated
packages, media, videos, render output, or `node_modules/`.

## Safe integration into the development branch

Extract the checkpoint ZIP outside the repository, then copy its tracked source
files into the repository. Before committing, review with:

```bash
git status --short
git diff -- . ':(exclude)package-lock.json'
npm test
```

Do not use `git clean` in a working tree that contains untracked media or test
projects.
