'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');

const PROJECT_FORMAT = 'Photo Story Creator Project';
const CURRENT_BROWSER_FORMAT = '1.9.1';

function validateProject(project) {
  if (!project || typeof project !== 'object' || Array.isArray(project)) {
    throw new TypeError('The project must contain a JSON object.');
  }
  if (project.format !== PROJECT_FORMAT) {
    throw new Error('This is not a Photo Story Creator project.');
  }
  if (typeof project.version !== 'string' || !project.version.trim()) {
    throw new Error('The project format version is missing.');
  }
  if (project.images !== undefined && !Array.isArray(project.images)) {
    throw new Error('The project image list is invalid.');
  }
  return project;
}

function parseProject(text) {
  return validateProject(JSON.parse(text));
}

function serializeProject(project) {
  validateProject(project);
  return `${JSON.stringify(project, null, 2)}\n`;
}

async function readProject(filePath) {
  const text = await fs.readFile(filePath, 'utf8');
  return { filePath: path.resolve(filePath), project: parseProject(text) };
}

async function writeProject(filePath, project) {
  const target = path.resolve(filePath);
  const temporary = `${target}.tmp-${process.pid}`;
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(temporary, serializeProject(project), { encoding: 'utf8', mode: 0o600 });
  await fs.rename(temporary, target);
  return { filePath: target };
}

function safeProjectFilename(name) {
  const base = String(name || 'Untitled Photo Story')
    .replace(/\.pscproj$/i, '')
    .replace(/[^a-z0-9._ -]+/gi, '_')
    .trim() || 'Untitled Photo Story';
  return `${base}.pscproj`;
}

module.exports = {
  CURRENT_BROWSER_FORMAT,
  PROJECT_FORMAT,
  parseProject,
  readProject,
  safeProjectFilename,
  serializeProject,
  validateProject,
  writeProject,
};
