"""

Demonstrates a dynamic Layout

"""

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
from rich.table import Table
from rich.progress import Progress

# console = Console()
layout = Layout()

layout.split(
    Layout(name="header", size=1),
    Layout(ratio=1, name="main"),
)

layout["main"].split_row(Layout(name="p盘任务详情", ratio=2), Layout(name="底边栏"))
layout["底边栏"].split(Layout(name='硬件使用详情'), Layout(name='p盘状态详情'), Layout(name='SSD详情'), Layout(name='HDD详情'))


class Clock:
    """Renders the time in the center of the screen."""

    def __rich__(self) -> Text:
        return Text(datetime.now().ctime(), style="bold magenta", justify="center")

layout["header"].update(Clock())

def get_plot_status(manager):
    n24 = manager.last_24h_finished_plot_number()
    n_all = len(manager.finish_time_list)
    remaining_n = manager._hdd.get_all_max_plot_number()
    running_n = manager.get_running_worker_num()
    l = [
        [str(n_all), str(n24), str(remaining_n), '--:--:--' if n24 == 0 else f'{remaining_n / n24 :.2f} 天', f'{running_n} 个' ]
    ]
    return l

def create_plot_status_table(manager):
    table = Table(show_footer=False)
    table_centered = Align.center(table)
    table.title = "P盘情况概览"
    table.add_column("本次总P盘数量", no_wrap=True)
    table.add_column("过去24小时P盘数量", no_wrap=True)
    table.add_column("磁盘剩余可储存数量", no_wrap=True)
    table.add_column("预估填满剩余时间", no_wrap=True)
    table.add_column("正在运行任务数", no_wrap=True)

    table.columns[0].style = "magenta"
    table.show_footer = True
    table.footer_style = "bright_red"
    rows = get_plot_status(manager)
    for row in rows:
        table.add_row(*row)
    return table

def get_hardware_input(manager):
    ssd_used, ssd_free, ssd_total = manager._ssd.get_total_ssd_status()
    hdd_used, hdd_free, hdd_total = manager._hdd.get_total_hdd_status()
    mem_used, mem_free, mem_total = manager._mem.get_used_memory(), manager._mem.get_free_memory(), manager._mem.max_memory
    mem_n = mem_free // (manager.config.memory / 1024)
    cpu_r_l = manager._cpu.free_cpu_list
    cpu_r_n = len(cpu_r_l)
    cpu_p_n = cpu_r_n / manager.config.thread_number
    l = [
        ['CPU', f'{manager._cpu.used_num}', f'{cpu_r_n}', f'{manager._cpu.thread_num}', f'{ 100 * float(manager._cpu.used_num) / manager._cpu.thread_num :.2f}%', f'{cpu_p_n}'],
        ['内存', f'{mem_used :.2f}G', f'{mem_free :.2f}G', f'{mem_total :.2f}G', f'{100 * manager._mem.get_mem_percent() :.2f}%', f'{mem_n}'],
        ['SSD', f'{ssd_used / 1024 :.2f}T', f'{ssd_free / 1024 :.2f}T', f'{ssd_total / 1024 :.2f}T', f'{ 100 * float(ssd_used) / ssd_total :.2f}%', f'{manager._ssd.get_all_max_plot_number()}'],
        ['HDD', f'{hdd_used / 1024 :.2f}T', f'{hdd_free / 1024 :.2f}T', f'{hdd_total / 1024 :.2f}T', f'{ 100 * float(hdd_used) / hdd_total :.2f}%', f'{manager._hdd.get_all_max_plot_number()}']
    ]
    return l

def create_hardware_table(manager):
    table = Table(show_footer=False)
    table_centered = Align.center(table)
    table.title = "硬件使用情况"
    table.add_column("硬件类型", no_wrap=True)
    table.add_column("使用量", no_wrap=True)
    table.add_column("剩余量", no_wrap=True)
    table.add_column("总量", no_wrap=True)
    table.add_column("使用率", no_wrap=True)
    table.add_column("最大可再申请任务数", no_wrap=True)

    table.columns[0].style = "magenta"
    table.show_footer = True
    table.footer_style = "bright_red"
    rows = get_hardware_input(manager)
    for row in rows:
        table.add_row(*row)
    return table

def get_plot_queue_status(manager):
    l = []
    for now_worker in manager.worker_queue:
        now_status = now_worker.get_info()
        progress = Progress()
        task = progress.add_task("进度", total=1.0)
        process_bar = Panel.fit(
            progress, title="当前进度"
        )
        progress.update(task, completed=now_status[3])
        now_status[3] = process_bar
        l.append(now_status)
    return l

def create_plot_queue_table(manager):
    table = Table(show_footer=False)
    table_centered = Align.center(table)
    table.title = "P盘任务运行情况"
    table.add_column("任务", no_wrap=True)
    table.add_column("pid", no_wrap=True)
    table.add_column("CPU核", no_wrap=True)
    table.add_column("进度", no_wrap=True)
    table.add_column("iter", no_wrap=True)
    table.add_column("步骤", no_wrap=True)
    table.add_column("开始时间", no_wrap=True)
    table.add_column("运行时间", no_wrap=True)
    table.add_column("预计剩余时间", no_wrap=True)
    table.add_column("plot缓存路径", no_wrap=True)
    table.add_column("输出路径", no_wrap=True)
    table.columns[0].style = "magenta"
    table.show_footer = True
    table.footer_style = "bright_red"

    rows = get_plot_queue_status(manager)
    for row in rows:
        table.add_row(*row)
    return table

def layout_update(manager):
    layout["硬件使用详情"].update(
        Columns([Panel(create_hardware_table(manager))])
    )

    layout["p盘任务详情"].update(
        Columns([Panel(create_plot_queue_table(manager))])
    )

    layout["p盘状态详情"].update(
        Columns([Panel(create_plot_status_table(manager))])
    )

    layout["SSD详情"].update(
        Columns([Panel(manager._ssd.view_info_table())])
    )

    layout["HDD详情"].update(
        Columns([Panel(manager._hdd.view_info_table())])
    )

    



# with Live(layout, screen=True, redirect_stderr=False) as live:
#     try:
#         while True:
#             sleep(1)
#     except KeyboardInterrupt:
#         pass
