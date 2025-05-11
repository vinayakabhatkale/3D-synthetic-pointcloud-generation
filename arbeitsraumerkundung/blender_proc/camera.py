class Camera:
    def __init__(self, fx, fy, cx, cy):
        self.__intrinsic = np.zeros(shape=(3,3))
        self.__intrinsic[0][0] = fx
        self.__intrinsic[1][1]= fy
        self.__intrinsic[2][0]= cx
        self.__intrinsic[2][1]= cy

    def get_intrinsic_matrix():
        return self.intrinsic

