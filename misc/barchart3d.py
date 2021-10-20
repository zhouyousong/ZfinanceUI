import math
import plotly.graph_objects as go


def barchart3d(labels, z_data, title, z_title,
               n_row=0, width=900, height=900, thikness=0.7, colorscale='Viridis',
               **kwargs):
    """
    Draws a 3D barchart
    :param labels: Array_like of bar labels
    :param z_data: Array_like of bar heights (data coords)
    :param title: Chart title
    :param z_title: Z-axis title
    :param n_row: Number of x-rows
    :param width: Chart width (px)
    :param height: Chart height (px)
    :param thikness: Bar thikness (0; 1)
    :param colorscale: Barchart colorscale
    :param **kwargs: Passed to Mesh3d()
    :return: 3D barchart figure
    """

    if n_row < 1:
        n_row = math.ceil(math.sqrt(len(z_data)))
    thikness *= 0.5
    ann = []

    fig = go.Figure()

    for iz, z_max in enumerate(z_data):
        x_cnt, y_cnt = iz % n_row, iz // n_row
        x_min, y_min = x_cnt - thikness, y_cnt - thikness
        x_max, y_max = x_cnt + thikness, y_cnt + thikness

        fig.add_trace(go.Mesh3d(
            x=[x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max],
            y=[y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min],
            z=[0, 0, 0, 0, z_max, z_max, z_max, z_max],
            alphahull=0,
            intensity=[0, 0, 0, 0, z_max, z_max, z_max, z_max],
            coloraxis='coloraxis',
            hoverinfo='skip',
            **kwargs))

        ann.append(dict(
            showarrow=False,
            x=x_cnt, y=y_cnt, z=z_max,
            text=f'<b>#{iz + 1}</b>',
            font=dict(color='white', size=11),
            bgcolor='rgba(0, 0, 0, 0.3)',
            xanchor='center', yanchor='middle',
            hovertext=f'{z_max} {labels[iz]}'))

    # mesh3d doesn't currently support showLegend param, so
    # add invisible scatter3d with names to show legend
    for i, label in enumerate(labels):
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            opacity=0,
            name=f'#{i + 1} {label}'))

    fig.update_layout(
        width=width, height=height,
        title=title, title_x=0.5,
        scene=dict(
            xaxis=dict(showticklabels=False, title=''),
            yaxis=dict(showticklabels=False, title=''),
            zaxis=dict(title=z_title),
            annotations=ann),
        coloraxis=dict(
            colorscale=colorscale,
            colorbar=dict(
                title=dict(
                    text=z_title,
                    side='right'),
                xanchor='right', x=1.0,
                xpad=0,
                ticks='inside')),
        legend=dict(
            yanchor='top', y=1.0,
            xanchor='left', x=0.0,
            bgcolor='rgba(0, 0, 0, 0)',
            itemclick=False,
            itemdoubleclick=False),
        showlegend=True)
    return fig
