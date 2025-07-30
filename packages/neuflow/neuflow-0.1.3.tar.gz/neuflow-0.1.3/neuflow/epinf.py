# -*- coding: utf-8 -*-
"""
Author: Xiang Yangcheng [https://github.com/Xayah-Hina]
GitHub: https://github.com/IME-lab-Hokudai/EPINF-NeuFlow
Last Modification Date: 2025-07-10
Description: The pytorch implementation of the paper "Efficient Physics Informed Neural Reconstruction of Diverse Fluid Dynamics from Sparse Observations".
License: Mozilla Public License 2.0 (MPL-2.0)
Copyright (c) 2025 Xiang Yangcheng, IME Lab, Hokkaido University, Japan.
"""
import dataclasses
import glob
import os
import typing

import lightning
import torch
import torchmetrics
import torchvision.utils

from .datasets import PIDatasetAPI, PINeuFlowDataset
from .models import EPINFHybridModel
from .plugins import PluginLoss
from .renderers import EPINFRenderer


class EPINFTrainer(lightning.LightningModule):
    @dataclasses.dataclass
    class EPINF:
        dataset: PINeuFlowDataset.Config = dataclasses.field(default_factory=PINeuFlowDataset.Config, metadata={'help': 'PI-NeuFlow dataset configuration'})
        model: EPINFHybridModel.Config = dataclasses.field(default_factory=EPINFHybridModel.Config, metadata={'help': 'model configuration'})
        renderer: EPINFRenderer.Config = dataclasses.field(default_factory=EPINFRenderer.Config, metadata={'help': 'renderer configuration'})

        gui: bool = dataclasses.field(default=False, metadata={'help': 'whether to use GUI for rendering'})
        test: bool = dataclasses.field(default=False, metadata={'help': 'test mode, load a checkpoint and test the model'})
        lrate: float = dataclasses.field(default=1e-3, metadata={'help': 'learning rate for the optimizer'})
        epochs: int = dataclasses.field(default=100, metadata={'help': 'number of epochs to train the model'})

        export_val_map: bool = dataclasses.field(default=False, metadata={'help': 'whether to output validation images'})
        export_model_only: bool = dataclasses.field(default=False, metadata={'help': 'whether to export model only'})
        fading_step: int = dataclasses.field(default=3000, metadata={'help': 'step at which the static fading starts'})

    def __init__(self, cfg: EPINF):
        super().__init__()
        self.cfg = cfg
        self.save_hyperparameters()
        self.model = EPINFHybridModel(cfg=cfg.model)
        self.renderer = EPINFRenderer(cfg=cfg.renderer)
        self.psnr = torchmetrics.image.PeakSignalNoiseRatio(data_range=1.0)
        self.ssim = torchmetrics.image.StructuralSimilarityIndexMeasure(data_range=1.0)
        self.lpips = torchmetrics.image.lpip.LearnedPerceptualImagePatchSimilarity(net_type='vgg')

        # temporary variables
        self.model_only_iter = 1

    def on_fit_start(self):
        dataset: PIDatasetAPI = self.trainer.datamodule
        mode: typing.Literal['hybrid', 'dynamic_only', 'static_only'] = 'hybrid'
        if self.cfg.dataset.dataset in ['scalar']:
            mode = 'dynamic_only'
        self.renderer.set_mode(mode)
        self.print(f">>> [Custom]: Renderer mode set to {mode} <<<")
        self.renderer.set_render_resolution(width=dataset.width, height=dataset.height)
        self.print(f">>> [Custom]: Renderer resolution set to {dataset.width}x{dataset.height} <<<")
        self.renderer.set_min_near_far(min_near=dataset.near_std, max_far=dataset.far_std)
        self.print(f">>> [Custom]: Near and far std set to {dataset.near_std} and {dataset.far_std} <<<")
        self.renderer.set_aabb_std(dataset.aabb_std)
        self.print(f">>> [Custom]: AABB std set to {dataset.aabb_std} <<<")
        self.renderer.set_bound_std(dataset.bound_std)
        self.print(f">>> [Custom]: Bound std set to {dataset.bound_std} <<<")
        self.renderer.set_background_color(dataset.background_color)
        self.print(f">>> [Custom]: Background color set to {dataset.background_color} <<<")
        self.renderer.to(device=self.device)
        print(f">>> [Custom]: Renderer moved to device {self.device} <<<")

    def on_train_batch_start(self, batch, batch_idx):
        self.model.set_time(batch['times'])
        for plugin in self.renderer.plugins:
            plugin.on_iter_start()

    def training_step(self, batch, batch_idx):
        result_maps, pixels, pixels_mask = self.renderer.forward(
            model=self.model,
            poses=batch['poses'],
            focals=batch['focals'],
            images=batch['images'],
            pose_indices=batch['pose_indices'] if 'pose_indices' in batch else None,
            images_masks=batch['images_masks'] if 'images_masks' in batch else None,
        )
        rgb_map = result_maps['rgb_map']
        img_loss = torch.nn.functional.mse_loss(rgb_map, pixels[..., :3])
        loss = img_loss
        self.log("img_loss", img_loss, on_step=True, on_epoch=False, prog_bar=True)

        for plugin_loss in filter(lambda v: isinstance(v, PluginLoss), self.renderer.plugins):
            loss += plugin_loss.loss
            self.log(f"{plugin_loss.name}", plugin_loss.loss, on_step=True, on_epoch=False, prog_bar=True)

        if 'rgb_map_static_independent' in result_maps:
            tempo_fading = min(max(self.global_step / self.cfg.fading_step, 0.0), 1.0)
            img_loss_static = torch.nn.functional.mse_loss(result_maps['rgb_map_static_independent'], pixels[..., :3])
            img_static_loss = tempo_fading * img_loss + (1 - tempo_fading) * img_loss_static
            loss += img_static_loss
            self.log("img_static_loss", img_static_loss, on_step=True, on_epoch=False, prog_bar=True)

        self.log("loss", loss, on_step=True, on_epoch=False, prog_bar=True)
        return loss

    def on_validation_batch_start(self, batch, batch_idx, dataloader_idx=0):
        if self.cfg.export_val_map:
            os.makedirs(os.path.join(self.logger.experiment.dir, 'validation_images'), exist_ok=True)
        self.model.set_time(batch['times'])

    def validation_step(self, batch, batch_idx):
        result_maps, pixels, pixels_mask = self.renderer.forward(
            model=self.model,
            poses=batch['poses'],
            focals=batch['focals'],
            images=batch['images'],
            pose_indices=batch['pose_indices'] if 'pose_indices' in batch else None,
            images_masks=batch['images_masks'] if 'images_masks' in batch else None,
        )
        val_loss = torch.nn.functional.mse_loss(result_maps['rgb_map'], pixels[..., :3])
        self.log("val_loss", val_loss, on_step=False, on_epoch=True, prog_bar=True)
        psnr = self.psnr(result_maps['rgb_map'], pixels[..., :3])
        self.log("val_psnr", psnr, on_step=False, on_epoch=True, prog_bar=True)
        ssim = self.ssim(result_maps['rgb_map'].permute(0, 3, 1, 2), pixels[..., :3].permute(0, 3, 1, 2))  # 如果是 HWC 格式，需转为 NCHW
        self.log("val_ssim", ssim, on_step=False, on_epoch=True, prog_bar=True)
        lpips = self.lpips(result_maps['rgb_map'].permute(0, 3, 1, 2), pixels[..., :3].permute(0, 3, 1, 2))
        self.log("val_lpips", lpips, on_step=False, on_epoch=True, prog_bar=True)

        if self.cfg.export_val_map:
            final_map = self.generate_map(result_maps, pixels, pixels_mask)
            torchvision.utils.save_image(final_map.permute(2, 0, 1), os.path.join(self.logger.experiment.dir, 'validation_images', f'{self.current_epoch}_{batch_idx}.png'))

        return val_loss

    def on_test_start(self):
        os.makedirs(os.path.join(self.logger.experiment.dir, 'test_images'), exist_ok=True)

    def test_step(self, batch, batch_idx):
        self.model.set_time(batch['times'])
        result_maps, pixels, pixels_mask = self.renderer.forward(
            model=self.model,
            poses=batch['poses'],
            focals=batch['focals'],
            images=batch['images'] if 'images' in batch else None,
            pose_indices=batch['pose_indices'] if 'pose_indices' in batch else None,
            images_masks=batch['images_masks'] if 'images_masks' in batch else None,
        )
        final_map = self.generate_map(result_maps, pixels, pixels_mask)
        psnr = self.psnr(result_maps['rgb_map'], pixels[..., :3])
        self.log("test_psnr", psnr, on_step=False, on_epoch=True, prog_bar=True)
        ssim = self.ssim(result_maps['rgb_map'].permute(0, 3, 1, 2), pixels[..., :3].permute(0, 3, 1, 2))  # 如果是 HWC 格式，需转为 NCHW
        self.log("test_ssim", ssim, on_step=False, on_epoch=True, prog_bar=True)
        lpips = self.lpips(result_maps['rgb_map'].permute(0, 3, 1, 2), pixels[..., :3].permute(0, 3, 1, 2))
        self.log("test_lpips", lpips, on_step=False, on_epoch=True, prog_bar=True)
        os.makedirs(os.path.join(self.logger.experiment.dir, 'test_images'), exist_ok=True)
        torchvision.utils.save_image(final_map.permute(2, 0, 1), os.path.join(self.logger.experiment.dir, 'test_images', f'{batch_idx}.png'))

    def on_test_end(self):
        image_dir = os.path.join(self.logger.experiment.dir, 'test_images')
        video_path = os.path.join(self.logger.experiment.dir, 'test_images', 'test_video.mp4')

        image_paths = sorted(
            glob.glob(os.path.join(image_dir, '*.png')),
            key=lambda x: int(os.path.basename(x).split('_')[-1].split('.')[0])
        )

        frames = []
        for path in image_paths:
            img = torchvision.io.read_image(path)  # (C, H, W), dtype=torch.uint8, range [0,255]
            if img.shape[0] == 1:
                img = img.expand(3, -1, -1)
            frames.append(img.permute(1, 2, 0))  # (H, W, C)

        video_tensor = torch.stack(frames, dim=0)  # (T, H, W, 3)
        torchvision.io.write_video(video_path, video_tensor, fps=24)
        print(f"✅ Video saved at {video_path}")

    def on_save_checkpoint(self, checkpoint):
        if self.cfg.export_model_only:
            path = os.path.join(self.logger.experiment.dir, 'model_only', f'model_only_{self.model_only_iter}.ckpt')
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path), exist_ok=True)
            torch.save({
                "state_dict": self.model.state_dict(),
                'model_name': self.model.__class__.__name__,
                "tsm": self.renderer.tsm.state_dict(),
                'model_cfg': self.cfg.model,
            }, path)
            print(f"✅ Model checkpoint saved at {path}")
            self.model_only_iter += 1

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(params=self.parameters(), lr=self.cfg.lrate, eps=1e-15)
        scheduler = {
            "scheduler": torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.9, patience=10, min_lr=1e-5),
            "monitor": "loss",  # what to monitor for the scheduler
            "interval": "epoch",  # when to step the scheduler
            "frequency": 1,
        }
        return {"optimizer": optimizer, "lr_scheduler": scheduler}

    @staticmethod
    def generate_map(result_maps, pixels, pixels_mask):
        rgb_map_column = torch.cat([rgb for rgb in result_maps['rgb_map']], dim=1)
        acc_map_column = torch.cat([rgb for rgb in result_maps['acc_map']], dim=1)
        depth_map_column = torch.cat([rgb for rgb in result_maps['depth_map']], dim=1)

        rgb_map_static_column = torch.cat([rgb for rgb in result_maps['rgb_map_static_independent']], dim=1) if 'rgb_map_static_independent' in result_maps else None
        acc_map_static_column = torch.cat([rgb for rgb in result_maps['acc_map_static_independent']], dim=1) if 'acc_map_static_independent' in result_maps else None
        depth_map_static_column = torch.cat([rgb for rgb in result_maps['depth_map_static_independent']], dim=1) if 'depth_map_static_independent' in result_maps else None

        rgb_map_dynamic_column = torch.cat([rgb for rgb in result_maps['rgb_map_dynamic_independent']], dim=1) if 'rgb_map_dynamic_independent' in result_maps else None
        acc_map_dynamic_column = torch.cat([rgb for rgb in result_maps['acc_map_dynamic_independent']], dim=1) if 'acc_map_dynamic_independent' in result_maps else None
        depth_map_dynamic_column = torch.cat([rgb for rgb in result_maps['depth_map_dynamic_independent']], dim=1) if 'depth_map_dynamic_independent' in result_maps else None

        pixels_column = torch.cat([pixel for pixel in pixels[..., :3]], dim=1) if pixels is not None else torch.zeros_like(rgb_map_column)
        pixels_mask_column = torch.cat([mask for mask in pixels_mask.unsqueeze(-1)], dim=1) if pixels_mask is not None else torch.zeros_like(rgb_map_column)

        if rgb_map_static_column is not None:
            rgb_map_column = torch.cat([rgb_map_static_column, rgb_map_column], dim=0)
        if acc_map_static_column is not None:
            acc_map_column = torch.cat([acc_map_static_column, acc_map_column], dim=0)
        if depth_map_static_column is not None:
            depth_map_column = torch.cat([depth_map_static_column, depth_map_column], dim=0)
        if rgb_map_dynamic_column is not None:
            rgb_map_column = torch.cat([rgb_map_column, rgb_map_dynamic_column], dim=0)
        if acc_map_dynamic_column is not None:
            acc_map_column = torch.cat([acc_map_column, acc_map_dynamic_column], dim=0)
        if depth_map_dynamic_column is not None:
            depth_map_column = torch.cat([depth_map_column, depth_map_dynamic_column], dim=0)

        N = rgb_map_column.shape[0] // pixels_column.shape[0]
        if N > 1:
            left_side = torch.cat([torch.zeros_like(pixels_column), pixels_column, pixels_mask_column.expand_as(pixels_column)], dim=0)
        else:
            left_side = torch.cat([pixels_column, pixels_mask_column.expand_as(pixels_column)], dim=1)
        right_side = torch.cat([rgb_map_column, acc_map_column.expand_as(rgb_map_column), depth_map_column.expand_as(rgb_map_column)], dim=1)

        final_map = torch.cat([left_side, right_side], dim=1)

        return final_map
