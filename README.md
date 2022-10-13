# cpsc547-relviz
Information visualization - CPSC 547 course project repository

Visualization user tasks within project scope:

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
