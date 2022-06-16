
import sys, time, os, math
import cv2
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

import Ui_Album, Ui_Camera


class CameraInit(QMainWindow, Ui_Camera.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CameraInit, self).__init__(parent)  # 初始化父类

        self.timer_camera = QtCore.QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture(0)
        self.CAM_NUM = 0
        self.setupUi(self)  # 初始化程序界面
        self.slot_init()  # 初始化槽函数

        self.win = AlbumInit()

    def slot_init(self):
        # 初始化槽
        self.timer_camera.timeout.connect(self.show_camera)
        self.button_open_camera.clicked.connect(self.button_open_camera_click)
        self.button_album.clicked.connect(self.button_open_album)
        self.button_cap.clicked.connect(self.capx)
        # self.close_camera.clicked.connect(self.closeEvent)

    def button_open_album(self):
        # 打开相册
        self.win.image_widget.list_files.clear()
        self.win.image_widget.get_files("./images")
        self.win.image_widget.show_images_list()
        self.win.show()

    def button_open_camera_click(self):
        if not self.timer_camera.isActive():#若定时器未启动
            flag = self.cap.read()
            self.cap.set(3, 320.0)
            self.cap.set(4, 240.0)
            if not flag:
                QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确",
                                              buttons=QtWidgets.QMessageBox.Ok,
                                              defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.timer_camera.start(30)# 定时器开始计时30ms，每过30ms从摄像头中取一帧显示

                self.button_open_camera.setText(u'关闭相机')
        else:
            self.timer_camera.stop()
            # self.cap.release()
            self.label_show_camera.clear()
            self.button_open_camera.setText(u'打开相机')

    def show_camera(self):
        flag, self.image = self.cap.read()

        image_t = self.image

        # 人脸检测
        face_detector = cv2.CascadeClassifier('./haarcascade_frontalface_alt.xml')

        # 沿y轴翻转图像，0沿着x轴翻转，小于0沿x和y轴翻转
        image_t = cv2.flip(image_t, 1)
        # 如果读取到图像
        if flag:
            # 将图像做灰度化处理
            gray = cv2.cvtColor(image_t, code=cv2.COLOR_BGR2GRAY)
            # 调用面部识别并返回坐标
            faces = face_detector.detectMultiScale(gray)

            # 用正方形框出人脸
            for x, y, w, h in faces:
                cv2.rectangle(image_t,
                              pt1=(x, y),
                              pt2=(x + w, y + h),
                              color=[0, 0, 255],
                              thickness=2)
                # 沿y轴翻转图像，0沿着x轴翻转，小于0沿x和y轴翻转
                self.image = cv2.flip(self.image, 1)

                value = 10
                part = self.image[x:x+w, y:y+h]#截取人脸区域
                part = cv2.bilateralFilter(part, value, value * 2, value / 2)  # 美颜处理
                self.image[x:x+w, y:y+h] = part#人脸美颜后重新放入原图片

                # 先将图⽚转化为float32类型，再除以255，得到0-1之间的数
                image_np = self.image.astype(np.float32) / 255

                # 设置调整颜色参数，小于1时，数值越小，越具有美白效果。反之，大于1时数值越大
                gamma1 = 0.6
                # 美白功能
                whitening = np.power(image_np, gamma1)
                # whitening = (whitening * 255).astype(np.uint8)

                # 去除噪点
                denoise = cv2.medianBlur(whitening, 5)

                # float32转unit8
                self.image = (denoise * 255).astype(np.uint8)

        show = cv2.resize(image_t, (640, 480))  # 把读到的帧的大小重新设置
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色

        self.showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                      QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(self.showImage))  # 往显示视频的Label里显示QImage

    def capx(self):

        FName = fr"./images/cap{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
        cv2.imwrite(FName + ".jpg", self.image)
        print(FName)
        # self.label_2.setPixmap(QtGui.QPixmap.fromImage(self.image))
        show = cv2.resize(self.image, (160, 120))  # 把读到的帧的大小重新设置为 640x480
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
        # print(show.shape[1], show.shape[0])
        # show.shape[1] = 320
        # show.shape[0] = 240
        self.showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                      QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.cap_label.setPixmap(QtGui.QPixmap.fromImage(self.showImage))
        self.showImage.save(FName + ".jpg", "JPG", 100)  # 100是指保存图片的质量因子

    def closeEvent(self, event):
        ok = QtWidgets.QPushButton()
        cacel = QtWidgets.QPushButton()

        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, u"关闭", u"是否关闭！")

        msg.addButton(ok, QtWidgets.QMessageBox.ActionRole)
        msg.addButton(cacel, QtWidgets.QMessageBox.RejectRole)
        ok.setText(u'确定')
        cacel.setText(u'取消')
        if msg.exec_() == QtWidgets.QMessageBox.RejectRole:
            event.ignore()
        else:
            if self.cap.isOpened():
                self.cap.release()
            if self.timer_camera.isActive():
                self.timer_camera.stop()
            event.accept()


class AlbumInit(QWidget, Ui_Album.Ui_Form):
    def __init__(self):
        super(AlbumInit, self).__init__()
        self.setupUi(self)
        # 添加自定义图像组件
        self.image_widget = ImageWidget(self, dir='images', col=4, w=600)
        self.image_widget.move(20, 100)
        self.slot_init()

    def slot_init(self):
        self.pB_previous.clicked.connect(lambda: self.image_widget.turn_page(-1))
        self.pB_next.clicked.connect(lambda: self.image_widget.turn_page(1))  # 图像列表翻页
        self.closep.clicked.connect(self.close)
        self.deletep.clicked.connect(self.image_widget.delete_picture)
        self.image_widget.signal_order.connect(self.change_path)
        self.image_widget.signal_page.connect(self.change_page)

    def change_path(self, path):
        self.lineEdit_path.setText(path)

    def change_page(self, index):
        self.lineEdit_page.setText(f"第{index}页")


class ImageWidget(QWidget):
    group_num = 1  # 图像列表当前组数（页数）
    list_files = []  # 图像文件路径集
    signal_order = pyqtSignal(str)  # 图像项目信号
    signal_page = pyqtSignal(int)  # 页数信号

    def __init__(self, parent=None, dir='./', col=1, w=10, h=None, suit=0):
        super(ImageWidget, self).__init__(parent)
        self.get_files(dir)
        self.col = col
        self.w = w
        self.suit = suit
        self.choose = None
        if h is None:
            self.h = self.w / self.col
        else:
            self.h = h
        self.setFixedSize(self.w, self.h)
        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.show_images_list()  # 初次加载形状图像列表

    def get_files(self, dir):  # 储存当前页需加载的图像路径
        for file in os.listdir(path=dir):  # 读取图像路径
            if file.endswith('jpg') or file.endswith('png'):
                self.list_files.append(dir + "/" + file)

    def show_images_list(self):  # 加载图像列表
        for i in range(self.hbox.count()):  # 每次加载先清空内容，避免layout里堆积label
            self.hbox.itemAt(i).widget().deleteLater()
        # 设置分段显示图像，每col个一段
        group_num = self.group_num
        start = 0
        end = self.col
        if group_num > 1:
            start = self.col * (group_num - 1)
            end = self.col * group_num
        count = 0  # 记录当前页载入的label数
        width = int(self.w / self.col)  # 自定义label宽度
        height = self.h  # 自定义label高度
        for index, path in enumerate(self.list_files):  # group_num = 1 则加载前col个，以此类推
            if index < start:
                continue
            elif index == end:
                break
            # 按路径读取成QPixmap格式的图像，根据适应方式调整尺寸
            if self.suit == 0:
                pix = QPixmap(path).scaled(width - 2 * self.col, height - 4)
            elif self.suit == 1:
                pix = QPixmap(path)
                pix = QPixmap(path).scaled(int(pix.width() * height / pix.height()) - 2 * self.col, height - 4)
            elif self.suit == 2:
                pix = QPixmap(path)
                pix = QPixmap(path).scaled(width - 2 * self.col, int(pix.height() * width / pix.width()) - 4)
            label = MyLabel(index)
            label.setPixmap(pix)  # 加载图片
            self.hbox.addWidget(label)  # 在水平布局中添加自定义label
            label.signal_order.connect(self.choose_image)  # 绑定自定义label点击信号
            count += 1
        if not count == self.col:
            for i in range(self.col - count):
                label = QLabel()
                self.hbox.addWidget(label)  # 在水平布局中添加空label补位

    def turn_page(self, num):  # 图像列表翻页
        flag = len(self.list_files)
        if self.group_num == 1 and num == -1:  # 到首页时停止上翻
            QMessageBox.about(self, "Remind", "This is the first page!")
        elif (self.group_num == math.ceil(flag / self.col) and num == 1) or flag == 0:  # 到末页时停止下翻
            QMessageBox.about(self, "Remind", "No more image! ")
        else:
            self.group_num += num  # 翻页
        self.signal_page.emit(self.group_num)
        self.show_images_list()  # 重新加载图像列表

    def choose_image(self, index):  # 选择图像
        lit = self.list_files[index].split('/')[2]  # 分离出文件名
        self.choose = self.list_files[index]
        self.signal_order.emit(lit)  # 把文件名显示在屏幕上

    def delete_picture(self, index):
        os.remove("./" + self.choose)
        self.list_files.clear()
        self.get_files("./images")
        self.show_images_list()


class MyLabel(QLabel):  # 自定义label，用于传递是哪个label被点击了
    signal_order = pyqtSignal(int)

    def __init__(self, order=None):
        super(MyLabel, self).__init__()
        self.order = order
        self.setStyleSheet("border-width: 2px; border-style: solid; border-color: gray")

    def mousePressEvent(self, e):  # 重载鼠标点击事件
        self.signal_order.emit(self.order)

    def clear(self):
        self.clear()


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    Camera = CameraInit()
    Camera.show()

    sys.exit(App.exec_())
