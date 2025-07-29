import asyncio
from threading import Thread
from time import sleep, ctime
from co6co.utils import log
from functools import partial
from types import FunctionType
from typing import Callable
from co6co.utils import isCallable


class ThreadEvent:
    """
    线程Event loop
    Run Event Loop in different thread.

    ## 因某些原因写了该类
    ## 1. asyncio.run 在 没有正在运行的事件循环 的情况下运行协程的
        ## wx_user_dict:list[dict]=asyncio.run(bll.get_subscribe_alarm_user(config.appid))
        ## alarm= alarm_bll(app)
        ## po:bizAlarmTypePO=asyncio.run(alarm.get_alram_type_desc(po.alarmType))
        ## 2. 正在运行的事件循环
        ## This event loop is already running
        ## import nest_asyncio
        ## loop = asyncio.get_event_loop()
        ## wx_user_dict:list[dict]=loop.run_until_complete(bll.get_subscribe_alarm_user(config.appid))

        ## 3. 创建任务
        ## task=asyncio.create_task(bll.get_subscribe_alarm_user(config.appid))
        ## wx_user_dict:list[dict]=asyncio.run(task)
        ## 4.底层使用
        ## asyncio.ensure_future(coro())
        ## 5.
    """
    @property
    def loop(self):
        return self._loop

    bck: FunctionType = None

    def __init__(self, threadName: str = None, quitBck: FunctionType = None):
        self._loop = asyncio.new_event_loop()
        # log.warn(f"ThreadEventLoop:{id(self._loop)}")
        Thread(target=self._start_background, daemon=True, name=threadName) .start()
        self.bck = quitBck

    def _start_background(self):
        asyncio.set_event_loop(self.loop)
        self._loop.run_forever()
        if self.bck != None and isCallable(self.bck):
            self.bck()

    def runTask(self, tastFun, *args, **kwargs):
        # log.warn(f"ThreadEventLoop22:{id(self._loop)}")
        task = asyncio.run_coroutine_threadsafe(tastFun(*args, **kwargs), loop=self._loop)
        return task.result()

    def _shutdown(self):
        self._loop.stop()
        # print("running:", self._loop.is_running()) #True
        # print("closed.", self._loop.is_closed())   #False

    def close(self):
        self._loop.call_soon_threadsafe(partial(self._shutdown))

    def __del__(self):
        self._loop.close()
        # log.warn("closed")
        # print("running:", self._loop.is_running()) #False
        # print("closed.", self._loop.is_closed())   #True


class EventLoop:
    """
    数据库操作
    定义异步方法
    运行 result=run(异步方法,arg)

    """
    _eventLoop: ThreadEvent
    _closed: bool = None

    def __init__(self) -> None:
        self._eventLoop = ThreadEvent()
        self._closed = False

    def run(self, task, *args, **argkv):
        if self._closed:
            raise RuntimeError('ThreadEvent is closed')
        data = self._eventLoop.runTask(task, *args, **argkv)
        return data

    def close(self):
        self._eventLoop.close()
        self._closed = True

    def __del__(self) -> None:
        if not self._closed:
            self._eventLoop.close()


class Executing:
    """
    线程 自己执行自己退出
    """
    _starting: bool = None

    @property
    def loop(self):
        return self._loop

    @property
    def runing(self):
        return self._starting

    bck: FunctionType = None
    args = None
    kvgs = None

    def __init__(self, threadName: str, func,   *args, **kvgs):
        '''
        threadName: 线程名
        func: 执行的方法 async   :Callable[[str], str]
        args:  func 参数
        kvgs: func 参数
        '''
        self._loop = asyncio.new_event_loop()
        self._isCallClose = False
        self.threadName = threadName
        self.bck = func
        self.args = args
        self.kvgs = kvgs
        Thread(target=self._start_background, daemon=True, name=threadName) .start()

        def _start_background(self):
            try:
                asyncio.set_event_loop(self.loop)
                log.log("线程'{}->{}'运行...".format(self.threadName, id(self.loop)))
                self.loop.run_until_complete(self.bck(*self.args, **self.kvgs))
                # await self.bck(*self.args,**self.kvgs)
            except Exception as e:
                log.warn("线程'{}->{}'执行出错:{}".format(self.threadName, id(self.loop), e))
            finally:
                log.log("线程'{}->{}'结束.".format(self.threadName, id(self.loop)))
                self.loop.close()


class TaskManage:
    _starting: bool = None

    @property
    def loop(self):
        return self._loop

    @property
    def runing(self):
        return self._starting

    bck: FunctionType = None

    def __init__(self, threadName: str = None):
        self._loop = asyncio.new_event_loop()
        self._isCallClose = False
        self.threadName = threadName
        Thread(target=self._start_background, daemon=True, name=threadName) .start()

    def _start_background(self):
        asyncio.set_event_loop(self.loop)
        log.log("线程'{}->{}'运行...".format(self.threadName, id(self.loop)))
        self._starting = True
        self._loop.run_forever()
        log.log("线程'{}->{}'结束.".format(self.threadName, id(self.loop)))
        self._starting = False

    def runTask(self, tastFun, callBck, *args, **kwargs):
        """
        不能回调 调用 close 因为还在执行中.
        """
        # log.warn(f"ThreadEventLoop22:{id(self._loop)}")
        # run_coroutine_threadsafe 从非事件循环线程向事件循环线程提交协程任务
        task = asyncio.run_coroutine_threadsafe(tastFun(*args, **kwargs), loop=self._loop)
        # .result() 方法等待协程的结果，或者使用 .add_done_callback() 添加回调来处理结果。
        if callBck != None:
            task.add_done_callback(callBck)
        else:
            return task.result()

    def _stop(self):
        self._loop.stop()
        self._starting = False

    def stop(self):
        """
        runTask: 执行完后后才能调用，可再回调中调用
        调用完记得关闭
        """
        self._loop.call_soon_threadsafe(self._stop)

    def close(self):
        self._loop.call_soon_threadsafe(self._loop.close)
        self._isCallClose = True

    def __del__(self):
        if not self._isCallClose:
            self._loop.close()
