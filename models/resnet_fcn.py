"""Resnet Fully Connected Network"""

import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

class ResNetFCN(nn.Module):

    def __init__(self, dataset, pretrained):
        super(ResNetFCN, self).__init__()
        
        self.n_classes = len(dataset.classes)
        # If only two classes, configure
        # for binary cross entropy
        if self.n_classes == 2:
            self.n_classes = 1

        # Retrieve pretrained resnet
        model = models.resnet101(pretrained=pretrained)

        # Remove last two layers (avg_pool and fc) of ResNet
        self.features = nn.Sequential(*list(model.children())[:-2])

        # Create new classification layer
        n_features = model.layer4[1].conv1.in_channels
        self.classifier = nn.Sequential(
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1,1)),
            nn.Conv2d(n_features, self.n_classes, kernel_size=1))

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x).squeeze()
        return x
