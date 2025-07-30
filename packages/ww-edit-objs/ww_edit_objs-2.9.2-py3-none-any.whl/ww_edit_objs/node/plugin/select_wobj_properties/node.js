"use strict";
const fs = require('fs');
const Path = require('path');
const os = require('os');
const servRoot = Path.resolve(`${fs.realpathSync(__dirname)}/../../..`);
const jsUtilDir = Path.resolve(`${servRoot}/../_util/node`);
const _util = require(Path.resolve(`${jsUtilDir}/_util.js`));

module.exports = {

// - called after client (host-node editor from browser) sends REST request to server (host-node runtime)
// - before server calls plugin backend service using RPC
// - here you can decorate plugin RPC arguments
// - or prepare session resources required by plugin service
prePluginServiceRPC: (pluginTriggerRequest) => {
    let pluginRpcArgs = pluginTriggerRequest.query;
    return pluginRpcArgs;
},

// Node-Editor Plugin Server Callback: RE-IMPLEMENT AS NEEDED
// - plugin server/client: node.js/node.html
// - called before server responds to client with plugin service RPC output
// - you can decorate plugin RPC output
// - or prepare session resources required by the plugin client
prePluginServerResponse: (pluginServOutput) => {
    let responseToPluginClient = pluginServOutput.payload;
    return responseToPluginClient;
}

}  // module.exports = {
