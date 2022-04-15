import numpy as np
from scipy.stats import truncnorm
from queue import PriorityQueue


def main():
    # hyperparameters
    NUM_CUSTOMERS = 160
    MAX_ARRIVAL_TIME = 8
    CustomerQueue = generate_customers(NUM_CUSTOMERS, MAX_ARRIVAL_TIME)


def get_truncated_norm(mean: float, stddev: float, low: float, high: float):
    return truncnorm(
        (low - mean) / stddev,
        (high - mean) / stddev,
        loc=mean,
        scale=stddev
    )


def generate_customers(numCustomers: int, maxArrivalTime: float,
                       mean: float = 0.5,
                       stddev: float = 5,
                       low: float = 5,
                       high: float = 15) -> PriorityQueue:
    """generates a priority queue of customers with different arrival times and work unit requirements

    Args:
        numCustomers (int): number of customers to generate into queue
        maxArrivalTime (float): latest time a customer can arrive
        mean (float, optional): mean of work unit norm distribution. Defaults to 0.5.
        stddev (float, optional): standard deviation of work unit norm distribution. Defaults to 5.
        low (float, optional): min value of work unit norm distribution. Defaults to 5.
        high (float, optional): max value of work unit norm distribution. Defaults to 15.

    Returns:
        PriorityQueue: priority queue ordered by arrival time containing work units of customers
    """
    customerQueue = PriorityQueue()

    TruncatedNorm = get_truncated_norm(mean, stddev, low, high)
    # genearte work units
    workUnits = TruncatedNorm.rvs(numCustomers)

    for i in range(numCustomers):
        # randomly generate work units and arrival time
        customerArirvalTime = np.random.uniform(0, maxArrivalTime)
        customerQueue.put((customerArirvalTime, workUnits[i]))

    return customerQueue


if __name__ == '__main__':
    main()
