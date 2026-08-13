'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const projectFiles = require('../../desktop/services/project-files');

const root = path.resolve(__dirname, '..', '..');
const samples = fs.readdirSync(path.join(root, 'samples'))
  .filter((name) => name.endsWith('.pscproj'));

for (const sample of samples) {
  test(`opens legacy fixture ${sample}`, () => {
    const source = fs.readFileSync(path.join(root, 'samples', sample), 'utf8');
    const project = projectFiles.parseProject(source);
    assert.equal(project.format, projectFiles.PROJECT_FORMAT);
    assert.ok(Array.isArray(project.images));
  });
}

test('serialization preserves unknown fields and project version', () => {
  const project = {
    format: projectFiles.PROJECT_FORMAT,
    version: '1.9.1',
    projectName: 'Compatibility test',
    images: [],
    futureField: { retained: true },
  };
  assert.deepEqual(projectFiles.parseProject(projectFiles.serializeProject(project)), project);
});

test('writeProject replaces through a temporary file', async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'psc-desktop-test-'));
  const target = path.join(directory, 'round-trip.pscproj');
  const project = { format: projectFiles.PROJECT_FORMAT, version: '1.9.1', images: [] };
  await projectFiles.writeProject(target, project);
  const loaded = await projectFiles.readProject(target);
  assert.deepEqual(loaded.project, project);
  assert.equal(fs.readdirSync(directory).length, 1);
});

test('safeProjectFilename always has one project extension', () => {
  assert.equal(projectFiles.safeProjectFilename('My Story.pscproj'), 'My Story.pscproj');
  assert.equal(projectFiles.safeProjectFilename('../unsafe/name'), '.._unsafe_name.pscproj');
});
