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
        self.list_flags = [[]]
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
        self.list_flags = [[]]
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
                        flag = self.list_flags[st_idx]
                        
                        if stock_w < prod_w or stock_h < prod_h:
                            continue

                        found = False
                        for i in range(len(flag) - 1):
                            gap_start, gap_end = flag[i], flag[i + 1]
                            # Điều kiện kiểm tra khoảng trống đủ để đặt sản phẩm
                            if prod_w <= gap_end - gap_start:
                                pos_x, pos_y = None, None
                                for x in range(gap_start, gap_end - prod_w + 1):
                                    for y in range(stock_h - prod_h + 1):
                                        if self._can_place_(stock, (x, y), prod_size):

                                            pos_x, pos_y = x, y
                                            self.paint(st_idx, pr_idx, (pos_x, pos_y), [])
                                            # thêm bước thêm action vào 1 danh sách
                                            self.action_list.append({"stock_idx": st_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": pr_idx})
                                            print({"stock_idx": st_idx, "size": prod_size, "position": (pos_x, pos_y), "product_idx": pr_idx})
                                            # Cập nhật flag
                                            flag.append(x+prod_w)
                                            flag.sort()
                                            found = True
                                            break  # Thoát khỏi vòng lặp tìm khoảng phù hợp
                                    if found:
                                        break
                            
                            if found:
                                break
                            
                        if found:
                            break
            
            # for st_idx in reversed(self.stocks_indices):
            #     if (self.cutted_stocks[st_idx]==0):
            #         continue
                
            #     change = False
            #     stock = self.stocks[st_idx]
            #     size = self._get_stock_size_(stock)

            #     # tìm product ảo
            #     temp_w = max(np.sum(stock>=0, axis=0))
            #     temp_h = max(np.sum(stock>=0, axis=1))
            #     # print (temp_w, " ", temp_h)

            #     # cắt thử các stock nhỏ hơn
            #     for st_idx2 in reversed(self.stocks_indices):
            #         check_stock = self.stocks[st_idx2]
            #         check_size = self._get_stock_size_(check_stock)
                    
            #         if (check_size[0] * check_size[1] < temp_w * temp_h):
            #             break

            #         if (check_size[0] * check_size[1] >= size[0] * size[1]):
            #             break

            #         # khi thay được ta thay tất cả các bước có stock index cũ sang mới, trong quá trình đó thực hiện paint -1 và cả product mới
            #         # Phát hỏi? liệu có cần phải paint lại không? có ảnh hưởng gì nhiều không? cái quantity khi dùng paint ra âm có sao không?
            #         if self._can_place_(check_stock, (0,0), (temp_w, temp_h)):
            #             for ac in self.action_list:
            #                 self.paint(st_idx, -1, (0,0), (temp_w, temp_h))
            #                 if ac['stock_idx']==st_idx:
            #                     self.paint(st_idx2, ac['product_idx'], ac['position'], ())
            #                     ac['stock_idx'] = st_idx2
            #                     change = True
            #     if not change:
            #         break            
                        

        # Lấy thời gian kết thúc
        end_time = time.time()
        self.total_time += end_time - start_time
        # Lấy product ra từ stock đã fill
        return self.get_from_stocks()

    # Hàm này sẽ có chức năng khởi tạo các giá trị bên trong hàm khởi tạo của class
    def init_variable(self, list_stocks, list_products):
        self.stocks = [np.copy(stock) for stock in list_stocks]
        self.products = []

        # Xoay sản phẩm để chiều rộng lớn hơn hoặc bằng chiều cao
        for prod in list_products:
            size = prod["size"]
            if size[1] > size[0]:
                size = size[::-1]
            self.products.append({"size": size, "quantity": prod["quantity"]})

        self.num_products = len(list_products)
        self.num_stocks = len(list_stocks)
        self.cutted_stocks = np.full((self.num_stocks,), fill_value=0, dtype=int)
        
        # Sắp xếp products theo kích thước 1 chiều giảm dần
        self.products_indices = sorted(
            range(self.num_products),
            key=lambda idx: max(self.products[idx]["size"]),
            reverse=True,
        )

        # Sắp xếp stocks theo kích thước 1 chiều giảm dần
        self.stocks_indices = sorted(
            range(self.num_stocks),
            key=lambda idx: max(self._get_stock_size_(self.stocks[idx])),
            reverse=True,
        )
        
        for idx in self.stocks_indices:
            stock_size = self._get_stock_size_(self.stocks[idx])
            if stock_size[1] > stock_size[0]:  # Rotate stock to ensure width >= height
                self.stocks[idx] = np.transpose(self.stocks[idx])

        for stock in self.stocks:
            stock_width, _ = self._get_stock_size_(stock)
            # Khởi tạo listflag là danh sách có một khoảng duy nhất ban đầu
            self.list_flags.append([0, stock_width])
            
        # Đếm số lượng mẫu cần cắt
        for prod in self.products:
            self.amount_of_products+=prod['quantity']
        
    # Mô tả: Hàm này sẽ tìm trong đống stock đã cắt, kiểm tra trong stock đã cắt đó nếu chứa product nào thì mình 
    # sẽ lấy index của product đó. Thực hiện tô lại màu -1 cho product đã lấy ra, chuyển cutted_stock về 0
    def get_from_stocks(self):                
        # lấy Action
        action = self.action_list[self.action_called]

        # xem đã đủ hay chưa, nếu đã lấy hết action, thì set first_action=True để reset cho dữ liệu mới
        if (self.action_called==self.amount_of_products-1):
            self.first_action = True
        else:
            self.action_called+=1

        return action
    
    # cân đo đông đếm
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