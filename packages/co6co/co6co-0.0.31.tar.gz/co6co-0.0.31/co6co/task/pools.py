
from concurrent.futures import ThreadPoolExecutor
import queue
import asyncio
import threading
from typing import Callable, Tuple, Any


async def timeout_async(timeout, func, *args, **kwargs):
    """ 
    loop = asyncio.get_event_loop()
    cap = loop.run_until_complete(timeout_async(5, open_video))

    :param timeout: 超时时间（秒）
    :return: 打开结果
    """
    try:
        # 等待指定的超时时间
        cap = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        return cap
    except asyncio.TimeoutError:
        print("Timeout occurred while opening the video stream.")
        return False


def timeout(timeout, func, throw: bool = True,  *args, **kwargs) -> Tuple[bool, Any | None]:
    """
    此函数用于在指定时间内尝试打开视频流
    :param timeout: 超时时间（秒）
    :param func , *args, **kwargs
    :param throw: 是否抛出异常

    func 执行异常会抛出异常

    :return: 是否超时,返回值
    """
    result = []
    exception = []

    def wrapper():
        try:
            result.append(func(*args, **kwargs))
        except Exception as e:
            exception.append(e)
    # 创建并启动新线程来打开视频流
    thread = threading.Thread(target=wrapper)
    thread.start()
    # 等待指定的超时时间
    thread.join(timeout)
    if thread.is_alive():
        # //todo 这里不知要怎么停止线程，_stop 有锁时，会有断言错误，
        # 如果线程仍在运行，说明超时了
        lock = thread._tstate_lock
        if lock is None:
            thread._stop()
        else:
            # 让它自己完成后停止
            pass
        return True, None
    if throw and exception:
        raise exception[0]
    return False, result[0]


class limitThreadPoolExecutor(ThreadPoolExecutor):
    """
    限制进程池队列长度（默认队列长度无限）
    防止内存爆满的问题

    # .shutdown(wait=True)
    # True  =>会阻塞主线程，直到 task 任务完成
    # False =>线程池会立即关闭，不再接受新任务，并且不会等待已提交的任务完成
    # 当 cancel_futures 为 True 时，在调用 shutdown 方法关闭线程池时，会尝试取消所有尚未开始执行的任 
    """

    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        # 不甚至将时无限队列长度
        self._work_queue = queue.Queue(self._max_workers * 2)  # 设置队列大小
