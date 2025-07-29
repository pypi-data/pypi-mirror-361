from sskw.tasks.celery_app import app
from sskw.tasks.models import MeetingSummeryRequest, MeetingSummeryResult

@app.task(name="sskw.meeting.text.summery")
def meeting_text_summery(input: MeetingSummeryRequest) -> MeetingSummeryResult:
    """
    会议语音文本提取会议纪要
    参数:
    - input (MeetingSummeryRequest): 输入数据结构
    
    返回:
    - MeetingSummeryResult: 处理结果
    """

    raise NotImplementedError("此任务必须在具体实现中完成")