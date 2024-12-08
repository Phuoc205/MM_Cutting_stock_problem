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
        self.action_list = [[]]
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
        self.action_list = [[]]
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

    # thêm trường hợp "paint" với prod_idx = -1 hay nói cách khác là xóa
    def paint(self, stock_idx, prod_idx, position, custom_size):
        width, height = (0, 0)
        if (prod_idx==-1):
            width, height = custom_size
        else:
            self.cutted_stocks[stock_idx] = 1
            size = self.products[prod_idx]["size"]
            width, height = size

            self.products[prod_idx]["quantity"] -= 1

        x, y = position
        stock = self.stocks[stock_idx]
        stock[x : x + width, y : y + height] = prod_idx
        
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

                        if stock_w < prod_w or stock_h < prod_h:
                            continue

                        pos_x, pos_y = None, None
                        for x in range(stock_w - prod_w + 1):
                            for y in range(stock_h - prod_h + 1):
                                if self._can_place_(stock, (x, y), prod_size):

                                    pos_x, pos_y = x, y
                                    self.paint(st_idx, pr_idx, (pos_x, pos_y), [])
                                    # thêm bước thêm action vào 1 danh sách
                                    self.action_list[st_idx].append({"stock_idx": st_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": pr_idx})
                                    break
                            if pos_x is not None and pos_y is not None:
                                break
                            
                        if pos_x is not None and pos_y is not None:
                            break
                        
                        # Dành cho xoay
                        for x in range(stock_w - prod_h + 1):
                            for y in range(stock_h - prod_w + 1):
                                if self._can_place_(stock, (x, y), prod_size):
                                    prod_size[0], prod_size[1] = prod_size[1], prod_size[0]
                                    pos_x, pos_y = x, y
                                    self.paint(st_idx, pr_idx, (pos_x, pos_y), [], )
                                    # thêm bước thêm action vào 1 danh sách
                                    self.action_list[st_idx].append({"stock_idx": st_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": pr_idx})
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
                        print("st_index ", st_idx , " : " ,np.sum(self.stocks[st_idx]>0))
                        print("st_index ", st_idx2, " : " ,np.sum(self.stocks[st_idx2]>0))
                        self.copyAtoB(st_idx, (0,0), st_idx2, (0,0), (temp_w, temp_h), False)
                        for ac in self.action_list[st_idx]:
                            ac_copy = ac.copy()  # Tạo bản sao của ac
                            ac_copy['stock_idx'] = st_idx2  # Thay đổi stock_idx trong bản sao
                            self.action_list[st_idx2].append(ac_copy)  # Thêm bản sao vào danh sách mới
                        
                        
                        self.action_list[st_idx].clear()
                        print("st_index ", st_idx ,  " : " ,np.sum(self.stocks[st_idx]>0))
                        print("st_index ", st_idx2 ,  " : ", np.sum(self.stocks[st_idx2]>0))
                        break
                        
                    # if self._can_place_(check_stock, (0,0), (temp_h, temp_w)):
                    #     self.copyAtoB(st_idx, (0,0), st_idx2, (0,0), (temp_w, temp_h), True)
                    #     for ac in self.action_list[st_idx]:
                    #         ac['stock_idx']==st_idx2
                    #         self.action_list[st_idx2].append(ac)
                            
                    #     self.action_list[st_idx].clear()
                    #     break

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
        width = max_col - min_col + 1
        height = max_row - min_row + 1

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

    def copyAtoB(self, idxA, posA, idxB, posB, size, rotate):
        # copy từ stock A sang stock B
        width = size[0]
        height = size[1]
        x_A, y_A = posA
        x_B, y_B = posB
        if not rotate :
            for i in range(width):
                for j in range(height):
                    self.stocks[idxB][x_B+i][y_B+j] = self.stocks[idxA][x_A+i][y_A+j]
                    self.stocks[idxA][x_A+i][y_A+j] = -1
        else :
            for i in range(width):
                for j in range(height):
                    self.stocks[idxB][x_B+j][y_B+i] = self.stocks[idxA][x_A+i][y_A+j]
                    self.stocks[idxA][x_A+i][y_A+j] = -1
                

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
        
        self.action_list = [[] for _ in range(self.num_stocks)]
        
    # Lấy từng action từ stock
    def get_from_stocks(self):
        # lấy Action
        flattened_action_list = [action for sublist in self.action_list for action in sublist]
        action = flattened_action_list[self.action_called]

        # xem đã đủ hay chưa, nếu đã lấy hết action, thì set first_action=True để reset cho dữ liệu mới
        if (self.action_called==self.amount_of_products-1):
            self.first_action = True
        else:
            self.action_called+=1

        return action
    
    # Đánh giá giải thuật
    def evaluate(self):
        # số stock sử dụng
        amount_stocks = np.sum(self.cutted_stocks)
        # tính diện tích đã dùng và đã cắt (filled)
        used = 0
        filled = 0
        for st_idx in self.stocks_indices:
            if (self.cutted_stocks[st_idx]==1):
                stock = self.stocks[st_idx]
                size = self._get_stock_size_(stock)

                filled += np.sum(stock>=0)
                used += size[0] * size[1]

        # hiển thị
        print("[----------==========| EVALUATE |==========----------]")
        print(" - Stocks used:    ", amount_stocks)
        print(" - Used Surface:   ", used)
        print(" - Waste Surface:  ", used - filled)
        print(" - Filled Surface: ", filled)
        print(" - Waste Percent:  ", (1-filled/used)*100, "%")
        print(" - Total Time:     ", self.total_time, "s")
        print("[----------==========| EVALUATE |==========----------]")