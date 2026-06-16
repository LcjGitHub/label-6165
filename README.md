# 家庭盆栽换盆历史

记录家中盆栽的换盆时间线，支持植物与换盆记录的增删改查。

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
