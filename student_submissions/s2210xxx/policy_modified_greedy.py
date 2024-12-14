from policy import Policy
import numpy as np
import time

class ModifiedGreedy(Policy):
    def __init__(self):

        self.first = True

        self.m_used_surface = 0
        self.m_filled_surface = 0
        self.m_used_stock = 0

        self.m_sorted_stock_index = 0
        self.m_sorted_product_index = 0

        self.odd_odd_stock_index = []
        self.odd_even_stock_index = []
        self.even_odd_stock_index = []
        self.even_even_stock_index = []

        self.total_time = 0

        pass

    def reset(self):

        self.first = True

        self.m_used_surface = 0
        self.m_filled_surface = 0
        self.m_used_stock = 0

        self.m_sorted_product_index = []

        self.odd_odd_stock_index = []
        self.odd_even_stock_index = []
        self.even_odd_stock_index = []
        self.even_even_stock_index = []

        self.total_time = 0

        pass

    def evaluate(self):
        print("[----------==========| EVALUATE BASIC FIRST FIT DECREASING |==========----------]")
        print(" - Stocks used:    ", self.m_used_stock)
        print(" - Used Surface:   ", self.m_used_surface)
        print(" - Waste Surface:  ", self.m_used_surface - self.m_filled_surface)
        print(" - Filled Surface: ", self.m_filled_surface)
        print(" - Waste Percent:  ", (1-self.m_filled_surface/self.m_used_surface)*100, "%")
        print(" - Total Time:     ", self.total_time, "s")
        print("[----------==========| EVALUATE BASIC FIRST FIT DECREASING |==========----------]")
        pass

    def init_indices(self, list_stocks, list_prods):
        
        sorted_products = sorted(list_prods, key=lambda product: product['size'][0] * product['size'][1], reverse=True)
        product_indies = []
        for s_st in range(len(sorted_products)):
            for st in range(len(list_prods)):
                if (np.shape(list_prods[st]['size'])==np.shape(sorted_products[s_st]['size'])) and (np.all(list_prods[st]['size']==sorted_products[s_st]['size'])):
                    product_indies.append(st)
        self.m_sorted_product_index = product_indies

        sorted_stocks = sorted(list_stocks, key=lambda stock: np.sum(np.any(stock != -2, axis=1)) * np.sum(np.any(stock != -2, axis=0)), reverse=True)
        stock_indies = []
        for s_st in range(len(sorted_stocks)):
            for st in range(len(list_stocks)):
                if (np.shape(list_stocks[st])==np.shape(sorted_stocks[s_st])) and (np.all(list_stocks[st]==sorted_stocks[s_st])):
                    stock_indies.append(st)
        sorted_stock_index = stock_indies

        for idx in sorted_stock_index:
            stock = list_stocks[idx]
            size = self._get_stock_size_(stock)
            if (size[0]%2==0):
                if (size[1]%2==0):
                    self.even_even_stock_index.append(idx)
                else:
                    self.even_odd_stock_index.append(idx)
            else:
                if (size[1]%2==0):
                    self.odd_even_stock_index.append(idx)
                else:
                    self.odd_odd_stock_index.append(idx)

        print(self.even_even_stock_index)
        print(self.even_odd_stock_index)
        print(self.odd_even_stock_index)
        print(self.odd_odd_stock_index)
        
        pass

    def get_action(self, observation, info):

        start_time = time.time()
        list_prods = observation["products"]
        list_stocks = observation["stocks"]

        # Descending
        if (self.first):
            self.reset()
            self.init_indices(list_stocks, list_prods)
            self.first = False

        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = 0, 0
        
        for pr_idx in self.m_sorted_product_index:
            prod = list_prods[pr_idx]
            prod_size = prod['size']
            if prod["quantity"] > 0:
                # Loop through all stocks

                toCheck = []
                if (prod_size[0]%2==0):
                    if (prod_size[1]%2==0):
                        toCheck = self.even_even_stock_index
                    else:
                        toCheck = self.even_odd_stock_index
                else:
                    if (prod_size[1]%2==0):
                        toCheck = self.odd_even_stock_index
                    else:
                        toCheck = self.odd_odd_stock_index

                for st_idx in toCheck:
                    stock = list_stocks[st_idx]
                    stock_w, stock_h = self._get_stock_size_(stock)
                    prod_w, prod_h = prod['size']

                    # evaluate
                    used = np.any(stock >= 0)
                    surface = stock_w * stock_h
                    filled = np.sum(stock >= 0)

                    if((stock_w < prod_w or stock_h < prod_h) and (stock_h < prod_w or stock_w < prod_h)):
                        continue
                    
                    pos_x, pos_y = None, None
                    for x in range(stock_w - prod_w + 1):
                        for y in range(stock_h - prod_h + 1):
                            if self._can_place_(stock, (x, y), (prod_w, prod_h)):
                                prod_size = (prod_w, prod_h)
                                stock_idx = st_idx

                                if (not used):
                                    self.m_used_surface += + surface
                                    self.m_used_stock += 1
                                
                                prod_surface = prod_w * prod_h
                                self.m_filled_surface += prod_surface
                                filled += prod_surface

                                pos_x, pos_y = x, y
                                break
                        if pos_x is not None and pos_y is not None:
                            break
                    if pos_x is not None and pos_y is not None:
                        stock_idx = st_idx
                        break

                    # cho xoay
                    pos_x, pos_y = None, None
                    for x in range(stock_w - prod_h + 1):
                        for y in range(stock_h - prod_w + 1):
                            if self._can_place_(stock, (x, y), (prod_h, prod_w)):
                                prod_size = (prod_h, prod_w)
                                stock_idx = st_idx

                                if (not used):
                                    self.m_used_surface += + surface
                                    self.m_used_stock += 1
                                
                                prod_surface = prod_w * prod_h
                                self.m_filled_surface += prod_surface
                                filled += prod_surface

                                pos_x, pos_y = x, y
                                break
                        if pos_x is not None and pos_y is not None:
                            break
                    if pos_x is not None and pos_y is not None:
                        stock_idx = st_idx
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

    # Student code here
    # You can add more functions if needed
