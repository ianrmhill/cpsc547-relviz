"""Generator functions that produce the Altair chart objects."""

import altair

__all__ = ['gen_plot_view', 'gen_strs_view', 'gen_layered_view']


def gen_plot_view(deg_data, average=False):
    # Setup multi-index ID column
    deg_data = deg_data.set_index(['param', 'circuit #', 'device #', 'lot #'])
    deg_data['sample #'] = deg_data.index
    deg_data = deg_data.reset_index()

    if average:
        return altair.Chart(deg_data).mark_line().encode(
            x='time',
            y='average(measured)'
        )
    else:
         return altair.Chart(deg_data).mark_line().encode(
            x='time',
            y='measured',
            detail='sample #'
        )


def gen_strs_view(strs_data, shade_cond):
    # Normalize the condition to a 0-1 range
    return altair.Chart(strs_data).mark_rect(
        color='red'
    ).encode(
        x='start time',
        x2='end time',
        opacity=shade_cond
    )


def gen_layered_view(plots, stressors):
    return altair.layer(stressors, plots)
