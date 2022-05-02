import time
import os
import torch
from torch import nn
from .train_utils import epoch_time


class PytorchModel(nn.Module):

    def __init__(self, name, device):
        self.name = name
        super(PytorchModel, self).__init__()
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available()
                                  else 'cpu')
        self.device = device

    def run(self, *input):
        """A general way to run the model.
        Usually tensor input -> tensor output"""
        raise NotImplementedError

    def loss(self, *input, **kwargs):
        """Call it during training. The output is loss and possibly others to
        display on tensorboard."""
        raise NotImplementedError

    def inference(self, *input):
        """Call it during inference.
        The output is usually numpy after argmax."""
        raise NotImplementedError

    def loss_function(self, *input):
        raise NotImplementedError

    def forward(self, mode, *input, **kwargs):
        if mode in ["run", 0]:
            return self.run(*input, **kwargs)
        elif mode in ['loss', 'train', 1]:
            return self.loss(*input, **kwargs)
        elif mode in ['inference', 'eval', 'val', 2]:
            return self.inference(*input, **kwargs)
        else:
            raise NotImplementedError

    def load_model(self, model_path, map_location=None):
        if map_location is None:
            map_location = self.device
        dic = torch.load(model_path, map_location=map_location)
        for name in list(dic.keys()):
            dic[name.replace('module.', '')] = dic.pop(name)
        self.load_state_dict(dic)
        self.to(self.device)

    @staticmethod
    def init_model(*inputs):
        raise NotImplementedError


class TrainingInterface:

    def __init__(self, device, model, parallel, log_path_mng, data_loaders,
                 summary_writers,
                 opt_scheduler, param_scheduler, n_epoch, **kwargs):
        self.model = model
        self.model.device = device
        if parallel:
            self.model = nn.DataParallel(self.model)
        self.model.to(device)
        self.path_mng = log_path_mng
        self.summary_writers = summary_writers
        self.data_loaders = data_loaders
        self.opt_scheduler = opt_scheduler
        self.param_scheduler = param_scheduler
        self.device = device
        self.n_epoch = n_epoch
        self.epoch = 0
        self.train_step = 0
        self.val_step = 0
        self.parallel = parallel
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def name(self):
        if self.parallel:
            return self.model.module.name
        else:
            return self.model.name

    @property
    def log_path(self):
        return self.path_mng.log_path

    @property
    def model_path(self):
        return self.path_mng.model_path

    @property
    def writer_path(self):
        return self.path_mng.writer_path

    @property
    def writer_names(self):
        return self.summary_writers.writer_names

    def _init_loss_dic(self):
        loss_dic = {}
        for key in self.writer_names:
            loss_dic[key] = 0.
        return loss_dic

    def _accumulate_loss_dic(self, loss_dic, loss_items):
        assert len(self.writer_names) == len(loss_items)
        for key, val in zip(self.writer_names, loss_items):
            loss_dic[key] += val.item()
        return loss_dic

    def _write_loss_to_dic(self, loss_items):
        loss_dic = {}
        assert len(self.writer_names) == len(loss_items)
        for key, val in zip(self.writer_names, loss_items):
            loss_dic[key] = val.item()
        return loss_dic

    def _batch_to_inputs(self, batch):
        raise NotImplementedError

    def train(self, **kwargs):
        self.model.train()
        self.param_scheduler.train()
        epoch_loss_dic = self._init_loss_dic()

        for i, batch in enumerate(self.data_loaders.train_loader):
            #print(len(batch))
            inputs = self._batch_to_inputs(batch)
            #print(type(input))
            self.opt_scheduler.optimizer_zero_grad()
            input_params = self.param_scheduler.step()
            #print(input_params.keys())
            outputs = self.model('train', *inputs, **input_params)
            outputs = self._sum_parallel_loss(outputs)
            loss = outputs[0]
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(),
                                           self.opt_scheduler.clip)
            self.opt_scheduler.step()
            self._accumulate_loss_dic(epoch_loss_dic, outputs)
            batch_loss_dic = self._write_loss_to_dic(outputs)
            self.summary_writers.write_task('train', batch_loss_dic,
                                            self.train_step)
            self.train_step += 1
        return epoch_loss_dic

    def _sum_parallel_loss(self, loss):
        if self.parallel:
            if isinstance(loss, tuple):
                return tuple([x.mean() for x in loss])
            else:
                return loss.mean()
        else:
            return loss

    def eval(self):
        self.model.eval()
        self.param_scheduler.eval()
        epoch_loss_dic = self._init_loss_dic()

        for i, batch in enumerate(self.data_loaders.val_loader):
            inputs = self._batch_to_inputs(batch)
            input_params = self.param_scheduler.step()
            with torch.no_grad():
                outputs = self.model('train', *inputs, **input_params)
                outputs = self._sum_parallel_loss(outputs)
            self._accumulate_loss_dic(epoch_loss_dic, outputs)
            batch_loss_dic = self._write_loss_to_dic(outputs)
            self.summary_writers.write_task('val', batch_loss_dic,
                                            self.val_step)
            self.val_step += 1
        return epoch_loss_dic

    def save_model(self, fn):
        if self.parallel:
            torch.save(self.model.module.state_dict(), fn)
        else:
            torch.save(self.model.state_dict(), fn)

    def epoch_report(self, start_time, end_time, train_loss, valid_loss):
        epoch_mins, epoch_secs = epoch_time(start_time, end_time)
        print(f'Epoch: {self.epoch + 1:02} | '
              f'Time: {epoch_mins}m {epoch_secs}s',
              flush=True)
        print(
            f'\tTrain Loss: {train_loss:.3f}', flush=True)
        print(
            f'\t Valid. Loss: {valid_loss:.3f}', flush=True)

    def run(self, start_epoch=0, start_train_step=0, start_val_step=0):
        self.epoch = start_epoch
        self.train_step = start_train_step
        self.val_step = start_val_step
        best_valid_loss = float('inf')

        for i in range(self.n_epoch):
            start_time = time.time()
            train_loss = self.train()['loss']
            val_loss = self.eval()['loss']
            end_time = time.time()
            self.save_model(self.path_mng.epoch_model_path(self.name))
            if val_loss < best_valid_loss:
                best_valid_loss = val_loss
                self.save_model(self.path_mng.valid_model_path(self.name))
            self.epoch_report(start_time, end_time, train_loss, val_loss)
            self.epoch += 1
        self.save_model(self.path_mng.final_model_path(self.name))
        print('Model saved.')




