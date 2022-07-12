#!/bin/env python

import os
import glob
import sys

import tqdm

from lsst.pipe.base import Pipeline


def main(root):
    for old_path in tqdm.tqdm(glob.glob(f"{os.environ['DRP_PIPE_DIR']}/pipelines/*/*.yaml")):
        new_path = old_path.replace(os.environ['DRP_PIPE_DIR'], root)[:-5]
        pipeline = Pipeline.from_uri(old_path)
        try:
            pipeline.write_to_uri(new_path, expand=True)
        except Exception as err:
            raise RuntimeError(f"Processing {new_path}.") from err


if __name__ == "__main__":
    main(sys.argv[1])