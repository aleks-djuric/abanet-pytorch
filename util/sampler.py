import torch
import torch.utils.data
import torchvision


class ImbalancedDatasetSampler(torch.utils.data.sampler.Sampler):
    """Samples elements randomly from a given list of indices for imbalanced dataset
    Arguments:
        indices (list, optional): a list of indices
        num_samples (int, optional): number of samples to draw
    """

    def __init__(self, dataset, indices=None, num_samples=None):

        # if indices is not provided,
        # all elements in the dataset will be considered
        self.indices = list(range(len(dataset))) \
            if indices is None else indices

        # if num_samples is not provided,
        # draw `len(indices)` samples in each iteration
        self.num_samples = len(self.indices) \
            if num_samples is None else num_samples

        # distribution of classes in the dataset
        label_to_count = {}
        for idx in self.indices:
            label = self._get_label(dataset, idx)
            if label in label_to_count:
                label_to_count[label] += 1
            else:
                label_to_count[label] = 1

        # weight for each sample
        weights = [1.0 / label_to_count[self._get_label(dataset, idx)]
                   for idx in self.indices]
        self.weights = torch.DoubleTensor(weights)

    def _get_label(self, dataset, idx):
        return dataset.samples[idx][1]

    def __iter__(self):
        return (self.indices[i] for i in torch.multinomial(
            self.weights, self.num_samples, replacement=True))

    def __len__(self):
        return self.num_samples


class ImbalancedDatasetSamplerBackground(torch.utils.data.sampler.Sampler):
    """Samples an equal number of training examples from each class. If
    backgnd_samp_prob param is provided, will sample background images with
    a probability of backgnd_samp_prob. Remaining classes will be sampled
    equally.

    Example:
        4 classes + backgnd = 5 classes
        backgnd_samp_prob = 0.4

        Background will be sampled with a probability of 0.4 while remaining
        classes are each sampled with a probability of (1.0-0.4)/4 = 0.15.
    """

    def __init__(self, dataset, dataset_args):
        self.n_samples = len(dataset)
        self.indices = list(range(self.n_samples))

        # Count number of samples per class
        label_to_count = {}
        for idx in self.indices:
            label = self._get_label(dataset, idx)
            if label in label_to_count:
                label_to_count[label] += 1
            else:
                label_to_count[label] = 1

        if dataset_args.backgnd_samp_prob:
            n_classes = len(dataset.classes)
            backgnd_label = dataset.classes.index('background')
            backgnd_weight = dataset_args.backgnd_samp_prob * n_classes
            foregnd_weight = (n_classes - backgnd_weight) / (n_classes - 1)
        else:
            foregnd_weight = 1.0

        weights = []
        for idx in self.indices:
            label = self._get_label(dataset, idx)
            if dataset_args.backgnd_samp_prob and label == backgnd_label:
                weights.append(backgnd_weight / label_to_count[label])
            else:
                weights.append(foregnd_weight / label_to_count[label])
        self.weights = torch.DoubleTensor(weights)

    def _get_label(self, dataset, idx):
        dataset_type = type(dataset)
        # if dataset_type is torchvision.datasets.DatasetFolder:
        #     return dataset.samples[idx][1]
        # else:
        #     raise NotImplementedError

    def __iter__(self):
        return (self.indices[i] for i in torch.multinomial(
            self.weights, self.n_samples, replacement=True))

    def __len__(self):
        return self.n_samples
