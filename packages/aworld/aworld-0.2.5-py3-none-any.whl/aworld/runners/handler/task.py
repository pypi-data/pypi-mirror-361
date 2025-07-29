# coding: utf-8
# Copyright (c) 2025 inclusionAI.
import abc
import time

from typing import AsyncGenerator

from aworld.core.common import TaskItem
from aworld.core.tool.base import Tool, AsyncTool

from aworld.core.event.base import Message, Constants, TopicType
from aworld.core.task import TaskResponse
from aworld.logs.util import logger
from aworld.output import Output
from aworld.runners.handler.base import DefaultHandler
from aworld.runners.hook.hook_factory import HookFactory
from aworld.runners.hook.hooks import HookPoint


class TaskHandler(DefaultHandler):
    __metaclass__ = abc.ABCMeta

    def __init__(self, runner: 'TaskEventRunner'):
        self.runner = runner
        self.retry_count = runner.task.max_retry_count
        self.hooks = {}
        if runner.task.hooks:
            for k, vals in runner.task.hooks.items():
                self.hooks[k] = []
                for v in vals:
                    cls = HookFactory.get_class(v)
                    if cls:
                        self.hooks[k].append(cls)

    @classmethod
    def name(cls):
        return "_task_handler"


class DefaultTaskHandler(TaskHandler):
    async def handle(self, message: Message) -> AsyncGenerator[Message, None]:
        if message.category != Constants.TASK:
            return

        logger.debug(f"task handler receive message: {message}")

        headers = {"context": message.context}
        topic = message.topic
        task_item: TaskItem = message.payload
        if topic == TopicType.SUBSCRIBE_TOOL:
            new_tools = message.payload.data
            for name, tool in new_tools.items():
                if isinstance(tool, Tool) or isinstance(tool, AsyncTool):
                    await self.runner.event_mng.register(Constants.TOOL, name, tool.step)
                    logger.info(f"dynamic register {name} tool.")
                else:
                    logger.warning(f"Unknown tool instance: {tool}")
            return
        elif topic == TopicType.SUBSCRIBE_AGENT:
            return
        elif topic == TopicType.ERROR:
            async for event in self.run_hooks(message, HookPoint.ERROR):
                yield event

            logger.warning(f"task {self.runner.task.id} stop, cause: {task_item.msg}")
            self.runner._task_response = TaskResponse(msg=task_item.msg,
                                                      answer='',
                                                      success=False,
                                                      id=self.runner.task.id,
                                                      time_cost=(time.time() - self.runner.start_time),
                                                      usage=self.runner.context.token_usage)
            await self.runner.task.outputs.mark_completed()
            await self.runner.stop()
        elif topic == TopicType.FINISHED:
            async for event in self.run_hooks(message, HookPoint.FINISHED):
                yield event

            self.runner._task_response = TaskResponse(answer=str(message.payload),
                                                      success=True,
                                                      id=self.runner.task.id,
                                                      time_cost=(time.time() - self.runner.start_time),
                                                      usage=self.runner.context.token_usage)

            logger.info(f"{self.runner.task.id} finished.")
            await self.runner.task.outputs.mark_completed()
            await self.runner.stop()
        elif topic == TopicType.START:
            async for event in self.run_hooks(message, HookPoint.START):
                yield event

            logger.info(f"task start event: {message}, will send init message.")
            if message.payload:
                yield message
            else:
                yield self.runner.init_message
        elif topic == TopicType.OUTPUT:
            yield message
        elif topic == TopicType.HUMAN_CONFIRM:
            logger.warn("=============== Get human confirm, pause execution ===============")
            if self.runner.task.outputs and message.payload:
                await self.runner.task.outputs.add_output(Output(data=message.payload))
            self.runner._task_response = TaskResponse(answer=str(message.payload),
                                                      success=True,
                                                      id=self.runner.task.id,
                                                      time_cost=(time.time() - self.runner.start_time),
                                                      usage=self.runner.context.token_usage)
            await self.runner.stop()
        elif topic == TopicType.CANCEL:
            # Avoid waiting to receive events and send a mock event for quick cancel
            yield Message(session_id=self.runner.context.session_id, sender=self.name(), category='mock')
            await self.runner.stop()


    async def run_hooks(self, message: Message, hook_point: str) -> AsyncGenerator[Message, None]:
        hooks = self.hooks.get(hook_point, [])
        for hook in hooks:
            try:
                msg = hook(message)
                if msg:
                    yield msg
            except:
                logger.warning(f"{hook.point()} {hook.name()} execute fail.")
