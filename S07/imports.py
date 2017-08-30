import pandas as pd
import cufflinks as cf
import numpy as np
import plotly
from plotly.graph_objs import Annotation, Annotations, Layout
from plotly.offline import iplot

from IPython.display import HTML, display

from plot import scatter_plot, heatmap_plot

cf.go_offline()
long_dim=1280
short_dim=long_dim*2/3
cf.set_config_file(dimensions=(long_dim,short_dim))