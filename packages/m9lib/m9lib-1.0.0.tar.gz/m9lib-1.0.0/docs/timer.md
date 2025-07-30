# uTimer

Simple class for measuring elapsed time.

## uTimer methods

**uTimer()**
- Starts the timer automatically

**Start()**
- Starts or restarts the timer

**Stop()**
- Stops the timer

**GetElapsedSeconds()**
- Returns elapsed seconds as a float since timer was started
- If timer has stopped, elapsed seconds is until the timer was stopped

**GetElapsedString(*Units*=None)**
- Converts **GetElapsedSeconds()** to a string.
- *Units* can be: "d", "h", "m", "s"
- If *Units* is None, units are calculated automatically


## Use example
```python
# creating an instance starts timer automatically
timer = uTimer()

# you can also restart the timer at any time
timer.Start()

# get elapsed seconds
timer.GetElapsedSeconds()

# get elapsed seconds as a string
timer.GetElapsedString()

# you can stop the timer, in which case elapsed seconds stops
timer.Stop()
```
