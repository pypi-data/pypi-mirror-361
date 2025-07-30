import os
import sys

import attr
import cv2
from detect_qt_binding import QtBindings, detect_qt_binding
from numpy import ndarray

qt_binding = detect_qt_binding()
if qt_binding == QtBindings.PyQt6:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6.QtWidgets import (
        QAbstractSlider,
        QApplication,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget
    )

    SLIDER_SINGLE_STEP_ADD = QAbstractSlider.SliderAction.SliderSingleStepAdd.value
    SLIDER_SINGLE_STEP_SUB = QAbstractSlider.SliderAction.SliderSingleStepSub.value
    SLIDER_PAGE_STEP_ADD = QAbstractSlider.SliderAction.SliderPageStepAdd.value
    SLIDER_PAGE_STEP_SUB = QAbstractSlider.SliderAction.SliderPageStepSub.value
    SLIDER_MOVE = QAbstractSlider.SliderAction.SliderMove.value


    def exec_and_exit(q_application):
        # type: (QApplication) -> None
        # To make the syntax Python 2-compatible
        sys.exit(getattr(q_application, 'exec')())

elif qt_binding == QtBindings.PySide6:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import (
        QAbstractSlider,
        QApplication,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget
    )

    SLIDER_SINGLE_STEP_ADD = QAbstractSlider.SliderAction.SliderSingleStepAdd.value
    SLIDER_SINGLE_STEP_SUB = QAbstractSlider.SliderAction.SliderSingleStepSub.value
    SLIDER_PAGE_STEP_ADD = QAbstractSlider.SliderAction.SliderPageStepAdd.value
    SLIDER_PAGE_STEP_SUB = QAbstractSlider.SliderAction.SliderPageStepSub.value
    SLIDER_MOVE = QAbstractSlider.SliderAction.SliderMove.value


    def exec_and_exit(q_application):
        # type: (QApplication) -> None
        # To make the syntax Python 2-compatible
        sys.exit(getattr(q_application, 'exec')())

elif qt_binding == QtBindings.PyQt5:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5.QtWidgets import (
        QAbstractSlider,
        QApplication,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget
    )

    SLIDER_SINGLE_STEP_ADD = int(QAbstractSlider.SliderAction.SliderSingleStepAdd)
    SLIDER_SINGLE_STEP_SUB = int(QAbstractSlider.SliderAction.SliderSingleStepSub)
    SLIDER_PAGE_STEP_ADD = int(QAbstractSlider.SliderAction.SliderPageStepAdd)
    SLIDER_PAGE_STEP_SUB = int(QAbstractSlider.SliderAction.SliderPageStepSub)
    SLIDER_MOVE = int(QAbstractSlider.SliderAction.SliderMove)


    def exec_and_exit(q_application):
        # type: (QApplication) -> None
        sys.exit(q_application.exec_())

elif qt_binding == QtBindings.PySide2:
    from PySide2.QtCore import Qt, QTimer
    from PySide2.QtGui import QImage, QPixmap
    from PySide2.QtWidgets import (
        QAbstractSlider,
        QApplication,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget
    )

    SLIDER_SINGLE_STEP_ADD = int(QAbstractSlider.SliderAction.SliderSingleStepAdd)
    SLIDER_SINGLE_STEP_SUB = int(QAbstractSlider.SliderAction.SliderSingleStepSub)
    SLIDER_PAGE_STEP_ADD = int(QAbstractSlider.SliderAction.SliderPageStepAdd)
    SLIDER_PAGE_STEP_SUB = int(QAbstractSlider.SliderAction.SliderPageStepSub)
    SLIDER_MOVE = int(QAbstractSlider.SliderAction.SliderMove)


    def exec_and_exit(q_application):
        # type: (QApplication) -> None
        sys.exit(q_application.exec_())

elif qt_binding == QtBindings.PyQt4:
    from PyQt4.QtCore import Qt, QTimer
    from PyQt4.QtGui import (
        QAbstractSlider,
        QApplication,
        QDesktopServices,
        QFileDialog,
        QHBoxLayout,
        QImage,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPixmap,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget
    )

    SLIDER_SINGLE_STEP_ADD = QAbstractSlider.SliderSingleStepAdd
    SLIDER_SINGLE_STEP_SUB = QAbstractSlider.SliderSingleStepSub
    SLIDER_PAGE_STEP_ADD = QAbstractSlider.SliderPageStepAdd
    SLIDER_PAGE_STEP_SUB = QAbstractSlider.SliderPageStepSub
    SLIDER_MOVE = QAbstractSlider.SliderMove


    def exec_and_exit(q_application):
        # type: (QApplication) -> None
        sys.exit(q_application.exec_())

elif qt_binding == QtBindings.PySide:
    from PySide.QtCore import Qt, QTimer
    from PySide.QtGui import (
        QAbstractSlider,
        QApplication,
        QDesktopServices,
        QFileDialog,
        QHBoxLayout,
        QImage,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPixmap,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget
    )

    SLIDER_SINGLE_STEP_ADD = int(QAbstractSlider.SliderAction.SliderSingleStepAdd)
    SLIDER_SINGLE_STEP_SUB = int(QAbstractSlider.SliderAction.SliderSingleStepSub)
    SLIDER_PAGE_STEP_ADD = int(QAbstractSlider.SliderAction.SliderPageStepAdd)
    SLIDER_PAGE_STEP_SUB = int(QAbstractSlider.SliderAction.SliderPageStepSub)
    SLIDER_MOVE = int(QAbstractSlider.SliderAction.SliderMove)


    def exec_and_exit(q_application):
        # type: (QApplication) -> None
        sys.exit(q_application.exec_())

else:
    raise ImportError(
        'We require one of PyQt6, PySide6, PyQt5, PySide2, PyQt4, or PySide. None of these packages were detected in your Python environment.')


@attr.s
class VideoPlayerState(object):
    pass


@attr.s
class VideoNotOpened(VideoPlayerState):
    pass


@attr.s
class VideoPlaybackInformation(object):
    video_path = attr.ib()  # type: str
    video_capture = attr.ib()  # type: cv2.VideoCapture
    total_frames = attr.ib()  # type: int
    curr_frame_idx = attr.ib()  # type: int
    curr_hwc_bgr_frame = attr.ib()  # type: ndarray
    fps = attr.ib()  # type: float


@attr.s
class VideoOpenedAndPaused(VideoPlayerState):
    video_playback_information = attr.ib()  # type: VideoPlaybackInformation


@attr.s
class VideoOpenedAndPlaying(VideoPlayerState):
    video_playback_information = attr.ib()  # type: VideoPlaybackInformation


class VideoPlayer(QMainWindow):
    def __init__(self):
        super(VideoPlayer, self).__init__()
        self.setWindowTitle('FramePerfect Video Analyzer')
        self.setGeometry(128, 128, 1280, 720)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Video display label
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet('background-color: black; color: white')
        main_layout.addWidget(self.video_label, 1)

        # Controls layout
        controls_layout = QHBoxLayout()

        # Open button
        self.open_button = QPushButton('Open Video')
        self.open_button.clicked.connect(self.open_video_callback)
        controls_layout.addWidget(self.open_button)

        # Play/Pause button
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.toggle_play_pause_callback)
        controls_layout.addWidget(self.play_button)

        # Previous frame button
        self.prev_button = QPushButton('Previous Frame')
        self.prev_button.clicked.connect(self.prev_callback)
        controls_layout.addWidget(self.prev_button)

        # Next frame button
        self.next_button = QPushButton('Next Frame')
        self.next_button.clicked.connect(self.next_callback)
        controls_layout.addWidget(self.next_button)

        # Save frame button
        self.save_button = QPushButton('Save Frame')
        self.save_button.clicked.connect(self.save_callback)
        controls_layout.addWidget(self.save_button)

        main_layout.addLayout(controls_layout)

        # Progress slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        # Enable slider tracking
        self.slider.setEnabled(True)
        self.slider.actionTriggered.connect(self.slider_action_triggered_callback)
        main_layout.addWidget(self.slider)

        # Status label
        self.status_label = QLabel('Ready')
        main_layout.addWidget(self.status_label)

        # Timer for video playback
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_callback)

        # State
        self.state = VideoPlayerState()  # type: VideoPlayerState
        self.handle_state_transition(VideoNotOpened())

    def handle_state_transition(self, new_state):
        # Cache the old state
        old_state = self.state
        # Save the new state
        self.state = new_state

        # Any state -> VideoNotOpened
        if isinstance(new_state, VideoNotOpened):
            # Clear video display label
            self.video_label.clear()

            # Disable buttons and slider
            for component in (
                    self.play_button,
                    self.prev_button,
                    self.next_button,
                    self.save_button,
                    self.slider
            ):
                component.setEnabled(False)

            # Display 'Play' on the play/pause button
            self.play_button.setText('Play')

            # Move the slider back
            self.slider.setValue(0)

            # Display 'Ready' on the status label
            self.status_label.setText('Ready')

            # Stop timer
            self.timer.stop()
        elif isinstance(new_state, VideoOpenedAndPaused):
            # VideoNotOpened -> VideoOpenedAndPaused
            if isinstance(old_state, VideoNotOpened):
                # Enable buttons and slider
                for component in (
                        self.play_button,
                        self.prev_button,
                        self.next_button,
                        self.save_button,
                        self.slider
                ):
                    component.setEnabled(True)

                # Update slider
                self.slider.setRange(0, new_state.video_playback_information.total_frames - 1)

                # Display current frame
                self.display_current_frame()
            # VideoOpenedAndPlaying -> VideoOpenedAndPaused
            elif isinstance(old_state, VideoOpenedAndPlaying):
                # Display 'Play' on the play/pause button
                self.play_button.setText('Play')

                # Stop timer
                self.timer.stop()
        elif isinstance(new_state, VideoOpenedAndPlaying):
            # VideoOpenedAndPaused -> VideoOpenedAndPlaying
            if isinstance(old_state, VideoOpenedAndPaused):
                # Display 'Pause' on the play/pause button
                self.play_button.setText('Pause')

                # Start timer
                interval = int(1000 / new_state.video_playback_information.fps)
                self.timer.setInterval(interval)
                self.timer.start()

    def load_video(self, video_path):
        # Transition to `VideoNotOpened` state
        self.handle_state_transition(VideoNotOpened())

        video_capture = cv2.VideoCapture(video_path)

        if not video_capture.isOpened():
            QMessageBox.critical(self, 'Error', 'Could not open video file %s' % video_path)
            return

        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        curr_frame_idx = 0
        fps = video_capture.get(cv2.CAP_PROP_FPS)

        ret, curr_hwc_bgr_frame_or_none = video_capture.read()
        if not ret or curr_hwc_bgr_frame_or_none is None:
            QMessageBox.critical(self, 'Error', 'Could not open video file %s' % video_path)
            return

        video_playback_information = VideoPlaybackInformation(
            video_path=video_path,
            video_capture=video_capture,
            total_frames=total_frames,
            curr_frame_idx=curr_frame_idx,
            curr_hwc_bgr_frame=curr_hwc_bgr_frame_or_none,
            fps=fps
        )

        # Transition to `VideoOpenedAndPaused` state
        self.handle_state_transition(VideoOpenedAndPaused(video_playback_information))

    def prev_frame(self):
        if isinstance(self.state, VideoOpenedAndPaused):
            video_playback_information = self.state.video_playback_information

            video_capture = video_playback_information.video_capture
            new_frame_idx = video_playback_information.curr_frame_idx - 1

            if new_frame_idx >= 0:
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, new_frame_idx)
                ret, new_hwc_bgr_frame_or_none = video_capture.read()
                if ret and new_hwc_bgr_frame_or_none is not None:
                    new_hwc_bgr_frame = new_hwc_bgr_frame_or_none

                    # Update video playback information
                    video_playback_information.curr_frame_idx = new_frame_idx
                    video_playback_information.curr_hwc_bgr_frame = new_hwc_bgr_frame
                    return True
        return False

    def next_frame(self):
        if isinstance(self.state, (VideoOpenedAndPaused, VideoOpenedAndPlaying)):
            video_playback_information = self.state.video_playback_information

            video_capture = video_playback_information.video_capture
            curr_frame_idx = video_playback_information.curr_frame_idx
            total_frames = video_playback_information.total_frames

            if curr_frame_idx >= total_frames - 1:
                return False  # Already at last frame

            ret, new_hwc_bgr_frame_or_none = video_capture.read()
            if ret and new_hwc_bgr_frame_or_none is not None:
                # Update video playback information
                video_playback_information.curr_frame_idx += 1
                video_playback_information.curr_hwc_bgr_frame = new_hwc_bgr_frame_or_none
                return True
        return False

    def seek_frame(self, new_frame_idx):
        if isinstance(self.state, VideoOpenedAndPaused):
            video_playback_information = self.state.video_playback_information

            video_capture = video_playback_information.video_capture
            total_frames = video_playback_information.total_frames

            if 0 <= new_frame_idx < total_frames:
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, new_frame_idx)
                ret, new_hwc_bgr_frame_or_none = video_capture.read()
                if ret and new_hwc_bgr_frame_or_none is not None:
                    new_hwc_bgr_frame = new_hwc_bgr_frame_or_none

                    # Update video playback information
                    video_playback_information.curr_frame_idx = new_frame_idx
                    video_playback_information.curr_hwc_bgr_frame = new_hwc_bgr_frame
                    return True
        return False

    def display_current_frame(self):
        if isinstance(self.state, (VideoOpenedAndPaused, VideoOpenedAndPlaying)):
            video_playback_information = self.state.video_playback_information

            total_frames = video_playback_information.total_frames
            curr_frame_idx = video_playback_information.curr_frame_idx
            curr_hwc_bgr_frame = video_playback_information.curr_hwc_bgr_frame

            # Convert BGR to RGB
            curr_hwc_rgb_frame = cv2.cvtColor(curr_hwc_bgr_frame, cv2.COLOR_BGR2RGB)

            # Convert to QImage
            height, width, channel = curr_hwc_rgb_frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(curr_hwc_rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

            # Scale to fit label while maintaining aspect ratio
            pixmap = QPixmap.fromImage(q_img)
            pixmap = pixmap.scaled(
                self.video_label.width(),
                self.video_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.slider.setValue(curr_frame_idx)
            self.video_label.setPixmap(pixmap)
            self.status_label.setText('Frame: %d/%d' % (curr_frame_idx + 1, total_frames))

    def open_video_callback(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Video Files (*.mp4 *.avi *.mov *.mkv *.flv)')
        video_path, _ = file_dialog.getOpenFileName(self, 'Open Video File')

        if video_path:
            self.load_video(video_path)

    def play_callback(self):
        if isinstance(self.state, VideoOpenedAndPaused):
            self.handle_state_transition(VideoOpenedAndPlaying(self.state.video_playback_information))

    def pause_callback(self):
        if isinstance(self.state, VideoOpenedAndPlaying):
            self.handle_state_transition(VideoOpenedAndPaused(self.state.video_playback_information))

    def toggle_play_pause_callback(self):
        if isinstance(self.state, VideoOpenedAndPaused):
            self.play_callback()
        elif isinstance(self.state, VideoOpenedAndPlaying):
            self.pause_callback()

    def stop_callback(self):
        if isinstance(self.state, (VideoOpenedAndPaused, VideoOpenedAndPlaying)):
            self.state.video_playback_information.video_capture.release()

        self.handle_state_transition(VideoNotOpened())

    def timer_callback(self):
        if isinstance(self.state, VideoOpenedAndPlaying):
            is_successful = self.next_frame()
            if not is_successful:
                self.pause_callback()
            self.display_current_frame()

    def prev_callback(self):
        self.pause_callback()
        if isinstance(self.state, VideoOpenedAndPaused):
            self.prev_frame()
            self.display_current_frame()

    def next_callback(self):
        self.pause_callback()
        if isinstance(self.state, VideoOpenedAndPaused):
            self.next_frame()
            self.display_current_frame()

    def seek_callback(self, new_frame_idx):
        self.pause_callback()
        if isinstance(self.state, VideoOpenedAndPaused):
            self.seek_frame(new_frame_idx)
            self.display_current_frame()

    def save_callback(self):
        self.pause_callback()
        if isinstance(self.state, VideoOpenedAndPaused):
            video_playback_information = self.state.video_playback_information
            video_path = video_playback_information.video_path
            curr_frame_idx = video_playback_information.curr_frame_idx
            curr_hwc_bgr_frame = video_playback_information.curr_hwc_bgr_frame

            # Set default filename
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            default_filename = '%s_frame_%d.png' % (video_name, curr_frame_idx)

            # Open save dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                'Save Current Frame',
                default_filename,
                'PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)'
            )

            if file_path:
                imwrite_ret = cv2.imwrite(file_path, curr_hwc_bgr_frame)
                if imwrite_ret:
                    self.status_label.setText('Frame saved to %s' % file_path)
                else:
                    QMessageBox.critical(self, 'Error', 'Could not save frame to %s' % file_path)

    def slider_action_triggered_callback(self, action):
        self.pause_callback()
        if isinstance(self.state, VideoOpenedAndPaused):
            if action == SLIDER_SINGLE_STEP_ADD:
                self.next_callback()
            elif action == SLIDER_SINGLE_STEP_SUB:
                self.prev_callback()
            elif action in (
                    SLIDER_PAGE_STEP_ADD,
                    SLIDER_PAGE_STEP_SUB,
                    SLIDER_MOVE
            ):
                self.seek_callback(self.slider.sliderPosition())

    def closeEvent(self, event):
        self.stop_callback()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    exec_and_exit(app)
