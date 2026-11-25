// Simulate what browser does when loading graphs.html
const fs = require('fs');
const path = require('path');

// 1. Mock window / document
global.window = global;
global.document = {
  fullscreenElement: null,
  documentElement: {
    requestFullscreen: async () => {},
  },
  getElementById: (id) => {
    return {
      id,
      innerHTML: '',
      innerText: '',
      textContent: '',
      style: {},
      classList: { add: () => {}, remove: () => {} },
      appendChild: () => {},
      addEventListener: () => {},
      closest: () => null
    };
  },
  createElement: (tag) => {
    return {
      tagName: tag,
      innerHTML: '',
      innerText: '',
      textContent: '',
      style: {},
      classList: { add: () => {}, remove: () => {} },
      appendChild: () => {},
      addEventListener: () => {},
      querySelector: () => ({ innerHTML: '', innerText: '', style: {} }),
      querySelectorAll: () => []
    };
  },
  addEventListener: () => {}
};
global.URLSearchParams = URLSearchParams;
global.location = { search: '?from=admin' };

// Load data.js
require('./Houses/admin/data.js');
console.log('ADMIN_DATA loaded:', !!global.window.ADMIN_DATA);
console.log('ADMIN_DATA houses count:', global.window.ADMIN_DATA?.houses?.length);
console.log('ADMIN_DATA students count:', global.window.ADMIN_DATA?.students?.length);

// Load graphs.js
try {
  require('./Houses/graphs.js');
  console.log('graphs.js loaded and executed successfully without error!');
} catch (e) {
  console.error('Error in graphs.js:', e);
}
