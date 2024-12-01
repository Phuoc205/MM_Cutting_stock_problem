from policy import Policy
import numpy as np

class Policy2312593(Policy):
    def __init__(self):
        self.stocks = None
        self.products = None
        self.num_stocks = 0
        self.num_products = 0
        self.cutted_stocks = None
        self.first_action =  True
        
    def paint(self, stock_idx, prod_idx, position):
        size = self.products[prod_idx]["size"]
        width, height = size
        x, y = position

        self.cutted_stocks[stock_idx] = 1
        stock = self.stocks[stock_idx]
        stock[x : x + width, y : y + height] = prod_idx
        self.products[prod_idx]["quantity"] -= 1
                        

    def get_action(self, observation, info):
        if self.first_action:
            self.init_variable(observation["stocks"], observation["products"])
            self.first_action = False
            
            # Descending
            products_indices = sorted(
                range(self.num_products),
                key=lambda idx: self.products[idx]["size"][0] * self.products[idx]["size"][1],
                reverse=True,
            )
            stocks_indices = sorted(
                range(self.num_stocks),
                key=lambda idx: self._get_stock_size_(self.stocks[idx])[0] * self._get_stock_size_(self.stocks[idx])[1],
                reverse=True,
            )
            print (products_indices)
            for pr_idx in products_indices:
                print(pr_idx , ": ", self.products[pr_idx]["quantity"])
                prod = self.products[pr_idx]
                # Kiểm tra số lượng của sản phẩm
                while prod["quantity"] > 0:
                    prod_size = prod["size"]

                    # Vòng lặp duyệt qua tất cả stock
                    for st_idx in stocks_indices:
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
                                    self.paint(st_idx, pr_idx, (pos_x, pos_y))
                                    break   
                            
                            if pos_x is not None and pos_y is not None:
                                break
                            
                        if pos_x is not None and pos_y is not None:
                            break      
                        
        # Lấy product ra từ stock đã fill
        stock_idx, prod_size, position = self.get_from_stocks()
        return {"stock_idx": stock_idx, "size": prod_size, "position": position}


    # Hàm này sẽ có chức năng khởi tạo các giá trị bên trong hàm khởi tạo của class
    def init_variable(self, list_stocks, list_products):
        self.stocks = [np.copy(stock) for stock in list_stocks]
        self.products = [{"size": prod["size"], "quantity": prod["quantity"]} for prod in list_products]

        self.num_products = len(list_products)
        self.num_stocks = len(list_stocks)
        self.cutted_stocks = np.full((self.num_stocks,), fill_value=0, dtype=int)
        
    # Mô tả: Hàm này sẽ tìm trong đống stock đã cắt, kiểm tra trong stock đã cắt đó nếu chứa product nào thì mình 
    # sẽ lấy index của product đó. Thực hiện tô lại màu -1 cho product đã lấy ra, chuyển cutted_stock về 0 
    def get_from_stocks(self):
        
        for st_idx in range(self.num_stocks):
            if self.cutted_stocks[st_idx] == 1:
                stock = self.stocks[st_idx]
                stock_w, stock_h = self._get_stock_size_(stock)
                
                for i in range(stock_w):
                    for j in range(stock_h):
                        if stock[i, j] > 0:
                            pr_idx = stock[i, j]
                            prod_w, prod_h = self.products[pr_idx]["size"]
                            prod_w, prod_h = int(prod_w), int(prod_h)

                            stock[i : i + prod_w, j : j + prod_h] = -1
                            
                            if(np.all(stock<0)):
                                self.cutted_stocks[st_idx] = 0
                                
                            return {"stock_idx": st_idx, "size": [prod_w, prod_h], "position": (i, j)}