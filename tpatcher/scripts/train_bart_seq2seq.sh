#!/usr/bin/env bash
DEVICE=4
SEED=42
python3 scripts/train_bart_seq2seq.py --seed=$SEED --device=$DEVICE