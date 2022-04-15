import numpy as np
from scipy.stats import truncnorm
from queue import PriorityQueue


class Window:
    def __init__(self, time: float = 0, efficiency: float = 10):
        self.time = time
        self.efficiency = efficiency

    def __lt__(self, obj):
        return ((self.time) < (obj.time))

    def __gt__(self, obj):
        return ((self.time) > (obj.time))

    def __le__(self, obj):
        return ((self.time) <= (obj.time))

    def __ge__(self, obj):
        return ((self.time) >= (obj.time))

    def __eq__(self, obj):
        return (self.time == obj.time)

    def __repr__(self):
        print(f'[WINDOW] Time: {self.time}, Eff: {self.efficiency}')


class Customer:
    def __init__(self, arrivalTime: float, workUnits: float):
        self.arrivalTime = arrivalTime
        self.workUnits = workUnits

    def __lt__(self, obj):
        return ((self.arrivalTime) < (obj.arrivalTime))

    def __gt__(self, obj):
        return ((self.arrivalTime) > (obj.arrivalTime))

    def __le__(self, obj):
        return ((self.arrivalTime) <= (obj.arrivalTime))

    def __ge__(self, obj):
        return ((self.arrivalTime) >= (obj.arrivalTime))

    def __eq__(self, obj):
        return (self.arrivalTime == obj.arrivalTime)

    def __repr__(self):
        print(f'[WINDOW] Time: {self.arrivalTime}, Eff: {self.workUnits}')


def main():
    # hyperparameters
    NUM_CUSTOMERS = 160
    MAX_ARRIVAL_TIME = 8
    NUM_WINDOWS = 10
    WORK_UNITS_PER_HOUR = 10
    BANK_WORKING_HOURS = 8

    CustomerQueue = generate_customers(NUM_CUSTOMERS, MAX_ARRIVAL_TIME)
    WindowQueue = PriorityQueue()

    for i in range(NUM_WINDOWS):
        WindowQueue.put(Window(efficiency=WORK_UNITS_PER_HOUR))

    while not CustomerQueue.empty():
        curWindow = WindowQueue.get()
        curCustomer = CustomerQueue.get()
        completedWorkTime = curWindow.time + curCustomer.workUnits / curWindow.efficiency
        # bank is closed after working hours hours, so stop helping customers
        # if a work request would go into after hours
        if completedWorkTime > BANK_WORKING_HOURS:
            CustomerQueue.put(curCustomer)
            break

        curCustomerWaitTime = curWindow.time - curCustomer.arrivalTime

        # put window back onto queue with updated time
        curWindow.time = completedWorkTime
        WindowQueue.put(curWindow)

    for i in range(NUM_WINDOWS):
        # total time,
        WindowQueue.put(())


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
        customerQueue.put(Customer(customerArirvalTime, workUnits[i]))

    return customerQueue


if __name__ == '__main__':
    main()
