"""Entry point for the GraceFall visualization tool"""

import altair

from gracefall.dataloader import load_gerabaldi_report
from gracefall.chart_generators import *


def main():
    # First load the test data
    filename = '../sample_data/amp_gain_test_compare/curr_ramp_test_report.json'
    test_data = load_gerabaldi_report(filename)
    # Note that the measurements dataframe is always in 'long-form' format

    # Now to begin visualizing!
    print(f"Generating view for test {test_data['Test Name']}")

    # First we generate individual charts for each test to be visualized
    # Within chart, need the actual data plots first
    test_plot = gen_plot_view(test_data['Measurements'])

    # Now also need the stress summary on the same set of axes
    strs_info = gen_strs_view(test_data['Stress Summary'], 'temp')

    # Layer the data plots with the stress summary
    full_view = gen_layered_view(test_plot, strs_info)

    # Configure global properties
    full_view = full_view.properties(width=1200, height=600)

    # Now arrange multiple tests for comparison

    # Finally, display the visualization
    full_view.show()


if __name__ == '__main__':
    main()
