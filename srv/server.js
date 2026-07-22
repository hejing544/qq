// QQ 服务端 — Express REST API + WebSocket
const express = require('express');
const cors = require('cors');
const http = require('http');
const { WebSocketServer } = require('ws');
const path = require('path');
const fs = require('fs');
const bcrypt = require('bcryptjs');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// 配置
const PORT = 3000;
const DATA_DIR = path.join(__dirname, 'data');
const USER_DB_FILE = path.join(DATA_DIR, 'user_db.json');
const HEARTBEAT_TIMEOUT = 60 * 1000;  // 60 秒无心跳视为离线
const CLEANUP_INTERVAL = 10 * 1000;   // 每 10 秒清理一次过期在线状态

// 确保数据目录存在
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// 中间件
app.use(cors());
app.use(express.json());

// ============== 数据层 ==============

function loadUsers() {
  if (fs.existsSync(USER_DB_FILE)) {
    try {
      const raw = fs.readFileSync(USER_DB_FILE, 'utf-8');
      return JSON.parse(raw);
    } catch (e) {
      console.error('加载用户数据库失败:', e.message);
    }
  }
  return {};
}

function saveUsers(users) {
  fs.writeFileSync(USER_DB_FILE, JSON.stringify(users, null, 2), 'utf-8');
}

// 初始化默认用户
function initDefaultUsers() {
  if (fs.existsSync(USER_DB_FILE)) return;
  const defaults = {
    "123456": {
      "account": "123456",
      "hash_pwd": bcrypt.hashSync("123456", 12),
      "nickname": "小明",
      "signature": "每一天，乐在沟通",
      "gender": "男",
      "age": "22",
      "city": "深圳",
      "createdAt": new Date().toISOString()
    },
    "admin": {
      "account": "admin",
      "hash_pwd": bcrypt.hashSync("admin", 12),
      "nickname": "管理员",
      "signature": "好好学习，天天向上",
      "gender": "男",
      "age": "25",
      "city": "北京",
      "createdAt": new Date().toISOString()
    },
    "qquser": {
      "account": "qquser",
      "hash_pwd": bcrypt.hashSync("qquser", 12),
      "nickname": "QQ用户",
      "signature": "这个人很懒，什么都没留下",
      "gender": "女",
      "age": "20",
      "city": "上海",
      "createdAt": new Date().toISOString()
    }
  };
  saveUsers(defaults);
  console.log('已初始化默认用户');
}

// 初始化数据
initDefaultUsers();
let users = loadUsers();

// 重新加载（供手动刷新）
function reloadUsers() {
  users = loadUsers();
}

// 在线用户追踪：account -> { nickname, lastHeartbeat }
const onlineUsers = new Map();

// 广播给所有 WebSocket 客户端
function broadcast(data) {
  wss.clients.forEach(client => {
    if (client.readyState === 1) {
      client.send(JSON.stringify(data));
    }
  });
}

// 更新用户心跳
function updateHeartbeat(account, nickname) {
  const wasOnline = onlineUsers.has(account);
  onlineUsers.set(account, {
    nickname,
    lastHeartbeat: Date.now()
  });
  if (!wasOnline) {
    console.log(`用户上线: ${account} (${nickname})`);
    broadcast({ type: 'user_online', account, nickname });
  }
}

// 清理过期心跳（超过 HEARTBEAT_TIMEOUT 未更新则视为离线）
function cleanupOfflineUsers() {
  const now = Date.now();
  for (const [account, info] of onlineUsers) {
    if (now - info.lastHeartbeat > HEARTBEAT_TIMEOUT) {
      onlineUsers.delete(account);
      console.log(`用户离线: ${account} (${info.nickname})`);
      broadcast({ type: 'user_offline', account, nickname: info.nickname });
    }
  }
}

// 定时清理
setInterval(cleanupOfflineUsers, CLEANUP_INTERVAL);

// 检查用户是否在线
function isUserOnline(account) {
  return onlineUsers.has(account);
}

// ============== REST API ==============

// 获取所有用户（不含密码，含在线状态）
app.get('/api/users', (req, res) => {
  reloadUsers();
  const now = Date.now();
  const list = Object.values(users).map(u => ({
    account: u.account,
    nickname: u.nickname,
    signature: u.signature,
    gender: u.gender,
    age: u.age,
    city: u.city,
    createdAt: u.createdAt,
    online: isUserOnline(u.account)
  }));
  res.json({ ok: true, users: list, total: list.length, onlineCount: onlineUsers.size });
});

// 获取单个用户
app.get('/api/users/:account', (req, res) => {
  reloadUsers();
  const user = users[req.params.account];
  if (!user) {
    return res.status(404).json({ ok: false, error: '用户不存在' });
  }
  const { hash_pwd, ...info } = user;
  res.json({ ok: true, user: info });
});

// 注册
app.post('/api/register', (req, res) => {
  reloadUsers();
  const { account, nickname, password } = req.body;

  if (!account || !nickname || !password) {
    return res.status(400).json({ ok: false, error: '账号、昵称和密码不能为空' });
  }
  if (users[account]) {
    return res.status(409).json({ ok: false, error: '账号已存在' });
  }

  users[account] = {
    account,
    hash_pwd: bcrypt.hashSync(password, 12),
    nickname,
    signature: '这个人很懒，什么都没留下',
    gender: '保密',
    age: '未知',
    city: '未知',
    createdAt: new Date().toISOString()
  };
  saveUsers(users);

  console.log(`新用户注册: ${account} (${nickname})`);
  broadcast({ type: 'user_registered', account, nickname, total: Object.keys(users).length });

  res.status(201).json({ ok: true, message: '注册成功', account });
});

// 登录验证
app.post('/api/login', (req, res) => {
  reloadUsers();
  const { account, password } = req.body;

  if (!account || !password) {
    return res.status(400).json({ ok: false, error: '账号和密码不能为空' });
  }

  const user = users[account];
  if (!user) {
    return res.status(401).json({ ok: false, error: '账号不存在' });
  }

  if (!bcrypt.compareSync(password, user.hash_pwd)) {
    return res.status(401).json({ ok: false, error: '密码错误' });
  }

  const { hash_pwd, ...info } = user;
  console.log(`用户登录: ${account}`);
  res.json({ ok: true, message: '登录成功', user: info });
});

// 更新用户信息
app.put('/api/users/:account', (req, res) => {
  reloadUsers();
  const { account } = req.params;
  if (!users[account]) {
    return res.status(404).json({ ok: false, error: '用户不存在' });
  }

  const allowedFields = ['nickname', 'signature', 'gender', 'age', 'city'];
  for (const key of Object.keys(req.body)) {
    if (allowedFields.includes(key)) {
      users[account][key] = req.body[key];
    }
  }
  saveUsers(users);

  broadcast({ type: 'user_updated', account });
  res.json({ ok: true, message: '更新成功', user: users[account] });
});

// 删除用户
app.delete('/api/users/:account', (req, res) => {
  reloadUsers();
  if (!users[req.params.account]) {
    return res.status(404).json({ ok: false, error: '用户不存在' });
  }

  delete users[req.params.account];
  saveUsers(users);

  console.log(`用户已删除: ${req.params.account}`);
  broadcast({ type: 'user_deleted', account: req.params.account, total: Object.keys(users).length });

  res.json({ ok: true, message: '删除成功' });
});

// 获取在线统计
app.get('/api/stats', (req, res) => {
  reloadUsers();
  const now = Date.now();
  const onlineList = [];
  for (const [account, info] of onlineUsers) {
    onlineList.push({
      account,
      nickname: info.nickname,
      onlineSeconds: Math.floor((now - info.lastHeartbeat) / 1000)
    });
  }
  res.json({
    ok: true,
    stats: {
      totalUsers: Object.keys(users).length,
      onlineCount: onlineUsers.size,
      onlineUsers: onlineList
    }
  });
});

// 心跳上报
app.post('/api/heartbeat', (req, res) => {
  const { account, nickname } = req.body;
  if (!account) {
    return res.status(400).json({ ok: false, error: '账号不能为空' });
  }
  updateHeartbeat(account, nickname || account);
  res.json({ ok: true, onlineCount: onlineUsers.size });
});

// 主动下线通知
app.post('/api/heartbeat/offline', (req, res) => {
  const { account } = req.body;
  if (!account) {
    return res.status(400).json({ ok: false, error: '账号不能为空' });
  }
  if (onlineUsers.has(account)) {
    const info = onlineUsers.get(account);
    onlineUsers.delete(account);
    console.log(`用户主动下线: ${account} (${info.nickname})`);
    broadcast({ type: 'user_offline', account, nickname: info.nickname });
  }
  res.json({ ok: true });
});

// ============== WebSocket ==============

wss.on('connection', (ws, req) => {
  const ip = req.socket.remoteAddress;
  console.log(`WebSocket 连接: ${ip}`);
  broadcast({ type: 'connection_count', count: [...wss.clients].filter(c => c.readyState === 1).length });

  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      console.log('收到消息:', msg);

      // 客户端可以发送 heartbeat 保持连接
      if (msg.type === 'ping') {
        ws.send(JSON.stringify({ type: 'pong' }));
      }
    } catch (e) {
      console.error('消息解析失败:', e.message);
    }
  });

  ws.on('close', () => {
    console.log(`WebSocket 断开: ${ip}`);
    broadcast({ type: 'connection_count', count: [...wss.clients].filter(c => c.readyState === 1).length });
  });

  // 发送欢迎信息
  ws.send(JSON.stringify({
    type: 'welcome',
    message: '已连接到 QQ 服务器',
    totalUsers: Object.keys(users).length
  }));
});

// ============== 生产环境：服务 Vue 静态文件 ==============

const distDir = path.join(__dirname, 'dist');
if (fs.existsSync(distDir)) {
  app.use(express.static(distDir));
  app.get('*', (req, res) => {
    // 不要拦截 API 路由
    if (!req.path.startsWith('/api/')) {
      res.sendFile(path.join(distDir, 'index.html'));
    }
  });
  console.log('✓ 静态文件服务已启用 (dist/)');
}

// ============== 启动 ==============

server.listen(PORT, () => {
  console.log(`\n  QQ 服务端已启动`);
  console.log(`  ────────────────────────────`);
  console.log(`  HTTP API : http://localhost:${PORT}/api/`);
  console.log(`  WebSocket: ws://localhost:${PORT}`);
  console.log(`  用户数据 : ${USER_DB_FILE}`);
  console.log(`  用户总数 : ${Object.keys(users).length}`);
  console.log(`  ────────────────────────────\n`);
});
