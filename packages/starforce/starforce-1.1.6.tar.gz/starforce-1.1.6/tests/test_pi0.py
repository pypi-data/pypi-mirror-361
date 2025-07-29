from starforce.datasets.lerobot_dataset import LeRobotDataset
import torch
from starforce.models.pretrained import PreTrainedConfig
from starforce.models.build_model import make_policy
from loguru import logger
import time


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float32
    # paligemma doesn't support bf16?
    # dtype = torch.float32
    logger.info(f"##info, device: {device}, dtype: {dtype}")

    # dataset_repo_id = "danaaubakirova/koch_test"
    # dataset_repo_id = "data/robotwin2lerobot/block_hammer_beat"
    dataset_repo_id = "/pfs/data/xiongxiao/lerobot_fps30/open_laptop"
    # ckpt_torch_dir = "/pfs/data/fgang/vla_holo/checkpoints/pi0"
    # ckpt_torch_dir = "/pfs/data/fgang/outputs_models/pi0-1-20000/pretrained_model"
    # ckpt_torch_dir = "/pfs/data/fgang/outputs_models/pi0-robotwin-30fps-tasks3"
    # ckpt_torch_dir = "/pfs/data/fgang/vla_holo/outputs/pi0-fixed-20ksteps"
    ckpt_torch_dir = "/pfs/data/fgang/outputs_models/pi0-robotwin-30fps-tasks5"

    dataset = LeRobotDataset(dataset_repo_id, episodes=[0])
    dataloader = torch.utils.data.DataLoader(
        dataset,
        num_workers=0,
        batch_size=1,
    )
    batch = next(iter(dataloader))
    # To device
    for k in batch:
        if isinstance(batch[k], torch.Tensor):
            batch[k] = batch[k].to(device=device, dtype=dtype)
    print(f'dataset.meta: {dataset.meta}')
    
    cfg = PreTrainedConfig.from_pretrained(ckpt_torch_dir, device=device)
    cfg.pretrained_path = ckpt_torch_dir
    policy = make_policy(cfg, ds_meta=dataset.meta)
    # policy.to(dtype)
    # print(policy)

    t0 = time.time()
    with torch.amp.autocast(device_type=device):
        benchmark_iters = 30
        for _ in range(benchmark_iters):
            # print(batch)
            t00 = time.time()
            action = policy.select_action(batch, n_steps_out=50)
            torch.cuda.synchronize()
            # print("##info, action:", action.shape, action.dtype, action.device, action, time.time() - t00)
    t1 = time.time()
    print(f'cost: {t1-t0:.3f}, avg: {(t1-t0)/benchmark_iters}')


if __name__ == "__main__":
    main()
