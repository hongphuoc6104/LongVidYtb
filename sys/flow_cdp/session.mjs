/** Persistent local session; fixed commands only, no arbitrary browser execution. */
import fs from 'node:fs';
import net from 'node:net';
import os from 'node:os';
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {browserConfig,debugEndpoint,inspect,safeResults,toolUrl,verifyBrowser} from './controller.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=fs.existsSync(path.join(here,'../pilot.py'))?path.resolve(here,'..'):path.resolve(here,'../..');

export function sessionSocketPath(targetRoot=root) {
  const suffix = process.env.VP_SESSION_KEY || '';
  const key = crypto.createHash('sha256').update(path.resolve(targetRoot) + suffix).digest('hex').slice(0, 16);
  const uid = typeof process.getuid === 'function' ? process.getuid() : 1000;
  const tmp = os.tmpdir();
  return path.join(tmp, `video-pilot-${uid}`, `flow-${key}.sock`);
}

export class Session {
  constructor(connect,verify=async()=>null){this.connect=connect;this.verify=verify;this.identity=null;this.browser=null;this.attempted=false;}
  async start(){
    if(this.browser?.isConnected()) {this.identity=await this.verify(this.browser);return {status:'connected',reused:true,identity:this.identity};}
    if(this.attempted) throw Error('Session ended: no automatic reconnect; restart the service explicitly');
    this.attempted=true;
    this.browser=await this.connect();
    try {this.identity=await this.verify(this.browser);} catch(e) {await this.stop();throw e;}
    return {status:'connected',reused:false,identity:this.identity};
  }
  status(){return {status:this.browser?.isConnected()?'connected':this.attempted?'disconnected':'not_connected'};}
  async stop(){if(this.browser) await this.browser.close();this.browser=null;this.identity=null;}
}

export async function serve(targetSocket=null, options={}){
  safeResults();
  const socketPath = targetSocket || options.socket || sessionSocketPath();
  const socketDir = path.dirname(socketPath);
  if (!fs.existsSync(socketDir)) {
    fs.mkdirSync(socketDir, { recursive: true, mode: 0o700 });
  } else {
    try { fs.chmodSync(socketDir, 0o700); } catch {}
  }
  if(fs.existsSync(socketPath)) {
    try { fs.unlinkSync(socketPath); } catch {}
  }

  const configPath = fs.existsSync(path.join(here, '../config.json')) ? path.join(here, '../config.json') : path.join(here, '../../config.json');
  const browserProfilesPath = path.join(here, 'browser-profiles.json');
  const config = {
    ...JSON.parse(fs.readFileSync(configPath, 'utf8')),
    ...(fs.existsSync(browserProfilesPath) ? JSON.parse(fs.readFileSync(browserProfilesPath, 'utf8')) : {}),
  };
  if (options.profile || process.env.VP_CHROME_PROFILE) {
    config.flow_profile_directory = options.profile || process.env.VP_CHROME_PROFILE;
  }
  const selected=browserConfig(config);
  let bound=null;
  const chromePort = options.port || process.env.VP_CHROME_PORT;
  const session=new Session(async()=>{
    if (chromePort) {
      return chromium.connectOverCDP(`http://127.0.0.1:${chromePort}`, {timeout:60000});
    }
    const activePortPath = path.join(selected.dataDir, 'DevToolsActivePort');
    if (!fs.existsSync(activePortPath)) {
      throw Error(`DEVTOOLS_PORT_NOT_FOUND: neither VP_CHROME_PORT nor ${activePortPath} exists`);
    }
    const endpoint=debugEndpoint(fs.readFileSync(activePortPath,'utf8'));
    return chromium.connectOverCDP(endpoint,{timeout:60000});
  }, async browser=>{
    const context=browser.contexts()[0];
    if(!context) throw Error('NO_CHROME_CONTEXT');
    if(bound) {
      if(bound.page.isClosed()) throw Error('BOUND_TAB_CLOSED');
      return bound.identity;
    }
    bound=await verifyBrowser(browser,config,true);
    if(bound.page.isClosed())throw Error('BOUND_TAB_CLOSED');
    return bound.identity;
  });
  const ensureBoundPage=async()=>{
    if(bound?.page && !bound.page.isClosed()) return bound;
    throw Error('BOUND_TAB_CLOSED: reconnect and verify the configured profile; do not replace the tab silently');
  };
  let queue=Promise.resolve();
  const server=net.createServer(client=>{
    let data='';
    client.on('error',()=>{});
    client.on('data',chunk=>{
      data+=chunk;
      if(data.length>8192){client.destroy();return;}
      if(!data.includes('\n'))return;
      client.removeAllListeners('data');
      const command=data.trim();
      if(command==='status') {
        client.end(JSON.stringify(session.status())+'\n');
        return;
      }
      queue=queue.then(async()=>{
        try {
          let result;
          if(command==='connect') {
            result=await session.start();
            await ensureBoundPage();
            if(bound?.page && !bound.page.url().startsWith(toolUrl)) {
              await bound.page.goto(toolUrl,{waitUntil:'domcontentloaded',timeout:30000});
            }
          }
          else if(command==='inspect') {
            if(session.status().status!=='connected') throw Error('CONNECT_FIRST: session unavailable');
            await ensureBoundPage();
            result=await inspect(config,session.browser,bound);
            fs.writeFileSync(path.join(safeResults(),`session-inspect-${Date.now()}.json`),JSON.stringify(result,null,2));
          } else if(['editor-inspect','reference-inspect'].includes(command) || command.startsWith('tool-snapshot')) {
            if(session.status().status!=='connected')throw Error('CONNECT_FIRST');
            await ensureBoundPage();
            const operations=await import('./browser-operations.mjs?revision='+Date.now());
            result=await operations.runOperation(command,bound);
          } else if(command==='stop') {
            if(bound && !bound.page.isClosed())await bound.page.close();
            await session.stop();result={status:'stopped'};
          } else throw Error('Unsupported session command');
          client.end(JSON.stringify(result)+'\n');
          if(command==='stop')server.close();
        }catch(e){client.end(JSON.stringify({status:'blocked',reason:e.message})+'\n');}
      });
    });
  });
  server.on('close',()=>{if(fs.existsSync(socketPath))fs.unlinkSync(socketPath);});
  const oldUmask = typeof process.umask === 'function' ? process.umask(0o177) : null;
  server.listen(socketPath, () => {
    try { fs.chmodSync(socketPath, 0o600); } catch {}
    console.log('Persistent session ready; run session.mjs connect once.');
  });
  if (oldUmask !== null) process.umask(oldUmask);
  for(const sig of ['SIGTERM','SIGINT'])process.on(sig,async()=>{await session.stop().catch(()=>{});server.close();});
}

export async function client(command, targetSocket=null){
  const socketPath = targetSocket || sessionSocketPath();
  await new Promise((resolve,reject)=>{
    const socket=net.createConnection(socketPath,()=>socket.write(command+'\n'));
    let response='';
    socket.setTimeout(180000,()=>socket.destroy(Error('SESSION_COMMAND_TIMEOUT: inspect status before retrying')));
    socket.on('data',d=>{response+=d;process.stdout.write(d);});
    socket.on('end',()=>{try {if(JSON.parse(response).status==='blocked')process.exitCode=2;}catch{process.exitCode=2;}resolve();});socket.on('error',reject);
  });
}

export function parseArgs(argv = process.argv.slice(2)) {
  const options = {};
  let cmd = null;
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--port' && i + 1 < argv.length) {
      options.port = parseInt(argv[++i], 10);
    } else if (arg === '--profile' && i + 1 < argv.length) {
      options.profile = argv[++i];
    } else if (arg === '--socket' && i + 1 < argv.length) {
      options.socket = argv[++i];
    } else if (!arg.startsWith('-') && !cmd) {
      cmd = arg;
    }
  }
  return { cmd: cmd || 'status', options };
}

if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const { cmd, options } = parseArgs();
  (cmd==='serve' ? serve(options.socket, options) : client(cmd, options.socket))
    .catch(e=>{console.error(e.message);process.exitCode=2;});
}
