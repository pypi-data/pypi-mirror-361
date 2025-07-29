# 导入所有任务模块，确保 @app.task 装饰器生效
# 这样第三方使用 celery_app 时，可以自动获取相应的 task 声明

from . import audio_transcription
from . import audio_format_conversion

# 导出所有任务模块，方便外部直接导入
__all__ = [
    'audio_transcription',
    'audio_format_conversion',
]