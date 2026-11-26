import re
import time

pattern = re.compile(r"your_regex_here")
strings = ["some string"] * 10000

rounds = 100

start = time.perf_counter()

for _ in range(rounds):
    for string in strings:
        pattern.search(string)

elapsed = time.perf_counter() - start

total = len(strings) * rounds

print(f"Total searches: {total}")
print(f"Time: {elapsed:.3f}s")
print(f"Searches per second: {total / elapsed:,.0f}")
print(f"Searches per 100ms: {total / elapsed * 0.1:,.0f}")