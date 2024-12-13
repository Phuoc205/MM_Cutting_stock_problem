from policy import Policy

import numpy as np
import copy as cp
import time

class Policy_Modified_Greedy(Policy):
    def __init__(self):

        self.first = True

        self.odd_odd_indices = []
        self.odd_even_indices = []
        self.even_odd_indices = []
        self.even_even_indices = []

        self.m_used_surface = 0
        self.m_filled_surface = 0
        self.m_used_stock = 0

        self.total_time = 0

        pass

    def reset(self):

        self.first = True

        self.odd_odd_indices = []
        self.odd_even_indices = []
        self.even_odd_indices = []
        self.even_even_indices = []

        self.m_used_surface = 0
        self.m_filled_surface = 0
        self.m_used_stock = 0

        self.total_time = 0

        pass

    # lấy 2 hàm bên policy.py qua 
    def _get_stock_size_(self, stock):
        stock_w = np.sum(np.any(stock != -2, axis=1))
        stock_h = np.sum(np.any(stock != -2, axis=0))

        return stock_w, stock_h

    def _can_place_(self, stock, position, prod_size):
        pos_x, pos_y = position
        prod_w, prod_h = prod_size

        return np.all(stock[pos_x : pos_x + prod_w, pos_y : pos_y + prod_h] == -1)

    def init_indices(self, stocks):
        
        for i, stock in enumerate(stocks):
            size = self._get_stock_size_(stock)

            if (size[0]%2==0):
                if (size[1]%2==0):
                    self.even_even_indices.append(i)
                else:
                    self.even_odd_indices.append(i)
            else:
                if (size[1]%2==0):
                    self.odd_even_indices.append(i)
                else:
                    self.odd_odd_indices.append(i)

        pass

    def get_action(self, observation, info):
        start_time = time.time()

        list_prods = observation["products"]
        list_stocks = observation["stocks"]

        if (self.first):
            self.reset()
            self.init_indices(list_stocks)
            self.first = False

        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = 0, 0

        # Pick a product that has quality > 0
        for prod in list_prods:
            if prod["quantity"] > 0:
                prod_size = prod["size"]

                toCheck = []
                
                if (prod_size[0]%2==0):
                    if (prod_size[1]%2==0):
                        toCheck = self.even_even_indices
                    else:
                        toCheck = self.even_odd_indices
                else:
                    if (prod_size[1]%2==0):
                        toCheck = self.odd_even_indices
                    else:
                        toCheck = self.odd_odd_indices

                for i in toCheck:
                    stock = list_stocks[i]
                    stock_w, stock_h = self._get_stock_size_(stock)
                    prod_w, prod_h = prod_size

                    used = np.any(stock >= 0)
                    surface = stock_w * stock_h
                    filled = np.sum(stock >= 0)

                    if stock_w >= prod_w and stock_h >= prod_h:
                        pos_x, pos_y = None, None
                        for x in range(stock_w - prod_w + 1):
                            for y in range(stock_h - prod_h + 1):
                                if self._can_place_(stock, (x, y), prod_size):
                                    pos_x, pos_y = x, y
                                    if (not used):
                                        self.m_used_surface += + surface
                                        self.m_used_stock += 1
                                
                                    prod_surface = prod_w * prod_h
                                    self.m_filled_surface += prod_surface
                                    filled += prod_surface

                                    break
                            if pos_x is not None and pos_y is not None:
                                break
                        if pos_x is not None and pos_y is not None:
                            stock_idx = i
                            break

                    if stock_w >= prod_h and stock_h >= prod_w:
                        for x in range(stock_w - prod_h + 1):
                            for y in range(stock_h - prod_w + 1):
                                prod_size[0], prod_size[1] = prod_size[1], prod_size[0]
                                if self._can_place_(stock, (x, y), prod_size):
                                    pos_x, pos_y = x, y

                                    if (not used):
                                        self.m_used_surface += + surface
                                        self.m_used_stock += 1
                                    
                                    prod_surface = prod_w * prod_h
                                    self.m_filled_surface += prod_surface
                                    filled += prod_surface

                                    break
                            if pos_x is not None and pos_y is not None:
                                break
                            
                        if pos_x is not None and pos_y is not None:
                            stock_idx = i
                            break

                    if pos_x is not None and pos_y is not None:
                        break

        end_time = time.time()
        self.total_time += end_time - start_time

        amount_of_products = 0
        for prod in list_prods:
            amount_of_products += prod['quantity']
        if (amount_of_products==1):
            self.first = True 

        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}
    
    # Đánh giá giải thuật
    def evaluate(self):
        # hiển thị
        print("[----------==========| EVALUATE MODIFIED GREEDY |==========----------]")
        print(" - Stocks used:    ", self.m_used_stock)
        print(" - Used Surface:   ", self.m_used_surface)
        print(" - Waste Surface:  ", self.m_used_surface - self.m_filled_surface)
        print(" - Filled Surface: ", self.m_filled_surface)
        print(" - Waste Percent:  ", (1-self.m_filled_surface/self.m_used_surface)*100, "%")
        print(" - Total Time:     ", self.total_time, "s")
        print("[----------==========| EVALUATE MODIFIED GREEDY |==========----------]")