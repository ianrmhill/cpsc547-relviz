# GraceFall
A visualization tool for examining wear-out reliability test data for model and test development


# Abstracted Task and Requirements:


## Four tasks for now:
	1. Examine the statistical distribution evolution of multiple data series as time progresses
		a. Find identifiable groups that show similar behaviour within the larger set
		b. Roughly track sample variance and likelihood region evolution, identify asymmetry
		c. Catch outlier samples and propose probable causes for the outliers using background/meta data
	2. Search for probable values in background/meta data that result in large changes to data series trends in time
	3. Evaluate the success/performance of proposed models in explaining the observed data series
	4. Compare multiple different sets of background/meta data and their corresponding sets of data series in terms of their influence on the outcomes of the previous three tasks *nice to have*


## Requirements:
	1. Must display multiple data series against time
		a. Up to five sets of data series can be visualized on the same axes
		b. Can focus on multiple time scales of interest on demand
		c. Data series must be individually viewable
		d. Statistical properties of sets of data series can be overlaid or substituted for raw data on demand *nice to have*
		e. Provide automated classification of data series into groupings by similarity *nice to have*
	2. Background/meta data is displayed alongside data series to maximize spatial "closeness" / minimize cognitive effort required to jump between viewing data series and meta data values
		a. Up to three meta data fields must be displayable simultaneously
	3. Proposal model outputs, dependent on background/meta data values, are displayable on the data series axes on demand
		a. Must be immediately visually distinguishable from displayed data series or statistical properties of the data series
	4. Up to four data series axes views can be displayed simultaneously, arranged to maximize spatial "closeness" / minimize cognitive effort required to jump between viewing different axes *nice to have*
Significant differences in background/meta data values between views can be highlighted on demand *nice to have*



# Visualization user tasks within project scope:

	1. Visualize test procedure stress summaries and failure criteria alongside measurement data plots to enable exploration and understanding of test results
	2. Compare measurement data between similar or repeated test runs and identify what aspects of the test procedure result in contrasting data
	3. Integrate candidate model displays to allow for visual analysis of fit quality on test measurement data
	4. Visually examine the uncertainty within a probabilistic degradation model with regards to predicting test measurement data (stretch goal)

Some specific tasks within user tasks 1 and 2:

	1. Recognize any stress phases where one mechanism dominates degradation and/or failures and identify the mechanism using professional judgement
	2. Identify critical thresholds in stress conditions resulting in sudden changes in degradation or failure behaviour
	3. Notice key differences between similar test procedures and how those differences affect test degradation or failure rates

Anticipated key design challenges:

	1. Displaying tests that contain information of interest in multiple time scale magnitudes
	2. Summarizing data from many individual samples to reduce visual clutter
	3. Visually displaying tests for comparison where procedures differ significantly
	4. How to effectively visualize a fitted model to enable abstract user tasks
	5. Everything related to visualizing probabilistic models
