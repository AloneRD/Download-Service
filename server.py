import asyncio
from asyncio.log import logger
import os
import logging
from functools import partial
from tabnanny import verbose

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound
import aiofiles

from cli import Cli


logger = logging.getLogger('download_service')


async def archive(request, response_delay, photo_directory_path):
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'

    folder_name = request.match_info['archive_hash']
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
            logger.info("Sending archive chunk ...")
    except asyncio.CancelledError:
        logger.warning("Download was interrupted")
        raise
    finally:
        if process.returncode is None:
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
        web.get('/archive/{archive_hash}/', partial(archive, photo_directory_path=args.path, response_delay=response_delay)),
    ])

    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s | %(levelname)s]: %(message)s')
    handler.setFormatter(formatter)
    
    logger.setLevel(args.verbose*10)
    logger.addHandler(handler)
    
    
    web.run_app(app)
