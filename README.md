# GFinder - 轻量级Web文件管理系统

GFinder是一个基于Vue + Django的轻量级Linux/Windows Web文件管理系统，通过Web界面实现文件的上传、下载、删除、重命名等基本操作，支持拖拽上传与拖拽移动，无需数据库，直接操作服务器的文件系统。

## 系统要求

- Python 3.6+
- Django 5.0+
- Node.js 和 npm（用于构建前端）

## 快速安装

### Windows

1. 确保已安装Python 3.6+
2. **重要：** 安装Node.js和npm
   - 访问 https://nodejs.org/ 下载并安装最新的LTS版本
   - 安装完成后，打开命令提示符，运行`npm -v`验证安装成功
3. 克隆或下载本项目
4. 运行`python start.py`启动服务

### Linux (Ubuntu/Debian)

1. 确保已安装Python 3.6+
2. 克隆或下载本项目
3. 运行`python3 start.py`启动服务
   - 脚本会自动检测并安装Node.js和npm（需要sudo权限）
   - 如果自动安装失败，请手动安装：`sudo apt install nodejs npm`

### Linux (CentOS/RHEL/Fedora)

1. 确保已安装Python 3.6+
2. 克隆或下载本项目
3. 运行`python3 start.py`启动服务
   - 脚本会自动检测并安装Node.js和npm（需要sudo权限）
   - 如果自动安装失败，请手动安装：`sudo yum install nodejs npm`

## 手动构建（高级用户）

如果需要手动构建前端：

```bash
cd frontend
npm install
npm run build
```

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

## 使用说明

系统将在 http://localhost:8000 启动（除非您指定了其他端口）。

### 启动参数

- `--port 8080`：指定端口号为8080
- `--build`：强制重新构建前端
- `--no-build`：跳过前端构建
- `--no-venv`：不使用虚拟环境

示例：`python start.py --port 8080 --build`

## 常见问题解决

1. **Linux终端显示乱码**：确保系统支持UTF-8编码
   - 安装中文语言包：`sudo apt-get install language-pack-zh-hans`
   - 设置UTF-8环境：`export LANG=zh_CN.UTF-8`

2. **npm安装失败**：
   - Windows：请手动访问 https://nodejs.org/ 下载安装
   - Linux：根据您的发行版，使用包管理器手动安装

3. **前端构建失败**：
   - 确保Node.js版本 >= 14.0.0
   - 尝试清除npm缓存：`npm cache clean --force`
   - 手动构建：`cd frontend && npm install && npm run build`

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