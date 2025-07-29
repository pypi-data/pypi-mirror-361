import time
from abc import ABC, abstractmethod
from functools import wraps
from resource import TaskResource
from typing import Generic, List, Type, TypeVar

from loguru import logger
from utils.annotation import frozen_attrs

TS = TypeVar("TS", bound=TaskResource)


@frozen_attrs("task_type", "task_resource")
class HuibiaoTask(Generic[TS], ABC):
    def __init__(self, task_type: str, task_id: str, task_resource_cls: Type[TS]):
        self.task_id = task_id
        self.task_type = task_type
        self.__resource: TS = task_resource_cls(task_id)

    @property
    def task_resource(self) -> TS:
        return self.__resource

    @abstractmethod
    async def pipeline(self):
        pass

    @staticmethod
    def StepAnnotation(
        step_name: str = None, *, depend: List[str] = None, output: str = None
    ):
        depend = list() if depend is None else depend

        def decorator(func):
            @wraps(func)
            async def wrapper(self: "HuibiaoTask[TS]", *args, **kwargs):
                name = step_name or func.__name__

                do_task = False  # 是否执行任务的标志

                if output is not None:
                    if not self.task_resource[output].is_completed():
                        do_task = True
                    else:
                        logger.info(
                            f"[{self.task_type}][{self.task_id}][{name}]产出资源[{output}]已完成"
                        )

                # 任务结束信号检测

                # 预加载资源 depend_resources
                if do_task:
                    # 加载依赖资源
                    for d_r in depend:
                        self.task_resource[d_r].load()

                    start = time.perf_counter()
                    result = await func(self, *args, **kwargs)
                    elapsed = time.perf_counter() - start
                    logger.info(
                        f"[{self.task_type}][{self.task_id}][{name}]耗时: {elapsed:.6f} 秒"
                    )

                    # 标记资源完成 output_resources
                    if output is not None:
                        self.task_resource[output].complete()

                    return result
                else:
                    logger.info(
                        f"[{self.task_type}][{self.task_id}][{name}]已完成，跳过该步骤"
                    )

            return wrapper

        return decorator
