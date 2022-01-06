# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import pathlib
import inotify.adapters
import inotify.constants
from base_camera import BaseCamera


class CameraFile(BaseCamera):
    @staticmethod
    def frames():
        filename = os.getenv("MOABFRAME", "/tmp/camera/frame.jpg")
        dirname = os.path.dirname(filename)

        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)

        i = inotify.adapters.Inotify()

        # inotify works on folder level, so extract folder from filename
        i.add_watch(dirname, inotify.constants.IN_CLOSE_WRITE)

        # filesystem event generator blocks until a change is detected
        for event in i.event_gen(yield_nones=False):
            with open(filename, "rb") as f:
                yield f.read()
