import time
import random
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


def random_color():
    return "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])


class CarList:
    def __init__(self, plot):
        self.carDic = {}
        self.plot = plot

    def update(self, cars):
        cid_set = set()
        for cid, lon, lat in cars:
            if cid not in self.carDic:
                car = Car(cid)
                car.append_ll(lon, lat)
                self.carDic[cid] = car
                #self.plot.addItem(car.scatter)
                self.plot.addItem(car.plot)
                self.plot.addItem(car.text)
            else:
                car = self.carDic[cid]
                car.append_ll(lon, lat)
            cid_set.add(cid)

        klist = []
        for k in self.carDic:
            if k not in cid_set:
                self.carDic[k].lost+=1
            else:
                self.carDic[k].lost=0
            # 这辆车更新连续5次没有,删除轨迹
            if self.carDic[k].lost>5:
                klist.append(k)

        for k in klist:
            sc = self.carDic.get(k)
            self.carDic.pop(k)
            self.plot.removeItem(sc.plot)
            self.plot.removeItem(sc.text)
            print('pop car:{}'.format(k))


class Car:
    def __init__(self, cid):
        self.cid = cid
        self.lons = []
        self.lats = []
        self.lost = 0
        color = random_color()
        # self.scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=1, color=color), symbol='o', size=1)
        self.plot = pg.PlotCurveItem(pen=pg.mkPen(width=1, color=color), symbol='o', size=1)
        self.text = pg.TextItem(cid,color)

    def append_ll(self, lon, lat):
        self.lons.append(lon)
        self.lats.append(lat)
        self.plot.setData(self.lons,self.lats)
        self.text.setPos(lon,lat)
        #self.scatter.setData(self.lons, self.lats)



class TrackDataLoader:
    def __init__(self, dataPath):
        self.lines = []
        with open(dataPath) as f:
            content = f.readlines()
        self.lines = [x.strip() for x in content]
        self.size = len(self.lines)
        self.idx = -1

    def next(self):
        self.idx+=1
        if self.idx>=self.size:
            return False, None
        else:
            return True, self.lines[self.idx]

def loadMap(path):
    with open(path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    laneDic = {}
    for line in content:
        items = line.replace("\"", "").split(",")
        lonlat = items[:-1]
        laneId = items[-1:][0]

        if laneId in laneDic.keys():
            laneDic[laneId].append(lonlat)
        else:
            laneDic[laneId] = [lonlat]
    return laneDic


laneDic = loadMap("./data/ObjectPL4.csv")
trackData = TrackDataLoader('./data/nanCarTrackData.txt')


class Graph:
    def __init__(self, ):
        self.speInd=-1
        self.frameLon = []
        self.frameLat = []
        self.maxLen = 50  # max number of data points to show on graph
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow()

        self.p1 = self.win.addPlot(colspan=2)

        # self.win.nextRow()
        self.curve1 = self.p1.plot()

        qpen = pg.mkPen(width=1, color=pg.mkColor("#6b6b6b"))

        for laneId in laneDic.keys():
            # 一条车道线上的所有线段
            laneFragList = laneDic[laneId]
            for frag in laneFragList:
                lon = []
                lat = []
                for ll in frag:
                    lonlat = ll.split()
                    lon.append(float(lonlat[0]))
                    lat.append(float(lonlat[1]))

                    lanePlot = self.p1.plot()
                    lanePlot.setData(lon, lat, pen=qpen)

        self.carList = CarList(self.p1)
        graphUpdateSpeedMs = 20
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(graphUpdateSpeedMs)
        QtGui.QApplication.instance().exec_()

    def update(self):
        have, line = trackData.next()
        self.speInd+=1
        if have:
            items = line.split(',')
            if len(items) < 2:
                return
            fid = items[0]
            print('processing frame {}'.format(fid))
            fcars = []
            num = int((len(items) - 1) / 3)
            for i in range(0, num):
                cid = items[1 + i * 3]
                lon = items[1 + i * 3 + 1]
                lat = items[1 + i * 3 + 2]
                fcars.append((cid, float(lon), float(lat)))
            self.carList.update(fcars)
            self.app.processEvents()


if __name__ == '__main__':
    g = Graph()

