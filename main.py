import numpy as np
from scipy.stats import truncnorm
from queue import PriorityQueue

def main():
    print('helloworld')

def get_truncated_norm(mean: float, stddev: float, low: float, high: float):
    return truncnorm(
        (low - mean) / stddev,
        (high - mean) / stddev,
        loc = mean,
        scale = stddev
    )


    
if __name__ == '__main__':
    main()