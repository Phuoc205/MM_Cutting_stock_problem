from policy import Policy
import numpy as np

class PolicyDynamic(Policy):
    def __init__(self, policy_id=1):
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"
        self.policy_id = policy_id

    def get_action(self, observation, info):
        # Parse observation
        stocks = observation["stocks"]  # List of stocks (matrices)
        products = observation["products"]  # List of products (dicts with size and quantity)

        # Build DP table for the largest stock
        max_w, max_h = stocks[0].shape()  # Assume all stocks have the same size

        # Initialize DP table
        dp = np.zeros((len(products) + 1, max_w + 1, max_h + 1), dtype=int)
        backtrack = np.full((len(products) + 1, max_w + 1, max_h + 1), -1, dtype=object)

        for i, product in enumerate(products, start=1):
            width, height = product["size"]
            quantity = product["quantity"]

            for w in range(max_w + 1):
                for h in range(max_h + 1):
                    # Case 1: Do not cut this product
                    dp[i][w][h] = dp[i - 1][w][h]

                    # Case 2: Cut this product (if it fits and quantity > 0)
                    if w >= width and h >= height and quantity > 0:
                        value_with_cut = dp[i - 1][w - width][h - height] + 1
                        if value_with_cut > dp[i][w][h]:
                            dp[i][w][h] = value_with_cut
                            backtrack[i][w][h] = (width, height)

        # Retrieve best fit from DP table
        best_stock_idx = -1
        best_product_idx = -1
        best_position = (0, 0)

        for stock_idx, stock in enumerate(stocks):
            stock_width = np.sum(np.any(stock != -2, axis=1))
            stock_height = np.sum(np.any(stock != -2, axis=0))

            # Start from the best state in the DP table for this stock
            w, h = stock_width, stock_height

            for i in range(len(products), 0, -1):
                if backtrack[i][w][h] != -1:
                    width, height = backtrack[i][w][h]

                    # Find the first empty position to place the product
                    for x in range(stock_width - width + 1):
                        for y in range(stock_height - height + 1):
                            if np.all(stock[x:x + width, y:y + height] == -1):
                                best_stock_idx = stock_idx
                                best_product_idx = i - 1
                                best_position = (x, y)
                                return {
                                    "stock_idx": best_stock_idx,
                                    "size": products[best_product_idx]["size"],
                                    "position": best_position,
                                }

        # If no valid action, return a dummy action
        return {
            "stock_idx": 0,
            "size": np.array([1, 1]),
            "position": np.array([0, 0]),
        }