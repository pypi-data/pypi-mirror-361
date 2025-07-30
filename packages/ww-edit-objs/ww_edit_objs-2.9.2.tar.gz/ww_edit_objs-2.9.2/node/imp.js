// <CAUTION
// KEEP ALL TAGGED COMMENTS: // <TAG , // TAG>
// CAUTION>
"use strict";
const fs = require('fs');
const Path = require('path');
const os = require('os');
const servRoot = Path.dirname(fs.realpathSync(__dirname));
const jsUtilDir = Path.resolve(`${servRoot}/../_util/node`);
const grpc = require(Path.resolve(`${jsUtilDir}/node_modules/@grpc/grpc-js`));
const jsApiGenDir = Path.resolve(`${jsUtilDir}/gen`);
const prog = require(Path.resolve(`${jsUtilDir}/_progress.js`));


function createRpcRequest (args, config)  {
    // <REQUIRE_MODULE_PB
    const messages = require(Path.resolve(`${jsApiGenDir}/ww_edit_objs_pb.js`));
    // REQUIRE_MODULE_PB>
    var request = new messages.Request();
    // <SHARED_CONFIG_RPC_STATIC
    request.setSaveconfig(config.saveconfig);
    request.setCfgfile(config.cfgfile);
    request.setDryrun(config.dryrun);
    request.setNotifyuser(config.notifyuser);
    request.setAppsessionid(args.appsessionid);
    // SHARED_CONFIG_RPC_STATIC>
    // <INPUT_RPC_STATIC
    request.setInputobjlist(args.inputobjlist);
    // INPUT_RPC_STATIC>
    // <CONFIG_RPC_STATIC
    request.setAllowcustomproperty(config.allowcustomproperty);
    request.setProperty(config.property);
    request.setValue(config.value);
    request.setConflictresolution(config.conflictresolution);
    request.setEnablerandomizer(config.enablerandomizer);
    request.setRandomizerminoffset(config.randomizerminoffset);
    request.setRandomizermaxoffset(config.randomizermaxoffset);
    // CONFIG_RPC_STATIC>
    return request;
}

function createRpcClient (port) {
    // <REQUIRE_MODULE_GRPC
    const services = require(Path.resolve(`${jsApiGenDir}/ww_edit_objs_grpc_pb.js`));
    // REQUIRE_MODULE_GRPC>

    // <CREATE_CLIENT_STATIC
    return new services.WwEditObjsClient(
    // CREATE_CLIENT_STATIC>
        `localhost:${port}`,
        grpc.credentials.createInsecure()
    );
}


module.exports = {

// name = [/path/to/]<service_name>[/node/imp.js]
name: Path.basename(servRoot),

callRpcMethod: (port, args, onRpcDone, node) => {
    let client = createRpcClient(port);
    let request = createRpcRequest(args, node.config);
    let meta = new grpc.Metadata();
    meta = prog.registerProgressToRpcMetadata(meta, node);
    let onStopMonitorProgress = prog.startMonitorProgress(
        port,
        meta,
        (progress) => { node.statusProgress(progress); }
    );
    // <RPC_STATIC
    client.wwEditObjs(request, meta, (err, reply) => {
    // RPC_STATIC>
        client.close();
        onStopMonitorProgress();
        onRpcDone(err, reply, node);
    });
},

extractRpcOutput: (output) => {
    return {
        // <OUTPUT_NODE
        passedobjlist: output.getPassedobjlist(),
        // OUTPUT_NODE>
    };
},

createSubprocOptions: (input, config) => {
    let opts = [
        // <INPUT_SUBPROC_REGULAR
        '-i', input.inputobjlist,
        // INPUT_SUBPROC_REGULAR>
        // <CONFIG_SUBPROC_REGULAR
        '-p', config.property,
        '-v', config.value,
        '-R', config.conflictresolution,
        '--randomizer-min-offset', config.randomizerminoffset,
        '--randomizer-max-offset', config.randomizermaxoffset,
        // CONFIG_SUBPROC_REGULAR>
    ];
    // <INPUT_SUBPROC_BOOL
    // INPUT_SUBPROC_BOOL>
    // <CONFIG_SUBPROC_BOOL
    if (config.allowcustomproperty) { opts.push('-c'); }
    if (config.enablerandomizer) { opts.push('-r'); }
    // CONFIG_SUBPROC_BOOL>
    return opts;
},

extractSubprocOutput: (reply) => {
    return {
        // <OUTPUT_NODE
        passedobjlist: reply.output.passedObjList,
        // OUTPUT_NODE>
    };
}


};  // module.exports = {
