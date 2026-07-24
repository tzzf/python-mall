# FastAPI 电商项目

FastAPI + Vue3 + Docker 的全栈电商系统，包含用户端商城和后台管理。

## 项目结构

```
project/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # 应用入口
│   │   ├── api/             # API 路由层
│   │   │   ├── v1/          # 用户端 API (/api/v1)
│   │   │   └── admin/       # 管理端 API (/api/admin)
│   │   ├── service/         # 业务逻辑层
│   │   ├── repository/      # 数据访问层
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── core/            # 核心配置（数据库、Redis、安全）
│   │   └── tasks/           # 定时任务（APScheduler）
│   ├── alembic/             # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
│
├── admin/                   # 后台管理前端（Vue3）
│   ├── src/
│   │   ├── api/             # axios API 调用
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── router/          # 路由 + 导航守卫
│   │   └── views/           # 页面组件
│   ├── nginx.conf
│   └── Dockerfile
│
├── mall/                    # 用户端商城前端（Vue3）
│   ├── src/
│   │   ├── api/
│   │   ├── stores/
│   │   ├── router/
│   │   └── views/
│   ├── nginx.conf
│   └── Dockerfile
│
├── docker-compose.yml       # 开发环境
├── docker-compose.prod.yml  # 生产环境
└── deploy.sh                # 一键部署脚本
```

## 技术栈

### 后端
- **FastAPI** — 异步 API 框架
- **SQLAlchemy 2.0** — 异步 ORM
- **PostgreSQL** — 主数据库
- **Redis** — 购物车存储、定时任务队列
- **Alembic** — 数据库迁移
- **APScheduler** — 定时任务
- **Pydantic** — 数据验证
- **JWT** — 身份认证

### 前端
- **Vue 3** + Composition API + `<script setup>`
- **TypeScript**
- **Vite** — 构建工具
- **Ant Design Vue 4** — UI 组件库
- **Pinia** — 状态管理
- **Vue Router 4** — 路由

## 架构设计

四层架构：

```
API 层（路由）→ Service 层（业务）→ Repository 层（数据）→ Model 层（数据库）
```

统一响应格式：`{ code: 200, data: ..., message: "success" }`

## 启动方式

### 开发环境

```bash
nvm use 20
docker-compose up --build

cd admin
npm run dev

cd mall
npm run dev
```

### 生产环境

```bash
chmod +x deploy.sh
./deploy.sh
```

## 服务地址

| 服务 | 地址 |
|------|------|
| 用户端商城 | http://localhost:3001 |
| 后台管理 | http://localhost:3000 |
| API 文档 | http://localhost:8000/docs/ |

## 数据库

| 数据库 | 表 |
|--------|----|
| `v1_users` | 商城用户 |
| `admin_users` | 管理员 |
| `categories` | 商品分类 |
| `products` | 商品 |
| `orders` | 订单 |
| `order_items` | 订单商品项 |
| `coupons` | 优惠券 |
| `user_coupons` | 用户领取的优惠券 |
| `cart_items` | 购物车（Redis） |
| `channel_invite_codes` | 渠道商邀请码 |
| `channel_applications` | 渠道商申请记录 |
| `channel_banks` | 渠道商银行卡 |
| `channel_commissions` | 佣金记录（冻结/可用/已提现） |
| `channel_withdrawals` | 提现申请 |
| `channel_settings` | L1/L2 佣金率配置 |
| `order_channels` | 订单与渠道商关联（用于佣金追溯） |

## 订单状态机

```
pending（待支付）→ paid（已支付）→ shipped（已发货）→ delivered（已收货）→ completed（已完成）
    ↓                   ↓
cancelled（取消）    refunding（退款中）→ refunded（已退款）
```

## 主要功能

### 用户端（mall）
- 商品浏览与搜索
- 分类筛选
- 购物车（Redis 存储）
- 下单 + 优惠券
- 模拟支付
- 订单管理（查看、退款、取消）
- **渠道商申请**：用户可申请成为渠道商，获得专属邀请码
- **邀请返利**：L1（直接）和 L2（间接）邀请奖励机制
- **佣金管理**：查看佣金明细、汇总、申请提现
- **银行卡管理**：渠道商绑定收款银行卡

### 管理端（admin）
- 商品增删改查（含 AI 生成商品图）
- 分类管理
- 订单状态管理（发货、退款）
- 优惠券管理
- 用户管理（启用/禁用）
- 渠道商管理（审核、佣金记录、提现审批）
- 渠道商银行信息查看

### AI 能力
- **商品图生成**：新产品创建时自动调用 MiniMax API 生成商品主图
- 支持本地缓存下载，绕过第三方 URL 有效期限制
- 幂等设计：已有图片不重复生成

## 技术细节

### 购物车存储
- Redis 存储，Key 模式：`cart:{user_id}`
- JSON 格式存储，支持跨会话持久化

### 订单超时处理
- 待支付订单使用 Redis Sorted Set 跟踪：`order:pending:timeout`
- APScheduler 每分钟清理超时未支付订单

### JWT 认证
- 基于 OAuth2PasswordBearer
- Token 有效期：30 分钟（可配置）

### 密码加密
- argon2-cffi + passlib

### 通用分页模块
- `core/pagination/` — 通用的分页基础设施
- `paginate()` 函数：接收 `BaseFilter` 子类，自动处理 count、主查询、排序
- 业务 Filter 类（如 `V1UserFilter`、`OrderFilter`）继承 `BaseFilter`，实现 `to_conditions()`、`custom_conditions()`、`get_joins()` 等方法
- 支持 JOIN 模式、额外列急加载、自定义排序方向
- **佣金模块**使用该分页系统：支持按 status 筛选佣金记录

### 佣金自动计算（AOP）
- `@observe_order_status_change` 装饰器（`core/aspects.py`）监听订单状态变化
- **pending → paid**：冻结佣金（frozen）
- **paid → completed**：解冻并落为可用佣金（available）
- 渠道商通过邀请码发展下级，L1/L2 佣金率可配置

