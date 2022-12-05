"""Arrangement functions to integrate and coordinate component Altair views."""

import altair

__all__ = ['assemble_test_view', 'arrange_test_views']


def assemble_test_view(time_plot, strs_plot, time_hint, pca_plot):
    return time_hint & time_plot & strs_plot & pca_plot


def arrange_test_views(test_view):
    # TODO
    return test_view
