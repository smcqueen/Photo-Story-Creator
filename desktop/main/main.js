'use strict';

const path = require('node:path');
const { app, BrowserWindow, shell } = require('electron');
const { registerIpcHandlers } = require('./ipc');

let mainWindow;

function isTrustedLocalUrl(url) {
  return url.startsWith('file:');
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 1024,
    minHeight: 700,
    show: false,
    backgroundColor: '#101827',
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
    },
  });

  mainWindow.removeMenu();
  mainWindow.once('ready-to-show', () => mainWindow.show());
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('https:')) shell.openExternal(url);
    return { action: 'deny' };
  });
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!isTrustedLocalUrl(url)) event.preventDefault();
  });
  mainWindow.loadFile(path.join(__dirname, '..', '..', 'index.html'));
  return mainWindow;
}

app.whenReady().then(() => {
  registerIpcHandlers();
  createMainWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

module.exports = { createMainWindow, isTrustedLocalUrl };
