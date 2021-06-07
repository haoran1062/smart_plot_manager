from datetime import datetime
from posix import CLD_DUMPED
from time import sleep
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich.panel import Panel
from utils.show_utils import *
from utils.manager import Manager
from config.cfg import Config

console = Console()


if __name__ == '__main__':
    cfg = Config()
    manager = Manager(cfg)
    manager.view_info()
    sleep(1)
    # manager.upgrade_worker_queue()
    # exit()

    with Live(layout, screen=True, redirect_stderr=False) as live:
        try:
            while True:
                sleep(1)
                manager.upgrade_worker_queue()
                layout_update(manager)
        except KeyboardInterrupt:
            pass



    



