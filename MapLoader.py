import matplotlib.pyplot as plt
from readWriteCsv import readCSV, writeCSV

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


laneDic = loadMap("./ObjectPL4.csv")

fig, ax = plt.subplots(figsize=(20, 10))

# maxLon = 116.295246632126
# minLon = 116.292585454555
# maxLat = 40.102184344432
# minLat = 40.0986955981234
# plt.axis('off')
vv = 0.0001

cameraPosNan=[116.29368250986,40.100478997299,37.298996113241]
cameraPosBei=[116.2936512593,40.100515399623,37.306298596784]

ax.scatter(cameraPosNan[0], cameraPosNan[1], c='r', marker='*', s=3, linewidths=10)
ax.scatter(cameraPosBei[0], cameraPosBei[1], c='r', marker='*', s=3, linewidths=10)

writeFileName='./testWrite.csv'


for laneId in laneDic.keys():
    print('---------- ', laneId)
    oneLane=[]
    # 一条车道线上的所有线段
    laneFragList = laneDic[laneId]
#    print(len(laneFragList), len(laneFragList[0]), laneFragList[0])
    segCount = 0
    for frag in laneFragList:
        # 存储一个线段上的经纬度点
        lon = []
        lat = []

        for ll in frag:
            lonlat = ll.split()
            lon.append(float(lonlat[0]))
            lat.append(float(lonlat[1]))
            oneLane.append(float(lonlat[0]))
            oneLane.append(float(lonlat[1]))
#            if '3' == laneId and 16 == segCount:
#                ax.scatter(float(lonlat[0]), float(lonlat[1]), c='b', marker='o', s=3, linewidths=10)
        # 绘制到界面上
        ax.text(lon[0], lat[0], laneId)
        ax.plot(lon, lat)
        ax.scatter(lon, lat, c='g', marker='o', s=3)
        segCount = segCount+1
        # break
#    if laneId=='-1':
#        break
#    writeCSV([oneLane], writeFileName)
plt.xlabel("lat")
plt.ylabel("lon")
# ax.set_xlim(minLat, maxLat)
# ax.set_ylim(minLon, maxLon)
plt.title("+++")
plt.show()

