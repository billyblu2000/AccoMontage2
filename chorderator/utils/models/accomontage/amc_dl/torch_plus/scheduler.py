import numpy as np
from .train_utils import scheduled_sampling

class _Scheduler:

    def __init__(self, step=0, mode='train'):
        self._step = step
        self._mode = mode

    def _update_step(self):
        if self._mode == 'train':
            self._step += 1
        elif self._mode == 'val':
            pass
        else:
            raise NotImplementedError

    def step(self):
        raise NotImplementedError

    def train(self):
        self._mode = 'train'

    def eval(self):
        self._mode = 'val'


class ConstantScheduler(_Scheduler):

    def __init__(self, param, step=0.):
        super(ConstantScheduler, self).__init__(step)
        self.param = param

    def step(self):
        self._update_step()
        return self.param


class TeacherForcingScheduler(_Scheduler):

    def __init__(self, high, low, f=scheduled_sampling, step=0):
        super(TeacherForcingScheduler, self).__init__(step)
        self.high = high
        self.low = low
        self._step = step
        self.schedule_f = f

    def get_tfr(self):
        return self.schedule_f(self._step, self.high, self.low)

    def step(self):
        tfr = self.get_tfr()
        self._update_step()
        return tfr


class OptimizerScheduler(_Scheduler):

    def __init__(self, optimizer, scheduler, clip, step=0):
        # optimizer and scheduler are pytorch class
        super(OptimizerScheduler, self).__init__(step)
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.clip = clip

    def optimizer_zero_grad(self):
        self.optimizer.zero_grad()

    def step(self, require_zero_grad=False):
        self.optimizer.step()
        self.scheduler.step()
        if require_zero_grad:
            self.optimizer_zero_grad()
        self._update_step()


class ParameterScheduler(_Scheduler):

    def __init__(self, step=0, mode='train', **schedulers):
        # optimizer and scheduler are pytorch class
        super(ParameterScheduler, self).__init__(step)
        self.schedulers = schedulers
        self.mode = mode

    def train(self):
        self.mode = 'train'
        for scheduler in self.schedulers.values():
            scheduler.train()

    def eval(self):
        self.mode = 'val'
        for scheduler in self.schedulers.values():
            scheduler.eval()

    def step(self, require_zero_grad=False):
        params_dic = {}
        for key, scheduler in self.schedulers.items():
            params_dic[key] = scheduler.step()
        return params_dic





