import json
import typing
from pathlib import Path

import torch
from torch.utils.data import Dataset

from util.globals import *

REMOTE_ROOT = f"{REMOTE_ROOT_URL}/data/dsets"


class CounterFactDataset(Dataset):
    def __init__(
        self,
        data_dir: str,
        multi: bool = False,
        size: typing.Optional[int] = None,
        *args,
        **kwargs,
    ):
        self.data = []
        data_dir = Path(data_dir)
        for i in range(2, 10):
            cf_loc = data_dir / (
                "seesaw_cf_P101_False_part_{i}.json"
            )
            if not cf_loc.exists():
                remote_url = f"{REMOTE_ROOT}/{'multi_' if multi else ''}counterfact.json"
                print(f"{cf_loc} does not exist. Downloading from {remote_url}")
                data_dir.mkdir(exist_ok=True, parents=True)
                torch.hub.download_url_to_file(remote_url, cf_loc)

            with open(cf_loc, "r") as f:
                self.data = self.data + json.load(f)
        if size is not None:
            self.data = self.data[:size]

        print(f"Loaded dataset with {len(self)} elements")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        return self.data[item]


class MultiCounterFactDataset(CounterFactDataset):
    def __init__(
        self, data_dir: str, size: typing.Optional[int] = None, *args, **kwargs
    ):
        super().__init__(data_dir, *args, multi=True, size=size, **kwargs)
