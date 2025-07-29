"""
A unified inferface calling Starforce & GR00T 1.5 & Pi0
model
"""

from starforce.infer.infer import StarForceVLA
from .infer_vlaholo import VLAHolo
from loguru import logger
import torch


class SVLA:

    def __init__(self, model_type: str, model_path: str, device="cuda"):
        avaliable_models = ["gr00t", "pi0", "starforce-s1"]
        if model_type in avaliable_models:
            ValueError(f"{model_type} not in avaliable_models: {avaliable_models}")
        self.device = device
        self._create_model(model_type=model_type, model_path=model_path, device=device)

    def _create_model(self, model_type, model_path, device):
        logger.info(f"creating {model_type} model.")
        if model_type == "gr00t":
            self.model = StarForceVLA(model_path=model_path, model_type=model_type)
        elif model_type == "starforce-s1":
            self.model = StarForceVLA(model_path=model_path, model_type=model_type)
        elif model_type == "pi0":
            self.model = VLAHolo(model_path, device=device)

    def select_action(self, batch_data, n_steps=50):
        for k in batch_data:
            if isinstance(batch_data[k], torch.Tensor):
                batch_data[k] = batch_data[k].to(device=self.device)
        actions = self.model.select_action(batch_data)
        return actions


if __name__ == "__main__":
    # Test all valid string cases
    # SVLA(model_type="Starforce", model_path="/models/starforce")
    # SVLA(model_type="Gr00t", model_path="/models/gr00t")
    vla = SVLA(model_type="pi0", model_path="/models/pi0")
