'use strict';

const { app, dialog, ipcMain } = require('electron');
const projectFiles = require('../services/project-files');
const ffmpeg = require('../services/ffmpeg');
const platform = require('../services/platform');

function registerIpcHandlers() {
  ipcMain.handle('psc:app-info', () => ({
    appVersion: app.getVersion(),
    platform: platform.describePlatform(),
  }));

  ipcMain.handle('psc:ffmpeg-status', () => ffmpeg.getStatus());

  ipcMain.handle('psc:open-project', async () => {
    const result = await dialog.showOpenDialog({
      title: 'Open Photo Story Creator Project',
      properties: ['openFile'],
      filters: [{ name: 'Photo Story Creator projects', extensions: ['pscproj', 'tlcproj'] }],
    });
    if (result.canceled || !result.filePaths[0]) return { canceled: true };
    return { canceled: false, ...(await projectFiles.readProject(result.filePaths[0])) };
  });

  ipcMain.handle('psc:save-project', async (_event, request) => {
    const suggestedName = projectFiles.safeProjectFilename(request?.suggestedName);
    const result = await dialog.showSaveDialog({
      title: 'Save Photo Story Creator Project',
      defaultPath: suggestedName,
      filters: [{ name: 'Photo Story Creator projects', extensions: ['pscproj'] }],
    });
    if (result.canceled || !result.filePath) return { canceled: true };
    const saved = await projectFiles.writeProject(result.filePath, request?.project);
    return { canceled: false, ...saved };
  });
}

module.exports = { registerIpcHandlers };
