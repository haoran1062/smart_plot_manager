

def do_plot(plot_args, log_file):
    args = ''
    if isinstance(plot_args, str) or isinstance(plot_args, list):
        args = plot_args
    elif isinstance(plot_args, dict):
        args = f"{plot_args['chia_exec']} plots create -k {plot_args['k']} -n {plot_args['queue_size']} -r {plot_args['thread_n']} -u {plot_args['bucket_n']} -b {plot_args['memory']} -t {plot_args['now_plot_path']} -d {plot_args['now_out_base_path']}"
    
    print(args)
    process = subprocess.Popen(
        args=args,
        stdout=log_file,
        stderr=log_file,
        shell=False,
        **kwargs,
    )
    return process


import time

from rich.progress import Progress

def test_progressbar():

    with Progress() as progress:
        task1 = progress.add_task("[red]Downloading...", total=1000)
        task2 = progress.add_task("[green]Processing...", total=1000)
        task3 = progress.add_task("[cyan]Cooking...", total=1000)
        while not progress.finished:
            progress.update(task1, advance=10.5)
            progress.update(task2, advance=10.3)
            progress.update(task3, advance=1.0)
            time.sleep(0.02)

if __name__ == '__main__':
    test_progressbar()