import numpy as np
import pyqtgraph as pg
import sys
from PyQt5.QtWidgets import QWidget,QApplication,QFrame,QGridLayout,QLabel,QPushButton,QVBoxLayout
from PyQt5.QtCore import Qt,QTimer
import math
import matplotlib.pyplot as plt

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
		retData = self.extractSpecificData(carId, 1)
		return retData
#		return 	self.trackData
		
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

            

def splitToCarInfo(rowData):
		carsInfo = {}
		carInfoLen = 6
		for index in range(math.floor(len(rowData)/carInfoLen)):
			carsInfo[int(rowData[index*carInfoLen+1])] = [int(rowData[0]), int(rowData[index*carInfoLen+2]), int(rowData[index*carInfoLen+3]), int(rowData[index*carInfoLen+4]), int(rowData[index*carInfoLen+5]), float(rowData[index*carInfoLen+6])]
		return carsInfo

if __name__ == '__main__':
	debugCarInd = 1861
	path = './data/nanCarData.txt'
	dataLoader = txtLoader(path)
	
	carsInfo = []
	frameCount = -1
	while True:
		frameCount+=1
		print('---- ', frameCount)
		oneRowCarsInfo = dataLoader.nextRow()
		if(oneRowCarsInfo[0] == ''):
			break
		carsInfo.append(splitToCarInfo(oneRowCarsInfo))
	
	
	carSpecificData=[]
	for frameIndex in range(len(carsInfo)):
#		print('+++++ ', frameIndex)
		for carkey, carValue in carsInfo[frameIndex].items():
			if carkey == debugCarInd:
				carSpecificData.append(carsInfo[frameIndex][carkey])


	for data in carSpecificData:
		print('--- ', data)
	
	showIndex = 2
	showData = [i[showIndex] for i in carSpecificData]
	
	for showDataInd in range(1, len(showData)):	
		if showData[showDataInd]>showData[showDataInd-1]:
			showData[showDataInd] = showData[showDataInd-1]
	
	fittingNum = 70
	interval = 1
	plt.figure()
	plt.plot(range(len(showData)), showData, color="r",linestyle = "--")
	
	fittingShowData = []
	fittingShowData = showData[0:fittingNum]
	for preInd in range(fittingNum, len(showData)):
		fittingData = showData[preInd-fittingNum:preInd]
		fittingData = fittingData[::interval]
		z1 = np.polyfit(range(preInd-fittingNum, preInd, interval), fittingData, 3) # 用3次多项式拟合
		p1 = np.poly1d(z1)
		
#		if preInd==400:
#			plt.plot(range(preInd-fittingNum, preInd), p1(range(preInd-fittingNum, preInd)), color="b",linestyle = "-")
			
		print('---- ', p1(preInd))
		fittingShowData.append(p1(preInd))
	
#	plt.plot(range(len(fittingShowData)), fittingShowData, color="b",linestyle = "-")
	
	plt.show()
		
	

