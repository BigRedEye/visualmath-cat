import cat
import numpy
import random
import math
from multiprocessing import Pool


def random_float():
    return numpy.random.uniform()


def random_prob(prob: float):
    return random_float() < prob


delta = 0
count = 0
stdev = 0


def worker(arg):
    tests = [i / 1000 for i in range(1, 1000)]
    db = cat.DataBase(tests)
    test = cat.Test(db, 10)
    examinee = cat.Examinee()

    real_theta = numpy.random.normal()

    # print('Theta: ', examinee._theta)
    # print('Real score: ', 10 - 10 / (1 + math.exp(real_theta)))

    tt = 0
    while True:
        t = test.select_task(examinee)
        if t is None:
            break
        # print('Your score is ', examinee.score() * 10)
        # print(f'test: {t}, difficulty: {tests[t]}')
        beta = math.log((1 - tests[t]) / tests[t])
        prob = 1 / (1 + math.exp(beta - real_theta))
        res = random_prob(prob)
        # print(f'prob = {prob}, res = {res}')
        # res = input('Enter result: 1 for correct answer, 0 for incorrect. $> ') == '1'
        test.add_answer(examinee, t, res)
        tt += 1

    score = examinee.score() * 10
    real_score = 10 - 10 / (1 + math.exp(real_theta))
    # print('Done! Your score is ', score)
    # print('Real score: ', real_score)
    delta = real_score - score
    return delta


def callback(dl):
    d = dl[0]
    global delta
    global count
    global stdev
    print("Delta: {}" % d)
    delta += d
    count += 1
    stdev += d ** 2


if __name__ == "__main__":
    delta = 0
    count = 0
    stdev = 0
    with Pool(12) as p:
        res = p.imap(worker, range(1000))
        for i in res:
            print("Delta:", i)
            delta += i
            count += 1
            stdev += i ** 2

    print("Average delta: ", delta / count)
    print("Stdev: ", stdev / count)
