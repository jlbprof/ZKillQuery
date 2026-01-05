import datetime
import time

# Option 1: Preferred - Use datetime with microsecond precision (recommended)
now = datetime.datetime.now(datetime.UTC)  # or .now() for local time
sortable_timestamp = now.strftime("%Y-%m-%d-%H-%M-%S-%f")  # .%f gives microseconds

print(sortable_timestamp)
