import asyncio
import re

from aiohttp import web
import aiofiles


async def archive(request):
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'

    # Отправляет клиенту HTTP заголовки
    await response.prepare(request)
    folder_name = re.match(r'/.*/(.*)/',str(request.rel_url)).group(1)
    process = await asyncio.subprocess.create_subprocess_exec(
        'zip',
        '-r',
        '-',
        '.',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=f'test_photos/{folder_name}'
    )
    while  not process.stdout.at_eof(): 
        stdout = await process.stdout.read(100*1000)
        await response.write(stdout)
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r', encoding='utf-8') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
