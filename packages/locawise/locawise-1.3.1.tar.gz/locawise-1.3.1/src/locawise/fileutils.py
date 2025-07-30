import os

import aiofiles


async def read_file(file_path: str) -> str:
    async with aiofiles.open(file_path, mode='r', encoding='UTF-8') as f:
        contents = await f.read()
        return contents


async def write_to_file(file_path: str, content: str):
    # Extract the directory path
    directory = os.path.dirname(file_path)

    # Create the directory if it doesn't exist
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    async with aiofiles.open(file_path, mode="w", encoding='UTF-8') as f:
        await f.write(content)
