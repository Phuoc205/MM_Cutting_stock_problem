from policy import Policy
import numpy as np

class Policy2312593(Policy):
    def __init__(self):
        pass

    def get_action(self, observation, info):
        list_prods = observation["products"]
        list_stocks = observation["stocks"]

        # Descending
        products_indices = sorted(
            range(len(list_prods)),
            key=lambda idx: list_prods[idx]["size"][0] * list_prods[idx]["size"][1],
            reverse=True,
        )
        stocks_indices = sorted(
            range(len(list_stocks)),
            key=lambda idx: self._get_stock_size_(list_stocks[idx])[0] * self._get_stock_size_(list_stocks[idx])[1],
            reverse=True,
        )

        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = 0, 0
        
        for pr_idx in products_indices:
            prod = list_prods[pr_idx]
            if prod["quantity"] > 0:
                prod_size = prod["size"]

                # Loop through all stocks
                for st_idx in stocks_indices:
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

        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}

    # Student code here
    # You can add more functions if needed
