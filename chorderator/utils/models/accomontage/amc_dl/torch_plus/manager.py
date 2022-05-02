import datetime
import os
import shutil
#from tensorboardX import SummaryWriter
from .train_utils import join_fn
import torch
from torch.utils.tensorboard import SummaryWriter



#todo copy every import file as readme


class LogPathManager:

    def __init__(self, readme_fn=None, log_path_name='result',
                 with_date=True, with_time=True,
                 writer_folder='writers', model_folder='models'):
        date = str(datetime.date.today()) if with_date else ''
        ctime = datetime.datetime.now().time().strftime("%H%M%S") \
            if with_time else ''
        log_folder = '_'.join([log_path_name, date, ctime])
        log_path = os.path.join('', log_folder)
        writer_path = os.path.join(log_path, writer_folder)
        model_path = os.path.join(log_path, model_folder)
        self.log_path = log_path
        self.writer_path = writer_path
        self.model_path = model_path
        LogPathManager.create_path(log_path)
        LogPathManager.create_path(writer_path)
        LogPathManager.create_path(model_path)
        if readme_fn is not None:
            shutil.copyfile(readme_fn, os.path.join(log_path, 'readme.txt'))

    @staticmethod
    def create_path(path):
        if not os.path.exists(path):
            os.mkdir(path)

    def epoch_model_path(self, model_name):
        model_fn = join_fn(model_name, 'epoch', ext='pt')
        return os.path.join(self.model_path, model_fn)

    def valid_model_path(self, model_name):
        model_fn = join_fn(model_name, 'valid', ext='pt')
        return os.path.join(self.model_path, model_fn)

    def final_model_path(self, model_name):
        model_fn = join_fn(model_name, 'final', ext='pt')
        return os.path.join(self.model_path, model_fn)


class DataLoaders:

    def __init__(self, train_loader, val_loader, bs_train, bs_val, device=None):
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.num_train_batch = len(train_loader)
        self.num_val_batch = len(val_loader)
        self.bs_train = bs_train
        self.bs_val = bs_val
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available()
                                  else 'cpu')
        self.device = device

    @staticmethod
    def get_loaders(seed, bs_train, bs_val,
                    portion=8, shift_low=-6, shift_high=5, num_bar=2,
                    contain_chord=True):
        raise NotImplementedError

    def batch_to_inputs(self, *input):
        raise NotImplementedError

    @staticmethod
    def _get_ith_batch(i, loader):
        assert 0 <= 0 < len(loader)
        for ind, batch in enumerate(loader):
            if i == ind:
                break
        return batch

    def get_ith_train_batch(self, i):
        return DataLoaders._get_ith_batch(i, self.train_loader)

    def get_ith_val_batch(self, i):
        return DataLoaders._get_ith_batch(i, self.val_loader)


class SummaryWriters:

    def __init__(self, writer_names, tags, log_path, tasks=('train', 'val')):
        # writer_names example: ['loss', 'kl_loss', 'recon_loss']
        # tags example: {'name1': None, 'name2': (0, 1)}
        self.log_path = log_path
        assert 'loss' == writer_names[0]
        self.writer_names = writer_names
        self.tags = tags
        self._regularize_tags()

        writer_dic = {}
        for name in writer_names:
            writer_dic[name] = SummaryWriter(os.path.join(log_path, name))
        self.writers = writer_dic

        all_tags = {}
        for task in tasks:
            task_dic = {}
            for key, val in self.tags.items():
                task_dic['_'.join([task, key])] = val
            all_tags[task] = task_dic
        self.all_tags = all_tags

    def _init_summary_writer(self):
        tags = {'batch_train': (0, 1, 2, 3, 4)}
        self.summary_writers = SummaryWriters(self.writer_names, tags,
                                              self.writer_path)

    def _regularize_tags(self):
        for key, val in self.tags.items():
            if val is None:
                self.tags[key] = tuple(range(len(self.writer_names)))

    def single_write(self, name, tag, val, step):
        self.writers[name].add_scalar(tag, val, step)

    def write_tag(self, task, tag, vals, step):
        assert len(vals) == len(self.all_tags[task][tag])
        for name_id, val in zip(self.all_tags[task][tag], vals):
            name = self.writer_names[name_id]
            self.single_write(name, tag, val, step)

    def write_task(self, task, vals_dic, step):
        for tag, name_ids in self.all_tags[task].items():
            vals = [vals_dic[self.writer_names[i]] for i in name_ids]
            self.write_tag(task, tag, vals, step)