# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Test Engine Module."""

from pathlib import Path

import pytest
import yaml

from anomalib.data import MVTecAD
from anomalib.engine import Engine
from anomalib.models import Padim


class TestEngine:
    """Test Engine."""

    @pytest.fixture()
    @staticmethod
    def fxt_full_config_path(tmp_path: Path) -> Path:
        """Fixture full configuration examples."""
        config_str = """
        seed_everything: true
        trainer:
            accelerator: auto
            strategy: auto
            devices: auto
            num_nodes: 1
            precision: null
            logger: null
            callbacks: null
            fast_dev_run: false
            max_epochs: null
            min_epochs: null
            max_steps: -1
            min_steps: null
            max_time: null
            limit_train_batches: null
            limit_val_batches: null
            limit_test_batches: null
            limit_predict_batches: null
            overfit_batches: 0.0
            val_check_interval: null
            check_val_every_n_epoch: 1
            num_sanity_val_steps: null
            log_every_n_steps: null
            enable_checkpointing: null
            enable_progress_bar: null
            enable_model_summary: null
            accumulate_grad_batches: 1
            gradient_clip_val: null
            gradient_clip_algorithm: null
            deterministic: null
            benchmark: null
            inference_mode: true
            use_distributed_sampler: true
            profiler: null
            detect_anomaly: false
            barebones: false
            plugins: null
            sync_batchnorm: false
            reload_dataloaders_every_n_epochs: 0
        logging:
            log_graph: false
        default_root_dir: results
        ckpt_path: null
        model:
            class_path: anomalib.models.Padim
            init_args:
                backbone: resnet18
                layers:
                - layer1
                - layer2
                - layer3
                pre_trained: true
                n_features: null
        data:
            class_path: anomalib.data.MVTecAD
            init_args:
                root: datasets/MVTecAD
                category: bottle
                train_batch_size: 32
                eval_batch_size: 32
                num_workers: 8
                test_split_mode: FROM_DIR
                test_split_ratio: 0.2
                val_split_mode: SAME_AS_TEST
                val_split_ratio: 0.5
                seed: null
        """
        config_dict = yaml.safe_load(config_str)
        config_file = tmp_path / "config.yaml"
        with config_file.open(mode="w") as file:
            yaml.dump(config_dict, file)
        return config_file

    @staticmethod
    def test_from_config(fxt_full_config_path: Path) -> None:
        """Test Engine.from_config."""
        with pytest.raises(FileNotFoundError):
            Engine.from_config(config_path="wrong_configs.yaml")

        engine, model, datamodule = Engine.from_config(config_path=fxt_full_config_path)
        assert engine is not None
        assert isinstance(engine, Engine)
        assert model is not None
        assert isinstance(model, Padim)
        assert datamodule is not None
        assert isinstance(datamodule, MVTecAD)
        assert datamodule.train_batch_size == 32
        assert datamodule.num_workers == 8

        # Override batch_size & num_workers
        override_kwargs = {
            "data.train_batch_size": 1,
            "data.num_workers": 1,
        }
        engine, model, datamodule = Engine.from_config(config_path=fxt_full_config_path, **override_kwargs)
        assert datamodule.train_batch_size == 1
        assert datamodule.num_workers == 1
