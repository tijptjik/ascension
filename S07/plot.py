from plotly.offline import plot, iplot
from plotly.graph_objs import Annotation, Annotations, Layout
from IPython.display import HTML, display

from game import player_abbr
import pandas as pd


def scatter_plot(roster_metrics, title, subtitle, x, y, xTitle, yTitle, scale_data=True, best_fit=False):
    width = 1920
    margin = (40,0,50,0)

    title = '<h1>{}</h1><h2>{}</h2>'.format(title, subtitle)

    if scale_data:
        df = roster_metrics.copy()[[x,y]].apply(lambda x : x - x.mean()).reset_index()
    else:
        df = roster_metrics.copy()[[x,y]].reset_index()

    plt = df.iplot(x=x, y=y, text='player', margin=margin, xTitle=xTitle, yTitle=yTitle, gridcolor='white', size=45, mode='markers', color='rgba(232,23,53,.2)', zerolinecolor='#ccc', asFigure=True)

    annotations = Annotations()

    for idx, row in df.apply(lambda x: x.replace(player_abbr) if x.dtype == object else x).iterrows():
        annotations.append(Annotation(text=row.player, x=row[x], y=row[y], xref='x1', yref='y1', showarrow=False, arrowhead=0, textangle=0, font={"color":'white','size':12}))
        
    plt.layout.update(
        annotations=annotations,
        hovermode="closest")

    colorscale = [[0.0, 'rgb(100,100,100)'],[1.0, 'rgb(153, 153, 245)']]

    plt.data[0].update(textfont=dict(
            color='white'
        ),line={
            'color': 'rgba(232, 23, 53, .8)',
            'width': 1.3},
        marker = {
            "color" : roster_metrics.score,
            "colorscale": colorscale
        },
        hoverinfo='text')


    # Line of Best Fit

    if best_fit:

        from sklearn.linear_model import LinearRegression as LR

        est = LR()
        est.fit(df[[x]], df[y])

        bestfit_line = pd.DataFrame([est.intercept_, roster_metrics[x].max() * est.coef_[0] + est.intercept_], [0, roster_metrics[x].max()]).iplot(asFigure=True, color='blue')

        plt.data.append(bestfit_line.data[0])

        plt.layout.showlegend = False

    x_range = abs(df[x].min() - df[x].max())
    y_range = abs(df[y].min() - df[y].max())
    plt.layout.xaxis1.update(dict(range=[df[x].min() - x_range/25, df[x].max() + x_range/25]))
    plt.layout.yaxis1.update(dict(range=[df[y].min() - y_range/25, df[y].max() + y_range/25]))

    return HTML(title + plot(plt,
            image_width=width,
            image='png',
            output_type='div',
            include_plotlyjs=False,
            show_link="False",
            link_text=""
        ))

def heatmap_plot(df, title, subtitle, colorscale, show_annotations=True):
    
    title = '<h1>{}</h1><h2>{}</h2>'.format(title, subtitle)
    
    vr = abs(df.min().min()) + df.max().max()
    mnr = abs(df.min().min())
    mxr = df.max().max()

    if colorscale is 'divergent': 
        colorscale = [
            [ 0,'#e64b51' ],
            [ mnr/7*1/vr,'#ed6964' ],
            [ mnr/7*2/vr,'#f48477' ],
            [ mnr/7*3/vr,'#f99e8b' ],
            [ mnr/7*4/vr,'#fdb69f' ],
            [ mnr/7*5/vr,'#ffcfb5' ],
            [ mnr/7*6/vr,'#ffe7cb' ],
            [ mnr/vr,'rgb(233,233,233)' ],
            [ (mxr/7*1+mnr)/vr,'#f0fdd5' ],
            [ (mxr/7*2+mnr)/vr,'#e1fbc8' ],
            [ (mxr/7*3+mnr)/vr,'#d2f8bd' ],
            [ (mxr/7*4+mnr)/vr,'#c3f6b2' ],
            [ (mxr/7*5+mnr)/vr,'#b2f3a7' ],
            [ (mxr/7*6+mnr)/vr,'#a1f19b' ],
            [ 1,'#90ee90' ]
        ]

    elif colorscale == 'divergent_blue':
        colorscale = [['0.0', 'rgb(165,0,38)'],
        [mnr/5*1/vr, 'rgb(215,48,39)'],
        [mnr/5*2/vr, 'rgb(244,109,67)'],
        [mnr/5*3/vr, 'rgb(253,174,97)'],
        [mnr/5*4/vr, 'rgb(254,224,144)'],
        [mnr/vr,'rgb(233,233,233)' ],
        [(mxr/5*1+mnr)/vr, 'rgb(224,243,248)'],
        [(mxr/5*2+mnr)/vr, 'rgb(171,217,233)'],
        [(mxr/5*3+mnr)/vr, 'rgb(116,173,209)'],
        [(mxr/5*4+mnr)/vr, 'rgb(69,117,180)'],
        ['1.0', 'rgb(49,54,149)']]
    
    elif colorscale is 'accent': 
        colorscale = [[0.0, 'rgb(233,233,233)'],[1.0, 'rgb(255, 86, 100)']]

    elif colorscale is 'accent_white': 
        colorscale = [[0.0, 'rgb(255,255,255)'],[1.0, 'rgb(255, 86, 100)']]
        
    elif colorscale is 'accent_green': 
        colorscale = [[0.0, 'rgb(233,233,233)'],[1.0, 'rgb(86, 255, 100)']]

    width = 1920
    margin = (198,44,148,12)

    plt = df.T.iplot(kind='heatmap', dimensions=(width,width/16*8), margin=margin, legend=False, asFigure=True)
    
    if show_annotations:
        
        annotations = Annotations()
        for n, row in enumerate(df.values):
            for m, val in enumerate(row):
                if val != 0:
                    annotations.append(Annotation(text=str(df.values[n][m]), x=df.columns[m], y=df.index[n],
                                                     xref='x1', yref='y1', showarrow=False, font={"color":'white'}))

        plt.layout.update(annotations=annotations)

    plt.data[0].colorscale = colorscale
    plt.data[0].update({'showscale':False})

    tickfont = dict(
        family='Open Sans',
        size=16
    )

    xtickfont = dict(
        family='Open Sans',
        size=16
    )

    titlefont = dict(
        family='Open Sans',
        size=32
    )


    plt.data[0]['ygap'] = 5
    plt.data[0]['xgap'] = 1
    plt.data[0]['hoverinfo'] = 'y+x'

    plt.layout.titlefont = titlefont

    plt.layout.yaxis1.update(dict(
    #         autorange=True,
            autorange='reversed',
            showline=False,
            autotick=False,
            tickwidth=0,
            tickfont=tickfont,
            zerolinewidth=2,
    #         categoryorder = "array",
            tickcolor='white',
    #         categoryarray = sorted(rosters.index.tolist(), key=lambda x: x.lower(), reverse=True)
        ))


    plt.layout.xaxis1.update(dict(
            autorange=True,
    #         showline=False,
    #         tickcolor='white',
            tickfont=xtickfont,
            tickangle=45
        ))

    plt.layout.margin['pad'] = 5

    return HTML(title + plot(plt,
        image_width=width,
        image='png',
        output_type='div',
        include_plotlyjs=False,
        show_link="False",
        link_text=""
    ))