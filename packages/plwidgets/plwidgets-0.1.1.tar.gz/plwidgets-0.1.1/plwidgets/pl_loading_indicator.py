from PySide6 import QtWidgets, QtCore, QtGui
from .pl_style_mixin import PlStyleMixin


class PlLoadingIndicator(PlStyleMixin, QtWidgets.QWidget):
    """
    A simple animated circular loading spinner.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._color = QtGui.QColor("#5683d1")
        self._thickness = 4
        self._speed = 2

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.rotate)
        self._timer.start(16)

        self.setMinimumSize(32, 32)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def rotate(self):
        self._angle = (self._angle + self._speed) % 360
        self.update()

    def paintEvent(self, _: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        size = min(self.width(), self.height())

        pen = QtGui.QPen(self._color, self._thickness)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)

        arc_rect = QtCore.QRectF(
            self._thickness, self._thickness,
            size - 2 * self._thickness,
            size - 2 * self._thickness
        )

        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        painter.translate(-self.width() / 2, -self.height() / 2)

        painter.drawArc(arc_rect, 0 * 16, 90 * 16)

    # === Style & Property Interface ===

    @QtCore.Property(QtGui.QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.update()

    @QtCore.Property(int)
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        self.update()

    @QtCore.Property(int)
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value
