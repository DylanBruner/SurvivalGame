import numpy
from numba import jit
from PIL import Image as img

class Surface:
    def __init__(self, size: tuple[int, int]):
        self._array = numpy.zeros((size[0], size[1], 4), dtype=numpy.uint8)
    
    def getArray(self) -> numpy.ndarray: return self._array
    
    def rect(self, topLeft: tuple[int, int], 
             bottomRight: tuple[int, int], color: tuple[int, int, int, int], fill: bool = True):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        

        if fill:
            self._array[topLeft[0]:bottomRight[0], topLeft[1]:bottomRight[1]] = color
        else:
            # trim the edges that aren't inside the rectangle
            self._array[topLeft[0]:bottomRight[0], topLeft[1]]     = color
            self._array[topLeft[0]:bottomRight[0], bottomRight[1]] = color
            self._array[topLeft[0], topLeft[1]:bottomRight[1]]     = color
            self._array[bottomRight[0], topLeft[1]:bottomRight[1]] = color

    def circle(self, center: tuple[int, int], radius: int, color: tuple[int, int, int, int], fill: bool = True):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)

        if fill:
            for x in range(center[0] - radius, center[0] + radius):
                for y in range(center[1] - radius, center[1] + radius):
                    if (x - center[0])**2 + (y - center[1])**2 <= radius**2:
                        self._array[x, y] = color
        else:
            for x in range(center[0] - radius, center[0] + radius):
                for y in range(center[1] - radius, center[1] + radius):
                    if (x - center[0])**2 + (y - center[1])**2 <= radius**2:
                        self._array[x, y] = color
            for x in range(center[0] - radius, center[0] + radius):
                for y in range(center[1] - radius, center[1] + radius):
                    if (x - center[0])**2 + (y - center[1])**2 <= (radius - 1)**2:
                        self._array[x, y] = (0, 0, 0, 0)
    
    def line(self, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int, int]):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        
        for x in range(start[0], end[0]):
            for y in range(start[1], end[1]):
                self._array[x, y] = color
    
    def pointInPolygon(self, point: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
        inside = False
        x = point[0]
        y = point[1]
        for i in range(len(polygon)):
            j = i - 1
            if (polygon[i][1] > y) != (polygon[j][1] > y):
                if x < (polygon[j][0] - polygon[i][0]) * (y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) + polygon[i][0]:
                    inside = not inside
        return inside
    
    def polygon(self, points: list[tuple[int, int]], color: tuple[int, int, int, int], fill: bool = True):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)

        if fill:
            for x in range(min(points, key=lambda x: x[0])[0], max(points, key=lambda x: x[0])[0]):
                for y in range(min(points, key=lambda x: x[1])[1], max(points, key=lambda x: x[1])[1]):
                    if self.pointInPolygon((x, y), points):
                        self._array[x, y] = color
        else:
            for x in range(min(points, key=lambda x: x[0])[0], max(points, key=lambda x: x[0])[0]):
                for y in range(min(points, key=lambda x: x[1])[1], max(points, key=lambda x: x[1])[1]):
                    if self.pointInPolygon((x, y), points):
                        self._array[x, y] = color
            for x in range(min(points, key=lambda x: x[0])[0], max(points, key=lambda x: x[0])[0]):
                for y in range(min(points, key=lambda x: x[1])[1], max(points, key=lambda x: x[1])[1]):
                    if self.pointInPolygon((x, y), points):
                        self._array[x, y] = (0, 0, 0, 0)
    
    def fill(self, color: tuple[int, int, int, int]):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        
        self._array[:, :] = color
    
    def blit(self, surface: 'Surface' or numpy.ndarray, pos: tuple[int, int]):
        if isinstance(surface, Surface):
            self._array[pos[0]:pos[0] + surface.getArray().shape[0], pos[1]:pos[1] + surface.getArray().shape[1]] = surface.getArray()
        elif isinstance(surface, numpy.ndarray):
            self._array[pos[0]:pos[0] + surface.shape[0], pos[1]:pos[1] + surface.shape[1]] = surface


class gpuUTILS:
    @staticmethod
    def imageFromPath(path: str, convert: str = "RGBA") -> numpy.ndarray:
        return numpy.array(img.open(path).convert(convert))