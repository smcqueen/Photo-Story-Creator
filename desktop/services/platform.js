'use strict';

function describePlatform() {
  return {
    os: process.platform,
    arch: process.arch,
    node: process.versions.node,
    supported: ['linux', 'win32', 'darwin'].includes(process.platform),
    primaryTarget: process.platform === 'linux',
  };
}

module.exports = { describePlatform };
