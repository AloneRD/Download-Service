import asyncio
import re
import os
import logging
from functools import partial

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound
import aiofiles

from cli import Cli



async def archive(request, response_delay, photo_directory_path, log,):
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'

    folder_name = re.match(r'/.*/(.*)/',str(request.rel_url)).group(1)
    if not os.path.exists(f'{photo_directory_path}/{folder_name}'):
        response.headers['Content-Type'] = 'text/html'
        raise HTTPNotFound(reason = "Архив не найден")

    await response.prepare(request)
    process = await asyncio.subprocess.create_subprocess_exec(
        'zip',
        '-r',
        '-',
        '.',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=f'{photo_directory_path}/{folder_name}'
    )
    try:
        while  not process.stdout.at_eof(): 
            stdout = await process.stdout.read(100*1000)
            await asyncio.sleep(response_delay)
            await response.write(stdout)
            if log == 'enable':
                logging.info("Sending archive chunk ...")
    except asyncio.CancelledError:
        if log == 'enable':
                logging.warning("Download was interrupted")
    finally:
        process.kill()

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r', encoding='utf-8') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    response_delay = 0

    cli = Cli()
    args = cli.parser.parse_args()

    if args.delay:
        response_delay = args.delay
        
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', partial(archive, photo_directory_path=args.path, response_delay=response_delay, log = args.log)),
    ])

    handler = logging.StreamHandler()
    logging.basicConfig(handlers=(handler,), 
                    format='[%(asctime)s | %(levelname)s]: %(message)s', 
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)
    
    web.run_app(app)
