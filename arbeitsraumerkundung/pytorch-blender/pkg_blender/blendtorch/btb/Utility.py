import bpy
import threading

# KeyFrameState should be thread-specific
class KeyFrameState(threading.local):
    def __init__(self):
        super(KeyFrameState, self).__init__()
        self.depth = 0


class KeyFrame:
    # Remember how many KeyFrame context manager have been applied around the current execution point
    state = KeyFrameState()

    def __init__(self, frame: int):
        """ Sets the frame number for its complete block.
        :param frame: The frame number to set. If None is given, nothing is changed.
        """
        self._frame = frame
        self._prev_frame = None

    def __enter__(self):
        KeyFrame.state.depth += 1
        if self._frame is not None:
            self._prev_frame = bpy.context.scene.frame_current
            bpy.context.scene.frame_set(self._frame)

    def __exit__(self, type, value, traceback):
        KeyFrame.state.depth -= 1
        if self._prev_frame is not None:
            bpy.context.scene.frame_set(self._prev_frame)

    @staticmethod
    def is_any_active() -> bool:
        """ Returns whether the current execution point is surrounded by a KeyFrame context manager.
        :return: True, if there is at least one surrounding KeyFrame context manager
        """
        return KeyFrame.state.depth > 0
