from policy import Policy
import numpy as np

class PolicyDynamic(Policy):
    def __init__(self, policy_id=1):
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"
        self.policy_id = policy_id
        self.memo = {}  # Bảng ghi nhớ cho DP

    def dp(self, state):
        """
        Hàm Dynamic Programming tính toán chi phí tối ưu từ trạng thái 'state'.

        Args:
            state (tuple): Trạng thái hiện tại (số lượng còn lại của từng loại yêu cầu).
        
        Returns:
            cost (float): Chi phí tối ưu từ trạng thái này.
            pattern (list): Cách cắt tối ưu tại trạng thái này.
        """
        if state in self.memo:
            return self.memo[state]

        # Nếu không còn yêu cầu nào
        if sum(state) == 0:
            return 0, []

        min_cost = float('inf')
        best_pattern = None

        # Thử tất cả các cách cắt có thể
        for pattern in self.generate_cutting_patterns(state):
            new_state = tuple(max(0, state[i] - pattern[i]) for i in range(len(state)))
            cost, _ = self.dp(new_state)
            if 1 + cost < min_cost:
                min_cost = 1 + cost
                best_pattern = pattern

        self.memo[state] = (min_cost, best_pattern)
        return min_cost, best_pattern

    def generate_cutting_patterns(self, state):
        """
        Sinh ra tất cả các cách cắt khả thi dựa trên trạng thái hiện tại.
        """
        # Ví dụ cơ bản: tạo các pattern cắt tùy thuộc vào trạng thái.
        num_items = len(state)
        patterns = []

        for i in range(1, 2**num_items):  # Tạo tổ hợp các cách cắt
            pattern = [int(x) for x in bin(i)[2:].zfill(num_items)]
            if all(state[j] >= pattern[j] for j in range(num_items)):  # Chỉ chọn pattern hợp lệ
                patterns.append(pattern)

        return patterns

    def get_action(self, observation, info):
        """
        Lựa chọn hành động dựa trên thuật toán DP.

        Args:
            observation: Trạng thái hiện tại của môi trường (số lượng yêu cầu).
            info: Thông tin thêm từ môi trường.
        
        Returns:
            action (list): Cách cắt tối ưu cho trạng thái hiện tại.
        """
        state = tuple(observation['demand'])  # Chuyển trạng thái thành tuple để lưu vào bảng ghi nhớ
        _, best_pattern = self.dp(state)
        return best_pattern if best_pattern else [0] * len(state)
