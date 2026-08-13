'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('photoStoryDesktop', Object.freeze({
  isDesktop: true,
  getAppInfo: () => ipcRenderer.invoke('psc:app-info'),
  getFfmpegStatus: () => ipcRenderer.invoke('psc:ffmpeg-status'),
  openProject: () => ipcRenderer.invoke('psc:open-project'),
  saveProject: (project, suggestedName) =>
    ipcRenderer.invoke('psc:save-project', { project, suggestedName }),
}));
