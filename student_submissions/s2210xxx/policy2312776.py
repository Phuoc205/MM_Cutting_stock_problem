from policy import Policy
import numpy as np


class Policy2312776(Policy):
    def __init__(self):
        stock = np.zeros({100,100})
        stock.fill(-1)
        self.stock = stock
    
    def get_action(self, observation, info):
        pass
    
    def findMin(stock):
        if not stock:
            return None
        
        minValue = stock[0]
        for ele in stock[1:]:
            if minValue > ele:
                minValue = ele
        return minValue
    

def Policy2312776(Policy):
    def __init__(self):
        # Student code here
        pass

    def get_action(self, observation, info):
        # Student code here
        pass

    # Student code here
    # You can add more functions if needed
