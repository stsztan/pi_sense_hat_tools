import math

def create_buckets(initial: int, final: int, n: int = 8):
    '''
    Creates n buckets based on initial and final integer numbers.
    
    Parameters:
        initial (int): Initial integer number to start with
        final (int): Final, but excludded integer number
        n (int): Number of buckets
    
    Returns:
        bucket_begins ([int]): List of bucket start integers, initial included, final excluded
    '''
    
    buckets_end = []

    range_len = final - initial
    float_steps = range_len / n
    
    # Calculate the range of each bucket
    for i in range(n):
        current_step = (i + 1) * float_steps
        current_bucket_end = initial + current_step
        current_bucket_stop = round(current_bucket_end)
        buckets_end.append(current_bucket_stop)
    
    initial_integer = math.floor(initial)
    buckets_begin_list = [initial_integer, *buckets_end]
    
    return buckets_begin_list
