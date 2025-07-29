from dotenv import load_dotenv

from huibiao_framework.utils.meta_class import OsAttrMeta

load_dotenv(".env")


class TaskConfig(metaclass=OsAttrMeta):
    TASK_RESOURCE_DIR: str = "/task_resource"


class MinioConfig(metaclass=OsAttrMeta):
    OSS_ENDPOINT: str
    OSS_AK: str
    OSS_SK: str
    OSS_BUCKET: str
    OSS_SECURE: bool = False


class ModelConfig(metaclass=OsAttrMeta):
    HUIZE_VLLM_QWEN_32B_AWQ_URL: str
