from policy import Policy

import numpy as np
import copy as cp
import time

class Policy2312776(Policy):
    def __init__(self):
        # data variable
        self.stocks = []
        self.products = []

        # other
        self.num_stocks = 0
        self.num_products = 0
        self.amount_of_products = 0

        # action variable
        self.action_list = []
        self.first_action = True
        self.action_called = 0

        # index variable
        self.stocks_indices = []
        self.products_indices = []

        # evaluate variable
        self.cutted_stocks = []
        self.total_time = 0
        
    def reset(self):
        # data variable
        self.stocks = []
        self.products = []

        # other
        self.num_stocks = 0
        self.num_products = 0
        self.amount_of_products = 0

        # action variable
        self.action_list = []
        self.first_action = True
        self.action_called = 0

        # index variable
        self.stocks_indices = []
        self.products_indices = []

        # evaluate variable
        self.cutted_stocks = []
        self.total_time = 0

    # lấy 2 hàm bên policy.py qua 
    def _get_stock_size_(self, stock):
        stock_w = np.sum(np.any(stock != -2, axis=1))
        stock_h = np.sum(np.any(stock != -2, axis=0))

        return stock_w, stock_h

    def _can_place_(self, stock, position, prod_size):
        pos_x, pos_y = position
        prod_w, prod_h = prod_size

        return np.all(stock[pos_x : pos_x + prod_w, pos_y : pos_y + prod_h] == -1)

    def paint(self, action):

        stock_idx = action["stock_idx"]
        size = action["size"]
        position = action["position"]

        width, height = size
        x, y = position

        # Check if the product is in the product list
        product_idx = None
        for i, product in enumerate(self.products):
            if np.array_equal(product["size"], size) or np.array_equal(
                product["size"], size[::-1]):
                if product["quantity"] == 0:
                    continue

                product_idx = i  # Product index starts from 0
                break

        if product_idx is not None:
            if 0 <= stock_idx < self.num_stocks:
                stock = self.stocks[stock_idx]
                # Check if the product fits in the stock
                stock_width = np.sum(np.any(stock != -2, axis=1))
                stock_height = np.sum(np.any(stock != -2, axis=0))
                if (
                    x >= 0
                    and y >= 0
                    and x + width <= stock_width
                    and y + height <= stock_height):
                    # Check if the position is empty
                    if np.all(stock[x : x + width, y : y + height] == -1):
                        self.cutted_stocks[stock_idx] = 1
                        stock[x : x + width, y : y + height] = product_idx
                        self.products[product_idx]["quantity"] -= 1
                        print(product_idx, "remain", self.products[product_idx]['quantity'])
                    else:
                        print("Action is not avaiable 1")
                else:
                    print(stock_idx, size, x,y, stock_width, stock_height, "Action is not avaiable 2")
        else:
            print("Action is not avaiable 3")
        
        if (np.all(stock<0)):
            self.cutted_stocks[stock_idx] = 0

        pass

    def get_action(self, observation, info):
        # Lấy thời gian bắt đầu
        start_time = time.time()
        # Chạy chương trình
        if self.first_action:
            # hàm reset
            self.reset()
            self.init_variable(observation["stocks"], observation["products"])
            print("===========================")
            print(self.amount_of_products)
            for pr_idx in self.products_indices:
                print(self.products[pr_idx])
            for st_idx in self.stocks_indices:
                print(self._get_stock_size_(self.stocks[st_idx]))
            print("===========================")
            self.first_action = False
            
            for pr_idx in self.products_indices:
                prod = self.products[pr_idx]
                # Kiểm tra số lượng của sản phẩm
                while prod["quantity"] > 0:
                    prod_size = prod["size"]

                    # Vòng lặp duyệt qua tất cả stock
                    for st_idx in self.stocks_indices:
                        stock = self.stocks[st_idx]
                        stock_w, stock_h = self._get_stock_size_(stock)
                        prod_w, prod_h = prod_size

                        if((stock_w < prod_w or stock_h < prod_h) and (stock_h < prod_w or stock_w < prod_h)):
                            continue
                        
                        pos_x, pos_y = None, None
                        
                        # Dành cho không xoay
                        if stock_w >= prod_w and stock_h >= prod_h:
                            for x in range(stock_w - prod_w + 1):
                                for y in range(stock_h - prod_h + 1):
                                    if self._can_place_(stock, (x, y), prod_size):
                                        pos_x, pos_y = x, y
                                        
                                        # thêm bước thêm action vào 1 danh sách
                                        act = {"stock_idx": st_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": pr_idx}
                                        print(act)
                                        self.action_list.append(act)
                                        self.paint(act)
                                        break
                                if pos_x is not None and pos_y is not None:
                                    break
                                
                            if pos_x is not None and pos_y is not None:
                                break
                        
                        # Dành cho xoay
                        if stock_w >= prod_h and stock_h >= prod_w:
                            new_size = prod_h, prod_w
                            
                            for x in range(stock_w - prod_h + 1):
                                for y in range(stock_h - prod_w + 1):
                                    if self._can_place_(stock, (x, y), new_size):
                                        pos_x, pos_y = x, y
                                        
                                        # thêm bước thêm action vào 1 danh sách
                                        act = {"stock_idx": st_idx, "size": new_size, "position": (pos_x, pos_y), "product_idx": pr_idx}
                                        print(act)
                                        self.action_list.append(act)
                                        self.paint(act)
                                        break
                                if pos_x is not None and pos_y is not None:
                                    break
                                
                            if pos_x is not None and pos_y is not None:
                                break
                            
            sorted_list = self.sort_stock_indices_by_bounding_box()
            for ele in reversed(sorted_list):
                st_idx = ele[0]
                if (self.cutted_stocks[st_idx]==0):
                    continue
                
                stock = self.stocks[st_idx]
                temp_w, temp_h = ele[1], ele[2]
                size = self._get_stock_size_(stock)
                # print (temp_w, " ", temp_h)

                # cắt thử các stock nhỏ hơn
                for st_idx2 in reversed(self.stocks_indices):
                    check_stock = self.stocks[st_idx2]
                    check_size = self._get_stock_size_(check_stock)
                    
                    if (check_size[0] * check_size[1] < temp_w * temp_h):
                        break

                    if (check_size[0] * check_size[1] >= size[0] * size[1]):
                        break

                    if self._can_place_(check_stock, (0,0), (temp_w, temp_h)):
                        self.copyAtoB(st_idx, (0,0), st_idx2, (0,0), (temp_w, temp_h))
                        break

        # Lấy thời gian kết thúc
        end_time = time.time()
        self.total_time += end_time - start_time
        # Lấy product ra từ stock đã fill
        return self.get_from_stocks()

    def calculate_bounding_box(self, stock):
        # Lấy chỉ số các phần tử không âm
        rows, cols = np.where(stock >= 0)

        if rows.size == 0 or cols.size == 0:  # Nếu không có sản phẩm nào
            return 0, 0

        # Tìm chỉ số hàng và cột nhỏ nhất, lớn nhất
        min_row, max_row = rows.min(), rows.max()
        min_col, max_col = cols.min(), cols.max()

        # Tính kích thước bao phủ
        width = max_row - min_row + 1
        height = max_col - min_col + 1

        return width, height
    
    def sort_stock_indices_by_bounding_box(self):
        """
        Sắp xếp danh sách các chỉ số stocks chưa bị cắt dựa trên diện tích bounding box từ bé đến lớn.
        """
        stocks_with_bounding = []

        for idx, stock in enumerate(self.stocks):
            if self.cutted_stocks[idx] == 1:
                width, height = self.calculate_bounding_box(stock)
                stocks_with_bounding.append((idx, width, height))
        
        sorted_stocks = sorted(
            stocks_with_bounding, key=lambda x: x[1] * x[2]
        )

        return sorted_stocks

    def copyAtoB(self, idxA, posA, idxB, posB, size):
        # copy từ stock A sang stock B
        width = size[0]
        height = size[1]
        x_A, y_A = posA
        x_B, y_B = posB
    
        for i in range(width):
            for j in range(height):
                self.stocks[idxB][x_B+i][y_B+j] = self.stocks[idxA][x_A+i][y_A+j]
                self.stocks[idxA][x_A+i][y_A+j] = -1

        for ac in self.action_list:
            if (ac['stock_idx']==idxA):
                ac['stock_idx'] = idxB 
        
        self.cutted_stocks[idxB] = 1   
        if (np.all(self.stocks[idxA]<0)):
            self.cutted_stocks[idxA] = 0
    

    # Initialize member variable
    def init_variable(self, list_stocks, list_products):
        self.stocks = cp.deepcopy(list_stocks)
        self.products = cp.deepcopy(list_products)

        for prod in self.products:
            self.amount_of_products+=prod['quantity']
        self.num_products = len(list_products)
        self.num_stocks = len(list_stocks)
        self.cutted_stocks = np.full((self.num_stocks,), fill_value=0, dtype=int)

        sorted_products = sorted(self.products, key=lambda product: product['size'][0] * product['size'][1], reverse=True)
        product_indies = []
        for s_st in range(len(sorted_products)):
            for st in range(len(self.products)):
                if (np.shape(self.products[st]['size'])==np.shape(sorted_products[s_st]['size'])) and (np.all(self.products[st]['size']==sorted_products[s_st]['size'])):
                    product_indies.append(st)
        self.products_indices = product_indies

        sorted_stocks = sorted(self.stocks, key=lambda stock: np.sum(np.any(stock != -2, axis=1)) * np.sum(np.any(stock != -2, axis=0)), reverse=True)
        stock_indies = []
        for s_st in range(len(sorted_stocks)):
            for st in range(len(self.stocks)):
                if (np.shape(self.stocks[st])==np.shape(sorted_stocks[s_st])) and (np.all(self.stocks[st]==sorted_stocks[s_st])):
                    stock_indies.append(st)
        self.stocks_indices = stock_indies
        
        self.action_list = []
        
    # Lấy từng action từ stock
    def get_from_stocks(self):
        # lấy Action
        action = self.action_list[self.action_called]

        # xem đã đủ hay chưa, nếu đã lấy hết action, thì set first_action=True để reset cho dữ liệu mới
        if (self.action_called>=self.amount_of_products-1):
            self.first_action = True
        else:
            self.action_called+=1

        return action
    
    # Đánh giá giải thuật
    def evaluate(self):
        # số stock sử dụng
        # amount_stocks = np.sum(self.cutted_stocks)
        # # tính diện tích đã dùng và đã cắt (filled)
        # used = 0
        # filled = 0
        # for st_idx in self.stocks_indices:
        #     if (self.cutted_stocks[st_idx]==1):
        #         stock = self.stocks[st_idx]
        #         size = self._get_stock_size_(stock)

        #         filled += np.sum(stock>=0)
                # used += size[0] * size[1]

        # hiển thị
        print("[----------==========| EVALUATE 2312776 |==========----------]")
        # print(" - Stocks used:    ", amount_stocks)
        # print(" - Used Surface:   ", used)
        # print(" - Waste Surface:  ", used - filled)
        # print(" - Filled Surface: ", filled)
        # print(" - Waste Percent:  ", (1-filled/used)*100, "%")
        print(" - Total Time:     ", self.total_time, "s")
        print("[----------==========| EVALUATE 2312776 |==========----------]")