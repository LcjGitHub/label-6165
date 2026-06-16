# 家庭盆栽换盆历史

记录家中盆栽的换盆时间线，支持植物与换盆记录的增删改查。

## 持续集成（CI）

项目已配置 GitHub Actions 自动化流水线，确保代码质量和稳定性。

### 流水线作用

在代码提交和合并请求时自动执行以下检查，任一步骤失败则标记检查未通过：

1. **安装依赖**：自动安装前端 npm 依赖和后端 Python 依赖
2. **前端类型检查与构建**：执行 TypeScript 类型检查（`tsc -b`）和生产环境构建（`vite build`）
3. **后端接口冒烟测试**：运行 12 个 API 接口测试用例，覆盖植物 CRUD、换盆记录、浇水记录、概览统计、CSV 导出等核心接口

### 触发条件

- **Push 事件**：向任意分支推送代码时自动触发
- **Pull Request 事件**：向任意分支创建或更新合并请求时自动触发

流水线配置文件位于 [.github/workflows/ci.yml](.github/workflows/ci.yml)。

### 本地复现检查步骤

在提交代码前，建议本地执行以下命令验证检查是否通过：

#### 1. 安装前端依赖

```bash
cd frontend
npm install
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 执行前端类型检查与生产构建

```bash
cd frontend
npm run build
```

该命令会依次执行 `tsc -b`（TypeScript 类型检查）和 `vite build`（生产构建）。

#### 4. 执行后端接口冒烟测试

```bash
cd backend
python smoke_test.py
```

或使用 pytest 直接运行：

```bash
cd backend
pytest smoke_test.py -v
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + shadcn/ui、TanStack Query、RHF + zod、lucide-react |
| 后端 | Flask + SQLite (`backend/data/plants.db`) |

## 启动

### 后端（端口 7000）

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python app.py
```

首次启动会自动创建数据库并写入 3 株植物的种子数据（每株 2 条换盆记录）。

### 前端（端口 7101）

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 [http://localhost:7101](http://localhost:7101)。

## 功能

- **植物列表**：名称、品种、购入日期、换盆次数
- **植物详情**：换盆时间线（日期 + 备注）
- **CRUD**：植物与换盆记录均可新增、编辑、删除

## 目录结构

```
├── backend/          # Flask API
│   ├── app.py        # 入口与路由
│   ├── db.py         # SQLite 连接
│   ├── seed.py       # 种子数据
│   └── data/         # 数据库文件（运行时生成）
├── frontend/         # React 前端
│   └── src/
│       ├── api/      # API 请求
│       ├── components/
│       └── pages/
└── README.md
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/plants` | 植物列表 |
| GET | `/api/plants/:id` | 植物详情 + 换盆时间线 |
| POST | `/api/plants` | 创建植物 |
| PUT | `/api/plants/:id` | 更新植物 |
| DELETE | `/api/plants/:id` | 删除植物 |
| POST | `/api/plants/:id/repotting` | 添加换盆记录 |
| PUT | `/api/plants/:id/repotting/:rid` | 更新换盆记录 |
| DELETE | `/api/plants/:id/repotting/:rid` | 删除换盆记录 |
