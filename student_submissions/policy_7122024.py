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
        self.stock_info = []
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
        self.stock_info = []
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

    # thu fit cac product tu stock from sang stock to
    # return fit (bool) - co fit duoc khong?
    #        action_list (list) - danh sach cac action tao boi viec fit
    #        goal_stock - to_stock sau khi fit
    #        from_list_products (np num of products row array) - danh sach so luong cac product trong stock from
    #        to_list_products (nhu tren) - danh sach so luong cac product trong stock to
    def _fit_(self, from_stock_idx, to_stock_idx):

        goal_stock = cp.deepcopy(self.stocks[to_stock_idx])
        width, height = self._get_stock_size_(goal_stock)
        from_list_products = cp.deepcopy(self.stock_info[from_stock_idx])
        to_list_products = np.full((self.num_products), fill_value = 0, dtype=int)

        fit = False
        action_list = []

        print(from_list_products)
        print(from_stock_idx)
        print(to_stock_idx)
        print(to_list_products)

        for i, prod_quantity in enumerate(from_list_products):

            prod = self.products[i]
            prod_size = prod["size"]
            cut = False
            while (prod_quantity>0):
                if width >= prod_size[0] and height >= prod_size[1]:
                    pos_x, pos_y = None, None
                    for x in range(width - prod_size[0] + 1):
                        for y in range(height - prod_size[1] + 1):
                            
                            if self._can_place_(goal_stock, (x, y), prod_size):
                                pos_x, pos_y = x, y
                                cut = True

                                from_list_products[i]-=1
                                goal_stock[pos_x: pos_x+prod_size[0], pos_y: pos_y + prod_size[1]] = i
                                to_list_products[i]+=1
                                prod_quantity-=1

                                action = {"stock_idx": to_stock_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": i, "rotate": False}
                                print(action)
                                action_list.append(action)
                                
                                break
                        if pos_x is not None and pos_y is not None:
                            break
                    if pos_x is not None and pos_y is not None:
                        continue
                
                pos_x, pos_y = None, None
                if width >= prod_size[1] and height >= prod_size[0]:
                    pos_x, pos_y = None, None
                    for x in range(width - prod_size[1] + 1):
                        for y in range(height - prod_size[0] + 1):
                            prod_size[0], prod_size[1] = prod_size[1], prod_size[0]
                            if self._can_place_(goal_stock, (x, y), prod_size):
                                pos_x, pos_y = x, y
                                cut = True

                                goal_stock[pos_x: pos_x+prod_size[0], pos_y: pos_y + prod_size[1]] = i
                                from_list_products[i]-=1
                                to_list_products[i]+=1
                                prod_quantity-=1

                                action = {"stock_idx": to_stock_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": i, "rotate": True}
                                print(action)
                                action_list.append(action)
                                
                                break
                        if pos_x is not None and pos_y is not None:
                            break
                    if pos_x is not None and pos_y is not None:
                        continue
                
                if not cut:
                    break

        print(from_list_products)
        if (np.all(from_list_products==0)):
            fit = True

        return fit, action_list, from_list_products, to_list_products

    # thêm trường hợp "paint" với prod_idx = -1 hay nói cách khác là xóa
    def paint(self, stock_idx, prod_idx, position, size):
        width, height = (0, 0)

        self.cutted_stocks[stock_idx] = 1
        width, height = size

        self.stock_info[stock_idx][prod_idx] += 1
        self.products[prod_idx]["quantity"] -= 1

        print("stock_idx", stock_idx, "prod_idx", prod_idx, "position", position, "size", size) 

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
            print("===========================")
            print(self.amount_of_products)
            for pr_idx in self.products_indices:
                print(self.products[pr_idx])
            for st_idx in self.stocks_indices:
                print(self._get_stock_size_(self.stocks[st_idx]))
            print("===========================")

            self.first_action = False
            cut = False
            for pr_idx in self.products_indices:
                prod = self.products[pr_idx]
                # Kiểm tra số lượng của sản phẩm
                while (prod["quantity"]>0):
                    print(self.products)
                    prod_size = prod["size"]

                    # Vòng lặp duyệt qua tất cả stock
                    for st_idx in self.stocks_indices:

                        stock = self.stocks[st_idx]
                        stock_w, stock_h = self._get_stock_size_(stock)
                        prod_w, prod_h = cp.deepcopy(prod_size)

                        if stock_w >= prod_w and stock_h >= prod_h:
                            pos_x, pos_y = None, None
                            for x in range(stock_w - prod_w + 1):
                                for y in range(stock_h - prod_h + 1):
                                    
                                    if self._can_place_(stock, (x, y), (prod_w, prod_h)):
                                        pos_x, pos_y = x, y
                                        cut = True

                                        self.paint(st_idx, pr_idx, (pos_x,pos_y), (prod_w, prod_h))
                                        action = {"stock_idx": st_idx, "size": (prod_w, prod_h), "position": (pos_x, pos_y), "product_idx": pr_idx}
                                        self.action_list.append(action)
                                        
                                        break
                                if pos_x is not None and pos_y is not None:
                                    break

                            if pos_x is not None and pos_y is not None:
                                break
                    
                        if stock_w >= prod_h and stock_h >= prod_w:
                            pos_x, pos_y = None, None
                            for x in range(stock_w - prod_h + 1):
                                for y in range(stock_h - prod_w + 1):
                                    if self._can_place_(stock, (x, y), (prod_h, prod_w)):
                                        pos_x, pos_y = x, y
                                        cut = True

                                        self.paint(st_idx, pr_idx, (pos_x,pos_y), (prod_h, prod_w))
                                        action = {"stock_idx": st_idx, "size": (prod_h, prod_w), "position": (pos_x, pos_y), "product_idx": pr_idx}
                                        self.action_list.append(action)
                                        
                                        break
                                if pos_x is not None and pos_y is not None:
                                    break
                                
                            if pos_x is not None and pos_y is not None:
                                break

            # if not cut:
            #     print("can't fulfill demand")
            #     return {'stock_idx': -1, 'size': (-1, -1), 'position': (-1, -1), 'product_idx': -1}

            # the update algo is here
            # Phát: ý tưởng là duyệt từ sau ra các stock đã cắt từ stock đó tìm
            # một product ảo (bao hết các product hiện có) rồi thử đặt vào các 
            # stock nhỏ hơn
            for st_idx in reversed(self.stocks_indices):
                print("from", st_idx)
                if (self.cutted_stocks[st_idx]==0):
                    continue

                change = False
                stock = self.stocks[st_idx]

                # tìm product ảo
                used_surface = np.sum(stock>=0)
                
                temp_w = max(np.sum(stock>=0, axis=0))
                temp_h = max(np.sum(stock>=0, axis=1))

                # cắt thử các stock nhỏ hơn
                for st_idx2 in reversed(self.stocks_indices):
                    if (st_idx2==st_idx):
                        break
                    print("to", st_idx2)
                    check_stock = self.stocks[st_idx2]
                    check_size = self._get_stock_size_(check_stock)
                    check_surface = check_size[0] * check_size[1]
                    
                    if (check_surface < used_surface):
                        continue

                    fit, fit_list, from_list_products, to_list_products = self._fit_(st_idx, st_idx2)

                    if (fit):
                        change = True
                        # clear old information
                        # clear action
                        self.action_list = [ac for ac in self.action_list if ac["stock_idx"] != st_idx]
                        
                        # clear paint
                        self.paint(st_idx, -1, (0,0), (temp_w, temp_h))
                        # print(self.stocks)
                        self.stock_info[st_idx] = from_list_products
                        
                        # add new action
                        for i, amount in enumerate(to_list_products):
                            self.products[i]["quantity"]+= amount
                        for ac in fit_list:
                            self.paint(ac["stock_idx"], ac["product_idx"], ac["position"], ac["size"])
                            self.action_list.append(ac)

                        print(self.products)
                        break

                if not change:
                    break

        # Lấy product ra từ stock đã fill
        end_time = time.time()
        self.total_time += end_time - start_time
        return self.get_from_stocks()

    # Hàm này sẽ có chức năng khởi tạo các giá trị bên trong hàm khởi tạo của class
    # Initialize member variable
    # Hàm này Phát làm lại vì cảm giác chương trình chạy nhanh hơn :vv, cái của Phước vấn đúng nhe.
    def init_variable(self, list_stocks, list_products):
        self.stocks = cp.deepcopy(list_stocks)
        self.products = cp.deepcopy(list_products)

        for prod in self.products:
            self.amount_of_products += prod['quantity']
        self.num_products = len(list_products)
        self.num_stocks = len(list_stocks)
        self.cutted_stocks = np.full((self.num_stocks,), fill_value=0, dtype=int)
        self.stock_info = np.full((self.num_stocks, self.num_products), fill_value=0, dtype = int)

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
        
    # Mô tả: Hàm này sẽ tìm trong đống stock đã cắt, kiểm tra trong stock đã cắt đó nếu chứa product nào thì mình 
    # sẽ lấy index của product đó. Thực hiện tô lại màu -1 cho product đã lấy ra, chuyển cutted_stock về 0 
    # Phát: thay vì chạy rồi lấy ra từng miếng thì trong quá trình cắt ta thêm vào action list để khi get thì trả về action lại index đó
    def get_from_stocks(self):
        action = self.action_list[self.action_called]

        # xem đã đủ hay chưa, nếu đã lấy hết action, thì set first_action=True để reset cho dữ liệu mới
        if (self.action_called==self.amount_of_products-1):
            self.first_action = True
        else:
            self.action_called+=1

        return action
    
    # cân đo đông đếm
    # Phước code thêm phần module time gì nha.
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