'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const root = path.resolve(__dirname, '..', '..');

test('browser release remains unchanged as the renderer entry point', () => {
  const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  assert.match(html, /Photo Story Creator 1\.9\.1/);
  assert.match(html, /defaults\.version='1\.9\.1'/);
});

test('Electron renderer is isolated from Node', () => {
  const main = fs.readFileSync(path.join(root, 'desktop', 'main', 'main.js'), 'utf8');
  assert.match(main, /contextIsolation:\s*true/);
  assert.match(main, /nodeIntegration:\s*false/);
  assert.match(main, /sandbox:\s*true/);
  assert.match(main, /setWindowOpenHandler/);
  assert.match(main, /will-navigate/);
});

test('preload exposes a narrow API instead of raw IPC', () => {
  const preload = fs.readFileSync(path.join(root, 'desktop', 'preload', 'preload.js'), 'utf8');
  assert.doesNotMatch(preload, /exposeInMainWorld\([^,]+,\s*ipcRenderer/);
  for (const method of ['getAppInfo', 'getFfmpegStatus', 'openProject', 'saveProject']) {
    assert.match(preload, new RegExp(method));
  }
});
