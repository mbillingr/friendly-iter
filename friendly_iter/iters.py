import time
from multiprocessing import Process, Queue
from multiprocessing.queues import Empty


class Iterator:
    def __init__(self, iterable):
        self.iter = iter(iterable)

    def fork(self):
        return ParallelIterator(self.iter)

    def map(self, func):
        self.iter = map(func, self.iter)

    def filter(self, func):
        self.iter = filter(func, self.iter)

    def flatten(self):
        self.iter = flatten(self.iter)

    def __iter__(self):
        return self.iter


class ParallelIterator:
    def __init__(self, iterable):
        self.input_iter = iter(iterable)
        self.pipeline = PipelineBuilder()

    def map(self, func):
        self.pipeline.transform(map, func)
        return self

    def filter(self, func):
        self.pipeline.transform(filter, func)
        return self

    def flatten(self):
        self.pipeline.transform(flatten)
        return self

    def join(self, n_jobs=4):
        return Iterator(self._join(n_jobs))

    def _join(self, n_jobs):
        iterator = self.input_iter

        distributor = Queue()
        collector = Queue()

        workers = [Process(target=worker,
                           args=(self.pipeline, distributor, collector, i)) for
                   i in range(n_jobs)]

        active_workers = n_jobs
        for w in workers:
            w.start()

        def get():
            nonlocal active_workers
            while active_workers > 0:
                y = collector.get()
                if y == DONE_WORKER:
                    active_workers -= 1
                else:
                    yield y

        buffer_size = n_jobs * 2
        for x in iterator:
            while distributor.qsize() >= buffer_size:
                try:
                    y = collector.get(timeout=0.1)
                    yield y
                except Empty:
                    pass
            distributor.put(x)

        for w in workers:
            distributor.put(STOP_WORKER)

        for w in workers:
            w.join()

        for y in get():
            yield y


def worker(pipeline, distributor, collector, i):
    def get():
        x = None
        while True:
            x = distributor.get()
            if x == STOP_WORKER:
                return
            yield x

    for x in pipeline.build(get()):
        collector.put(x)
    collector.put(DONE_WORKER)


STOP_WORKER = b'STOP'
DONE_WORKER = b'DONE'


class PipelineBuilder:
    def __init__(self):
        self.transformers = []

    def transform(self, func, *args):
        self.transformers.append((func, args))

    def build(self, input_iter):
        it = input_iter
        for func, args in self.transformers:
            it = func(*args, it)
        return it


def flatten(iterator):
    for inner in iterator:
        yield from inner


if __name__ == '__main__':
    def delay(x):
        time.sleep(0.1)
        return x


    def listify(x):
        return [x + 10, x + 20, x + 30]


    def is_negative(x):
        return x < 0


    # it works when we produce less output than input
    start = time.time()
    it = Iterator(range(10))
    it.map(delay)
    it.filter(is_negative)

    print(list(it))
    print('duration:', time.time() - start)

    # it works when we produce more output than input
    start = time.time()
    it = Iterator(range(10))
    it.map(listify)
    it.map(delay)
    it.flatten()

    print(list(it))
    print('duration:', time.time() - start)

    # and it's faster in parallel

    # it works when we produce less output than input
    start = time.time()
    it = Iterator(range(10))
    it = it.fork()
    it.map(delay)
    # it.map(lambda x: x ** 2)
    it.filter(is_negative)
    it = it.join()

    print(list(it))
    print('duration:', time.time() - start)

    # it works when we produce more output than input
    start = time.time()
    it = Iterator(range(10))
    it = it.fork()
    it.map(listify)
    it.map(delay)
    it.flatten()
    it = it.join()

    print(list(it))
    print('duration:', time.time() - start)
