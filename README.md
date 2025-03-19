# GFinder - 轻量级Web文件管理系统

GFinder是一个基于Vue + Django的轻量级Linux/Windows Web文件管理系统，通过Web界面实现文件的上传、下载、删除、重命名等基本操作，支持拖拽上传与拖拽移动，无需数据库，直接操作服务器的文件系统。

## 功能特点

- 基本文件操作：上传、下载、删除、重命名、新建文件/文件夹
- 拖拽功能：拖拽上传、拖拽移动
- 文件预览：文本、图片、PDF等预览支持
- 界面展示：类似文件管理器的操作界面，面包屑导航
- 右键管理：WEB界面对象的右键管理，包括复制，粘贴，删除，剪切
- 智能存储：根据系统自动设置默认存储位置，Windows为d:\data，Linux为/var/opt/gfinder/data

## 技术栈

- 前端：Vue 3 + Element Plus
- 后端：Django + Django REST Framework
- 文件操作：Python内置os和shutil模块

## 部署方式

### 环境要求

- Python 3.8+
- Node.js 14+ (仅在手动构建前端时需要)
- NPM 6+ (仅在手动构建前端时需要)

### 方式一：一键自动部署(推荐)

启动脚本会自动处理所有依赖和环境配置：

1. 运行启动脚本(自动创建虚拟环境、安装依赖、构建前端并启动)：
   ```
   python start.py
   ```

#### 启动脚本高级选项

- 强制重新构建前端：`python start.py --build`
- 跳过前端构建：`python start.py --no-build`
- 自定义端口：`python start.py --port 8080`
- 不使用虚拟环境：`python start.py --no-venv`

### 方式二：手动分步部署

如果您希望更灵活地控制部署过程，可以按以下步骤手动部署：

1. 创建并激活虚拟环境：
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

2. 安装Python依赖：
   ```
   pip install django django-cors-headers
   ```

3. 手动构建前端：
   ```
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. 启动Django服务：
   ```
   python manage.py runserver
   ```

系统将在 http://localhost:8000 启动（除非您指定了其他端口）。

## 虚拟环境(venv)

GFinder默认使用Python虚拟环境来隔离项目依赖，避免与系统Python环境产生冲突：

- 虚拟环境会自动创建在项目根目录的`venv`文件夹中
- 所有Python依赖都会安装在虚拟环境中，不会影响系统环境
- 如果您不希望使用虚拟环境，可以使用`--no-venv`选项

## 项目结构

```
/gfinder/
│── backend/                # Django 后端
│   ├── views.py            # 视图处理
│   ├── urls.py             # 路由配置
│   └── file_operations/    # 文件操作逻辑
│── frontend/               # Vue 前端
│   ├── components/         # 组件目录
│   ├── views/              # 视图页面
│   └── store/              # 状态管理
│── gfinder/                # Django项目配置
│── venv/                   # Python虚拟环境(自动创建)
│── manage.py               # Django管理脚本
│── start.py                # 启动脚本
│── README.md               # 项目说明
```

## 注意事项

- 请勿在生产环境中使用默认的SECRET_KEY，应该在生产环境中更改它
- 默认情况下，服务器运行在8000端口，可以在启动脚本中修改
- 文件操作直接影响服务器文件系统，请谨慎使用

## 许可

MIT许可证 