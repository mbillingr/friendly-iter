from multiprocessing import Process, Queue
from multiprocessing.queues import Empty

DEFAULT_NUMBER_OF_WORKERS = 4


class Iterator:
    def __init__(self, iterable):
        self.iter = iter(iterable)

    def fork(self, n_jobs=DEFAULT_NUMBER_OF_WORKERS):
        return ParallelIterator(self.iter, n_jobs=n_jobs)

    def map(self, func):
        self.iter = map(func, self.iter)

    def filter(self, func):
        self.iter = filter(func, self.iter)

    def flatten(self):
        self.iter = flatten(self.iter)

    def __iter__(self):
        return self.iter


class ParallelIterator:
    def __init__(self, iterable, n_jobs=DEFAULT_NUMBER_OF_WORKERS):
        self.n_jobs = n_jobs
        self.input_iter = iter(iterable)
        self.pipeline = IteratorPipeline()

    def map(self, func):
        self.pipeline.add_transform(map, func)
        return self

    def filter(self, func):
        self.pipeline.add_transform(filter, func)
        return self

    def flatten(self):
        self.pipeline.add_transform(flatten)
        return self

    def join(self):
        wc = WorkCoordinator(n_workers=self.n_jobs)
        output_iter = wc.run(self.input_iter, self.pipeline)
        return Iterator(output_iter)


class WorkCoordinator:
    def __init__(self, n_workers, input_buffer_size=None, result_poll_interval=0.1):
        self.distributor = Queue()
        self.collector = Queue()
        self.n_workers = n_workers
        self.input_buffer_size = input_buffer_size or n_workers * 2
        self.poll_interval = result_poll_interval
        self.workers = []
        self.active_workers = 0

    def run(self, input_iter, pipeline):
        self.start_workers(pipeline)
        yield from self.balance_inputs_and_outputs(input_iter)
        self.stop_workers()
        yield from self.remaining_results()

    def start_workers(self, pipeline):
        self.active_workers = self.n_workers
        self.workers = [Process(target=worker, args=(pipeline, self.distributor, self.collector, i)) for i in
                        range(self.n_workers)]
        for w in self.workers:
            w.start()

    def stop_workers(self):
        for _ in self.workers:
            self.distributor.put(STOP_WORKER)
        for w in self.workers:
            w.join()

    def balance_inputs_and_outputs(self, input_iter):
        for x in input_iter:
            while self.input_queue_is_full():
                yield from self.try_get_result()
            self.distributor.put(x)

    def input_queue_is_full(self):
        return self.distributor.qsize() >= self.input_buffer_size

    def try_get_result(self):
        try:
            y = self.collector.get(timeout=self.poll_interval)
            yield y
        except Empty:
            pass

    def remaining_results(self):
        while self.active_workers > 0:
            y = self.collector.get()
            if y == DONE_WORKER:
                self.active_workers -= 1
            else:
                yield y


def worker(pipeline, distributor, collector, i):
    def get():
        while True:
            x = distributor.get()
            if x == STOP_WORKER:
                return
            yield x

    for x in pipeline.apply(get()):
        collector.put(x)
    collector.put(DONE_WORKER)


STOP_WORKER = b'STOP'
DONE_WORKER = b'DONE'


class IteratorPipeline:
    def __init__(self):
        self.transformers = []

    def add_transform(self, func, *args):
        self.transformers.append((func, args))

    def apply(self, input_iter):
        it = input_iter
        for func, args in self.transformers:
            it = func(*args, it)
        return it


def flatten(iterator):
    for inner in iterator:
        yield from inner
