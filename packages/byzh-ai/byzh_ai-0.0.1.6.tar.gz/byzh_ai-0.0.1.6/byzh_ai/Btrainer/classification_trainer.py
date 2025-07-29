import os
import time
from pathlib import Path
from typing import Literal

import pandas as pd
import copy
import torch
from torch import nn
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix

from byzh_core.Btqdm import B_Tqdm
from byzh_core.Bwriter import B_Writer
from byzh_core.Bbasic import B_Color, B_Appearance

from ..Bearly_stop import *
from ..Butils import b_get_device, b_get_gpu_nvidia

from .trainer import B_Trainer

class B_Classification_Trainer(B_Trainer):

    def calculate_model(self, dataloader=None, model=None, inputs_func=None, outputs_func=None, labels_func=None):
        '''
        如果不指定, 则用类内的
        :param dataloader: 默认self.val_loader
        :param model: 默认self.model
        :return: accuracy, f1_score, confusion_matrix, inference_time, params
        '''
        if dataloader==None:
            dataloader = self.val_loader
        if model==None:
            model = self.model
        model.eval()

        if inputs_func is not None:
            assert callable(inputs_func), "inputs_func必须为可调用对象"
            self.inputs_func = inputs_func
        if outputs_func is not None:
            assert callable(outputs_func), "outputs_func必须为可调用对象"
            self.outputs_func = outputs_func
        if labels_func is not None:
            assert callable(labels_func), "labels_func必须为可调用对象"
            self.labels_func = labels_func

        correct = 0
        total = 0
        y_true = []
        y_pred = []
        inference_time = []
        with torch.no_grad():
            for inputs, labels in dataloader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                labels = self.labels_func(labels)
                inputs = self.inputs_func(inputs)
                start_time = time.time()
                outputs = model(inputs)
                end_time = time.time()
                outputs = self.outputs_func(outputs)

                _, predicted = torch.max(outputs, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                y_true.extend(labels.cpu().numpy())
                y_pred.extend(predicted.cpu().numpy())
                inference_time.append(end_time - start_time)

                self._spikingjelly_process()
        # 平均推理时间
        inference_time = sum(inference_time) / len(inference_time)
        # acc & f1 & cm
        accuracy = correct / total
        f1_score = self.get_f1_score(y_true, y_pred)
        confusion_matrix = self.get_confusion_matrix(y_true, y_pred)
        # 参数量
        params = sum(p.numel() for p in model.parameters())

        info = f'[calc] accuracy: {accuracy:.3f}, f1_score: {f1_score:.3f}'
        self._print_and_toWriter(info)
        info = f'------ inference_time: {inference_time:.2e}s, params: {params / 1e3}K'
        self._print_and_toWriter(info)

        return accuracy, f1_score, confusion_matrix, inference_time, params


