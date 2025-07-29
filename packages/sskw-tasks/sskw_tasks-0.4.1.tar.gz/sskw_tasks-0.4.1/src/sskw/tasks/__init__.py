# 导入所有任务模块，确保 @app.task 装饰器生效
# 这样第三方使用 celery_app 时，可以自动获取相应的 task 声明

# from . import audio_transcription_sensevoice_cpu
# from . import audio_transcription_sensevoice_gpu
# from . import audio_transcription_paraformer_cpu
# from . import audio_transcription_paraformer_gpu
# from . import audio_format_conversion

# # 导出所有任务模块，方便外部直接导入
# __all__ = [
#     'audio_transcription_sensevoice_cpu',
#     'audio_transcription_sensevoice_gpu',
#     'audio_transcription_paraformer_cpu',
#     'audio_transcription_paraformer_gpu',
#     'audio_format_conversion',
# ]