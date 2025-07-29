import { spawn } from 'child_process';

// const asblockPlugin = '/home/user/.config/google-chrome/Default/Extensions/adblock';

const args = [
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--disable-dev-shm-usage',
  '--disable-gpu',
  '--disable-software-rasterizer',
  '--user-data-dir=/home/user/.browser-context'
];

args.push(
  // 避免缓存积累影响性能
  '--disable-application-cache',

  // 关闭所有硬件加速特性，防止 GPU 相关崩溃
  '--disable-accelerated-2d-canvas',
  '--disable-accelerated-video-decode',

  // 禁用后台渲染，减少无关资源消耗
  '--disable-background-timer-throttling',
  '--disable-backgrounding-occluded-windows',
  '--disable-renderer-backgrounding',

  // 避免过度日志影响性能
  '--disable-logging',

  // 禁用不必要的多媒体解码
  '--mute-audio',

  // 避免崩溃时弹窗
  '--no-default-browser-check',
  '--no-first-run',
  '--headless=new',
);

args.push(
  `--remote-debugging-port=9222`,
  '--remote-debugging-address=0.0.0.0',
  'about:blank',
);

const chromePath = '/usr/bin/google-chrome';

// 启动 Chrome 并启用远程调试
const chrome = spawn(chromePath, args, {
  env: { ...process.env, DISPLAY: ':99' }
});

chrome.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

chrome.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

chrome.on('close', (code) => {
  console.log(`Chrome process exited with code ${code}`);
});

console.log('Browser launched and ready...');

// 保持进程不退出，并监听中止信号
process.stdin.resume();
process.on('SIGINT', () => process.exit());
process.on('SIGTERM', () => process.exit());