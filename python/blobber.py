#!/usr/bin/env python3

import math
import numpy
import collections
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore


def load_image(path):
    image = Image.open(path)
    image.load()
    return numpy.asarray(image, dtype="float32") / 65535.0


class Viewer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._min_x = 0
        self._max_x = 350
        self._min_y = 0
        self._max_y = 350
        self._min_z = 100
        self._max_z = 300
        self._data = numpy.array([
            load_image("Sem2_Z_16a/Sem2_Z_16a_%04d.tif" % z)
            for z in range(self._min_z, self._max_z + 1)])
            #for z in range(1365)])
        self._z = (self._min_z + self._max_z) // 2
        self._start_z = self._z
        self._reset()

    def _reset(self):
        self._start_pos = None
        self._end_pos = None
        self._radius = 0
        self._threshold_factor = 0.5

        self._clip_min = 0.0
        self._clip_max = 1.0
        self._swatch = QtGui.QColor()

        self._rot = 0
        self._profile = [0] * 100
        self._update_img()
        self.repaint()

    def _update_img(self):
        self._rot += 1.0
        #import scipy.ndimage.interpolate
        #scipy.ndimage.interpolate.rotate(self._data, 0.1, 

        zdata = self._data[self._z - self._min_z]
        w, h = zdata.shape
        d = (zdata - self._clip_min) / ((self._clip_max - self._clip_min) or 1)
        d = numpy.uint8(numpy.clip(d * 255, 0, 255))
        d = numpy.dstack((d, d, d, d))
        print(d.shape)
        self._img = QtGui.QImage(d, w, h, w*4, QtGui.QImage.Format_RGB32)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.drawImage(0, 0, self._img)
        painter.fillRect(self._img.width() + 10, 10, 100, 100, self._swatch)

        painter.setPen(QtGui.QColor(0, 0, 0))
        x0 = self._img.width() + 10
        y0 = 120
        graph_max = max(self._profile) or 1
        for x in range(100):
            v = (100 * self._profile[x]) // graph_max
            #print(x, v)
            painter.drawLine(x0+x, y0 + 100, x0+x, y0 + 100 - v)
        painter.setPen(QtGui.QColor(255, 0, 0))
        x = 100 * self._threshold_factor
        painter.drawLine(x0+x, y0, x0+x, y0 + 100)
        if self._start_pos is not None:
            #painter.drawLine(self._start_pos, self._end_pos)
            x = self._start_pos.x()
            y = self._start_pos.y()
            r = self._radius
            dz = abs(self._z - self._start_z)
            r = math.sqrt(r*r - dz*dz) if dz < r else 0
            painter.setPen(QtGui.QColor(255, 255, 255, 100))
            painter.drawArc(x - r, y - r, 2 * r, 2 * r, 0, 5760)
            self.fill_blob(painter, x, y, r)

        painter.end()

    def fill_blob(self, painter, x0, y0, r0):
        tf = self._threshold_factor
        threshold = (1.0 - tf) * self._clip_min + tf * self._clip_max
        polygon = QtGui.QPolygonF()
        zdata = self._data[self._z - self._min_z]

        center_v = zdata[y0][x0]
        segs = 64
        for seg in range(segs):
            r = r0
            motion = r0 / 5
            dx = math.cos(math.radians(seg * 360 / segs))
            dy = math.sin(math.radians(seg * 360 / segs))
            for i in range(10):
                x = int(x0 + r * dx)
                y = int(y0 + r * dy)
                circle_v = zdata[y][x]
                outer_v = zdata[y+dy*motion][x+dx*motion]

                # Heading for brighter
                if center_v < threshold:
                    if circle_v < outer_v:
                        r += motion / 2
                    else:
                        r -= motion / 2
                else:
                    if circle_v < outer_v:
                        r -= motion / 2
                    else:
                        r += motion / 2
                motion /= 2
            polygon.append(QtCore.QPointF(x, y))
        painter.setBrush(QtGui.QColor(255, 0, 0, 100))
        painter.drawPolygon(polygon)

    def mousePressEvent(self, event):
        self._start_pos = event.pos()
        self._start_z = self._z

    def mouseMoveEvent(self, event):
        self._end_pos = event.pos()
        dx = abs(self._end_pos.x() - self._start_pos.x())
        dy = abs(self._end_pos.y() - self._start_pos.y())
        self._radius = math.sqrt(dx * dx + dy * dy)

        zdata = self._data[self._z - self._min_z]
        c = 255 * zdata[self._end_pos.y()][self._end_pos.x()]
        self._swatch = QtGui.QColor(c, c, c)

        self._calc_graph()
        self._update_img()
        self.repaint()

    def mouseReleaseEvent(self, event):
        self._end_pos = event.pos()
        self._calc_graph()
        self._update_img()
        self.repaint()
        if self._end_pos == self._start_pos:
            print("RESET")
            self._reset()

    def wheelEvent(self, event):
        direction = 1 if event.angleDelta().y() < 0 else -1
        if event.buttons():
            self._threshold_factor += 0.01 * direction
            if self._threshold_factor > 1.0:
                self._threshold_factor = 1.0
            if self._threshold_factor < 0.0:
                self._threshold_factor = 0.0
        else:
            self._z += direction
            if self._z < self._min_z:
                self._z = self._min_z
            if self._z > self._max_z:
                self._z = self._max_z
            self._update_img()
        self.repaint()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Down:
            self._start_z += 1
            self.repaint()
        elif key == QtCore.Qt.Key_Up:
            self._start_z -= 1
            self.repaint()
        elif key == QtCore.Qt.Key_Left:
            self._radius -= 1
            self.repaint()
        elif key == QtCore.Qt.Key_Right:
            self._radius += 1
            self.repaint()

    def _calc_graph(self):
        x0 = self._start_pos.x()
        y0 = self._start_pos.y()
        r = self._radius

        r2 = r * r
        samples = []
        zdata = self._data[self._z - self._min_z]
        for y in range(int(-r), int(r)):
            for x in range(int(-r), int(r)):
                d2 = x*x + y*y
                if d2 < r2:
                    samp = zdata[y0+y][x0+x]
                    samples.append(samp)
                    d = math.sqrt(d2)
        a = min(samples)
        b = max(samples)

        profile = [0] * 100
        for d in samples:
            c = int(99 * (d - a) / (b - a))
            profile[c] += 1
        self._clip_min = a
        self._clip_max = b
        self._profile = profile





def main():
    app = QtWidgets.QApplication([])
    dialog = Viewer()
    dialog.move(30, 100)
    dialog.resize(800, 700)
    dialog.show()
    app.exec_()


if __name__ == "__main__":
    main()
