"""Entry point for the GraceFall visualization tool"""

import altair

from gracefall.dataloader import load_gerabaldi_report


def main():
    filename = '../sample_data/amp_gain_test_compare/curr_ramp_test_report.json'
    test_data = load_gerabaldi_report(filename)
    # Now to begin visualizing!
    print(test_data['Test Name'])



if __name__ == '__main__':
    main()
