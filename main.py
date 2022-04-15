import numpy as np
from scipy.stats import truncnorm
from queue import PriorityQueue
from datetime import datetime
from typing import List, Tuple

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
        return f'[WINDOW] Time: {self.time}, Eff: {self.efficiency}'


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
        return f'[CUSTOMER] Arrival Time: {self.arrivalTime}, Work Units: {self.workUnits}'


def main():
    # hyperparameters
    NUM_DAYS_SIMULATED = 10000
    NUM_CUSTOMERS = 160
    NUM_WINDOWS = 10
    TELLER_EFFICIENCY = 10
    BANK_WORKING_HOURS = 8
    LIGHT_QUEUE_CUTOFF = 0.5

    lines = []
    headers = 'num days simulated,num customers,num windows,bank working hours,work units per hour per window,avg wait time,avg unhelped customers\n'
    lines.append(headers)

    startTime = datetime.now()

    for NUM_WINDOWS in [9, 10, 11]:
        waitTimes = []
        unhelpedCustomers = []

        for i in range(NUM_DAYS_SIMULATED):
            # generate customers
            CustomerQueue = generate_customers(NUM_CUSTOMERS, BANK_WORKING_HOURS)
            
            # create separate queue for light requests
            TempQueue = PriorityQueue()
            LightCustomerQueue = PriorityQueue()
            for Customer in CustomerQueue.queue:
                if Customer.workUnits > 0.5:
                    TempQueue.put(Customer)
                else:
                    LightCustomerQueue.put(Customer)
            CustomerQueue = TempQueue
            
            # simulate normal lines
            waitTimeList, numUnhelpedCustomers = simulate_day(
                CustomerQueue, NUM_WINDOWS, BANK_WORKING_HOURS, TELLER_EFFICIENCY)
            waitTimes += waitTimeList
            unhelpedCustomers.append(numUnhelpedCustomers)
            
            waitTimeList, numUnhelpedCustomers = simulate_day(
                LightCustomerQueue, 1, BANK_WORKING_HOURS, TELLER_EFFICIENCY)
            waitTimes += waitTimeList
            unhelpedCustomers.append(numUnhelpedCustomers)
            
        avgTimeWaiting = sum(waitTimes) / len(waitTimes)
        avgUnhelpedCustomers = sum(unhelpedCustomers) / len(unhelpedCustomers)

        line = f'{NUM_DAYS_SIMULATED},{NUM_CUSTOMERS},{NUM_WINDOWS},{BANK_WORKING_HOURS},{TELLER_EFFICIENCY},{avgTimeWaiting},{avgUnhelpedCustomers}\n'
        lines.append(line)

    print(datetime.now() - startTime)

    with open('results_light_queue.csv', 'w') as FILE:
        FILE.writelines(lines)


def simulate_day(CustomerQueue: PriorityQueue(), numWindows: int, bankWorkingHours: float, tellerEfficiency: float):
    """simulates one day of teller simulation

    Args:
        numCustomers (int): number of customers to generate
        bankWorkingHours (float): number of hours bank is open
        numWindows (int): number of windows in bank
        tellerEfficiency (float): efficiency of each bank teller

    Returns:
        List[List[float], int]: list of wait times and number of unhelped customers
    """

    waitTimes = []

    # create windows
    WindowQueue = PriorityQueue()
    for i in range(numWindows):
        WindowQueue.put(Window(efficiency=tellerEfficiency))

    while not CustomerQueue.empty():
        curWindow = WindowQueue.get()
        curCustomer = CustomerQueue.get()

        # update time to match customer arrival time if window has been sitting empty
        if curWindow.time < curCustomer.arrivalTime:
            curWindow.time = curCustomer.arrivalTime

        completedWorkTime = curWindow.time + curCustomer.workUnits / curWindow.efficiency
        # bank is closed after working hours, so stop helping customers
        # if a work request would go into after hours
        if completedWorkTime > bankWorkingHours:
            CustomerQueue.put(curCustomer)
            break

        curCustomerWaitTime = curWindow.time - curCustomer.arrivalTime
        waitTimes.append(curCustomerWaitTime)

        # put window back onto queue with updated time
        curWindow.time = completedWorkTime
        WindowQueue.put(curWindow)

    unhelpedCustomers = len(CustomerQueue.queue)

    return (waitTimes, unhelpedCustomers)


def get_truncated_norm(mean: float, stddev: float, low: float, high: float):
    return truncnorm(
        (low - mean) / stddev,
        (high - mean) / stddev,
        loc=mean,
        scale=stddev
    )


def generate_customers(numCustomers: int, bankWorkingHours: float,
                       mean: float = 0.5,
                       stddev: float = 5,
                       low: float = 5,
                       high: float = 15) -> PriorityQueue:
    """generates a priority queue of customers with different arrival times and work unit requirements

    Args:
        numCustomers (int): number of customers to generate into queue
        bankWorkingHours (float): how long bank is open
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
        customerArirvalTime = np.random.uniform(0, bankWorkingHours)
        customerQueue.put(Customer(customerArirvalTime, workUnits[i]))

    return customerQueue


if __name__ == '__main__':
    main()
