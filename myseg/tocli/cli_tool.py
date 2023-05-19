"""
cli通用函数
"""
import asyncio


async def async_input(prompt=''):
    """
    异步输入
    """
    try:
        return await asyncio.to_thread(input, prompt)
    except AttributeError:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, input, prompt)
