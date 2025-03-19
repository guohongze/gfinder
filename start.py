#!/usr/bin/env python
"""
GFinder 启动脚本
根据系统环境自动配置并启动服务
"""

import os
import sys
import platform
import subprocess
import webbrowser
import argparse
import venv
import site
from pathlib import Path

def create_default_directory():
    """创建默认数据目录"""
    system = platform.system()
    if system == 'Windows':
        data_dir = 'd:\\data'
    else:  # Linux, Darwin等
        data_dir = '/var/opt/gfinder/data'
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"创建数据目录: {data_dir}")
    
    return data_dir

def get_venv_path(base_dir):
    """获取虚拟环境路径"""
    return os.path.join(base_dir, "venv")

def get_venv_bin_dir(venv_dir):
    """获取虚拟环境二进制目录"""
    if platform.system() == 'Windows':
        return os.path.join(venv_dir, 'Scripts')
    return os.path.join(venv_dir, 'bin')

def get_venv_python(venv_dir):
    """获取虚拟环境Python解释器路径"""
    bin_dir = get_venv_bin_dir(venv_dir)
    if platform.system() == 'Windows':
        return os.path.join(bin_dir, 'python.exe')
    return os.path.join(bin_dir, 'python')

def create_or_update_venv(venv_dir):
    """创建或更新虚拟环境"""
    if not os.path.exists(venv_dir):
        print(f"创建虚拟环境: {venv_dir}")
        venv.create(venv_dir, with_pip=True)
        return True
    else:
        print(f"使用已存在的虚拟环境: {venv_dir}")
        return False

def install_requirements_in_venv(venv_dir):
    """在虚拟环境中安装所需的Python依赖"""
    python_exec = get_venv_python(venv_dir)
    bin_dir = get_venv_bin_dir(venv_dir)
    
    try:
        # 使用虚拟环境中的pip安装依赖
        print("正在安装依赖...")
        # 使用subprocess运行命令，确保使用虚拟环境中的pip
        subprocess.check_call([python_exec, "-m", "pip", "install", "django", "django-cors-headers"])
        print("依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装依赖失败: {e}")
        return False

def build_frontend(force_build=False):
    """构建前端"""
    # 获取当前脚本所在目录
    base_dir = Path(__file__).resolve().parent
    frontend_dir = os.path.join(base_dir, 'frontend')
    dist_dir = os.path.join(frontend_dir, 'dist')
    
    # 如果dist目录不存在或强制构建
    if not os.path.exists(dist_dir) or force_build:
        print("需要构建前端...")
        if os.path.exists(os.path.join(frontend_dir, 'package.json')):
            try:
                # 检查系统类型选择正确的构建命令
                if platform.system() == 'Windows':
                    print("在Windows上构建前端...")
                    # 使用cmd保证兼容性
                    subprocess.check_call('cd frontend && npm install', shell=True)
                    subprocess.check_call('cd frontend && npm run build', shell=True)
                else:
                    print("在Linux/Mac上构建前端...")
                    subprocess.check_call('cd frontend && npm install && npm run build', shell=True)
                print("前端构建完成")
            except subprocess.CalledProcessError as e:
                print(f"前端构建失败: {e}")
                print("请手动构建前端: cd frontend && npm install && npm run build")
        else:
            print("未找到前端项目，请检查frontend目录")
    else:
        print("前端已构建")

def main():
    """主函数"""
    # 获取当前脚本所在目录
    base_dir = Path(__file__).resolve().parent
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='启动GFinder服务')
    parser.add_argument('--build', action='store_true', help='强制重新构建前端')
    parser.add_argument('--no-build', action='store_true', help='跳过前端构建')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口号')
    parser.add_argument('--no-venv', action='store_true', help='不使用虚拟环境')
    args = parser.parse_args()
    
    # 创建数据目录
    data_dir = create_default_directory()
    print(f"数据存储位置: {data_dir}")
    
    # 处理虚拟环境
    venv_dir = get_venv_path(base_dir)
    
    # 如果指定不使用虚拟环境
    if args.no_venv:
        print("按要求不使用虚拟环境")
        install_in_global = True
    else:
        # 创建或更新虚拟环境
        is_new_venv = create_or_update_venv(venv_dir)
        
        # 在虚拟环境中安装依赖
        if is_new_venv or not check_venv_dependencies(venv_dir):
            install_requirements_in_venv(venv_dir)
    
    # 如果未明确指定跳过构建，则检查并构建前端
    if not args.no_build:
        build_frontend(force_build=args.build)
    
    # 检查前端是否已构建
    frontend_dir = os.path.join(base_dir, 'frontend', 'dist')
    if not os.path.exists(frontend_dir):
        print("警告: 前端文件未构建，可能影响系统使用")
        print("您可以运行: python start.py --build 来构建前端")
    
    # 启动Django服务
    port = args.port
    host = '0.0.0.0'
    print(f"正在启动GFinder服务，访问地址: http://localhost:{port}")
    
    # 自动打开浏览器
    webbrowser.open(f"http://localhost:{port}")
    
    # 设置Django环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gfinder.settings')
    
    if args.no_venv:
        # 在当前环境运行Django
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])
    else:
        # 在虚拟环境中运行Django
        python_exec = get_venv_python(venv_dir)
        manage_py = os.path.join(base_dir, 'manage.py')
        subprocess.call([python_exec, manage_py, 'runserver', f'{host}:{port}'])

def check_venv_dependencies(venv_dir):
    """检查虚拟环境中是否已安装所需依赖"""
    python_exec = get_venv_python(venv_dir)
    
    try:
        # 检查django是否已安装
        result = subprocess.run(
            [python_exec, "-c", "import django; import corsheaders; print('OK')"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == 'OK'
    except Exception:
        return False

if __name__ == '__main__':
    main() 