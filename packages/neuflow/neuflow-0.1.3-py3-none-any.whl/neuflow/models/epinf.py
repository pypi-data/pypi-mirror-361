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
import math

import tinycudann
import torch

from .api import ModelAPI


class EPINFStaticModel(ModelAPI):
    @dataclasses.dataclass
    class Config:
        num_layers_sigma: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the sigma network'})
        hidden_dim_sigma: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the sigma network'})
        num_layers_rgb: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the RGB network'})
        hidden_dim_rgb: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the RGB network'})
        geo_feat_dim: int = dataclasses.field(default=32, metadata={'help': 'geometric feature dimension'})
        num_layers_bg: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the background network'})
        hidden_dim_bg: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the background network'})
        use_background: bool = dataclasses.field(default=False, metadata={'help': 'whether to use background in the dataset'})

    def __init__(self, cfg: Config):
        super().__init__(cfg=cfg)

        bound = 1
        self.encoder_sigma = tinycudann.Encoding(
            n_input_dims=3,
            encoding_config={
                "otype": "HashGrid",
                "n_levels": 16,
                "n_features_per_level": 2,
                "log2_hashmap_size": 19,
                "base_resolution": 16,
                "per_level_scale": 2 ** (math.log2(2048 * bound / 16) / (16 - 1)),
            },
        )
        self.sigma_net = tinycudann.Network(
            n_input_dims=int(self.encoder_sigma.n_output_dims),
            n_output_dims=1 + cfg.geo_feat_dim,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": cfg.hidden_dim_sigma,
                "n_hidden_layers": cfg.num_layers_sigma - 1,
            },
        )

        self.encoder_dir = tinycudann.Encoding(
            n_input_dims=3,
            encoding_config={
                "otype": "SphericalHarmonics",
                "degree": 4,
            },
        )
        self.color_net = tinycudann.Network(
            n_input_dims=int(self.encoder_dir.n_output_dims) + cfg.geo_feat_dim,
            n_output_dims=3,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": cfg.hidden_dim_rgb,
                "n_hidden_layers": cfg.num_layers_rgb - 1,
            },
        )

        if cfg.use_background:
            self.encoder_bg = tinycudann.Encoding(
                n_input_dims=2,
                encoding_config={
                    "otype": "HashGrid",
                    "n_levels": 4,
                    "n_features_per_level": 2,
                    "log2_hashmap_size": 19,
                    "base_resolution": 16,
                    "per_level_scale": 2 ** (math.log2(2048 * bound / 4) / (4 - 1)),
                },
            )
            self.bg_net = tinycudann.Network(
                n_input_dims=int(self.encoder_dir.n_output_dims) + int(self.encoder_bg.n_output_dims),
                n_output_dims=3,
                network_config={
                    "otype": "FullyFusedMLP",
                    "activation": "ReLU",
                    "output_activation": "None",
                    "n_neurons": cfg.hidden_dim_bg,
                    "n_hidden_layers": cfg.num_layers_bg - 1,
                },
            )

    def sigma(self, xyz):
        xyz_encoded = self.encoder_sigma(xyz)
        h = self.sigma_net(xyz_encoded)
        sigma = torch.nn.functional.relu(h[..., :1])
        geo_feat = h[..., 1:]
        return sigma, geo_feat

    def rgb(self, xyz, view_dirs, geo_feat, cond=None):
        view_dirs_encoded = self.encoder_dir(view_dirs)
        h = self.color_net(torch.cat([view_dirs_encoded, geo_feat], dim=-1))
        rgb = torch.sigmoid(h)
        return rgb

    def background(self, sph, view_dirs):
        sph_encoded = self.encoder_bg(sph)
        view_dirs_encoded = self.encoder_dir(view_dirs)
        h = self.bg_net(torch.cat([view_dirs_encoded, sph_encoded], dim=-1))
        rgb_bg = torch.sigmoid(h)
        return rgb_bg


class EPINFDynamicModel(ModelAPI):
    @dataclasses.dataclass
    class Config:
        num_layers_sigma: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the sigma network'})
        hidden_dim_sigma: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the sigma network'})
        num_layers_rgb: int = dataclasses.field(default=3, metadata={'help': 'number of layers for the RGB network'})
        hidden_dim_rgb: int = dataclasses.field(default=64, metadata={'help': 'hidden dimension for the RGB network'})
        geo_feat_dim: int = dataclasses.field(default=32, metadata={'help': 'geometric feature dimension'})

    def __init__(self, cfg: Config):
        super().__init__(cfg=cfg)

        bound = 1
        self.encoder = tinycudann.Encoding(
            n_input_dims=4,
            encoding_config={
                "otype": "HashGrid",
                "n_levels": 16,
                "n_features_per_level": 2,
                "log2_hashmap_size": 19,
                "base_resolution": 16,
                "per_level_scale": 2 ** (math.log2(2048 * bound / 16) / (16 - 1)),
            },
        )

        self.sigma_net = tinycudann.Network(
            n_input_dims=int(self.encoder.n_output_dims),
            n_output_dims=1 + cfg.geo_feat_dim,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": cfg.hidden_dim_sigma,
                "n_hidden_layers": cfg.num_layers_sigma - 1,
            },
        )

        self.encoder_dir = tinycudann.Encoding(
            n_input_dims=3,
            encoding_config={
                "otype": "SphericalHarmonics",
                "degree": 4,
            },
        )

        self.color_net = tinycudann.Network(
            n_input_dims=int(self.encoder_dir.n_output_dims) + cfg.geo_feat_dim,
            n_output_dims=3,
            network_config={
                "otype": "FullyFusedMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": cfg.hidden_dim_rgb,
                "n_hidden_layers": cfg.num_layers_rgb - 1,
            },
        )

        self._time = None

    @property
    def time(self):
        assert self._time is not None
        assert isinstance(self._time, torch.Tensor)
        assert self._time.shape[0] == 1
        return self._time

    def set_time(self, time):
        self._time = time

    def sigma(self, xyz):
        xyzt = torch.cat([xyz, self.time.unsqueeze(0).expand_as(xyz[..., :1])], dim=-1)
        xyzt_encoded = self.encoder(xyzt)
        h = self.sigma_net(xyzt_encoded)
        sigma = torch.nn.functional.relu(h[..., :1])
        geo_feat = h[..., 1:]
        return sigma, geo_feat

    def rgb(self, xyz, view_dirs, geo_feat, cond=None):
        view_dirs_encoded = self.encoder_dir(view_dirs)
        h = self.color_net(torch.cat([view_dirs_encoded, geo_feat], dim=-1))
        rgb = torch.sigmoid(h)
        return rgb

    def background(self, sph, view_dirs):
        raise NotImplementedError("Background rendering is not implemented for dynamic models.")


class EPINFHybridModel(ModelAPI):
    @dataclasses.dataclass
    class Config:
        static: EPINFStaticModel.Config = dataclasses.field(default_factory=EPINFStaticModel.Config, metadata={'help': 'Configuration for the static model'})
        dynamic: EPINFDynamicModel.Config = dataclasses.field(default_factory=EPINFDynamicModel.Config, metadata={'help': 'Configuration for the dynamic model'})

    def __init__(self, cfg: Config):
        super().__init__(cfg=cfg)
        self.static_renderer: EPINFStaticModel = EPINFStaticModel(cfg=cfg.static)
        self.dynamic_renderer: EPINFDynamicModel = EPINFDynamicModel(cfg=cfg.dynamic)

    @property
    def time(self):
        return self.dynamic_renderer.time

    def set_time(self, time):
        self.dynamic_renderer.set_time(time)

    def sigma(self, xyz):
        sigma_static, geo_feat_static = self.static_renderer.sigma(xyz)
        sigma_dynamic, geo_feat_dynamic = self.dynamic_renderer.sigma(xyz)
        return sigma_static + sigma_dynamic, geo_feat_static + geo_feat_dynamic

    def rgb(self, xyz, view_dirs, geo_feat, cond=None):
        raise NotImplementedError("Hybrid model does not support direct RGB rendering. Use static or dynamic renderer instead.")

    def background(self, sph, view_dirs):
        raise NotImplementedError("Background rendering is not implemented for hybrid models. Use static or dynamic renderer instead.")
