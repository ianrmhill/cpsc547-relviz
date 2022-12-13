"""Entry point for the GraceFall visualization tool"""

import altair

from gracefall.dataloader import load_gerabaldi_report
from gracefall.view_generators import *
from gracefall.view_arrangers import *
from gracefall.data_processors import *


def main():
    # Input arguments added directly in code for now, will move to CLI args or GUI later
    tests = ['curr_ramp_test']

    # First load the test data
    filename = '../sample_data/amp_gain_test_compare/curr_ramp_test_report.json'
    # Note that the measurements dataframe is always in 'long-form' format
    test_data = load_gerabaldi_report(filename)

    # Altair/Vega-Lite has very restricted support for interactivity, so we have to compute aggregate statistics
    # manually then create an additional column to distinguish whether a given series is an aggregate stat or not
    test_data = inject_aggregate_stats(test_data)

    # Setup multi-index ID column
    deg_data = test_data['Measurements'].set_index(['param', 'circuit #', 'device #', 'lot #'])
    deg_data['sample #'] = deg_data.index
    test_data['Measurements'] = deg_data.reset_index()

    # Now to begin visualizing!
    print(f"Generating visualization for {test_data['Test Name']}")

    # Setup up custom visual theme for the visualization
    def gracefall_theme():
        return {
            'config': {
                'background': '#B0B0B0',
                'view': {'fill': '#CFCFCF'},
                'padding': 10,
                'font': 'Nirmala UI'
            }
        }
    altair.themes.register('gracefall', gracefall_theme)
    altair.themes.enable('gracefall')



    # Components each graphs; for aligning PCA selection
    selectors = {}

    # May need to arrange multiple tests for comparison
    for test in tests:
        # First construct the squeeze view for the full time interval hint bar
        time_squeeze = gen_time_hint_view(test_data['Measurements'], selectors)

        # Next we generate the time series plot for the test
        test_plot = gen_plot_view(test_data['Measurements'], selectors)

        # Now for the stress summary cloud plots synchronized with the time series plot on the time axis
        strs_info = gen_strs_view(test_data['Stress Summary'], selectors)

        # Next construct the PCA plot that can be swapped in instead of the time-series views
        pca_plot = gen_pca_view(test_data['Measurements'], selectors)

        # Layer/place the component views to build out the full test view
        test_view = assemble_test_view(test_plot, strs_info, time_squeeze, pca_plot)

    # Next arrange multiple test views for comparison if needed
    full_view = arrange_test_views(test_view)

    # Debug
    #print(full_view.to_dict())

    # Finally, display the visualization
    full_view.show()


if __name__ == '__main__':
    main()
