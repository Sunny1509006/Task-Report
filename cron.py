import asyncio
from app.services.scheduler import start_scheduler

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_scheduler())