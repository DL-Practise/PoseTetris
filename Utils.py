import math

class Point:
    def __init__(self, x, y):
        self.X = x
        self.Y = y


class Line:
    def __init__(self, point1, point2):
        self.Point1 = point1
        self.Point2 = point2


def GetAngle(l1, l2):
    line1_point1, line1_point2 = l1
    line2_point1, line2_point2 = l2
    line1 = Line(Point(line1_point1[0], line1_point1[1]), Point(line1_point2[0], line1_point2[1]))
    line2 = Line(Point(line2_point1[0], line2_point1[1]), Point(line2_point2[0], line2_point2[1]))

    dx1 = line1.Point1.X - line1.Point2.X
    dy1 = line1.Point1.Y - line1.Point2.Y
    dx2 = line2.Point1.X - line2.Point2.X
    dy2 = line2.Point1.Y - line2.Point2.Y
    angle1 = math.atan2(dy1, dx1)
    angle1 = int(angle1 * 180 / math.pi)
    # print(angle1)
    angle2 = math.atan2(dy2, dx2)
    angle2 = int(angle2 * 180 / math.pi)
    # print(angle2)
    if angle1 * angle2 >= 0:
        insideAngle = abs(angle1 - angle2)
    else:
        insideAngle = abs(angle1) + abs(angle2)
        if insideAngle > 180:
            insideAngle = 360 - insideAngle

    if insideAngle != 0 and insideAngle != 180:
        insideAngle = insideAngle % 180
        
    return insideAngle
    
if __name__ == '__main__':


    res = GetAngle([[0.25336927223719674, 0.3779264214046823], [0.2695417789757412, 0.6354515050167224]], \
                   [ [0.5849102, 0.2969229], [0.5991784, 0.50112796]])
    print(res)
    