from sskw.tasks.celery_app import app
from sskw.tasks.models import MeetingTextRefineRequest, MeetingTextRefineResult

@app.task(name="sskw.meeting.text.refine")
def meeting_text_refine(input: MeetingTextRefineRequest) -> MeetingTextRefineResult:
    """
    会议语音文本LLM优化

    参数:
    - input (MeetingTextRefineRequest): 输入数据结构
    
    返回:
    - MeetingTextRefineResult: 处理结果
    """

    raise NotImplementedError("此任务必须在具体实现中完成")
