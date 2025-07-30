// <CAUTION
// KEEP ALL TAGGED COMMENTS: // <TAG , // TAG>
// CAUTION>
"use strict";

const fs = require('fs');
const Path = require('path');
const os = require('os');
const servRoot = Path.dirname(fs.realpathSync(__dirname));
const jsUtilDir = Path.resolve(`${servRoot}/../_util/node`);
const _util = require(Path.resolve(`${jsUtilDir}/_util.js`));


const globals = _util.createNodeGlobals(servRoot);

module.exports = function(RED) {
    // <ACTION
    function RunNode_WwEditObjs(config) {
    // ACTION>
        _util.processNode(RED, this, config, globals);
    }
    // <REGISTER_ACTION
    RED.nodes.registerType(globals.name, RunNode_WwEditObjs);
    // REGISTER_ACTION>

    // <REGISTER_EDITOR_PLUGINS
    _util.registerNodeEditorPluginSaaP(RED, this, globals, 'select_files_folders.load_preset');
    _util.registerNodeEditorPluginSaaP(RED, this, globals, 'open_session_root.inspect_session');
    _util.registerNodeEditorPluginSaaP(RED, this, globals, 'ww_edit_objs.select_wobj_properties');
    _util.registerNodeEditorPluginNSaaP(RED, this, globals, '_util.reset_config');
    // REGISTER_EDITOR_PLUGINS>
}

module.exports.globals = globals;
