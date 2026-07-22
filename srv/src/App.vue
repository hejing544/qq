<template>
  <div class="app">
    <!-- 顶部导航 -->
    <header class="app-header">
      <div class="header-left">
        <span class="logo">🐧</span>
        <h1>QQ 服务端管理面板</h1>
      </div>
      <div class="header-right">
        <div class="stat-badge">
          <span class="stat-label">注册用户</span>
          <span class="stat-value">{{ totalUsers }}</span>
        </div>
        <div class="stat-badge online">
          <span class="stat-label">在线连接</span>
          <span class="stat-value">{{ onlineCount }}</span>
        </div>
        <div class="ws-status" :class="{ connected: wsConnected }">
          <span class="ws-dot"></span>
          {{ wsConnected ? 'WebSocket 已连接' : 'WebSocket 断开' }}
        </div>
      </div>
    </header>

    <!-- Tab 导航 -->
    <nav class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        {{ tab.label }}
        <span v-if="tab.id === 'users'" class="tab-count">{{ totalUsers }}</span>
      </button>
    </nav>

    <!-- Tab 内容 -->
    <main class="tab-content">
      <!-- 用户管理 Tab -->
      <UserList v-if="activeTab === 'users'" :users="users" :loading="loading" @refresh="fetchUsers" @delete="deleteUser" />

      <!-- 统计 Tab -->
      <div v-else-if="activeTab === 'stats'" class="stats-page">
        <h2>📊 服务统计</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-card-icon">👥</div>
            <div class="stat-card-num">{{ totalUsers }}</div>
            <div class="stat-card-label">注册用户总数</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-icon">🟢</div>
            <div class="stat-card-num">{{ onlineCount }}</div>
            <div class="stat-card-label">WebSocket 连接数</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-icon">📅</div>
            <div class="stat-card-num">{{ todayNewUsers }}</div>
            <div class="stat-card-label">今日新增</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-icon">🕐</div>
            <div class="stat-card-num">{{ serverUptime }}</div>
            <div class="stat-card-label">服务运行时间</div>
          </div>
        </div>

        <!-- 用户分布 -->
        <div class="dist-section">
          <h3>用户性别分布</h3>
          <div class="gender-bar">
            <div class="bar-segment male" :style="{ width: genderDist.male + '%' }">
              👨 {{ genderDist.male }}%
            </div>
            <div class="bar-segment female" :style="{ width: genderDist.female + '%' }">
              👩 {{ genderDist.female }}%
            </div>
            <div class="bar-segment unknown" :style="{ width: genderDist.unknown + '%' }">
              ❓ {{ genderDist.unknown }}%
            </div>
          </div>
        </div>

        <div class="dist-section">
          <h3>用户城市分布</h3>
          <div class="city-tags">
            <span v-for="(count, city) in cityDist" :key="city" class="city-tag">
              📍 {{ city }}: {{ count }}
            </span>
            <span v-if="Object.keys(cityDist).length === 0" class="no-data">暂无数据</span>
          </div>
        </div>
      </div>

      <!-- API 文档 Tab -->
      <div v-else-if="activeTab === 'api'" class="api-page">
        <h2>📡 API 接口文档</h2>
        <div class="api-list">
          <div v-for="ep in apiEndpoints" :key="ep.method + ep.path" class="api-card">
            <div class="api-meta">
              <span class="api-method" :class="ep.method">{{ ep.method }}</span>
              <span class="api-path">{{ ep.path }}</span>
            </div>
            <div class="api-desc">{{ ep.desc }}</div>
          </div>
        </div>
      </div>
    </main>

    <!-- 实时日志 -->
    <footer class="log-bar">
      <span class="log-title">📋 实时日志</span>
      <span v-for="(log, i) in logs" :key="i" class="log-entry">
        {{ log }}
      </span>
      <span v-if="logs.length === 0" class="log-empty">等待事件...</span>
    </footer>
  </div>
</template>

<script>
import UserList from './components/UserList.vue'

export default {
  name: 'App',
  components: { UserList },
  data() {
    return {
      activeTab: 'users',
      tabs: [
        { id: 'users', label: '用户管理', icon: '👥' },
        { id: 'stats', label: '数据统计', icon: '📊' },
        { id: 'api', label: 'API 文档', icon: '📡' }
      ],
      users: [],
      totalUsers: 0,
      onlineCount: 0,
      loading: false,
      wsConnected: false,
      ws: null,
      logs: [],
      serverStartTime: Date.now(),
      serverUptime: '--',
      uptimeTimer: null,
      apiEndpoints: [
        { method: 'GET', path: '/api/users', desc: '获取所有注册用户列表' },
        { method: 'GET', path: '/api/users/:account', desc: '获取指定用户信息' },
        { method: 'POST', path: '/api/register', desc: '注册新用户 { account, nickname, password }' },
        { method: 'POST', path: '/api/login', desc: '用户登录验证 { account, password }' },
        { method: 'PUT', path: '/api/users/:account', desc: '更新用户资料 { nickname, signature, gender, age, city }' },
        { method: 'DELETE', path: '/api/users/:account', desc: '删除用户' },
        { method: 'GET', path: '/api/stats', desc: '获取服务统计信息' },
        { method: 'WS', path: 'ws://localhost:3000', desc: 'WebSocket 实时推送' }
      ]
    }
  },
  computed: {
    todayNewUsers() {
      const today = new Date().toISOString().slice(0, 10);
      return this.users.filter(u => u.createdAt && u.createdAt.startsWith(today)).length;
    },
    genderDist() {
      const total = this.users.length || 1;
      const male = this.users.filter(u => u.gender === '男').length;
      const female = this.users.filter(u => u.gender === '女').length;
      const unknown = this.users.length - male - female;
      return {
        male: Math.round(male / total * 100),
        female: Math.round(female / total * 100),
        unknown: Math.round(unknown / total * 100)
      };
    },
    cityDist() {
      const dist = {};
      this.users.forEach(u => {
        if (u.city && u.city !== '未知') {
          dist[u.city] = (dist[u.city] || 0) + 1;
        }
      });
      return Object.fromEntries(
        Object.entries(dist).sort((a, b) => b[1] - a[1])
      );
    }
  },
  methods: {
    async fetchUsers() {
      this.loading = true;
      try {
        const res = await fetch('/api/users');
        const data = await res.json();
        if (data.ok) {
          this.users = data.users;
          this.totalUsers = data.total;
          this.onlineCount = data.onlineCount || this.users.filter(u => u.online).length;
        }
      } catch (e) {
        this.addLog('获取用户列表失败: ' + e.message);
      } finally {
        this.loading = false;
      }
    },

    async deleteUser(account) {
      if (!confirm(`确定删除用户 "${account}" 吗？此操作不可恢复。`)) return;
      try {
        const res = await fetch(`/api/users/${account}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.ok) {
          this.addLog(`已删除用户: ${account}`);
          this.fetchUsers();
        }
      } catch (e) {
        this.addLog('删除用户失败: ' + e.message);
      }
    },

    connectWebSocket() {
      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${location.host}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.wsConnected = true;
        this.addLog('WebSocket 已连接');
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          switch (msg.type) {
            case 'welcome':
              this.addLog(`服务器欢迎: ${msg.message} (用户总数: ${msg.totalUsers})`);
              break;
            case 'user_registered':
              this.addLog(`新用户注册: ${msg.account} (${msg.nickname})`);
              this.fetchUsers();
              break;
            case 'user_updated':
              this.addLog(`用户信息更新: ${msg.account}`);
              this.fetchUsers();
              break;
            case 'user_deleted':
              this.addLog(`用户已删除: ${msg.account}`);
              this.fetchUsers();
              break;
            case 'user_online':
              this.addLog(`用户上线: ${msg.account} (${msg.nickname})`);
              this.updateUserOnlineStatus(msg.account, true);
              this.onlineCount = Math.max(0, this.onlineCount + 1);
              break;
            case 'user_offline':
              this.addLog(`用户离线: ${msg.account} (${msg.nickname})`);
              this.updateUserOnlineStatus(msg.account, false);
              this.onlineCount = Math.max(0, this.onlineCount - 1);
              break;
            case 'connection_count':
              // WebSocket 连接数（与心跳在线数不同）
              break;
          }
        } catch (e) {
          // 忽略非 JSON 消息
        }
      };

      this.ws.onclose = () => {
        this.wsConnected = false;
        this.addLog('WebSocket 断开，3秒后重连...');
        setTimeout(() => this.connectWebSocket(), 3000);
      };

      this.ws.onerror = () => {
        this.addLog('WebSocket 连接错误');
      };
    },

    addLog(text) {
      const time = new Date().toLocaleTimeString();
      this.logs.unshift(`[${time}] ${text}`);
      if (this.logs.length > 50) this.logs.pop();
    },

    updateUserOnlineStatus(account, online) {
      const user = this.users.find(u => u.account === account);
      if (user) {
        user.online = online;
      }
    },

    updateUptime() {
      const elapsed = Math.floor((Date.now() - this.serverStartTime) / 1000);
      const h = Math.floor(elapsed / 3600);
      const m = Math.floor((elapsed % 3600) / 60);
      const s = elapsed % 60;
      this.serverUptime = `${h}时${m}分${s}秒`;
    }
  },

  mounted() {
    this.fetchUsers();
    this.connectWebSocket();
    this.uptimeTimer = setInterval(() => this.updateUptime(), 1000);
  },

  beforeUnmount() {
    if (this.ws) this.ws.close();
    if (this.uptimeTimer) clearInterval(this.uptimeTimer);
  }
}
</script>

<style>
/* ========== 全局样式 ========== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  background: #f0f2f5;
  color: #333;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ========== 顶部导航 ========== */
.app-header {
  background: linear-gradient(135deg, #12b7f5 0%, #0d8ed9 100%);
  color: #fff;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  font-size: 28px;
}

.header-left h1 {
  font-size: 18px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-badge {
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  padding: 6px 14px;
  text-align: center;
  backdrop-filter: blur(4px);
}

.stat-badge.online {
  background: rgba(82, 196, 26, 0.3);
}

.stat-label {
  display: block;
  font-size: 11px;
  opacity: 0.85;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
}

.ws-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  background: rgba(255,255,255,0.15);
  padding: 6px 12px;
  border-radius: 20px;
}

.ws-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff4d4f;
}

.ws-status.connected .ws-dot {
  background: #52c41a;
}

/* ========== Tab 导航 ========== */
.tab-bar {
  display: flex;
  gap: 0;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 24px;
  position: sticky;
  top: 60px;
  z-index: 99;
}

.tab-btn {
  padding: 14px 24px;
  border: none;
  background: none;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: inherit;
}

.tab-btn:hover {
  color: #12b7f5;
  background: #f5f9ff;
}

.tab-btn.active {
  color: #12b7f5;
  border-bottom-color: #12b7f5;
  font-weight: 600;
}

.tab-icon {
  font-size: 16px;
}

.tab-count {
  background: #12b7f5;
  color: #fff;
  font-size: 11px;
  padding: 1px 7px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

/* ========== 内容区 ========== */
.tab-content {
  flex: 1;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* ========== 统计页 ========== */
.stats-page h2,
.api-page h2 {
  margin-bottom: 24px;
  font-size: 22px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.stat-card-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.stat-card-num {
  font-size: 32px;
  font-weight: 700;
  color: #12b7f5;
  margin-bottom: 4px;
}

.stat-card-label {
  font-size: 13px;
  color: #999;
}

.dist-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.dist-section h3 {
  font-size: 16px;
  margin-bottom: 16px;
}

.gender-bar {
  display: flex;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  font-size: 13px;
}

.bar-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  transition: width 0.5s;
}

.bar-segment.male {
  background: #1890ff;
}

.bar-segment.female {
  background: #eb2f96;
}

.bar-segment.unknown {
  background: #d9d9d9;
  color: #666;
}

.city-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.city-tag {
  background: #f0f2f5;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
}

.no-data {
  color: #999;
  font-size: 13px;
}

/* ========== API 文档页 ========== */
.api-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.api-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: background 0.2s;
}

.api-card:hover {
  background: #fafcff;
}

.api-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 280px;
}

.api-method {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  min-width: 52px;
  text-align: center;
}

.api-method.GET { background: #52c41a; }
.api-method.POST { background: #1890ff; }
.api-method.PUT { background: #fa8c16; }
.api-method.DELETE { background: #ff4d4f; }
.api-method.WS { background: #722ed1; }

.api-path {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  color: #333;
}

.api-desc {
  font-size: 13px;
  color: #888;
}

/* ========== 底部日志 ========== */
.log-bar {
  background: #1a1a2e;
  color: #a0a0b0;
  padding: 8px 24px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  overflow-x: auto;
  white-space: nowrap;
  position: sticky;
  bottom: 0;
  height: 36px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.log-title {
  color: #52c41a;
  font-weight: 600;
  flex-shrink: 0;
}

.log-entry {
  color: #689f63;
  flex-shrink: 0;
}

.log-empty {
  color: #555;
  font-style: italic;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .header-right {
    display: none;
  }

  .tab-bar {
    overflow-x: auto;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .api-meta {
    min-width: auto;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
