import torch
import torch.nn as nn

class Branch0(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Branch0, self).__init__()
        self.conv0 = nn.Conv2d(in_channels, out_channels, kernel_size=1, padding=0)
        self.bt0 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x0 = self.conv0(x)
        x0 = self.bt0(x0)
        return x0

class Branch1(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Branch1, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bt1 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x1 = self.conv1(x)
        x1 = self.bt1(x1)
        return x1

class Branch2(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Branch2, self).__init__()
        self.conv2_1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bt2_1 = nn.BatchNorm2d(out_channels)
        self.rl2_1 = nn.LeakyReLU(inplace=True)
        self.conv2_2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, dilation=1)
        self.bt2_2 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x2 = self.conv2_1(x)
        x2 = self.bt2_1(x2)
        x2 = self.rl2_1(x2)
        x2 = self.conv2_2(x2)
        x2 = self.bt2_2(x2)
        return x2

class Branch3(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Branch3, self).__init__()
        self.conv3_1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bt3_1 = nn.BatchNorm2d(out_channels)
        self.rl3_1 = nn.LeakyReLU(inplace=True)
        self.conv3_2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, dilation=1)
        self.bt3_2 = nn.BatchNorm2d(out_channels)
        self.rl3_2 = nn.LeakyReLU(inplace=True)
        self.conv3_3 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=2, dilation=2)
        self.bt3_3 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x3 = self.conv3_1(x)
        x3 = self.bt3_1(x3)
        x3 = self.rl3_1(x3)
        x3 = self.conv3_2(x3)
        x3 = self.bt3_2(x3)
        x3 = self.rl3_2(x3)
        x3 = self.conv3_3(x3)
        x3 = self.bt3_3(x3)
        return x3

class Branch4(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Branch4, self).__init__()
        self.conv4_1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bt4_1 = nn.BatchNorm2d(out_channels)
        self.rl4_1 = nn.LeakyReLU(inplace=True)
        self.conv4_2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, dilation=1)
        self.bt4_2 = nn.BatchNorm2d(out_channels)
        self.rl4_2 = nn.LeakyReLU(inplace=True)
        self.conv4_3 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=2, dilation=2)
        self.bt4_3 = nn.BatchNorm2d(out_channels)
        self.rl4_3 = nn.LeakyReLU(inplace=True)
        self.conv4_4 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=5, dilation=5)
        self.bt4_4 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x4 = self.conv4_1(x)
        x4 = self.bt4_1(x4)
        x4 = self.rl4_1(x4)
        x4 = self.conv4_2(x4)
        x4 = self.bt4_2(x4)
        x4 = self.rl4_2(x4)
        x4 = self.conv4_3(x4)
        x4 = self.bt4_3(x4)
        x4 = self.rl4_3(x4)
        x4 = self.conv4_4(x4)
        x4 = self.bt4_4(x4)
        return x4

# Dual attention in spatial channel
class DASC(nn.Module):
    def __init__(self, in_channels):
        super().__init__()
        reduction = max(4, in_channels // 16)
        self.c_attn = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, reduction, 1),
            nn.ReLU(),
            nn.Conv2d(reduction, in_channels, 1),
            nn.Sigmoid())
        self.s_attn = nn.Sequential(
            nn.Conv2d(in_channels, 1, 1),
            nn.Sigmoid())

    def forward(self, x):
        return x * self.c_attn(x) + x * self.s_attn(x)

class ResB(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ResB, self).__init__()
        self.branch0 = Branch0(in_channels, out_channels)
        self.branch1 = Branch1(in_channels, out_channels // 4)
        self.branch2 = Branch2(in_channels, out_channels // 4)
        self.branch3 = Branch3(in_channels, out_channels // 4)
        self.branch4 = Branch4(in_channels, out_channels // 4)
        self.rl = nn.LeakyReLU(inplace=True)
        self.dasc = DASC(out_channels)

    def forward(self, x):
        x0 = self.branch0(x)
        x1 = self.branch1(x)
        x2 = self.branch2(x)
        x3 = self.branch3(x)
        x4 = self.branch4(x)
        x5 = torch.cat((x1, x2, x3, x4), dim=1)
        x6 = x0 + x5
        x7 = self.dasc(self.rl(x6))
        return x7


' Downsampling block '


class DownB(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DownB, self).__init__()
        self.res = ResB(in_channels, out_channels)
        self.pool = nn.MaxPool2d(kernel_size=2)

    def forward(self, x):
        x1 = self.res(x)   # b c h w
        x2 = self.pool(x1)   # b c h*2 w*2
        return x2, x1


' Upsampling block '


class UpB(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(UpB, self).__init__()
        self.up = nn.ConvTranspose2d(
            in_channels, out_channels, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.res = ResB(out_channels * 2, out_channels)

    def forward(self, x, x_):
        x1 = self.up(x)                   # torch.Size([1, 512, 28, 28])
        x2 = torch.cat((x1, x_), dim=1)   # torch.Size([1, 1024, 28, 28])
        x3 = self.res(x2)                 # torch.Size([1, 512, 28, 28])
        return x3


' Output layer '


class Outconv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Outconv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1, padding=0)

    def forward(self, x):
        x1 = self.conv(x)
        return x1


class cbl(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(cbl, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bt = nn.BatchNorm2d(out_channels)
        self.lu = nn.LeakyReLU(inplace=True)

    def forward(self, x):
        x = self.conv(x)
        x = self.bt(x)
        return self.lu(x)


' Architecture of MSR-UNet '

# Multi-scale Residual UNet
class MSRUNet(nn.Module):
    def __init__(self, in_channels=3, num_classes=21):
        super(MSRUNet, self).__init__()
        # 下采样模块
        self.down1 = DownB(in_channels, 64)
        self.down2 = DownB(64, 128)
        self.down3 = DownB(128, 256)
        self.down4 = DownB(256, 512)

        # 残差模块
        self.res_block = ResB(512, 1024)

        # 上采样模块
        self.up1 = UpB(1024, 512)
        self.up2 = UpB(512, 256)
        self.up3 = UpB(256, 128)
        self.up4 = UpB(128, 64)

        # 输出层
        self.out_conv = Outconv(64, num_classes)
        self.drop = nn.Dropout(0.3)

        # 多尺度特征融合层
        self.up_conv1 = nn.ConvTranspose2d(128, 32, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.up_conv2 = nn.ConvTranspose2d(256, 32, kernel_size=3, stride=4, output_padding=1)
        self.up_conv3 = nn.ConvTranspose2d(512, 32, kernel_size=3, stride=8, output_padding=5)

        # 特征融合块
        self.conv_block1 = cbl(96, 64)
        self.conv_block1_final = cbl(128, 64)

        # 跨层连接模块
        self.down_shortcut1 = nn.Conv2d(64, 64, kernel_size=2, stride=2)
        self.up_shortcut2 = nn.ConvTranspose2d(256, 64, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.up_shortcut3 = nn.ConvTranspose2d(512, 64, kernel_size=3, stride=4, output_padding=1)

        # 中间特征处理模块
        self.conv_block2 = cbl(192, 128)
        self.conv_block2_final = cbl(256, 128)
        self.down_shortcut2 = nn.Conv2d(64, 128, stride=4, kernel_size=4)
        self.down_shortcut3 = nn.Conv2d(128, 128, kernel_size=2, stride=2)
        self.up_shortcut4 = nn.ConvTranspose2d(512, 128, kernel_size=3, stride=2, padding=1, output_padding=1)

        # 深层特征融合
        self.conv_block3 = cbl(384, 256)
        self.conv_block3_final = cbl(512, 256)

    def forward(self, x):
        # 下采样阶段
        x1, x1_skip = self.down1(x)
        x2, x2_skip = self.down2(x1)
        x3, x3_skip = self.down3(x2)
        x4, x4_skip = self.down4(x3)

        # 残差模块
        x4 = self.drop(x4)
        x5 = self.res_block(x4)

        # 上采样阶段1
        x6 = self.up1(x5, x4_skip)

        # 多尺度特征融合1
        down_feat1 = self.down_shortcut2(x1_skip)
        down_feat2 = self.down_shortcut3(x2_skip)
        up_feat1 = self.up_shortcut4(x4_skip)
        fused_feat1 = torch.cat([down_feat1, down_feat2, up_feat1], dim=1)
        fused_feat1 = self.conv_block3(fused_feat1)
        fused_feat1 = torch.cat([x3_skip, fused_feat1], dim=1)
        fused_feat1 = self.conv_block3_final(fused_feat1)

        # 上采样阶段2
        x7 = self.up2(x6, fused_feat1)

        # 多尺度特征融合2
        down_feat3 = self.down_shortcut1(x1_skip)
        up_feat2 = self.up_shortcut2(x3_skip)
        up_feat3 = self.up_shortcut3(x4_skip)
        fused_feat2 = torch.cat([down_feat3, up_feat2, up_feat3], dim=1)
        fused_feat2 = self.conv_block2(fused_feat2)
        fused_feat2 = torch.cat([x2_skip, fused_feat2], dim=1)
        fused_feat2 = self.conv_block2_final(fused_feat2)

        # 上采样阶段3
        x8 = self.up3(x7, fused_feat2)

        # 多尺度特征融合3
        up_feat4 = self.up_conv3(x4_skip)
        up_feat5 = self.up_conv2(x3_skip)
        up_feat6 = self.up_conv1(x2_skip)
        fused_feat3 = torch.cat([up_feat4, up_feat5, up_feat6], dim=1)
        fused_feat3 = self.conv_block1(fused_feat3)
        fused_feat3 = torch.cat([x1_skip, fused_feat3], dim=1)
        fused_feat3 = self.conv_block1_final(fused_feat3)

        # 最终上采样
        x9 = self.up4(x8, fused_feat3)

        # 输出层
        return self.out_conv(x9)



if __name__=="__main__":
    from pyzjr.nn.tools import model_complexity_info, summary_2
    model = MSRUNet(num_classes=2)
    model_complexity_info(model, (3, 224, 224))
    summary_2(model, (3, 224, 224))