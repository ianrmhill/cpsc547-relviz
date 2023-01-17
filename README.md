# GraceFall
A visualization tool for examining wear-out reliability test data for model and test development


# Setup instructions
For development, do:
```
pip install -e .
```

Required packages are listed in the requirements.txt file and can be installed using:
```
pip install -r requirements.txt
```

For a quick run that will open the visualizer in your default web browser, go into ./gracefall and run
```
python main.py
```


# Currently Covered User Tasks:

| Task ID  | Description |
| ------------- | ------------- |
| T1    | Examine the statistical distribution evolution of multiple data series as time progresses  |
| T1.a  | Find identifiable groups that show similar behaviour within the larger set  |
| T1.b  | Roughly track sample variance and likelihood region evolution, identify asymmetries  |
| T1.c  | Catch outlier samples and propose probable causes for the outliers using background/meta data  |
| T2    | Search for probable values in background/meta data that result in large changes to data series trends in time  |

