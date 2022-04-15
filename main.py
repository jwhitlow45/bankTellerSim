import numpy as np
from scipy.stats import truncnorm
from queue import PriorityQueue

def main():
    for i in generate_customers(160, 8).queue:
        print(i)

def get_truncated_norm(mean: float, stddev: float, low: float, high: float):
    return truncnorm(
        (low - mean) / stddev,
        (high - mean) / stddev,
        loc = mean,
        scale = stddev
    )

def generate_customers(numCustomers: int, maxArrivalTime: float) -> PriorityQueue:
    customerQueue = PriorityQueue()
    
    TruncatedNorm = get_truncated_norm(0.5, 5, 5, 15)
    # genearte work units
    workUnits = TruncatedNorm.rvs(numCustomers)
    
    for i in range(numCustomers):
        # randomly generate work units and arrival time
        customerArirvalTime = np.random.uniform(0, maxArrivalTime)
        customerQueue.put((customerArirvalTime, workUnits[i]))
        
    return customerQueue
    
if __name__ == '__main__':
    main()