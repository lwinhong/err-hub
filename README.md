# ErrHub

轻量级异常收集与管理平台。后端 Flask + PostgreSQL，前端 Vue 3 + Element Plus，Docker 一键部署。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 API | Python 3.12 / Flask / SQLAlchemy / Gunicorn |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 6 |
| 前端 | Vue 3 / Element Plus / Vite / vue-i18n |
| 反向代理 | Nginx (Alpine) |
| 包管理 | uv (后端) / pnpm (前端) |

---

## 项目结构

```
err-hub/
├── backend/          # Flask API 服务
│   ├── app/
│   │   ├── api/v1/   # 接口路由
│   │   ├── models/   # 数据模型
│   │   ├── static/   # SDK 静态文件 (error-feedback.js)
│   │   └── ...
│   └── Dockerfile
├── frontend/         # Vue 3 管理后台
│   ├── src/
│   │   ├── i18n/     # 国际化配置与语言包
│   │   └── ...
│   └── Dockerfile
└── docker/
    ├── docker-compose.yml
    ├── nginx/        # 网关 Nginx 配置
    ├── volumes/      # 持久化数据目录
    └── .env          # 环境变量（从 .env.example 复制）
```

---

## 快速开始

### 前置条件

- Docker >= 20.10
- Docker Compose >= 2.0
- Make（可选，直接用 docker compose 命令亦可）

### 1. 配置环境变量

```bash
cd docker
cp .env.example .env
# 编辑 .env，按需修改密码、端口等
```

关键配置项：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `GATEWAY_PORT` | `80` | 对外暴露端口 |
| `SECRET_KEY` | - | Flask Session 密钥，**生产环境必须修改** |
| `JWT_SECRET_KEY` | - | JWT 签名密钥，**生产环境必须修改** |
| `SUPERADMIN_USERNAME` | `admin` | 超级管理员用户名 |
| `SUPERADMIN_PASSWORD` | `admin123` | 超级管理员初始密码 |
| `DATA_RETENTION_DAYS` | `90` | 错误数据保留天数 |
| `POSTGRES_PASSWORD` | `errhub` | 数据库密码 |

### 2. 一键构建并启动

```bash
make up        # 构建镜像 + 启动所有服务
```

或分步执行：

```bash
make build     # 仅构建镜像
make start     # 仅启动容器
```

启动后访问 `http://<your-ip>:<GATEWAY_PORT>` 进入管理后台。

---

## Make 命令一览

| 命令 | 说明 |
|------|------|
| `make build` | 构建 api 和 web 镜像 |
| `make up` | 构建并启动所有服务（后台运行） |
| `make start` | 启动已构建的容器 |
| `make stop` | 停止所有容器（保留数据） |
| `make restart` | 重启所有容器 |
| `make down` | 停止并删除容器和网络 |
| `make rebuild` | 重建 api/gateway 镜像并强制重启（**代码修改后用此命令**） |
| `make rebuild-all` | 重建全部镜像并强制重启 |
| `make logs` | 实时查看所有服务日志 |
| `make logs-api` | 仅查看 API 服务日志 |
| `make status` | 查看各容器运行状态 |
| `make clean` | 停止容器并删除数据卷（**慎用，会丢数据**） |

---

## 代码修改后如何生效

修改后端代码或 Nginx 配置后，执行：

```bash
make rebuild          # 重建 api 镜像 + 强制重启 api 和 gateway
```

修改前端代码后，执行：

```bash
make rebuild-all      # 重建全部镜像
```

---

## Web SDK 接入

在你的 HTML 页面中引入即可，无需安装任何依赖：

```html
<script src="http://your-domain/sdk/error-feedback.js"
        data-api-token="项目的 API Token"
        data-auto-capture="true"
        data-environment="production"
        data-before-send="onBeforeErrorSend">
</script>

<script>
  // 手动上报
  ErrHub.report('TypeError', '按钮点击失败', { severity: 'error' });

  // 捕获 Error 对象
  try { riskyOp(); } catch (e) { ErrHub.captureException(e); }

  // 上报前回调（可选）
  window.onBeforeErrorSend = function (payload) {
    payload.context.user_id = currentUser?.id;
    return payload;   // 返回 false 可取消本次上报
  };
</script>
```

**script 标签属性：**

| 属性 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `data-api-token` | 是 | - | 项目 API Token（管理后台创建项目后获取） |
| `data-auto-capture` | 否 | `true` | 自动捕获未处理异常和 Promise rejection |
| `data-environment` | 否 | `production` | 环境标识 |
| `data-before-send` | 否 | - | window 上的回调函数名，上报前触发 |

**window.ErrHub 方法：**

| 方法 | 说明 |
|------|------|
| `ErrHub.report(type, message, opts?)` | 手动上报一条错误 |
| `ErrHub.captureException(error, opts?)` | 上报 Error 对象（自动解析 name/message/stack） |
| `ErrHub.flush()` | 立即发送队列中所有待上报的错误 |

**beforeSend 回调规则：**
- 返回 `payload`（可修改后）→ 继续上报
- 不返回（无 `return`）→ 继续上报原始 payload
- 返回 `false` → 取消本次上报
- 抛出异常 → 静默降级，仍发送原始 payload

---

## API 鉴权

### 管理后台接口（JWT）

```
POST /api/v1/auth/login
Content-Type: application/json
{ "username": "admin", "password": "admin123" }

→ { "access_token": "..." }

# 后续请求携带：
Authorization: Bearer <access_token>
```

### 错误上报接口（API Token）

```
POST /api/v1/errors
X-API-Token: <项目 API Token>
Content-Type: application/json
{
  "exception_type": "ValueError",
  "message": "invalid input"
}
```

---

## 数据持久化

数据存储在 `docker/volumes/` 目录下：

```
docker/volumes/
├── postgres/    # PostgreSQL 数据文件
└── redis/       # Redis dump.rdb
```

**备份：** 直接打包 `docker/volumes/` 目录即可。

**重置：** `make clean` 会删除 volumes，重新 `make up` 即可初始化空库。

---

## 国际化 (i18n)

前端使用 [vue-i18n](https://vue-i18n.intlify.dev/) 实现多语言支持，当前支持 **中文 (zh-CN)** 和 **英文 (en)**。

### 语言检测与切换

- **首次访问**：自动检测浏览器 `navigator.language`，`zh` 开头使用中文，其他语言回退为英文
- **手动切换**：点击顶部导航栏的语言切换下拉菜单即可切换
- **偏好持久化**：用户选择的语言保存在 `localStorage` 的 `locale` 键中，下次访问优先使用

### 目录结构

```
frontend/src/i18n/
├── index.js              # i18n 初始化、语言检测逻辑
└── locales/
    ├── zh-CN.js           # 中文语言包
    └── en.js              # 英文语言包
```

### 添加新语言

1. 在 `frontend/src/i18n/locales/` 下新建语言文件（如 `ja.js`），参照现有语言包的 key 结构填写翻译
2. 在 `frontend/src/i18n/index.js` 中：
   - 导入新语言包，添加到 `messages` 对象
   - 在 `languages` 数组中追加 `{ code: 'ja', label: '日本語' }`
   - 在 `langMap` 中添加浏览器语言前缀映射（如 `ja: 'ja'`）
3. 如需 Element Plus 组件库的联动，导入对应的 Element Plus locale（如 `element-plus/es/locale/lang/ja`）并在 `App.vue` 的 `elementLocale` computed 中添加判断

**无需修改任何组件模板**，语言切换菜单会自动根据 `languages` 数组渲染。

### 添加新的翻译 key

1. 在 `zh-CN.js` 和 `en.js` 中同时添加相同的 key 路径
2. 在组件中通过 `t('key.path')` 或模板中 `{{ t('key.path') }}` 使用

**注意事项：**
- vue-i18n 中 `{` 和 `}` 是插值语法的特殊字符，翻译文本中如需显示字面量花括号，需使用 `{'{'}` 和 `{'}'}` 转义
- 例如要显示 `{"user_id": "123"}`，应写为：`"如 {'{'}\"user_id\": \"123\"{'}'}"`
