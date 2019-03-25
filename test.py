import cat
import numpy
import random
import math
from multiprocessing import Pool


def random_float():
    return numpy.random.uniform()


def random_prob(prob: float):
    return random_float() < prob


def worker(arg):
    tests = [i / 1000 for i in range(1, 1000)]
    db = cat.DataBase(tests)
    test = cat.Test(db, 10)
    examinee = cat.Examinee()

    real_theta = numpy.random.normal()

    while True:
        t = test.select_task(examinee)
        if t is None:
            break
        beta = math.log((1 - tests[t]) / tests[t])
        prob = 1 / (1 + math.exp(beta - real_theta))
        res = random_prob(prob)
        test.add_answer(examinee, t, res)

    score = examinee.score() * 10
    real_score = 10 - 10 / (1 + math.exp(real_theta))
    delta = real_score - score
    return delta


if __name__ == "__main__":
    delta = 0
    count = 0
    variance = 0
    with Pool(12) as p:
        res = p.imap(worker, range(1000))
        for i in res:
            print("Delta:", i)
            delta += i
            count += 1
            variance += i ** 2

    print("Average delta: ", delta / count)
    print("Stdev: ", math.sqrt(variance / count - 1))
