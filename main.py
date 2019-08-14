from os.path import join, dirname
import datetime

import pandas as pd
from scipy.signal import savgol_filter

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.palettes import Blues4
from bokeh.plotting import figure

from bokeh.models import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import viridis
from bokeh.transform import linear_cmap
import ipywidgets as widgets
from bokeh.io import output_notebook, push_notebook, show
from bokeh.models import HoverTool
from bokeh.models import LinearAxis, Range1d,DatetimeTickFormatter,BasicTickFormatter,SingleIntervalTicker

def remove_dupl(x):
  return list(dict.fromkeys(x))

corr_zc_tymy=pd.read_csv(join(dirname(__file__), 'data/corr_zc_tymy.csv'),sep=";",encoding="utf-8").set_index(["OP zamestnance","date_survey_month"])
scatter_cds = ColumnDataSource(dict(x=[],y=[],color=[],ZC=[],Agent=[]))


align_kw = dict(
    _css = (('.widget-label', 'min-width', '20ex'),),
    margin = '0px 0px 5px 12px'
)

region_widget = Select(
    options=["VŠE"] + list(corr_zc_tymy.Region.drop_duplicates()),
    # rows=10,
    title='REGION:',
)    


mesice_widget = Select(
    options=['VŠE','LEDEN','ÚNOR','BŘEZEN','DUBEN'],
    # rows=10,
    title='MESIC:',
)

x_widget = Select(
    options=['MOJE DATA - SMLOUVY','PLNĚNÍ EE (%)','PLNĚNÍ EE (ABS)', 'SCORE_MEAN', 'SCORE_MIN'],
    # rows=10,
    title='OSA X:',
)

y_widget = Select(
    options=['MOJE DATA - SMLOUVY','PLNĚNÍ EE (%)','PLNĚNÍ EE (ABS)', 'SCORE_MEAN', 'SCORE_MIN'],
    # rows=10,
    title='OSA Y:',
)

def printer_double(attrname, old, new):
    mesice={'LEDEN':1,'ÚNOR':2,'BŘEZEN':3,'DUBEN':4}
    print(mesice_widget.value)
    print(region_widget.value)
    if (mesice_widget.value==u"VŠE"):
        if (region_widget.value!=u"VŠE"): corr_zc_tymy_filtr=corr_zc_tymy[corr_zc_tymy.Region==region_widget.value].copy()    
    if (mesice_widget.value!=u"VŠE"):
        if (region_widget.value!=u"VŠE"): corr_zc_tymy_filtr=corr_zc_tymy[corr_zc_tymy.Region==region_widget.value].loc[(slice(None),[mesice[mesice_widget.value]]), :].copy()                
    if (mesice_widget.value!=u"VŠE"):
        if (region_widget.value==u"VŠE"): corr_zc_tymy_filtr=corr_zc_tymy.loc[(slice(None),[mesice[mesice_widget.value]]), :].copy()                            
    if (mesice_widget.value==u"VŠE"):            
        if (region_widget.value==u"VŠE"): corr_zc_tymy_filtr=corr_zc_tymy.copy()
    data_zc=corr_zc_tymy_filtr["ZC"].tolist()
    print(data_zc)
    call_colors = viridis(len(remove_dupl(data_zc)))
    color_key_value_pairs = list(zip(remove_dupl(data_zc), call_colors))
    color_dict = dict(color_key_value_pairs)   
    colors = [color_dict[x] for x in corr_zc_tymy_filtr['ZC']]
    corr_zc_tymy_filtr["color"]=colors
    if x_widget.value=='MOJE DATA - SMLOUVY': osa_x="PARTNER"
    if x_widget.value=='PLNĚNÍ EE (%)': osa_x="Plnění EE"
    if x_widget.value=='PLNĚNÍ EE (ABS)': osa_x="Plnění EE_abs"
    if x_widget.value=='SCORE_MEAN': osa_x="score_mean"
    if x_widget.value=='SCORE_MIN': osa_x="score_min"

    if y_widget.value=='MOJE DATA - SMLOUVY': osa_y="PARTNER"
    if y_widget.value=='PLNĚNÍ EE (%)': osa_y="Plnění EE"
    if y_widget.value=='PLNĚNÍ EE (ABS)': osa_y="Plnění EE_abs"
    if y_widget.value=='SCORE_MEAN': osa_y="score_mean"
    if y_widget.value=='SCORE_MIN': osa_y="score_min"
     
    scatter_cds.data = dict(x=corr_zc_tymy_filtr[osa_x],y=corr_zc_tymy_filtr[osa_y],color=corr_zc_tymy_filtr["color"],ZC=corr_zc_tymy_filtr["ZC"],Agent=corr_zc_tymy_filtr["ID agenta/cesty"])            



hover = HoverTool(tooltips=[('ZC', '@ZC'),('Agent','@Agent')])
p=figure(title="Vztah plnění a spokojenosti, jednotliví agenti", tools=["box_zoom","lasso_select","reset",hover])
p.circle("x", "y",color="color", size=10,source=scatter_cds)

region_widget.on_change('value', printer_double)
mesice_widget.on_change('value', printer_double)

x_widget.on_change('value', printer_double)
y_widget.on_change('value', printer_double)

controls = column(region_widget, mesice_widget,x_widget,y_widget)

curdoc().add_root(row(p, controls))
curdoc().title = "ZC"
