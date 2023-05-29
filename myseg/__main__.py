"""
入口
"""
import asyncio

from myseg.tocli.cli_main import cli_main


async def main():
    """
    入口
    """
    await cli_main()


if __name__ == '__main__':
    asyncio.run(main())
