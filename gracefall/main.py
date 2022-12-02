"""Entry point for the GraceFall visualization tool"""

import altair

from gracefall.dataloader import load_gerabaldi_report
from gracefall.view_generators import *
from gracefall.view_arrangers import *


def main():
    # Input arguments added directly in code for now, will move to CLI args or GUI later
    tests = ['curr_ramp_test']

    # First load the test data
    filename = '../sample_data/amp_gain_test_compare/curr_ramp_test_report.json'
    # Note that the measurements dataframe is always in 'long-form' format
    test_data = load_gerabaldi_report(filename)

    # Now to begin visualizing!
    print(f"Generating visualization for {test_data['Test Name']}")

    # May need to arrange multiple tests for comparison
    for test in tests:
        # First construct the squeeze view for the full time interval hint bar
        time_squeeze, intrvl_sel = gen_time_hint_view(test_data['Measurements'])

        # Next we generate the time series plot for the test
        test_plot = gen_plot_view(test_data['Measurements'], intrvl_sel)

        # Now for the stress summary cloud plots synchronized with the time series plot on the time axis
        strs_info = gen_strs_view(test_data['Stress Summary'], intrvl_sel)

        # Next construct the PCA plot that can be swapped in instead of the time-series views
        pca_plot = gen_pca_view(test_data['Measurements'])

        # Layer/place the component views to build out the full test view
        test_view = assemble_test_view(test_plot, strs_info, time_squeeze)

    # Next arrange multiple test views for comparison if needed
    full_view = arrange_test_views(test_view)

    # Now arrange multiple tests for comparison

    # Finally, display the visualization
    full_view.show()


if __name__ == '__main__':
    main()
