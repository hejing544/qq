<template>
  <div class="user-list-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <h2>👥 注册用户列表</h2>
      <div class="toolbar-actions">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchText"
            type="text"
            placeholder="搜索账号 / 昵称 / 城市..."
            class="search-input"
          />
        </div>
        <button class="btn-refresh" @click="$emit('refresh')" :disabled="loading">
          🔄 {{ loading ? '加载中...' : '刷新' }}
        </button>
      </div>
    </div>

    <!-- 用户表格 -->
    <div class="table-wrapper">
      <table class="user-table">
        <thead>
          <tr>
            <th>#</th>
            <th>头像</th>
            <th>账号</th>
            <th>昵称</th>
            <th>状态</th>
            <th>性别</th>
            <th>年龄</th>
            <th>城市</th>
            <th>个性签名</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredUsers.length === 0 && !loading">
            <td colspan="11" class="empty-cell">
              <div class="empty-state">
                <span class="empty-icon">📭</span>
                <p v-if="searchText">没有匹配的用户</p>
                <p v-else>暂无注册用户</p>
              </div>
            </td>
          </tr>
          <tr v-for="(user, index) in filteredUsers" :key="user.account" class="user-row">
            <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
            <td>
              <div class="avatar" :style="{ background: avatarColor(user.account) }">
                {{ user.nickname.charAt(0) }}
              </div>
            </td>
            <td class="account-cell">{{ user.account }}</td>
            <td class="nickname-cell">
              <span class="nickname">{{ user.nickname }}</span>
            </td>
            <td>
              <span class="status-badge" :class="{ online: user.online }">
                <span class="status-dot"></span>
                {{ user.online ? '在线' : '离线' }}
              </span>
            </td>
            <td>
              <span class="gender-badge" :class="genderClass(user.gender)">
                {{ genderIcon(user.gender) }} {{ user.gender }}
              </span>
            </td>
            <td>{{ user.age }}</td>
            <td>
              <span class="city-tag" v-if="user.city && user.city !== '未知'">
                📍 {{ user.city }}
              </span>
              <span v-else class="unknown-text">未知</span>
            </td>
            <td class="signature-cell">
              <span class="signature" :title="user.signature">{{ user.signature }}</span>
            </td>
            <td class="time-cell">{{ formatDate(user.createdAt) }}</td>
            <td>
              <div class="action-btns">
                <button class="btn-detail" @click="showDetail(user)" title="查看详情">
                  📋
                </button>
                <button class="btn-delete" @click="$emit('delete', user.account)" title="删除用户">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="currentPage === 1" @click="currentPage--">◀ 上一页</button>
      <span v-for="p in visiblePages" :key="p">
        <button
          v-if="p !== '...'"
          class="page-num"
          :class="{ active: p === currentPage }"
          @click="currentPage = p"
        >{{ p }}</button>
        <span v-else class="ellipsis">...</span>
      </span>
      <button :disabled="currentPage === totalPages" @click="currentPage++">下一页 ▶</button>
      <span class="page-info">共 {{ totalUsers }} 条 / {{ totalPages }} 页</span>
    </div>

    <!-- 用户详情弹窗 -->
    <div v-if="selectedUser" class="modal-overlay" @click.self="selectedUser = null">
      <div class="modal-card">
        <button class="modal-close" @click="selectedUser = null">✕</button>
        <div class="modal-header">
          <div class="modal-avatar" :style="{ background: avatarColor(selectedUser.account) }">
            {{ selectedUser.nickname.charAt(0) }}
          </div>
          <h3>{{ selectedUser.nickname }}</h3>
          <p class="modal-account">账号: {{ selectedUser.account }}</p>
        </div>
        <div class="modal-body">
          <div class="info-row">
            <span class="info-label">性别</span>
            <span class="info-value">{{ selectedUser.gender }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">年龄</span>
            <span class="info-value">{{ selectedUser.age }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">城市</span>
            <span class="info-value">{{ selectedUser.city }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">个性签名</span>
            <span class="info-value">{{ selectedUser.signature }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">注册时间</span>
            <span class="info-value">{{ formatDate(selectedUser.createdAt) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserList',
  props: {
    users: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  emits: ['refresh', 'delete'],
  data() {
    return {
      searchText: '',
      currentPage: 1,
      pageSize: 12,
      selectedUser: null
    }
  },
  computed: {
    filteredUsers() {
      if (!this.searchText.trim()) return this.users;
      const q = this.searchText.toLowerCase();
      return this.users.filter(u =>
        u.account.toLowerCase().includes(q) ||
        (u.nickname && u.nickname.toLowerCase().includes(q)) ||
        (u.city && u.city.toLowerCase().includes(q))
      );
    },
    totalUsers() {
      return this.filteredUsers.length;
    },
    totalPages() {
      return Math.ceil(this.totalUsers / this.pageSize) || 1;
    },
    visiblePages() {
      const pages = [];
      const total = this.totalPages;
      const cur = this.currentPage;
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        pages.push(1);
        if (cur > 3) pages.push('...');
        for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) {
          pages.push(i);
        }
        if (cur < total - 2) pages.push('...');
        pages.push(total);
      }
      return pages;
    },
    pagedUsers() {
      const start = (this.currentPage - 1) * this.pageSize;
      return this.filteredUsers.slice(start, start + this.pageSize);
    }
  },
  watch: {
    searchText() {
      this.currentPage = 1;
    }
  },
  methods: {
    avatarColor(account) {
      const colors = [
        '#12b7f5', '#1890ff', '#52c41a', '#fa8c16',
        '#eb2f96', '#722ed1', '#13c2c2', '#f5222d',
        '#2f54eb', '#a0d911', '#fa541c', '#f759ab'
      ];
      let hash = 0;
      for (const c of account) hash = c.charCodeAt(0) + ((hash << 5) - hash);
      return colors[Math.abs(hash) % colors.length];
    },
    genderIcon(gender) {
      return gender === '男' ? '👨' : gender === '女' ? '👩' : '❓';
    },
    genderClass(gender) {
      return gender === '男' ? 'male' : gender === '女' ? 'female' : 'unknown';
    },
    formatDate(isoStr) {
      if (!isoStr) return '—';
      const d = new Date(isoStr);
      const pad = n => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    },
    showDetail(user) {
      this.selectedUser = user;
    }
  }
}
</script>

<style scoped>
/* ========== 工具栏 ========== */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar h2 {
  font-size: 22px;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 0 12px;
  transition: border-color 0.2s;
}

.search-box:focus-within {
  border-color: #12b7f5;
  box-shadow: 0 0 0 2px rgba(18, 183, 245, 0.1);
}

.search-icon {
  font-size: 14px;
}

.search-input {
  border: none;
  outline: none;
  padding: 10px 8px;
  font-size: 14px;
  width: 240px;
  font-family: inherit;
}

.btn-refresh {
  background: #12b7f5;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-refresh:hover {
  background: #0d8ed9;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ========== 表格 ========== */
.table-wrapper {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  overflow-x: auto;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.user-table thead {
  background: #fafafa;
}

.user-table th {
  padding: 14px 12px;
  text-align: left;
  font-weight: 600;
  color: #666;
  font-size: 13px;
  white-space: nowrap;
  border-bottom: 1px solid #f0f0f0;
}

.user-table td {
  padding: 12px;
  border-bottom: 1px solid #f5f5f5;
  white-space: nowrap;
}

.user-row {
  transition: background 0.15s;
}

.user-row:hover {
  background: #f5f9ff;
}

.user-row:last-child td {
  border-bottom: none;
}

/* 头像 */
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 15px;
}

/* 昵称 */
.nickname {
  font-weight: 600;
  color: #333;
}

/* 个性签名 */
.signature-cell {
  max-width: 180px;
}

.signature {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #999;
  font-size: 13px;
}

/* 在线状态 */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  background: #f5f5f5;
  color: #999;
}

.status-badge.online {
  background: #f6ffed;
  color: #52c41a;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #d9d9d9;
}

.status-badge.online .status-dot {
  background: #52c41a;
  box-shadow: 0 0 4px rgba(82, 196, 26, 0.6);
}

/* 性别 */
.gender-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
}

.gender-badge.male {
  background: #e6f7ff;
  color: #1890ff;
}

.gender-badge.female {
  background: #fff0f6;
  color: #eb2f96;
}

.gender-badge.unknown {
  background: #f5f5f5;
  color: #999;
}

.city-tag {
  font-size: 13px;
}

.unknown-text {
  color: #ccc;
}

.time-cell {
  font-size: 12px;
  color: #aaa;
}

/* 操作按钮 */
.action-btns {
  display: flex;
  gap: 6px;
}

.btn-detail,
.btn-delete {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-detail:hover {
  border-color: #12b7f5;
  background: #e6f7ff;
}

.btn-delete:hover {
  border-color: #ff4d4f;
  background: #fff2f0;
}

/* 空状态 */
.empty-cell {
  text-align: center;
  padding: 60px 20px !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #ccc;
}

.empty-icon {
  font-size: 48px;
}

.empty-state p {
  font-size: 14px;
  color: #999;
}

/* ========== 分页 ========== */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.pagination button {
  padding: 8px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  border-color: #12b7f5;
  color: #12b7f5;
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination .page-num.active {
  background: #12b7f5;
  color: #fff;
  border-color: #12b7f5;
}

.ellipsis {
  padding: 0 4px;
  color: #999;
}

.page-info {
  margin-left: 12px;
  font-size: 13px;
  color: #999;
}

/* ========== 用户详情弹窗 ========== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  width: 420px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 16px 48px rgba(0,0,0,0.2);
  position: relative;
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #f0f0f0;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.modal-close:hover {
  background: #ff4d4f;
  color: #fff;
}

.modal-header {
  text-align: center;
  padding: 32px 24px 20px;
  background: linear-gradient(135deg, #e6f7ff 0%, #f0f5ff 100%);
  border-radius: 16px 16px 0 0;
}

.modal-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 28px;
  margin: 0 auto 12px;
}

.modal-header h3 {
  font-size: 20px;
  margin-bottom: 4px;
}

.modal-account {
  font-size: 13px;
  color: #999;
}

.modal-body {
  padding: 20px 24px 32px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: #666;
  font-size: 14px;
}

.info-value {
  color: #333;
  font-size: 14px;
}
</style>
