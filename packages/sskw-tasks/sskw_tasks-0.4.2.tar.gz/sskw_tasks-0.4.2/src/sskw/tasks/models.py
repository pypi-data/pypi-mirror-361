from pydantic import BaseModel
from typing import List, Dict


class AudioTranscriptionRequest(BaseModel):
    audio_urls: List[str]
    data_id: str    

class AudioTranscriptionResult(BaseModel):
    audio_urls: List[str]       #原始待转换的urls
    data_id: str                #透传的data_id
    result_url: str             #转写结果url地址
    merged_audio_url: str       #合并后或本身只有一个的对应的url地址


class AudioFormatConversionRequest(BaseModel):
    from_url: str
    from_format: str
    to_format: str
    data_id: str

class AudioFormatConversionResult(BaseModel):
    from_url: str
    from_format: str
    to_format: str
    data_id: str
    to_url: str

class MeetingTextRefineRequest(BaseModel):
    textUrl: str
    ragTextUrl: str
    data_id: str

class MeetingTextRefineResult(BaseModel):
    textUrl: str
    ragTextUrl: str
    data_id: str
    resultUrl: str

class MeetingSummeryRequest(BaseModel):
    textUrl: str
    ragTextUrl: str
    data_id: str

class MeetingSummeryResult(BaseModel):
    textUrl: str
    ragTextUrl: str
    data_id: str
    resultUrl: str