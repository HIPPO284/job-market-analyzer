class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, value):
        self.heap.append(value)

        i = len(self.heap) - 1

        while i > 0:
            parent = (i - 1) // 2

            if self.heap[parent] <= self.heap[i]:
                break

            self.heap[parent], self.heap[i] = self.heap[i], self.heap[parent]

            i = parent

    def peek(self):
        if len(self.heap) == 0:
            return None

        return self.heap[0]

    def pop(self):
        if len(self.heap) == 0:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        minimum = self.heap[0]

        self.heap[0] = self.heap.pop()

        i = 0

        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i

            if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
                smallest = left

            if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
                smallest = right

            if smallest == i:
                break

            self.heap[i], self.heap[smallest] = (
                self.heap[smallest],
                self.heap[i],
            )

            i = smallest

        return minimum


heap = MinHeap()

heap.push(5)
heap.push(3)
heap.push(8)
heap.push(1)
heap.push(4)

print(heap.heap)
print(heap.peek())

print(heap.pop())
print(heap.heap)
#  最小



class MaxHeap:
    def __init__(self):
        self.heap = []

    def peek(self):
        if len(self.heap) == 0:
            return None

        return self.heap[0]

    def push(self, value):
        self.heap.append(value)

        i = len(self.heap) - 1

        while i > 0:
            parent = (i - 1) // 2

            if self.heap[parent] >= self.heap[i]:
                break

            self.heap[parent], self.heap[i] = (
                self.heap[i],
                self.heap[parent],
            )

            i = parent

    def pop(self):
        if len(self.heap) == 0:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        maximum = self.heap[0]

        self.heap[0] = self.heap.pop()                      # 最后一个元素搬到heap[0]

        i = 0

        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            largest = i

            if (
                left < len(self.heap)
                and self.heap[left] > self.heap[largest]
            ):
                largest = left

            if (
                right < len(self.heap)
                and self.heap[right] > self.heap[largest]
            ):
                largest = right

            if largest == i:
                break

            self.heap[i], self.heap[largest] = (
                self.heap[largest],
                self.heap[i],
            )

            i = largest

        return maximum


























