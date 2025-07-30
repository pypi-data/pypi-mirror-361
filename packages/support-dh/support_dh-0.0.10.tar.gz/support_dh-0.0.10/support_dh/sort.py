import random

def is_sorted(arr: list) -> bool:
    """check if the list is sorted"""
    for i in range(len(arr)-1):
        if arr[i] <= arr[i+1]:
            if i >= len(arr)-2:
                return True
        elif arr[i] > arr[i+1]:
            return False
            
def quick_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    lesser_arr, equal_arr, graeter_arr = [], [], []
    for num in arr:
        if num < pivot:
            lesser_arr.append(num)
        elif num > pivot:
            graeter_arr.append(num)
        else:
            equal_arr.append(num)
    return quick_sort(lesser_arr) + equal_arr + quick_sort(graeter_arr)

def bogo_sort(arr: list) -> list:
    """the slowest sorting algorithms"""
    while True:
        random.shuffle(arr)
        if is_sorted(arr):
            return arr
        
def counting_sort(arr: list) -> list:
    """counting sort"""
    count = [0] * (max(arr)+1)
    for num in arr:
        count[num] += 1
    for i in range(1, len(count)):
        count[i] += count[i-1]
    result = [0]*len(arr)
    for num in arr:
        idx = count[num]
        result[idx-1] = num
        count[num] -= 1
    return result

def radix_sort(arr: list) -> list:
    """it use counting sort"""
    def _radix_sort(arr: list):
        max1 = max(arr)
        exp1 = 1
        while max1//exp1 > 0:
            _counting_sort(arr, exp1)
            exp1 *= 10

        return arr
    def _counting_sort(arr: list, exp: int) -> None:
        result = [0]*len(arr)
        count = [0]*10
        for i in range(len(arr)):
            idx = (arr[i]//exp)
            count[int((idx)%10)] += 1

        for j in range(1, 10):
            count[j] += count[j-1]

        i = len(arr)-1
        while i>=0:
            idx = (arr[i]/exp)
            result[count[int((idx)%10)] - 1] = arr[i]
            count[int((idx)%10)] -= 1
            i -= 1
        i = 0
        for i in range(len(arr)):
            arr[i] = result[i]
    return _radix_sort(arr)

if __name__ == "__main__":
    import time
    A = [i for i in range(1000000)]
    random.shuffle(A)
    random.shuffle(A)
    A.append(1)
    T = time.time()
    quick_sort(A)
    print(f"{time.time() - T}s")