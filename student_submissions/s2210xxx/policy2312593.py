from policy import Policy
import numpy as np
import copy as cp
import time

class Policy2312593(Policy):
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
                                    self.action_list.append({"stock_idx": st_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": pr_idx})
                                    break
                            if pos_x is not None and pos_y is not None:
                                break
                            
                        if pos_x is not None and pos_y is not None:
                            break
                        
                        # Dành cho xoay
                        # for x in range(stock_w - prod_h + 1):
                        #     for y in range(stock_h - prod_w + 1):
                        #         if self._can_place_(stock, (x, y), prod_size):
                        #             prod_size[0], prod_size[1] = prod_size[1], prod_size[0]
                        #             pos_x, pos_y = x, y
                        #             self.paint(st_idx, pr_idx, (pos_x, pos_y), [], )
                        #             # thêm bước thêm action vào 1 danh sách
                        #             self.action_list.append({"stock_idx": st_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": pr_idx})
                        #             break
                        #     if pos_x is not None and pos_y is not None:
                        #         break
                            
                        # if pos_x is not None and pos_y is not None:
                        #     break
                        
                        
        
            # the update algo is here
            # Phát: ý tưởng là duyệt từ sau ra các stock đã cắt từ stock đó tìm
            # một product ảo (bao hết các product hiện có) rồi thử đặt vào các 
            # stock nhỏ hơn
            for st_idx in reversed(self.stocks_indices):
                if (self.cutted_stocks[st_idx]==0):
                    continue
                
                change = False
                stock = self.stocks[st_idx]
                size = self._get_stock_size_(stock)

                # tìm product ảo
                temp_w = max(np.sum(stock>=0, axis=0))
                temp_h = max(np.sum(stock>=0, axis=1))
                # print (temp_w, " ", temp_h)

                # cắt thử các stock nhỏ hơn
                for st_idx2 in reversed(self.stocks_indices):
                    check_stock = self.stocks[st_idx2]
                    check_size = self._get_stock_size_(check_stock)
                    
                    if (check_size[0] * check_size[1] < temp_w * temp_h):
                        break

                    if (check_size[0] * check_size[1] >= size[0] * size[1]):
                        break

                    # khi thay được ta thay tất cả các bước có stock index cũ sang mới, trong quá trình đó thực hiện paint -1 và cả product mới
                    # Phát hỏi? liệu có cần phải paint lại không? có ảnh hưởng gì nhiều không? cái quantity khi dùng paint ra âm có sao không?
                    if self._can_place_(check_stock, (0,0), (temp_w, temp_h)):
                        for ac in self.action_list:
                            self.paint(st_idx, -1, (0,0), (temp_w, temp_h))
                            if ac['stock_idx']==st_idx:
                                self.paint(st_idx2, ac['product_idx'], ac['position'], ())
                                ac['stock_idx'] = st_idx2
                                change = True
                if not change:
                    break

        # Lấy thời gian kết thúc
        end_time = time.time()
        self.total_time += end_time - start_time
        # Lấy product ra từ stock đã fill
        return self.get_from_stocks()

    # Hàm này sẽ có chức năng khởi tạo các giá trị bên trong hàm khởi tạo của class
    # Initialize member variable
    # Hàm này Phát làm lại vì cảm giác chương trình chạy nhanh hơn :vv, cái của Phước vấn đúng nhe.
    def init_variable(self, list_stocks, list_products):
        self.stocks = cp.deepcopy(list_stocks)
        self.products = cp.deepcopy(list_products)
        # self.stocks = [np.copy(stock) for stock in list_stocks]
        # self.products = [{"size": prod["size"], "quantity": prod["quantity"]} for prod in list_products]

        for prod in self.products:
            self.amount_of_products+=prod['quantity']
        self.num_products = len(list_products)
        self.num_stocks = len(list_stocks)
        self.cutted_stocks = np.full((self.num_stocks,), fill_value=0, dtype=int)
        
        # Sort
        # self.products_indices = sorted(
        #     range(self.num_products),
        #     key=lambda idx: self.products[idx]["size"][0] * self.products[idx]["size"][1],
        #     reverse=True,
        # )

        sorted_products = sorted(self.products, key=lambda product: product['size'][0] * product['size'][1], reverse=True)
        # sorted_products = sorted(self.products, key=lambda product: product['size'][0], reverse=True)
        product_indies = []
        for s_st in range(len(sorted_products)):
            for st in range(len(self.products)):
                if (np.shape(self.products[st]['size'])==np.shape(sorted_products[s_st]['size'])) and (np.all(self.products[st]['size']==sorted_products[s_st]['size'])):
                    product_indies.append(st)
        self.products_indices = product_indies

        # self.stocks_indices = sorted(
        #     range(self.num_stocks),
        #     key=lambda idx: self._get_stock_size_(self.stocks[idx])[0] * self._get_stock_size_(self.stocks[idx])[1],
        #     reverse=True,
        # )

        sorted_stocks = sorted(self.stocks, key=lambda stock: np.sum(np.any(stock != -2, axis=1)) * np.sum(np.any(stock != -2, axis=0)), reverse=True)
        stock_indies = []
        for s_st in range(len(sorted_stocks)):
            for st in range(len(self.stocks)):
                if (np.shape(self.stocks[st])==np.shape(sorted_stocks[s_st])) and (np.all(self.stocks[st]==sorted_stocks[s_st])):
                    stock_indies.append(st)
        self.stocks_indices = stock_indies
        
    # Mô tả: Hàm này sẽ tìm trong đống stock đã cắt, kiểm tra trong stock đã cắt đó nếu chứa product nào thì mình 
    # sẽ lấy index của product đó. Thực hiện tô lại màu -1 cho product đã lấy ra, chuyển cutted_stock về 0 
    # Phát: thay vì chạy rồi lấy ra từng miếng thì trong quá trình cắt ta thêm vào action list để khi get thì trả về action lại index đó
    def get_from_stocks(self):
        
        # prod_size = [0, 0]
        # stock_idx = -1
        # pos_x, pos_y = 0, 0
        # cutted = False
        # for st_idx in self.stocks_indices:
        # # for st_idx in range(self.num_stocks):
        #     if self.cutted_stocks[st_idx] == 1:
        #         stock = self.stocks[st_idx]
        #         stock_w, stock_h = self._get_stock_size_(stock)
                
        #         for i in range(stock_w):
        #             for j in range(stock_h):
        #                 if stock[i, j] >= 0:
        #                     pr_idx = stock[i, j]
        #                     prod_w, prod_h = self.products[pr_idx]["size"]
        #                     prod_w, prod_h = int(prod_w), int(prod_h)
                            
        #                     stock[i : i + prod_w, j : j + prod_h] = -1
                            
        #                     if np.all(stock<0):
        #                         self.cutted_stocks[st_idx] = 0
                                
        #                     pos_x, pos_y = i, j
        #                     prod_size = [prod_w, prod_h]
        #                     stock_idx = st_idx
        #                     cutted = True
                            
        #                     if cutted:
        #                         break
                        
        #             if cutted:
        #                 break
                        
        #         if cutted:
        #             break
                
        # lấy Action
        action = self.action_list[self.action_called]

        # xem đã đủ hay chưa, nếu đã lấy hết action, thì set first_action=True để reset cho dữ liệu mới
        if (self.action_called==self.amount_of_products-1):
            self.first_action = True
        else:
            self.action_called+=1

        return action
    
    # cân đo đông đếm
    # Phước code thêm phần module time gì nha.  @Reply: Xong rồi nhá, nó ngắn thật :V
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