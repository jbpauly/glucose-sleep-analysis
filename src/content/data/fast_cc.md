Cumulative hours of fasting logged in Zero Fasting for a single day,
and **maximum** consecutive hours fasted in a single day, including continuous hours carried over from previous day(s).

Zero Fasting logs export in the following format: 

|Date   |Start|End  |Hours|Night Eating|
|-------|-----|-----|-----|------------|
|1/17/21|19:15|12:00|16   |1           |
|1/16/21|19:45|10:14|14   |2           |
|1/15/21|21:00|10:00|13   |3           |


These logs are converted to the daily cumulative and consecutive hours using a 
[custom module](https://github.com/jbpauly/glucose-sleep-analysis/blob/main/src/zero.py).

Below is a visual guide to the cumulative and consecutive hours calculation.