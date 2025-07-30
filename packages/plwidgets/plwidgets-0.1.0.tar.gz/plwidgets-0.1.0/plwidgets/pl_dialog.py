from PySide6 import QtWidgets, QtCore, QtGui
from .pl_style_mixin import PlStyleMixin
from .pl_resizable_mixin import PlResizableMixin
from .pl_title_bar import PlTitleBar


class PlDialog(PlStyleMixin, PlResizableMixin, QtWidgets.QDialog):
    """
    Custom dialog with a styled title bar, frameless window,
    and a content area ready for custom widgets.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Style properties
        self._backgroundColor = QtGui.QColor("#1f2227")

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)

        self._mainLayout = QtWidgets.QVBoxLayout(self)
        self._mainLayout.setContentsMargins(1, 1, 1, 1)
        self._mainLayout.setSpacing(0)

        self._titleBar = PlTitleBar(self)
        self._mainLayout.addWidget(self._titleBar)

        self._contentLayout = QtWidgets.QVBoxLayout()
        self._contentLayout.setContentsMargins(4, 4, 4, 4)
    
        self._contentArea = QtWidgets.QWidget(self)
        self._contentLayout.addWidget(self._contentArea)
        self._mainLayout.addLayout(self._contentLayout)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        color = self.property("titleBarColor") or self._backgroundColor
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(color)
        painter.drawRect(self.rect())

        pen = QtGui.QPen(QtGui.QColor("#454c58"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(self.rect().adjusted(0, 0, 0, 0))

    def setLayout(self, layout):
        self._contentArea.setLayout(layout)

    def setTitle(self, text: str):
        self._titleBar.title = text

    def addMenuWidget(self, widget: QtWidgets.QWidget):
        self._titleBar.menuArea.addWidget(widget)

    def size(self):

        rect = self.rect()
        title_rect = self._titleBar.rect()
        rect.adjust(0, title_rect.y(), 0, title_rect.height()*-1)
        return QtCore.QSize(rect.width(), rect.height())

    def contentGeometry(self):
        rect = self.rect()
        title_rect = self._titleBar.rect()
        rect.adjust(0, title_rect.y(), 0, title_rect.height()*-1)

        global_pos = self.mapToGlobal(QtCore.QPoint(0, title_rect.height()))
        return QtCore.QRect(global_pos, rect.size())

    # === Style & Property Interface ===
    
    @QtCore.Property(QtGui.QColor)
    def backgroundColor(self):
        return self._titleBarColor

    @backgroundColor.setter
    def backgroundColor(self, color: QtGui.QColor):
        self._backgroundColor = color
        self.update()