class Answer:
    """
    Examinee answer
    """

    def __init__(self, task_id: int, answer: bool):
        self._task_id = task_id
        self._answer = answer

    @property
    def task_id(self):
        return self._task_id

    @property
    def answer(self):
        return self._answer


class Examinee:
    """
    Base examinee class
    """

    def __init__(self):
        """
        Initializes new examinee
        """
        self._answered_items = []

    def add_answer(self, task_id: int, answer: bool):
        self._answered_items.append(Answer(task_id, answer))

    def score(self) -> float:
        raise NotImplementedError()

    def update_proficiency(self, theta: float):
        raise NotImplementedError()

    @property
    def answers(self):
        return self._answered_items


class Test:
    """
    Abstract base test class
    """

    def __init__(self, test_size: int):
        self._test_size = test_size

    def select_task(self, user: Examinee):
        """
        Select next task based on examinee answers
        """
        if len(user.answers) >= self._test_size:
            return None
        return self._selector(user)

    def add_answer(self, user: Examinee, task_id: int, answer: bool):
        user.add_answer(task_id, answer)
        self._update(user)

    def _selector(self, user: Examinee):
        raise NotImplementedError()

    def _update(self, user: Examinee):
        raise NotImplementedError()
