class Config(object):
    def __init__(self):
        self.chia_exec = '/usr/lib/chia-blockchain/resources/app.asar.unpacked/daemon/chia'
        self.thread_number = 2
        self.max_thread_num = 6
        self.delay_minute = 15
        self.k = 32
        self.bucket = 128
        self.memory = 4000.0
        self.log_path = 'outputs/'
        self.end_1 = 799
        self.end_2 = 833
        self.end_3 = 2472
        self.end_4 = 2624
        self.cpu_affinity = True
        self.max_parallel_num = 6
