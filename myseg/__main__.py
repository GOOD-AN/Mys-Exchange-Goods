"""
入口
"""
import asyncio

from myseg import scheduler
from myseg.tocli.cli_exchange import cli_init_task
from myseg.tocli.cli_main import cli_main


async def main():
    """
    入口
    """
    scheduler.start()
    await cli_init_task()
    await cli_main()


if __name__ == '__main__':
    asyncio.run(main())
