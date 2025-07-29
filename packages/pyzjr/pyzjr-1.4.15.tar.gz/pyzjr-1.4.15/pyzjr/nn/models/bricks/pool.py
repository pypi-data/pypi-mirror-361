"""
Copyright (c) 2024, Auorui.
All rights reserved.

The Torch implementation of average pooling and maximum pooling has been compared with the official Torch implementation
Time: 2024-01-22  17:28
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from pyzjr.data.utils.tuplefun import to_2tuple, to_4tuple

class MaxPool2d(nn.Module):
    """
    定义MaxPool2d类，结合了普通池化和矢量化池化的功能
    池化层计算公式:
        output_size = [(input_size−kernel_size) // stride + 1]
    """
    def __init__(self, kernel_size, stride, is_vectoring=True):
        super(MaxPool2d, self).__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.is_vectoring = is_vectoring

    def max_pool2d_traditional(self, input_tensor):
        batch_size, channels, height, width = input_tensor.size()
        output_height = (height - self.kernel_size) // self.stride + 1
        output_width = (width - self.kernel_size) // self.stride + 1
        output_tensor = torch.zeros(batch_size, channels, output_height, output_width)

        for i in range(output_height):
            for j in range(output_width):
                window = input_tensor[:, :,
                         i * self.stride: i * self.stride + self.kernel_size, j * self.stride: j * self.stride + self.kernel_size]
                output_tensor[:, :, i, j] = torch.max(window.reshape(batch_size, channels, -1), dim=2)[0]
        return output_tensor

    def max_pool2d_vectorized(self, input_tensor):
        unfolded = input_tensor.unfold(2, self.kernel_size, self.stride).unfold(3, self.kernel_size, self.stride)
        max_values, _ = unfolded.max(dim=-1)
        max_values, _ = max_values.max(dim=-1)
        return max_values

    def forward(self, input_tensor):
        if self.is_vectoring:
            return self.max_pool2d_vectorized(input_tensor)
        else:
            return self.max_pool2d_traditional(input_tensor)


class AvgPool2d(nn.Module):
    """
    定义AvgPool2d类，结合了普通池化和矢量化池化的功能
    池化层计算公式:
        output_size = [(input_size−kernel_size) // stride + 1]
    """
    def __init__(self, kernel_size, stride, is_vectoring=True):
        super(AvgPool2d, self).__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.is_vectoring = is_vectoring

    def avg_pool2d_traditional(self, input_tensor):
        batch_size, channels, height, width = input_tensor.size()
        output_height = (height - self.kernel_size) // self.stride + 1
        output_width = (width - self.kernel_size) // self.stride + 1
        output_tensor = torch.zeros(batch_size, channels, output_height, output_width)

        for i in range(output_height):
            for j in range(output_width):
                window = input_tensor[:, :,
                         i * self.stride: i * self.stride + self.kernel_size, j * self.stride: j * self.stride + self.kernel_size]
                output_tensor[:, :, i, j] = torch.mean(window.reshape(batch_size, channels, -1), dim=2)
        return output_tensor

    def avg_pool2d_vectorized(self, input_tensor):
        unfolded = input_tensor.unfold(2, self.kernel_size, self.stride).unfold(3, self.kernel_size, self.stride)
        avg_values = unfolded.mean(dim=-1)
        avg_values = avg_values.mean(dim=-1)
        return avg_values

    def forward(self, input_tensor):
        if self.is_vectoring:
            return self.avg_pool2d_vectorized(input_tensor)
        else:
            return self.avg_pool2d_traditional(input_tensor)

class StridedPool2d(nn.Module):
    """
    实现一个跨步卷积层Strided Convolution, 本质上可以实现类似于池化操作的效果。
    通过步幅stride大于 1 的卷积操作来实现空间分辨率的降低。
    """
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=2, is_relu=True):
        super(StridedPool2d, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=1)
        self.relu = nn.ReLU(inplace=True)
        self.is_relu = is_relu

    def forward(self, x):
        x = self.conv(x)
        if self.is_relu:
            x = self.relu(x)
        return x

class MedianPool2d(nn.Module):
    """ Median pool (usable as median filter when stride=1) module.
    Hacked together by / Copyright 2020 Ross Wightman
    Currently, it is rarely used in CNN, and the code is taken
    from the project pytorch-image-models

    Args:
         kernel_size: size of pooling kernel, int or 2-tuple
         stride: pool stride, int or 2-tuple
         padding: pool padding, int or 4-tuple (l, r, t, b) as in pytorch F.pad
         same: override padding and enforce same padding, boolean
    """

    def __init__(self, kernel_size=3, stride=1, padding=0, same=False):
        super(MedianPool2d, self).__init__()
        self.k = to_2tuple(kernel_size)
        self.stride = to_2tuple(stride)
        self.padding = to_4tuple(padding)  # convert to l, r, t, b
        self.same = same

    def _padding(self, x):
        if self.same:
            ih, iw = x.size()[2:]
            if ih % self.stride[0] == 0:
                ph = max(self.k[0] - self.stride[0], 0)
            else:
                ph = max(self.k[0] - (ih % self.stride[0]), 0)
            if iw % self.stride[1] == 0:
                pw = max(self.k[1] - self.stride[1], 0)
            else:
                pw = max(self.k[1] - (iw % self.stride[1]), 0)
            pl = pw // 2
            pr = pw - pl
            pt = ph // 2
            pb = ph - pt
            padding = (pl, pr, pt, pb)
        else:
            padding = self.padding
        return padding

    def forward(self, x):
        x = F.pad(x, self._padding(x), mode='reflect')
        x = x.unfold(2, self.k[0], self.stride[0]).unfold(3, self.k[1], self.stride[1])
        x = x.contiguous().view(x.size()[:4] + (-1,)).median(dim=-1)[0]
        return x


def adaptive_pool2d(input_tensor, output_size, pool_type='max'):
    """
    两种选择型自适应池化，'max' 和 'avg'

    Args:
        - input_tensor: 输入张量
        - output_size: 输出尺寸
        - pool_type: 池化类型，可以是 'max' 或 'avg'

    Returns:
        - output_tensor: 池化后的张量
    """
    if pool_type == 'max':
        pool_func = F.adaptive_max_pool2d
    elif pool_type == 'avg':
        pool_func = F.adaptive_avg_pool2d
    else:
        raise ValueError("Unsupported pooling type. Use 'max' or 'avg'.")

    output_tensor = pool_func(input_tensor, output_size)
    return output_tensor

def adaptive_avgmax_pool2d(x, output_size):
    """
    两种选择型自适应池化，'max' 和 'avg'的平均值

    Args:
        - x: 输入张量
        - output_size: 输出尺寸

    Returns:
        - 池化后的张量的平均值
    """
    x_avg = F.adaptive_avg_pool2d(x, output_size)
    x_max = F.adaptive_max_pool2d(x, output_size)
    return 0.5 * (x_avg + x_max)

def adaptive_catavgmax_pool2d(x, output_size):
    """
    两种选择型自适应池化，'max' 和 'avg'的cat连接

    Args:
        - x: 输入张量
        - output_size: 输出尺寸

    Returns:
        - 连接池化后的张量
    """
    x_avg = F.adaptive_avg_pool2d(x, output_size)
    x_max = F.adaptive_max_pool2d(x, output_size)
    return torch.cat((x_avg, x_max), dim=1)

class AdaptiveAvgMaxPool2d(nn.Module):
    """
    自适应平均最大池化的PyTorch模块

    Args:
        - output_size: 输出尺寸
    """
    def __init__(self, output_size=1):
        super(AdaptiveAvgMaxPool2d, self).__init__()
        self.output_size = output_size

    def forward(self, x):
        return adaptive_avgmax_pool2d(x, self.output_size)

class AdaptiveCatAvgMaxPool2d(nn.Module):
    """
    自适应连接平均最大池化的PyTorch模块

    Args:
        - output_size: 输出尺寸
    """
    def __init__(self, output_size=1):
        super(AdaptiveCatAvgMaxPool2d, self).__init__()
        self.output_size = output_size

    def forward(self, x):
        return adaptive_catavgmax_pool2d(x, self.output_size)

class FastAdaptiveAvgPool2d(nn.Module):
    """
    自定义的自适应平均池化层

    Args:
        - flatten: 是否对结果进行扁平化
    """
    def __init__(self, flatten=False):
        super(FastAdaptiveAvgPool2d, self).__init__()
        self.flatten = flatten

    def forward(self, x):
        return x.mean((2, 3)) if self.flatten else x.mean((2, 3), keepdim=True)


class SelectAdaptivePool2d(nn.Module):
    """
    Selectable global pooling layer with dynamic input kernel size
    """
    def __init__(self, output_size=1, pool_type='fast', flatten=False):
        super(SelectAdaptivePool2d, self).__init__()
        self.pool_type = pool_type or ''  # convert other falsy values to empty string for consistent TS typing
        self.flatten = flatten
        if pool_type == '':
            self.pool = nn.Identity()  # pass through
        elif pool_type == 'fast':
            assert output_size == 1
            self.pool = FastAdaptiveAvgPool2d(self.flatten)
        elif pool_type == 'avg':
            self.pool = nn.AdaptiveAvgPool2d(output_size)
        elif pool_type == 'max':
            self.pool = nn.AdaptiveMaxPool2d(output_size)
        elif pool_type == 'avgmax':
            self.pool = AdaptiveAvgMaxPool2d(output_size)
        elif pool_type == 'catavgmax':
            self.pool = AdaptiveCatAvgMaxPool2d(output_size)
        else:
            assert False, 'Invalid pool type: %s' % pool_type

    def forward(self, x):
        x = self.pool(x)
        return x


if __name__ == "__main__":
    input_tensor = torch.rand((1, 3, 32, 32))
    output_max = adaptive_pool2d(input_tensor, (1, 1), pool_type='max')
    output_avg = adaptive_pool2d(input_tensor, (1, 1), pool_type='avg')
    output_avgmax = adaptive_avgmax_pool2d(input_tensor, (1, 1))
    output_catavgmax = adaptive_catavgmax_pool2d(input_tensor, (1, 1))
    output_fast = SelectAdaptivePool2d()(input_tensor)
    print("自适应最大池化结果：\n", output_max.shape)
    print("\n自适应平均池化结果：\n", output_avg.shape)
    print("\n自适应平均池化与自适应最大池化的结合结果：\n", output_avgmax.shape)
    print("\n自适应平均池化与自适应最大池化的连接结果：\n", output_catavgmax.shape)
    print("\n自定义的自适应平均池化层:\n", output_fast.shape)

    # MaxPool2d与AvgPool2d手写测试实验
    input_data = torch.rand((1, 3, 3, 3))
    # input_data = torch.Tensor([[[[0.3939, 0.8964, 0.3681],
    #                            [0.5134, 0.3780, 0.0047],
    #                            [0.0681, 0.0989, 0.5962]],
    #                           [[0.7954, 0.4811, 0.3329],
    #                            [0.8804, 0.3986, 0.3561],
    #                            [0.2797, 0.3672, 0.6508]],
    #                           [[0.6309, 0.1340, 0.0564],
    #                            [0.3101, 0.9927, 0.5554],
    #                            [0.0947, 0.2305, 0.8299]]]])

    print(input_data.shape)
    is_vectoring = False
    kernel_size = 3
    stride = 2
    MaxPool2d1 = nn.MaxPool2d(kernel_size, stride)
    output_data_with_torch_max = MaxPool2d1(input_data)
    AvgPool2d1 = nn.AvgPool2d(kernel_size, stride)
    output_data_with_torch_avg = AvgPool2d1(input_data)
    AvgPool2d2 = AvgPool2d(kernel_size, stride, is_vectoring)
    output_data_with_torch_Avg = AvgPool2d2(input_data)
    MaxPool2d2 = MaxPool2d(kernel_size, stride, is_vectoring)
    output_data_with_torch_Max = MaxPool2d2(input_data)
    # output_data_with_max = max_pool2d(input_data, kernel_size, stride)
    # output_data_with_avg = avg_pool2d(input_data, kernel_size, stride)

    print("\ntorch.nn pooling Output:")
    print(output_data_with_torch_max,"\n",output_data_with_torch_max.size())
    print(output_data_with_torch_avg,"\n",output_data_with_torch_avg.size())
    print("\npooling Output:")
    print(output_data_with_torch_Max,"\n",output_data_with_torch_Max.size())
    print(output_data_with_torch_Avg,"\n",output_data_with_torch_Avg.size())
    # 直接使用bool方法判断会因为浮点数的原因出现偏差
    print(torch.allclose(output_data_with_torch_max,output_data_with_torch_Max))
    print(torch.allclose(output_data_with_torch_avg,output_data_with_torch_Avg))
    # tensor([[[[0.8964]],       # output_data_with_max
    #          [[0.8804]],
    #          [[0.9927]]]])
    # tensor([[[[0.3686]],       # output_data_with_avg
    #           [[0.5047]],
    #           [[0.4261]]]])

    input_data = torch.rand((1, 3, 64, 64))
    strided_conv = StridedPool2d(3, 64)
    output_data = strided_conv(input_data)
    print("Input shape:", input_data.shape)
    print("Output shape:", output_data.shape)