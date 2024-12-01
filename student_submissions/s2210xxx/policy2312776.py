from policy import Policy
import numpy as np
from scipy.optimize import linprog
import time

class Simplex:
    def __init__(self, L, products, b, a):
        self.L = L  # Chiều dài của tấm stock
        self.products = products  # Chiều dài của các sản phẩm
        self.b = b  # Số lượng sản phẩm cần cắt
        self.a = a  # Ma trận a_ij (số lượng sản phẩm j có thể cắt từ stock i)
        self.num_stock = a.shape[0]  # Số lượng loại tấm stock
        self.num_products = len(products)  # Số lượng sản phẩm
        self.tableau = None  # Bảng Simplex
        self.basis = []  # Biến cơ sở ban đầu

    def initialize_tableau(self):
        # Xây dựng bảng Simplex ban đầu
        identity = np.eye(self.num_stock)
        self.tableau = np.hstack((self.a, identity, self.b.reshape(-1, 1)))

        # Thêm hàng hàm mục tiêu (chúng ta tối thiểu hóa số tấm stock)
        z_row = np.hstack((-np.ones(self.num_stock), np.zeros(self.num_stock + 1)))
        self.tableau = np.vstack((self.tableau, z_row))

        # Xác định biến cơ sở ban đầu
        self.basis = list(range(self.num_products, self.num_products + self.num_stock))
        
    def solve(self):
        # Giải bài toán Simplex sử dụng scipy linprog
        c = np.ones(self.num_stock)
        result = linprog(c, A_ub=self.a, b_ub=self.b, method='simplex')
        return result.x, result.fun  # Trả về số lượng tấm stock và chi phí tối thiểu

    def get_action(self):
        # Trả về hành động (tấm stock và vị trí cắt) dựa trên kết quả giải bài toán
        solution, _ = self.solve()
        return solution
    
class Policy2312776(Policy):
    
    def __init__(self, simplex = False):
        # Giả sử `simplex` là một đối tượng hoặc phương thức tối ưu
        self.simplex = simplex
        self.evalue = {}

    def get_action(self, observation, info):
        # Lấy thông tin về các sản phẩm và các tấm stock từ observation
        stocks = observation["stocks"]
        products = observation["products"]

        # Quyết định hành động (chọn sản phẩm và tấm stock để cắt)
        # Dựa trên các thông tin trong Simplex và environment
        action = self._select_action(stocks, products, info)

        # Trả về hành động dưới dạng một dictionary
        return action

    def _select_action(self, stocks, products, info):
        """
        Phương thức này có thể sử dụng thuật toán Simplex hoặc một chiến lược tối ưu
        để chọn hành động phù hợp (chọn sản phẩm, tấm stock, vị trí cắt).
        """
        
        # Tìm tấm stock phù hợp để cắt sản phẩm
        stock_idx, size, position = self.execute_simplex(stocks, products)

        # Tạo hành động
        action = {
            "stock_idx": stock_idx,
            "size": size,
            "position": position
        }

        return action

    def _get_available_product(self, products):
        """Tìm sản phẩm có sẵn chưa được cắt hết"""
        for product in products:
            if product["quantity"] > 0:
                return product
        return None

    def execute_simplex(self, stocks, products):
        """
        Phương thức này sử dụng Simplex để tìm tấm stock và vị trí cắt tối ưu.
        """
        
        
        # Thiết lập bài toán tối ưu với Simplex
        # Giả sử có các biến: X[i] = 1 nếu sản phẩm thứ i được cắt vào stock thứ i, và 0 nếu không
        num_stocks = len(stocks)
        num_products = len(products)
        
        # Lấy diện tích của phần stock chưa được fill, phần fill rồi sẽ là 0
        areas = []
        for stock in stocks:
            # Kiểm tra xem stock có ô trống (-1) tức là được fill hay không
            if np.any(stock == -1):
                # Nếu đã được fill rồi, diện tích là 0
                areas.append(0)
            else:
                # Tính diện tích hợp lệ (không phải -2)
                valid_area = np.sum(stock != -2)
                areas.append(valid_area)
            
        # Hàm mục tiêu: tối thiểu hóa diện tích sử dụng
        c = np.array(areas)
        
        # Ràng buộc: kích thước sản phẩm phải vừa với tấm stock
        A_eq = []
        b_eq = []

        # Các ràng buộc để sản phẩm có thể vừa trong stock
        for i, stock in enumerate(stocks):
            stock_width = np.sum(np.any(stock != -2, axis=1))
            stock_height = np.sum(np.any(stock != -2, axis=0))
            
            # Ràng buộc về diện tích stock
            row = np.zeros(num_stocks)
            row[i] = 1
            A_eq.append(row)
            b_eq.append(stock_width * stock_height)
        
        # Giải bài toán tối ưu hóa tuyến tính
        result = linprog(c, A_eq=np.array(A_eq), b_eq=np.array(b_eq), method='simplex')

        # Kiểm tra kết quả
        if result.success:
            # Chọn tấm stock và vị trí cắt từ kết quả của Simplex
            stock_idx = np.argmax(result.x)
            return stock_idx, (0, 0)  # Vị trí cắt có thể là (0, 0) hoặc tính toán thêm
        else:
            return None, None

    def fill_in_stock(self, stock, product):
        stock_w = np.sum(np.any(stock != -2, axis=1))
        stock_h = np.sum(np.any(stock != -2, axis=0))
        prod_w = product['width']
        prod_h = product['height']
        pos_x, pos_y = None
        
        for x in range(stock_w - prod_w + 1):
            for y in range(stock_h - prod_h + 1):
                if self._can_place_(stock, (x, y), product['size']):
                    pos_x, pos_y = x, y
                    break
            if pos_x is not None and pos_y is not None:
                break
            
        if pos_x is not None and pos_y is not None:
            return True  # Trả về True nếu đã fill thành công

        return False

    def get_evaluate(self):
        return self.evalue
    
class Policy2312593(Policy):
    def __init__(self):
        self.stocks = None
        self.products = None
        self.num_stocks = 0
        self.num_products = 0
        self.cutted_stocks = None
        self.first_action =  False
        
    def paint(self, stock_idx, prod_idx, position):
        size = self.products[prod_idx]["size"]
        width, height = size
        x, y = position

        # Check if the product is in the product list
        product_idx = None
        for i, product in enumerate(self.products):
            if np.array_equal(product["size"], size):
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
                    and y + height <= stock_height
                ):
                    # Check if the position is empty
                    if np.all(stock[x : x + width, y : y + height] == -1):
                        self.cutted_stocks[stock_idx] = 1
                        stock[x : x + width, y : y + height] = product_idx
                        self.products[product_idx]["quantity"] -= 1
                        

    def get_action(self, observation, info):
        if self.first_action:
            list_prods = observation["products"]
            list_stocks = observation["stocks"]
            self.init_variable(list_stocks, list_prods)
            
            # Descending
            sorted_products = sorted(list_prods, key=lambda product: product['size'][0] * product['size'][1], reverse=True)
            product_indies = []
            for s_st in range(self.num_products):
                for st in range(self.num_products):
                    if (np.shape(list_prods[st]['size'])==np.shape(sorted_products[s_st]['size'])) and (np.all(list_prods[st]['size']==sorted_products[s_st]['size'])):
                        product_indies.append(st)

            sorted_stocks = sorted(list_stocks, key=lambda stock: np.sum(np.any(stock != -2, axis=1)) * np.sum(np.any(stock != -2, axis=0)), reverse=True)
            stock_indies = []
            for s_st in range(self.num_stocks):
                for st in range(self.num_stocks):
                    if (np.shape(list_stocks[st])==np.shape(sorted_stocks[s_st])) and (np.all(list_stocks[st]==sorted_stocks[s_st])):
                        stock_indies.append(st)

            prod_size = [0, 0]
            stock_idx = -1
            pos_x, pos_y = 0, 0
            
            for pr_idx in product_indies:
                prod = list_prods[pr_idx]
                if prod["quantity"] > 0:
                    prod_size = prod["size"]

                    # Loop through all stocks
                    for st_idx in stock_indies:
                        stock = list_stocks[st_idx]
                        stock_w, stock_h = self._get_stock_size_(stock)
                        prod_w, prod_h = prod_size

                        if stock_w < prod_w or stock_h < prod_h:
                            continue

                        pos_x, pos_y = None, None
                        for x in range(stock_w - prod_w + 1):
                            for y in range(stock_h - prod_h + 1):
                                if self._can_place_(stock, (x, y), prod_size):
                                    pos_x, pos_y = x, y
                                    break
                            if pos_x is not None and pos_y is not None:
                                break

                        if pos_x is not None and pos_y is not None:
                            stock_idx = st_idx
                            break

                    if pos_x is not None and pos_y is not None:
                        break
        
        # Lấy product ra từ stock đã fill

        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}

    def init_variable(self, list_stocks, list_products):
        self.stocks = list_stocks
        self.products = list_products
        self.num_products = len(list_products)
        self.num_stocks = len(list_stocks)
        self.cutted_stocks = np.full((self.num_stocks,), fill_value=0, dtype=int)

    def get_from_stocks(self):
        for i in self.num_stocks:
            if self.cutted_stocks[i] == 1:
                stock = self.stocks[i]
                