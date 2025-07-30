"use strict";
const fs = require('fs');
const Path = require('path');
const os = require('os');
const servRoot = Path.resolve(`${__dirname}/../../..`);
const jsUtilDir = Path.resolve(`${servRoot}/../_util/node`);
const _util = require(Path.resolve(`${jsUtilDir}/_util.js`));
const flowtest = require(Path.resolve(`${jsUtilDir}/_flowtest.js`));


// __file__: service/node/test/<testcase>/flow.test.js
var _pathMan = new _util.PathMan(Path.resolve(`${__dirname}/../../..`));
_pathMan.createTestcasePaths(Path.basename(__dirname));

var _tester = new flowtest.FlowTester(_pathMan);
_tester.init();
_tester.defineDefaultFixtureForEach();

describe(`${_pathMan.paths.servName}.node`, () => {

	_tester.defineNodeLoadingTest();

	// Define flow test in one of the following ways:
	// - 1: Create and export your flow from Node-RED;
	//      describe the test goal in flow's "info" field;
	//      then call:
	//      _tester.loadFlowTest(flowCfgFile, ...);
	// - 2: Define your flow json object by hand, e.g., myFlow;
	//      then call:
	//      _tester.defineFlowTest(description, myFlow, ...);
	// - Optional: define beforeEach(()=>{}) and afterEach(()=>{}) 
	//             for pre/post-processing this context
	// Refer to _util/_flowtest.js for details
	// Refer to start_flow and find_files_folders for examples
});
