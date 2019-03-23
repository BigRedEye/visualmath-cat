import math
import heapq
import types
import random
import scipy.optimize
import numpy as np


def proportion_correct_beta(proportion: float):
    """
    Return item difficulty based on proportion of correct answers
    Based on the following article, this method gives a fairly high correlation with
    real beta value.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.489.86&rep=rep1&type=pdf

    Parameters:
    proportion -- number of correct answers,
        divided by the number of students who answered the question.

    Based on
    """
    return math.log((1 - proportion) / proportion)


class Item:
    """
    Task with specified difficulty (beta parameter).
    Uses 1-PL (Rasch) IRT model.

    Parameters:
    task -- unique task id
    proportion -- number of correct answers,
        divided by the number of students who answered the question.
    """

    def __init__(self, task: int, proportion: float):
        self._task = task
        self._beta = proportion_correct_beta(proportion)

    @property
    def beta(self) -> float:
        """Return item difficulty"""
        return self._beta

    @property
    def task(self) -> int:
        """Return task id"""
        return self._task


class ExamineeProficiency:
    """
    Examinee proficiency level
    Examinee with profficency level \theta solves task with difficulty \beta
        with probability \frac{\exp{\theta - \beta}}{1 + \exp{\theta - \beta}}
    """

    def __init__(self):
        """
        Initializes proficiency with random standard normal distributed value.
        """
        self._theta = np.random.normal()

    @property
    def theta(self) -> float:
        """Return proficiency level"""
        return self._theta

    def set(self, theta: float):
        self._theta = theta


class Examinee(types.Examinee):
    """
    Holds examinee answers
    """

    def __init__(self):
        """
        Initializes new examinee
        """
        super().__init__()
        self._proficiency = ExamineeProficiency()

    def update_proficiency(self, theta: float):
        """
        Update proficiency
        """
        self._proficiency.set(theta)

    def score(self) -> float:
        """
        Return examinee score in range [0, 1].
        """
        return 1 - 1 / (1 + math.exp(self._theta))

    @property
    def _theta(self) -> float:
        """
        Return estimated examinee proficency coefficient
        """
        return self._proficiency.theta


class DataBase:
    """
    Holds all available questions for test
    """

    def __init__(self, tasks: list = None):
        """
        Initializes database
        """
        self._tasks = []
        if tasks:
            self.load_tasks(tasks)

    def load_tasks(self, tasks):
        """
        Loads database from array of tasks.

        Parameters:
        tasks -- array of item difficulties
        """
        unsorted = []
        for i, prop in enumerate(tasks):
            unsorted.append(Item(task=i, proportion=prop))
        self._tasks = sorted(unsorted, key=lambda x: x.beta)
        self._task_by_id = {x.task: x for x in unsorted}

    def bounds(self) -> tuple:
        """
        Return theta bounds
        """
        return (self._tasks[0].beta * 2, self._tasks[-1].beta * 2)

    @property
    def tasks(self):
        return self._tasks

    def task_by_id(self, task_id):
        return self._task_by_id[task_id]


def solving_probability(theta, beta):
    """
    Return probablity of correct answer

    Parameters:
    theta -- examinee prficiency
    beta -- task difficulty
    """
    return 1 / (1 + math.exp(beta - theta))


def log_likelihood(theta, *args):
    db = args[0]
    answers = args[1]

    sum = 0
    for ans in answers:
        prob = solving_probability(theta, db.task_by_id(ans.task_id).beta)
        if ans.answer:
            sum += math.log(prob)
        else:
            sum += math.log(1 - prob)
    return sum


def neg_log_likelihood(x, *args):
    return -log_likelihood(x, *args)


def info(theta, beta):
    prob = solving_probability(theta, beta)
    return prob * (1 - prob)


class Test(types.Test):
    """
    IRT-based computer adaptive test
    """

    def __init__(self, db: DataBase, test_size: int, selection_size: int = 5):
        super().__init__(test_size)
        self._db = db
        self._selection_size = selection_size

    def _update(self, user: types.Examinee):
        theta = scipy.optimize.differential_evolution(
            neg_log_likelihood,
            bounds=[self._db.bounds()],
            args=(self._db, user.answers),
        ).x[0]
        user.update_proficiency(theta)

    def _selector(self, user: types.Examinee):
        unvisited_items = []
        visited = {x.task_id for x in user.answers}

        heap = []
        not_visited = filter(lambda x: x.task not in visited, self._db.tasks)
        for i in not_visited:
            element = (info(user._theta, i.beta), i.task)
            if len(heap) < self._selection_size:
                heapq.heappush(heap, element)
            else:
                heapq.heappushpop(heap, element)
        if len(heap):
            return heap[random.randrange(len(heap))][1]
        else:
            return None
