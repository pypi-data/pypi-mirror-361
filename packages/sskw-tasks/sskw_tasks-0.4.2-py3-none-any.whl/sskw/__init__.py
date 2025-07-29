"""
SSKW Shared Celery Task Declaration Package

This package provides shared celery task declarations for audio processing workflows.
"""

# 包元信息
__version__ = "0.4.2"
__name__ = "sskw"
__title__ = "sskw-tasks"
__author__ = "liwei"
__email__ = "491520313@qq.com"
__description__ = "sskw shared celery task declaration"
__license__ = "MIT"
__homepage__ = "https://tasks.sensearray.com/docs"
__requires_python__ = ">=3.8"

# 导入子包以便于访问
try:
    from . import tasks
except ImportError:
    tasks = None

# 导出的公共接口
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__license__",
    "__homepage__",
    "tasks",
]

# 便捷的版本检查函数
def get_version():
    """返回当前包的版本号"""
    return __version__

def get_package_info():
    """返回包的详细信息"""
    return {
        "name": __name__,
        "title": __title__,
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "license": __license__,
        "homepage": __homepage__,
        "requires_python": __requires_python__,
    }
