# Copyright Teklia (contact@teklia.com) & Denis Coquenet
# This code is licensed under CeCILL-C

# -*- coding: utf-8 -*-
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s/%(name)s: %(message)s",
)

TRAIN_NAME = "train"
VAL_NAME = "dev"
TEST_NAME = "test"
SPLIT_NAMES = [TRAIN_NAME, VAL_NAME, TEST_NAME]
