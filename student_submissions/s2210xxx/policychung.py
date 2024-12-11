from policy import Policy
from student_submissions.s2210xxx.policy2312776 import Policy2312776
from student_submissions.s2210xxx.policy2312593 import Policy2312593
import numpy as np

class Policychung(Policy):
    def __init__(self, policy_id=1):
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"

        # Student code here
        if policy_id == 1:
            self.Policy = Policy2312776()
        elif policy_id == 2:
            self.Policy = Policy2312593()
            

    def get_action(self, observation, info):
        return self.Policy.get_action(observation, info)
    
    def evaluate(self):
        return self.Policy.evaluate()
    

    # Student code here
    # You can add more functions if needed