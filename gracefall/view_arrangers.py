"""Arrangement functions to integrate and coordinate component Altair views."""

import altair

__all__ = ['assemble_test_view', 'arrange_test_views']


def assemble_test_view(time_plot, strs_plot, time_hint, pca_plot):
    time_series = time_hint & time_plot & strs_plot
    return altair.hconcat(time_series, pca_plot, center=True)


def arrange_test_views(test_view):
    # Did not have time to reach multi-test viewing within project scope
    return test_view
