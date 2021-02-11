import time

from friendly_iter import Iterator


def delay(x):
    time.sleep(0.1)
    return x


def listify(x):
    return [x + 10, x + 20, x + 30]


def is_negative(x):
    return x < 0


if __name__ == '__main__':
    class TimeIt:
        def __enter__(self):
            self.start = time.time()

        def __exit__(self, exc_type, exc_val, exc_tb):
            print('duration:', time.time() - self.start)


    # it works when we produce less output than input
    with TimeIt():
        it = Iterator(range(10))
        it.map(delay)
        it.filter(is_negative)
        print(list(it))

    # it works when we produce more output than input
    with TimeIt():
        it = Iterator(range(10))
        it.map(listify)
        it.map(delay)
        it.flatten()
        print(list(it))

    # and it's faster in parallel

    # it works when we produce less output than input
    with TimeIt():
        it = Iterator(range(10))
        it = it.fork()
        it.map(delay)
        # it.map(lambda x: x ** 2)
        it.filter(is_negative)
        it = it.join()
        print(list(it))

    # it works when we produce more output than input
    with TimeIt():
        it = Iterator(range(10))
        it = it.fork()
        it.map(listify)
        it.map(delay)
        it.flatten()
        it = it.join()
        print(list(it))
