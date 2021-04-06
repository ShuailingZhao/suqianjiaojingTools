import numpy as np
import pyqtgraph as pg
import sys
from PyQt5.QtWidgets import QWidget,QApplication,QFrame,QGridLayout,QLabel,QPushButton,QVBoxLayout
from PyQt5.QtCore import Qt,QTimer
import math
import matplotlib.pyplot as plt
from scipy import signal
import pywt

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

def getFittingData(data, fittingPointNum = 70, interval = 1):
	fittingShowData = []
	fittingShowData = data[0:fittingPointNum]
	for preInd in range(fittingPointNum, len(data)):
		fittingData = data[preInd-fittingPointNum:preInd]
		fittingData = fittingData[::interval]
		z1 = np.polyfit(range(preInd-fittingPointNum, preInd, interval), fittingData, 3) # 用3次多项式拟合
		p1 = np.poly1d(z1)
		
#		if preInd==400:
#			plt.plot(range(preInd-fittingNum, preInd), p1(range(preInd-fittingNum, preInd)), color="b",linestyle = "-")
			
#		print('---- ', p1(preInd))
		fittingShowData.append(p1(preInd))
	return fittingShowData


def getDataOf(carInd, path):
	dataLoader = txtLoader(path)
	carsInfo = []
	frameCount = -1
	while True:
		frameCount+=1
		oneRowCarsInfo = dataLoader.nextRow()
		if(oneRowCarsInfo[0] == ''):
			break
		carsInfo.append(splitToCarInfo(oneRowCarsInfo))
	
	
	carSpecificData=[]
	for frameIndex in range(len(carsInfo)):
#		print('+++++ ', frameIndex)
		for carkey, carValue in carsInfo[frameIndex].items():
			if carkey == carInd:
				carSpecificData.append(carsInfo[frameIndex][carkey])
	return carSpecificData

def noLargerfilterData(showData):
	for showDataInd in range(1, len(showData)):
		if showData[showDataInd]>showData[showDataInd-1]:
			showData[showDataInd] = showData[showDataInd-1]
	return showData

def noLessfilterData(showData):
	for showDataInd in range(1, len(showData)):
		if showData[showDataInd]<showData[showDataInd-1]:
			showData[showDataInd] = showData[showDataInd-1]
	return showData

def getDelta(data):
	delta = []
	for dataInd in range(1, len(data)):
		delta.append(data[dataInd] - data[dataInd-1])
	delta.append(delta[-1])
	
	return delta		


def mean_filter(kernel_size, data):
	if kernel_size%2==0 or kernel_size<=1:
		print('kernel_size滤波核的需为大于1的奇数')
		return
	else:
		padding_data = []
		mid = kernel_size//2
		for i in range(mid):
			padding_data.append(data[0])
		padding_data.extend(data)
		for i in range(mid):
			padding_data.append(data[-1])
	result = []
	for i in range(0, len(padding_data)-2*mid, 1):
		temp = 0
		for j in range(kernel_size):
			temp += padding_data[i+j]
		temp = temp / kernel_size
		result.append(temp)
	return result

def Exponential_Weighted_average(data, alpha1):
	result = []
	temp = data[0]
	for i in range(len(data)):
		temp = alpha1*temp + (1-alpha1)*data[i]
		result.append(temp)
	return result

def Exponential_DelaWeighted_average(data, delta, alpha1):
	result = [data[0]]
	
	for i in range(1,len(data)):
		temp = data[i-1]+delta[i-1]
#		temp = result[-1]+delta[i-1]
		tempRet = alpha1*temp + (1-alpha1)*data[i]
		result.append(tempRet)
	return result

def get_gaussian_kernel(kernel_size):
	kernel = []
	for i in range(kernel_size//2 + 1, 0, -1):
		kernel.append(np.exp(-i**2/2))
	for j in range(kernel_size//2 -1, -1, -1):
		kernel.append(kernel[j])
	kernel = np.array(kernel)
	kernel = kernel / np.sum(kernel)
	return kernel

def Gaussian(kernel_size, data):
	if kernel_size%2==0 and kernel_size<=1:
		print('输入size必须为大于1的基数')
		return
	padding_data = []
	mid = kernel_size//2
	for i in range(mid):
		padding_data.append(0)
	padding_data.extend(data)
	for i in range(mid):
		padding_data.append(0)
        
	kernel = get_gaussian_kernel(kernel_size)
	result = []
	for i in range(0, len(padding_data)-2*mid, 1):
		temp = 0 
		for j in range(kernel_size):
			temp += kernel[j]*padding_data[i+j]
		result.append(temp)
	return result

def Wavelet_Transform(data):
	w = pywt.Wavelet('db8')  # 选用Daubechies8小波
	maxlev = pywt.dwt_max_level(len(data), w.dec_len)
	coeffs = pywt.wavedec(data, 'db8', level=maxlev)
	for i in range(1, len(coeffs)):
		coeffs[i] = pywt.threshold(coeffs[i], 0.8*max(coeffs[i]))
	result = pywt.waverec(coeffs, 'db8')
	return result
	
def ShakeOff(inputs,N):
	usenum = inputs[0]								#有效值
	i = 0 											#标记计数器
	for index,tmp in enumerate(inputs):
		if tmp != usenum:					
			i = i + 1
			if i >= N:
				i = 0
				inputs[index] = usenum
	return inputs

def AmplitudeLimitingShakeOff(inputs,Amplitude,N):
	#print(inputs)
	tmpnum = inputs[0]
	for index,newtmp in enumerate(inputs):
		if np.abs(tmpnum-newtmp) > Amplitude:
			inputs[index] = tmpnum
		tmpnum = newtmp
	#print(inputs)
	usenum = inputs[0]
	i = 0
	for index2,tmp2 in enumerate(inputs):
		if tmp2 != usenum:
			i = i + 1
			if i >= N:
				i = 0
				inputs[index2] = usenum
	#print(inputs)
	return inputs

def WeightBackstepAverage(inputs):
	weight = np.array(range(1,np.shape(inputs)[0]+1))			#权值列表
	weight = weight/weight.sum()
 
	for index,tmp in enumerate(inputs):
		inputs[index] = inputs[index]*weight[index]
	return inputs

def ArithmeticAverage(inputs,per):
	if np.shape(inputs)[0] % per != 0:
		lengh = np.shape(inputs)[0] / per
		for x in range(int(np.shape(inputs)[0]),int(lengh + 1)*per):
			inputs = np.append(inputs,inputs[np.shape(inputs)[0]-1])
	inputs = inputs.reshape((-1,per))
	mean = []
	for tmp in inputs:
		mean.append(tmp.mean())
	return mean



if __name__ == '__main__':
	debugCarInd = 1510 # The show car ID
	path = './data/nanCarData.txt'
	carSpecificData = getDataOf(debugCarInd, path)
	for data in carSpecificData:
		print('--- ', data)
	
	showIndex = 2 # carId,x,y,w,h,realW
	showData = [i[showIndex] for i in carSpecificData]
	
	showData = noLargerfilterData(showData)
	delta = getDelta(showData)
	b, a = signal.butter(8, 0.3, 'lowpass')   #配置滤波器 8 表示滤波器的阶数
	filterDelta = signal.filtfilt(b, a, delta)  #data为要过滤的信号
#	filterDelta = ArithmeticAverage(delta,5)
	filterShowData = signal.filtfilt(b, a, showData)  #data为要过滤的信号

	
	plt.figure()
	plt.plot(range(len(showData)), showData, color="r",linestyle = "--")
	plt.plot(range(len(filterShowData)), filterShowData, color="g",linestyle = "-.")
	
	plt.figure()
	plt.plot(range(len(delta)), delta, color="b",linestyle = "-")
	plt.plot(range(len(filterDelta)), filterDelta, color="g",linestyle = "-")


#	fittingShowData = getFittingData(showData)
#	plt.plot(range(len(fittingShowData)), fittingShowData, color="b",linestyle = "-")
	
	plt.show()
		
	

