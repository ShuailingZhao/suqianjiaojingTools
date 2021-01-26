import csv
import json


class FrameObjects:
    def __init__(self, oid, box, w, type):
        self.oid = oid
        self.box = box
        self.width =  w
        self.type = type

class DetectCsvLoader:
    def __init__(self, csvFile):
        self.frames = []
        self.idx = -1
        with open(csvFile, encoding='utf-8-sig') as f:
            cf = csv.reader(f)
            header = next(cf)
            for r in cf:
                frameId = r[0]
                objIds = json.loads(r[1])
                boxes = json.loads(r[2])
                widths = json.loads(r[3])
                types = json.loads(json.dumps(eval(r[4])))
                objList = []
                for oid, box, width , type in zip(objIds, boxes, widths, types):
                    objList.append(FrameObjects(oid, (box[0],box[1],box[2],box[3]), width, type))
                self.frames.append((frameId,objList))

    def next(self):
        self.idx += 1
        if self.idx >= len(self.frames):
            return False, None
        else:
            return True, self.frames[self.idx]

    def writeZhaosl(self, out):
        fo = open(out,'w')
        for k in self.frames:
            fid = k[0]
            line = []
            line.append(str(fid))
            for f in k[1]:
                line.append(str(f.oid))
                for x in f.box:
                    line.append(str(x))
                line.append(str(f.width))
            fo.write(','.join(line)+"\n")

        fo.close()


if __name__  == '__main__':
    csvFile = 'final_result_undistort20000101_061954.csv'
    outFile = 'final_result_undistort20000101_061954.txt'
    # csvFile = 'final_result_undis20210118_143813.csv'
    # outFile = 'final_result_undis20210118_143813.txt'
    csv = DetectCsvLoader(csvFile)
    csv.writeZhaosl(outFile)
    print("+++++++++++ done +++++++++++++")

