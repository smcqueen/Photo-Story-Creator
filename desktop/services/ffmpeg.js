'use strict';

const { execFile } = require('node:child_process');
const { promisify } = require('node:util');

const execFileAsync = promisify(execFile);

async function probe(command) {
  try {
    const { stdout, stderr } = await execFileAsync(command, ['-version'], {
      encoding: 'utf8',
      timeout: 5000,
      windowsHide: true,
    });
    const firstLine = `${stdout}\n${stderr}`.split(/\r?\n/).find(Boolean) || '';
    return { available: true, command, version: firstLine };
  } catch (error) {
    return { available: false, command, error: error.code || error.message };
  }
}

async function getStatus() {
  const [ffmpeg, ffprobe] = await Promise.all([probe('ffmpeg'), probe('ffprobe')]);
  return { ffmpeg, ffprobe };
}

module.exports = { getStatus, probe };
