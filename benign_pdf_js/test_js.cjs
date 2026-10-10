'use strict';
// Mock API semantics only: NOT a PDF viewer execution result.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const js = fs.readFileSync(path.join(__dirname, 'artifacts', 'test.js'), 'utf8');
const names = ['test_status', 'viewer_type', 'viewer_version', 'viewer_variation'];
function run(app) {
  const fields = Object.fromEntries(names.map(n => [n, {value: n === 'test_status' ? 'NOT_RUN' : 'UNKNOWN'}]));
  const context = {app, getField(name) { assert.ok(names.includes(name)); return fields[name]; }};
  vm.runInNewContext(js, context, {timeout: 1000});
  return fields;
}
const observed = run({viewerType:'MockReader', viewerVersion:24.1, viewerVariation:'MockVariation'});
assert.equal(observed.test_status.value, 'JS_EXECUTED');
assert.equal(observed.viewer_type.value, 'MockReader');
assert.equal(String(observed.viewer_version.value), '24.1');
assert.equal(observed.viewer_variation.value, 'MockVariation');
console.log('PASS normal mock fields');
for (const missing of ['viewerType', 'viewerVersion', 'viewerVariation']) {
  const app = {viewerType:'MockReader', viewerVersion:24.1, viewerVariation:'MockVariation'};
  Object.defineProperty(app, missing, {get() {throw new Error('API unavailable');}});
  const f = run(app);
  assert.equal(f.test_status.value, 'JS_EXECUTED');
  const mapping = {viewerType:'viewer_type', viewerVersion:'viewer_version', viewerVariation:'viewer_variation'};
  assert.equal(f[mapping[missing]].value, 'UNKNOWN');
  for (const prop of Object.keys(mapping).filter(p => p !== missing)) {
    assert.notEqual(f[mapping[prop]].value, 'UNKNOWN');
  }
  console.log('PASS independent unavailable API:', missing);
}
assert.doesNotMatch(js, /launchURL|submitForm|exportDataObject|importDataObject|saveAs|eval\s*\(|Function\s*\(|setTimeOut|setInterval|XMLHttpRequest|fetch\s*\(|https?:|require\s*\(|app\.alert/);
console.log('PASS forbidden-operation lexical check (supplements source review)');
