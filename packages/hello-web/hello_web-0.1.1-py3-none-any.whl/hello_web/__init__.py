"""Hello Web - A simple Flask demo package."""

__version__ = "0.1.0"

from .main import app, main

# 让用户可以直接调用 hello_web.run()
def run():
    """Start the Flask application."""
    main()

# 导出主要的对象
__all__ = ['app', 'main', 'run']
