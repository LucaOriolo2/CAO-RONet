# CAO-RONet on HeRCULES

Fork of [NEU-REAL/CAO-RONet](https://github.com/NEU-REAL/CAO-RONet) used as a learning-based
4D radar odometry baseline on HeRCULES (Continental ARS548). The network, losses and training
schedule are unchanged; the changes only add the dataset and fix the evaluation protocol.

## Changes from upstream
- `dataset/hercules_clip_odm.py`: HeRCULES samples in the upstream clip format (same point
  sampling, features `[v_r, RCS, RCS]` and augmentation as the View-of-Delft class).
- `configs_hercules.yaml`: upstream hyperparameters; model selection on the **validation**
  split (upstream selects the checkpoint on the evaluation split it reports); KITTI-style
  segment errors over 100–800 m.
- `main_odm.py`: `--config` and `--eval_split` arguments; any `*Clip*` dataset uses the
  sequential training/evaluation loops.
- `clip_util_odm.py`, `KITTI_odometry_evaluation_tool/evaluation_delft.py`: output folders,
  evaluated sequences and segment lengths read from the config (upstream defaults kept).

## Data
Samples are produced by `baselines/caoronet/export_hercules.py` of the main thesis repository
from the raw radar scans (`Radar/Continental/*.bin`) and the GT synchronised to the radar
timestamps, with the same train / val / test split as the proposed model:
`<root>/{train,val,test}/<sequence>/<k>_<t1_ns>_<t2_ns>.json` (k = pair index; training clips
also come time-reversed as `<sequence>_rev`, as the upstream augmentation).

## Usage
```bash
# training (checkpoint selected on val)
python main_odm.py --config configs_hercules.yaml --dataset herculesClipDatasetOdm \
    --model ronet --exp_name ronet_hercules --dataset_path <root>
# evaluation of the selected checkpoint on test
python main_odm.py --config configs_hercules.yaml --dataset herculesClipDatasetOdm \
    --model ronet --exp_name ronet_hercules --dataset_path <root> --eval --eval_split test
```
Predicted poses (KITTI format, one per radar scan, radar frame) are written to
`eval_result/data_hercules/<sequence>.txt`.
