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
import locale
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict

# 中英文消息字典
MESSAGES = {
    'zh': {
        'creating_data_dir': "创建数据目录: {}",
        'data_location': "数据存储位置: {}",
        'creating_venv': "创建虚拟环境: {}",
        'using_existing_venv': "使用已存在的虚拟环境: {}",
        'installing_deps': "正在安装依赖...",
        'deps_installed': "依赖安装完成",
        'deps_failed': "依赖安装失败: {}",
        'using_venv_path': "使用虚拟环境包路径: {}",
        'venv_not_exist': "错误: 虚拟环境site-packages不存在: {}",
        'no_venv': "按要求不使用虚拟环境",
        'deps_install_failed': "依赖安装失败，请检查错误信息",
        'checking_npm': "检查npm是否已安装...",
        'npm_not_found': "未找到npm，需要安装Node.js...",
        'installing_npm': "正在自动安装npm...",
        'npm_install_success': "npm安装成功",
        'npm_install_failed': "自动安装npm失败",
        'npm_windows_guide': "请手动安装Node.js和npm: 访问 https://nodejs.org/ 下载安装包",
        'npm_detected': "检测到npm版本: {}",
        'frontend_build_needed': "需要构建前端...",
        'building_windows': "在Windows上构建前端...",
        'building_linux': "在Linux/Mac上构建前端...",
        'frontend_build_complete': "前端构建完成",
        'frontend_build_failed': "前端构建失败: {}",
        'frontend_build_manual': "请手动构建前端: cd frontend && npm install && npm run build",
        'frontend_not_found': "未找到前端项目，请检查frontend目录",
        'frontend_built': "前端已构建",
        'warning_no_frontend': "警告: 前端文件未构建，可能影响系统使用",
        'build_guide': "您可以运行: python start.py --build 来构建前端",
        'starting_service': "正在启动GFinder服务，访问地址: http://localhost:{}",
        'browser_open_failed': "无法自动打开浏览器，请手动访问: http://localhost:{}",
        'django_import_failed': "导入Django失败: {}",
        'try_venv_python': "尝试使用虚拟环境Python执行...",
        'django_start_failed': "启动Django服务失败: {}",
        'check_venv_deps': "请确保虚拟环境中已安装所有依赖",
        'locale_not_supported': "注意: 您的系统不支持中文显示，将使用英文提示"
    },
    'en': {
        'creating_data_dir': "Creating data directory: {}",
        'data_location': "Data storage location: {}",
        'creating_venv': "Creating virtual environment: {}",
        'using_existing_venv': "Using existing virtual environment: {}",
        'installing_deps': "Installing dependencies...",
        'deps_installed': "Dependencies installed successfully",
        'deps_failed': "Failed to install dependencies: {}",
        'using_venv_path': "Using virtual env path: {}",
        'venv_not_exist': "Error: Virtual env site-packages does not exist: {}",
        'no_venv': "Not using virtual environment as requested",
        'deps_install_failed': "Dependencies installation failed, check error messages",
        'checking_npm': "Checking if npm is installed...",
        'npm_not_found': "npm not found, Node.js is required...",
        'installing_npm': "Automatically installing npm...",
        'npm_install_success': "npm installed successfully",
        'npm_install_failed': "Failed to automatically install npm",
        'npm_windows_guide': "Please install Node.js and npm manually: visit https://nodejs.org/ to download",
        'npm_detected': "Detected npm version: {}",
        'frontend_build_needed': "Frontend build is needed...",
        'building_windows': "Building frontend on Windows...",
        'building_linux': "Building frontend on Linux/Mac...",
        'frontend_build_complete': "Frontend build completed",
        'frontend_build_failed': "Frontend build failed: {}",
        'frontend_build_manual': "Please build frontend manually: cd frontend && npm install && npm run build",
        'frontend_not_found': "Frontend project not found, please check frontend directory",
        'frontend_built': "Frontend already built",
        'warning_no_frontend': "Warning: Frontend files not built, may affect system usage",
        'build_guide': "You can run: python start.py --build to build the frontend",
        'starting_service': "Starting GFinder service, access at: http://localhost:{}",
        'browser_open_failed': "Unable to open browser automatically, please visit: http://localhost:{}",
        'django_import_failed': "Failed to import Django: {}",
        'try_venv_python': "Trying to use virtual environment Python...",
        'django_start_failed': "Failed to start Django service: {}",
        'check_venv_deps': "Please ensure all dependencies are installed in the virtual environment",
        'locale_not_supported': "Note: Your system does not support Chinese display, using English prompts"
    }
}

# 检测系统是否支持中文
def check_chinese_support() -> bool:
    """
    检测系统是否支持中文显示
    
    Returns:
        bool: 是否支持中文
    """
    try:
        # 尝试设置中文区域
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
        return True
    except locale.Error:
        try:
            # 尝试其他可能的中文区域名称
            locale.setlocale(locale.LC_ALL, 'zh_CN.utf8')
            return True
        except locale.Error:
            pass
    
    # 检查是否有任何中文区域可用
    try:
        output = subprocess.check_output(['locale', '-a'], text=True)
        return any(loc.startswith('zh_') for loc in output.splitlines())
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return False

# 设置语言和编码
supports_chinese = check_chinese_support()
lang = 'zh' if supports_chinese else 'en'

# 设置输出编码，解决Linux终端汉字显示问题
if platform.system() != 'Windows':
    # 确保标准输出使用UTF-8编码
    if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'UTF-8':
        sys.stdout.reconfigure(encoding='utf-8')

def print_message(key: str, *args) -> None:
    """
    打印本地化消息
    
    Args:
        key: 消息键
        args: 格式化参数
    """
    message = MESSAGES[lang].get(key, MESSAGES['en'].get(key, key))
    formatted_message = message.format(*args) if args else message
    
    try:
        # 尝试直接打印
        print(formatted_message)
    except UnicodeEncodeError:
        # 如果编码错误，尝试使用UTF-8编码打印
        try:
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout.buffer.write(formatted_message.encode('utf-8'))
                sys.stdout.buffer.write(b'\n')
                sys.stdout.buffer.flush()
        except Exception:
            # 最后的备选方案：打印ASCII版本
            print(formatted_message.encode('utf-8', errors='replace').decode('ascii', errors='replace'))

def create_default_directory() -> str:
    """
    创建默认数据目录
    
    Returns:
        str: 数据目录的路径
    """
    system = platform.system()
    if system == 'Windows':
        data_dir = 'd:\\data'
    else:  # Linux, Darwin等
        data_dir = '/var/opt/gfinder/data'
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print_message('creating_data_dir', data_dir)
    
    return data_dir

def get_venv_path(base_dir: str) -> str:
    """
    获取虚拟环境路径
    
    Args:
        base_dir: 基础目录路径
        
    Returns:
        str: 虚拟环境路径
    """
    return os.path.join(base_dir, "venv")

def get_venv_bin_dir(venv_dir: str) -> str:
    """
    获取虚拟环境二进制目录
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        str: 二进制目录路径
    """
    if platform.system() == 'Windows':
        return os.path.join(venv_dir, 'Scripts')
    return os.path.join(venv_dir, 'bin')

def get_venv_python(venv_dir: str) -> str:
    """
    获取虚拟环境Python解释器路径
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        str: Python解释器路径
    """
    bin_dir = get_venv_bin_dir(venv_dir)
    if platform.system() == 'Windows':
        return os.path.join(bin_dir, 'python.exe')
    return os.path.join(bin_dir, 'python')

def get_venv_site_packages(venv_dir: str) -> str:
    """
    获取虚拟环境的site-packages路径
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        str: site-packages目录路径
    """
    if platform.system() == 'Windows':
        return os.path.join(venv_dir, 'Lib', 'site-packages')
    else:
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        return os.path.join(venv_dir, 'lib', python_version, 'site-packages')

def create_or_update_venv(venv_dir: str) -> bool:
    """
    创建或更新虚拟环境
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        bool: 是否为新创建的虚拟环境
    """
    if not os.path.exists(venv_dir):
        print_message('creating_venv', venv_dir)
        venv.create(venv_dir, with_pip=True)
        return True
    else:
        print_message('using_existing_venv', venv_dir)
        return False

def install_requirements_in_venv(venv_dir: str) -> bool:
    """
    在虚拟环境中安装所需的Python依赖
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        bool: 安装是否成功
    """
    python_exec = get_venv_python(venv_dir)
    
    try:
        print_message('installing_deps')
        requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        if os.path.exists(requirements_file):
            subprocess.check_call([python_exec, "-m", "pip", "install", "-r", requirements_file])
        else:
            subprocess.check_call([python_exec, "-m", "pip", "install", "django", "django-cors-headers"])
        print_message('deps_installed')
        return True
    except subprocess.CalledProcessError as e:
        print_message('deps_failed', e)
        return False

def check_venv_dependencies(venv_dir: str) -> bool:
    """
    检查虚拟环境中是否已安装所需依赖
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        bool: 依赖是否已安装
    """
    python_exec = get_venv_python(venv_dir)
    
    try:
        result = subprocess.run(
            [python_exec, "-c", "import django; import corsheaders; print('OK')"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == 'OK'
    except Exception:
        return False

def check_npm_installed() -> Tuple[bool, str]:
    """
    检查npm是否已安装
    
    Returns:
        Tuple[bool, str]: (是否已安装, 版本信息)
    """
    try:
        if platform.system() == 'Windows':
            # Windows系统使用shell=True来运行命令
            npm_version = subprocess.check_output('npm --version', 
                                                 shell=True, 
                                                 text=True).strip()
        else:
            # 非Windows系统使用普通方式
            npm_version = subprocess.check_output(['npm', '--version'], 
                                                text=True).strip()
        return True, npm_version
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, ""

def install_npm() -> bool:
    """
    在Linux系统上自动安装npm
    
    Returns:
        bool: 安装是否成功
    """
    if platform.system() == 'Windows':
        return False  # Windows不自动安装
    
    try:
        # 检测Linux发行版
        if os.path.exists('/etc/debian_version'):
            # Debian/Ubuntu
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'nodejs', 'npm'])
        elif os.path.exists('/etc/redhat-release'):
            # CentOS/RHEL/Fedora
            subprocess.check_call(['sudo', 'yum', 'install', '-y', 'epel-release'])
            subprocess.check_call(['sudo', 'yum', 'install', '-y', 'nodejs', 'npm'])
        elif os.path.exists('/etc/arch-release'):
            # Arch Linux
            subprocess.check_call(['sudo', 'pacman', '-Sy', '--noconfirm', 'nodejs', 'npm'])
        else:
            # 其他Linux发行版
            return False
        
        return True
    except subprocess.SubprocessError:
        return False

def build_frontend(force_build: bool = False) -> None:
    """
    构建前端
    
    Args:
        force_build: 是否强制重新构建
    """
    base_dir = Path(__file__).resolve().parent
    frontend_dir = os.path.join(base_dir, 'frontend')
    dist_dir = os.path.join(frontend_dir, 'dist')
    
    if not os.path.exists(dist_dir) or force_build:
        print_message('frontend_build_needed')
        
        # 检查npm是否已安装
        print_message('checking_npm')
        npm_installed, npm_version = check_npm_installed()
        
        if not npm_installed:
            print_message('npm_not_found')
            
            if platform.system() != 'Windows':
                # Linux自动安装npm
                print_message('installing_npm')
                if install_npm():
                    print_message('npm_install_success')
                    npm_installed, npm_version = check_npm_installed()
                else:
                    print_message('npm_install_failed')
            else:
                # Windows提供安装指南
                print_message('npm_windows_guide')
                return
        
        if npm_installed:
            print_message('npm_detected', npm_version)
            
            if os.path.exists(os.path.join(frontend_dir, 'package.json')):
                try:
                    if platform.system() == 'Windows':
                        print_message('building_windows')
                        subprocess.check_call('cd frontend && npm install', shell=True)
                        subprocess.check_call('cd frontend && npm run build', shell=True)
                    else:
                        print_message('building_linux')
                        # 确保在Linux上使用UTF-8环境变量
                        my_env = os.environ.copy()
                        my_env["LANG"] = "en_US.UTF-8"
                        my_env["LC_ALL"] = "en_US.UTF-8"
                        subprocess.check_call('cd frontend && npm install && npm run build', 
                                             shell=True, env=my_env)
                    print_message('frontend_build_complete')
                except subprocess.CalledProcessError as e:
                    print_message('frontend_build_failed', e)
                    print_message('frontend_build_manual')
            else:
                print_message('frontend_not_found')
    else:
        print_message('frontend_built')

def main() -> None:
    """主函数"""
    base_dir = Path(__file__).resolve().parent
    
    # 如果不支持中文，显示提示
    if not supports_chinese and lang == 'en':
        print_message('locale_not_supported')
    
    parser = argparse.ArgumentParser(description='启动GFinder服务')
    parser.add_argument('--build', action='store_true', help='强制重新构建前端')
    parser.add_argument('--no-build', action='store_true', help='跳过前端构建')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口号')
    parser.add_argument('--no-venv', action='store_true', help='不使用虚拟环境')
    args = parser.parse_args()
    
    data_dir = create_default_directory()
    print_message('data_location', data_dir)
    
    venv_dir = get_venv_path(base_dir)
    
    if args.no_venv:
        print_message('no_venv')
    else:
        is_new_venv = create_or_update_venv(venv_dir)
        
        if is_new_venv or not check_venv_dependencies(venv_dir):
            if not install_requirements_in_venv(venv_dir):
                print_message('deps_install_failed')
                return
        
        venv_site_packages = get_venv_site_packages(venv_dir)
        if os.path.exists(venv_site_packages):
            print_message('using_venv_path', venv_site_packages)
            sys.path.insert(0, venv_site_packages)
        else:
            print_message('venv_not_exist', venv_site_packages)
            return
    
    if not args.no_build:
        build_frontend(force_build=args.build)
    
    frontend_dir = os.path.join(base_dir, 'frontend', 'dist')
    if not os.path.exists(frontend_dir):
        print_message('warning_no_frontend')
        print_message('build_guide')
    
    port = args.port
    host = '0.0.0.0'
    print_message('starting_service', port)
    
    # 在Linux下可能不一定会自动打开浏览器
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        print_message('browser_open_failed', port)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gfinder.settings')
    
    # 设置环境变量确保子进程也使用UTF-8
    if platform.system() != 'Windows':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LC_ALL'] = 'en_US.UTF-8'
    
    try:
        if args.no_venv:
            from django.core.management import execute_from_command_line
            execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])
        else:
            try:
                import django
                from django.core.management import execute_from_command_line
                execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])
            except ImportError as e:
                print_message('django_import_failed', e)
                print_message('try_venv_python')
                python_exec = get_venv_python(venv_dir)
                manage_py = os.path.join(base_dir, 'manage.py')
                # 在Linux上使用UTF-8环境变量
                my_env = os.environ.copy()
                if platform.system() != 'Windows':
                    my_env["PYTHONIOENCODING"] = "utf-8"
                    my_env["LANG"] = "en_US.UTF-8"
                    my_env["LC_ALL"] = "en_US.UTF-8"
                subprocess.check_call([python_exec, manage_py, 'runserver', f'{host}:{port}'], env=my_env)
    except Exception as e:
        print_message('django_start_failed', e)
        print_message('check_venv_deps')
        return

if __name__ == '__main__':
    main() 