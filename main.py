import numpy as np
from scipy.stats import truncnorm
from queue import PriorityQueue
from datetime import datetime


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
    WORK_UNITS_PER_HOUR = 10
    BANK_WORKING_HOURS = 8
    
    lines = []
    headers = 'num days simulated,num customers,bank working hours,num windows,work units per hour per window,avg wait time,avg unhelped customers\n'
    lines.append(headers)
    
    startTime = datetime.now()
    
    for NUM_WINDOWS in [9, 10, 11]:
        waitTimes = []
        unhelpedCustomers = []
        
        for i in range(NUM_DAYS_SIMULATED):
            # create windows
            WindowQueue = PriorityQueue()
            for i in range(NUM_WINDOWS):
                WindowQueue.put(Window(efficiency=WORK_UNITS_PER_HOUR))

            # create customers
            CustomerQueue = generate_customers(NUM_CUSTOMERS, BANK_WORKING_HOURS)

            while not CustomerQueue.empty():
                curWindow = WindowQueue.get()
                curCustomer = CustomerQueue.get()

                # update time to match customer arrival time if window has been sitting empty
                if curWindow.time < curCustomer.arrivalTime:
                    curWindow.time = curCustomer.arrivalTime

                completedWorkTime = curWindow.time + curCustomer.workUnits / curWindow.efficiency
                # bank is closed after working hours hours, so stop helping customers
                # if a work request would go into after hours
                if completedWorkTime > BANK_WORKING_HOURS:
                    CustomerQueue.put(curCustomer)
                    break

                curCustomerWaitTime = curWindow.time - curCustomer.arrivalTime
                waitTimes.append(curCustomerWaitTime)

                # put window back onto queue with updated time
                curWindow.time = completedWorkTime
                WindowQueue.put(curWindow)

            unhelpedCustomers.append(len(CustomerQueue.queue))


        avgTimeWaiting = sum(waitTimes) / len(waitTimes)
        avgUnhelpedCustomers = sum(unhelpedCustomers) / len(unhelpedCustomers)
        
        line = f'{NUM_DAYS_SIMULATED},{NUM_CUSTOMERS},{BANK_WORKING_HOURS},{NUM_WINDOWS},{WORK_UNITS_PER_HOUR},{avgTimeWaiting},{avgUnhelpedCustomers}\n'
        lines.append(line)
        
    print(datetime.now() - startTime)
        
    with open('results_short_queue.csv', 'w') as FILE:
        FILE.writelines(lines)


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
