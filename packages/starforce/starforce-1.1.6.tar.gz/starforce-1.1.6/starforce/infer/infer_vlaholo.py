"""
vlaholo inference wrapper
inside starforce

You can call pi0 like structure directly in starforce
"""

import vlaholo
from vlaholo.common.policies_config import PreTrainedConfig
from vlaholo.models.build_model import make_policy


class VLAHolo:

    def __init__(self, model_path, device="cuda"):
        cfg = PreTrainedConfig.from_pretrained(model_path, device=device)
        cfg.pretrained_path = model_path
        # todo: try remove dataset.meta
        self.policy = make_policy(cfg)

    def select_action(self, batch_data):
        actions = self.policy.select_action(batch_data)
        return actions
