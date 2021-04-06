import numpy as np
import pyqtgraph as pg
import sys
from PyQt5.QtWidgets import QWidget,QApplication,QFrame,QGridLayout,QLabel,QPushButton,QVBoxLayout
from PyQt5.QtCore import Qt,QTimer
import math


class txtLoader:
	def __init__(self, dataPath):
		self.f = open(dataPath,"r")

	def nextRow(self):
		oneLine = self.f.readline().strip('\n')
		data = oneLine.split(',')
		return data
	
	def close(self):
		self.f.close()


class trackLoader:
	def __init__(self, dataPath):
		self.trackDataLoader = txtLoader(dataPath)
		self.trackData={}
		self.trackDataDisappearFrame={}
		self.maxDisappearFrame=5

	def updateData(self, carId):
		retData = []
		rowData = self.trackDataLoader.nextRow()
		carsInfo = self.splitToCarInfo(rowData)
		if carId not in carsInfo:
			return retData
		
		for carsInfoKey, carInfoValue in carsInfo.items():
			if carsInfoKey in self.trackData:
				self.trackData[carsInfoKey].append(carInfoValue)
			else:
				self.trackData[carsInfoKey] = [carInfoValue]
		
		for trackDataKey in list(self.trackData.keys()):
			if trackDataKey not in carsInfo:
				self.recordDisappearTimes(trackDataKey)
				self.EraseExceedMaxDisappearFrameTrackData(trackDataKey)
#		self.printTrackData()
#		retData = self.extractSpecificData(carId, 1)
#		return retData

		return 	self.trackData
		
	def recordDisappearTimes(self, trackDataKey):
		for index in range(len(self.trackData[trackDataKey])):
			self.trackData[trackDataKey][index][-1]+=1
	
	def EraseExceedMaxDisappearFrameTrackData(self, trackDataKey):
		if self.trackData[trackDataKey][0][-1]>=self.maxDisappearFrame:
			self.trackData.pop(trackDataKey)
		
	
	def splitToCarInfo(self, rowData):
		carsInfo = {}
		carInfoLen = 6
		for index in range(math.floor(len(rowData)/carInfoLen)):
			carsInfo[int(rowData[index*carInfoLen+1])] = [int(rowData[0]), int(rowData[index*carInfoLen+2]), int(rowData[index*carInfoLen+3]), int(rowData[index*carInfoLen+4]), int(rowData[index*carInfoLen+5]), float(rowData[index*carInfoLen+6]), 0]
		return carsInfo
	
	def printTrackData(self):
		for key, value in self.trackData.items():
			for index in range(len(value)):
				print(key, ' -- ', value[index])
				
	def extractSpecificData(self, key, valueIndex):
		retValue = []
		if key not in self.trackData:
			return retValue

		for index in range(len(self.trackData[key])):
			reValue.append(self.trackData[key][index][valueIndex])
		return retValue
			
		
	def close(self):
		self.trackDataLoader.close()

            
class Example(QWidget):

	def __init__(self, dataPath):
		super(Example, self).__init__()
		self.initUI()
		self.generate_image()
		self.carTrackData = trackLoader(dataPath)
		self.frameIndex=0

	def initUI(self):
		self.setGeometry(200,200,1000,800)#窗口的位置和大小
		self.setWindowTitle("实时刷新正余弦波形图")
		self.gridLayout = QGridLayout(self)

		self.frame = QFrame(self)
		self.frame.setFrameShape(QFrame.Panel)#边框样式
		self.frame.setFrameShadow(QFrame.Plain)
		self.frame.setLineWidth(2)
		self.frame.setStyleSheet("background-color:rgb(0,255,255);")

		self.label = QLabel(self)
		self.label.setText("正弦函数&余弦函数")
		self.label.setAlignment(Qt.AlignCenter)

		self.button = QPushButton(self)
		self.button.setText("生成波形图")
		self.button.clicked.connect(self.btnClick)

		self.gridLayout.addWidget(self.frame,0,0,1,2)#将边框，标签，按钮添加到分布对象
		self.gridLayout.addWidget(self.label,1,0,1,1)
		self.gridLayout.addWidget(self.button,1,1,1,1)

		self.setLayout(self.gridLayout)

	def generate_image(self):
		verticalLayout = QVBoxLayout(self.frame)
		win = pg.GraphicsLayoutWidget(self.frame)
		verticalLayout.addWidget(win)
		p = win.addPlot(title="动态波形图")
		p.showGrid(x=True,y=True)
		p.setLabel(axis="left",text="Amplitude / V")
		p.setLabel(axis="bottom",text="t / s")
		#        p.setRange(xRange=[0,2], yRange=[0,1.5], padding=0)
		p.setTitle("y1 = sin(x)  y2 = cos(x)")
		p.addLegend()

		self.curve1 = p.plot(pen="r",name="y1")
		self.curve2 = p.plot(pen="g",name="y2")

		self.Fs = 1024.0 #采样频率
		self.N = 1024    #采样点数
		self.f0 = 4.0    #信号频率
		self.pha = 0     #初始相位
		self.t = np.arange(self.N) / self.Fs    #时间向量 1*1024的矩阵

	def plotData(self):
		self.frameIndex+=1
		showCarId = 6
		data = self.carTrackData.updateData(showCarId)
#		print('======= ', self.frameIndex, ' , ', data)
		self.pha += 10
		self.curve1.setData(range(len(data)) , data)
		
	def btnClick(self):
		self.button.setText("再次点击加速！")
		timer = QTimer(self)
		timer.timeout.connect(self.plotData)
		timer.start(100)#定时器的触发间隔
	def close(self):
		self.carTrackData.close()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Example('./data/nanCarData.txt')
	ex.show()
	sys.exit(app.exec_())
	Example.close()
