class Line:
    def __init__(self, x1,y1,x2,y2):
        self.x1=int(x1)
        self.x2=int(x2)
        self.y1=int(y1)
        self.y2=int(y2)    
        self.slope=(y2-y1)/(x2-x1)

    

    def get_slope(self):
        if self.x2-self.x1==0:
            return(100000000)
        if self.y1==self.y2:
            return(.00000000000001)
        else:
            return((self.y2-self.y1)/(self.x2-self.x1))
    


           