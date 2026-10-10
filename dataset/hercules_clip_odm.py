#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HeRCULES (Continental ARS548) odometry samples in the CAO-RONet clip format.

Samples are written by the export script of the comparison study (one JSON per pair of
consecutive radar scans): {"pc1": [[x, y, z, RCS, v_r], ...], "pc2": [...], "trans": T_r1_r2}.
Layout: <root>/<partition>/<sequence>/<k>_<t1_ns>_<t2_ns>.json (k = pair index). Same sampling, features and
augmentation as the View-of-Delft class; only the folder indexing and calibration differ.
"""

import os
import numpy as np
from torch.utils.data import Dataset

from .vod_clip_odm import vodClipDatasetOdm


class herculesClipDatasetOdm(vodClipDatasetOdm):

    def __init__(self, args, root='', partition='train', textio=None):
        Dataset.__init__(self)
        self.npoints = args.num_points
        self.textio = textio
        # Radar resolution: only read by the scene-flow utilities, not by odometry; VoD values kept
        self.res = {'r_res': 0.2,
                    'theta_res': 1.5 * np.pi / 180,
                    'phi_res': 1.5 * np.pi / 180}
        # No camera in this setup: identity placeholders for the shared args
        self.camera_projection_matrix = np.eye(3, 4, dtype=np.float32)
        self.t_camera_radar = np.eye(4, dtype=np.float32)
        self.eval = args.eval
        self.partition = partition
        self.root = os.path.join(root, self.partition)
        self.interval = 0.05
        self.mini_clip_len = args.mini_clip_len
        self.update_len = args.update_len
        self.clips = sorted(os.listdir(self.root))
        self.mini_samples = []
        self.samples = []
        self.clips_info = []

        for clip in self.clips:
            clip_path = os.path.join(self.root, clip)
            # Pair files are named <k>_<t1_ns>_<t2_ns>.json: order by the pair index
            samples = sorted(os.listdir(clip_path), key=lambda x: int(x.split('_')[0]))

            if self.eval:
                self.clips_info.append({'clip_name': clip,
                                        'index': [len(self.samples), len(self.samples) + len(samples)]})
                for s in samples:
                    self.samples.append(os.path.join(clip_path, s))
            else:
                # Non-overlapping mini clips of consecutive pairs
                for i in range(len(samples) // self.mini_clip_len):
                    st = i * self.mini_clip_len
                    mini = [os.path.join(clip_path, samples[st + j]) for j in range(self.mini_clip_len)]
                    self.samples.extend(mini)
                    self.mini_samples.append(mini)

        if self.textio is not None:
            if self.eval:
                self.textio.cprint(self.partition + ' : ' + str(len(self.samples)) + ' frames')
            else:
                self.textio.cprint(self.partition + ' : ' + str(len(self.mini_samples)) + ' mini_clips')
