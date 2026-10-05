class Stack:

    def __init__(self):

        self.stack = []

    def size(self):
        return len(self.stack)

    def top(self):

        if self.size() > 0:
            return self.stack[-1]
        else:
            return None

    def push(self, obj):

        self.stack.append(obj)

    def pop(self):
        return self.stack.pop()
