import argparse

import numba as nb
import numpy as np

@nb.vectorize(['int32(int32)'], target='cuda')
def check_prime_gpu(num):
    for i in range(2, (num // 2) + 1):
       if (num % i) == 0:
           return 0
    return num

@nb.vectorize(['int32(int32)'], target='parallel')
def check_prime_no_gpu(num):
    for i in range(2, (num // 2) + 1):
       if (num % i) == 0:
           return 0
    return num

def check_primes(limit, use_gpu=True, last=10):
   numbers = np.arange(0, limit, dtype=np.int32)
   if use_gpu:
       primes = check_prime_gpu(numbers)
   else:
       primes = check_prime_no_gpu(numbers)
   return [n for n in np.flatnonzero(primes)[-1*last:]]


parser = argparse.ArgumentParser()
parser.add_argument("--no_gpu", action="store_true", help="Turn off GPU usage")
parser.add_argument("limit", type=int, help="Higher integer to check")
parser.add_argument("--last", type=int, default=10,
                    help="Number of last ""primes to return (default: 10)")

if __name__ == "__main__":
    args = parser.parse_args()
    use_gpu = False if args.no_gpu else True
    print(check_primes(args.limit, use_gpu, args.last))
