#------Librerías-------

import seaborn as sns  
import pandas as pd
import plotly.express as px
import faicons as fa

from shared import app_dir, tips
from shiny import reactive, render #App NO
from shiny.express import input, ui
from shinywidgets import render_plotly



#-------Obtención y carga de datos-------

tips = sns.load_dataset("tips")
tips.to_csv("tips.csv", index=False)

#Definimos el rango de valores para el control deslizante

bill_rng = (tips["total_bill"].min(), tips["total_bill"].max())

#-------Configuración de la página-------

#---Estilos---

ui.include_css("styles.css")

#---Título---

ui.page_opts(title = "Tipping Insights", fillable=True)

#fillable=True aprovecha mejor el espacio

#---Barra lateral---

with ui.sidebar(title="Filters", open="desktop", width="20%"):

    #Control deslizante 
    ui.input_slider(
        "total_bill",           #ID
        "Total payable",        #Etiqueta
        bill_rng[0],            #Valor máximo
        bill_rng[1],            #Valor mínimo
        value=bill_rng,         #Valor inicial
        post = "$"               #Unidad
    
    )               
    #Checkbox 
    ui.input_checkbox_group(
        "smoker",                  #ID
        "Smoker",                  #Etiqueta         
        choices=["Yes", "No"],     #Opciones disponibles
        selected=["Yes", "No"],    #Opciones seleccionadas 
        inline=False               #Disposición
    )
                        
    #Checkbox
    ui.input_checkbox_group(
        "time", 
        "Mealtime", 
        ["Lunch", "Dinner"], 
        selected=["Lunch", "Dinner"],
        inline=True
        )  
    
    #Checkbox
    ui.input_checkbox_group("day", 
                            "Days", 
                            choices=["Thur", "Fri", "Sat", "Sun"],
                            selected=["Thur", "Fri", "Sat", "Sun"], 
                            inline=True
                            ) 

    #Botón reset para reiniciar filtros
    ui.input_action_button("reset", "Reset filter") 

#------Iconos de la interfaz-------factura promedio, tamaño medio del grupo-, total de propinas y propina media

ICONS = {
    "credit-card":fa.icon_svg("credit-card", "solid"),
    "users": fa.icon_svg("users", "solid"),
    "dollar": fa.icon_svg("dollar-sign", "solid"),           
    "hand": fa.icon_svg("hand-holding-dollar", "solid"),
    "ellipsis": fa.icon_svg("ellipsis", "solid")
}

#-------Cajas de valores-------

#Fila de cajas de valores
with ui.layout_columns(col_widths=[3,3,3,3], fill=False):

    #Primera: factura media
    with ui.value_box(showcase=ICONS["credit-card"], theme="bg-gradient-blue-purple"):

        "Average Bill",

        @render.express
        def factura_media():
            d = tips_data() 
            if d.shape[0] > 0:
                bill = d.total_bill.mean()
                f"{bill:.2f}$"  
            else:
                "Data not available."          
                
    #Segunda: tamaño medio del grupo
    with ui.value_box(showcase=ICONS["users"], theme="bg-gradient-blue-purple"):
        "Average Party Size"

        @render.express 
        def tamaño_grupo_medio():
            d = tips_data()
            if d.shape[0] > 0:
                grupo_medio = d["size"].mean()
                f"{grupo_medio:.1f} people"
            else: 
                "Data not available."

    #Tercera: total de propinas
    with ui.value_box(showcase=ICONS["dollar"], theme="bg-gradient-blue-purple"):
        "Total Tips Collected"
       
        @render.express
        def total_propinas():
            d = tips_data()
            if d.shape[0]>0:
                total=d["tip"].sum()
                f"{total:.2f} $"
            else: 
                "Data not available."

    #Cuarta: propina media
    with ui.value_box(showcase=ICONS["hand"], theme="bg-gradient-blue-purple"):
        "Average Tip"

        @render.express
        def propina_media():
            d = tips_data()
            if d.shape[0] > 0:
                f"{d.tip.mean():.2f} $"
            else: 
                "Data not available."

#-------Tarjetas-------

#Diseño principal con cuatro tarjetas: 
with ui.layout_columns(col_widths=[6, 6]): 

    #Primera tarjeta: Tabla de datos
    with ui.card(full_screen=True, height="400px"):
        ui.card_header("Tips Dataset", class_="d-flex justify-content-between align-items-center")

        @render.data_frame
        def table(): 
            d = tips_data()[["day", "time", "total_bill", "tip", "size"]].rename(columns={
                "day": "Day",
                "time": "Mealtime",
                "total_bill": "Total payable ($)",
                "tip": "Tip ($)",
                "size": "Group size"
            })
            return render.DataGrid(d)

    #Segunda tarjeta: Gráfico de dispersión para mostrar la relación factura-propina
    with ui.card(full_screen=True, height = "400px"):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Relationship between Tip and Total Bill"

            #Menú emergente para opciones de color
            with ui.popover(title="Display options", placement="top"):
                ICONS["ellipsis"]

                ui.input_radio_buttons(
                    "scatter_color", 
                    "Dot color",
                    ["none", "sex", "smoker", "day", "time"],
                    inline=True
                )
                #Opción para tamaño
                ui.input_checkbox(
                    "show_size",
                    "display group size with point size",
                    value=False
                )
                
        #Renderizado del gráfico de dispersión
        @render_plotly
        def scatterplot():
            color = input.scatter_color()
            use_size = input.show_size()

            fig = px.scatter(
                tips_data(),
                x="total_bill",
                y="tip",
                color=None if color == "none" else color,
                size="size" if use_size else None, 
                trendline="lowess" #Linea de tendencia
            )
            #Ajustar el tamaño del gráfico para que ocupe todo el espacio disponible
            fig.update_layout(
                autosize = True,
                margin = dict(l=50, r=30, t=30, b=50)
            )
            return fig

with ui.layout_columns(col_widths=[6, 6]): 

    #Tercera tarjeta: gráfico de densidad
    with ui.card(full_screen=True, height="400px"):
        with ui.card_header("Tip percentage", class_="d-flex justify-content between align-items-center"):
            
            #Menú emergente para opciones de división
            with ui.popover(title="Display options"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "tips_perc_y",
                    "Split by",
                    ["sex", "smoker", "day", "time"],
                    selected="day", #valor predeterminado
                    inline = False
                )
        #Renderizado del gráfico de densidad
        @render_plotly
        def tip_perc():
            from ridgeplot import ridgeplot #importamos la función ridgeplot
            #Preparamos datos
            dat=tips_data()
            
            if dat.shape[0] == 0:#
                return px.bar(title = "No data")#
            else:
                dat["percent"] = dat.tip/dat.total_bill #Cálculo del porcentaje de propina
                yvar = input.tips_perc_y()               #variable para dividir 
                uvals = dat[yvar].unique()              #Valores únicos de esa variable

                #Crear muestras para cada valor único
                samples = [[dat.percent[dat[yvar]==val]] for val in uvals]

                    #Crear el gráfico ridgeplot
                plt = ridgeplot(
                    samples=samples,
                    labels=uvals,
                    bandwidth=0.01,
                    colorscale="viridis",
                    colormode="row-index"
                )

                #Ajustar leyenda
                plt.update_layout(
                    legend=dict(
                        orientation="h", yanchor="bottom",xanchor="center", x=0.5
                    ),
                    autosize=True, 
                    margin=dict(l=50, r=30, t=30, b=50)
                )
                return plt
    
    #Cuarta tarjeta: Gráfico de barras que muestra las propinas por día de la semana
    with ui.card(full_screen=True, height="400px"):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Tips by day of the week"
        with ui.popover(title="Display options", placement="top-right"):
            ICONS["ellipsis"]
            ui.input_radio_buttons(
                "bar_metric", 
                "Metric:",
                ["Total Tips Collected", "Average Tip", "Average Tip Percentage"],
                selected="Total Tips Collected"
            )
            ui.input_checkbox('show_day_count', 
                              "Show the number of visits per day",
                              value=True)
        @render_plotly
        def tips_by_day():
            d = tips_data()

            if d.shape[0] == 0:
                return px.bar (title="No data")
            
            metric=input.bar_metric()

            if metric == 'Total tips collected':
                day_tips = d.groupby('day')['tip'].sum().reset_index()
                y_title ='Total Tips Collected ($)'
            elif metric == 'Average Tip':
                day_tips = d.groupby('day')['tip'].mean().reset_index()
                y_title = "Average Tip ($)"
            else: 
                d['percent'] = d.tip/d.total_bill*100
                day_tips = d.groupby('day')['percent'].mean().reset_index()
                y_title='Average Tip Percentage (%)'

            #Renombrar columnas
            day_tips.columns = ['day', 'value']

            #Ordenar días
            day_order = ['Thur', 'Fri', 'Sat', 'Sun']
            day_tips['day'] = pd.Categorical(day_tips['day'], categories=day_order, ordered=True)
            day_tips = day_tips.sort_values('day')

            #Configuración base para la gráfica
            fig_params = {
            'x': 'day',
            'y': 'value',
            'color':'day',
            'labels': {'value': y_title, 'day':'Día de la semana'},
            'title': f'{metric} por dia de la semana'
        }
                
            #Mostrar conteo de visitas si está activado
            if input.show_day_count():
                day_count = d.groupby('day').size().reset_index()
                day_count.columns = ['day', 'count']
                day_count['day'] = pd.Categorical(day_count['day'], categories=day_order, ordered=True)
                day_count = day_count.sort_values('day')

                fig_params['custom_data'] = [day_count['count']]
                hover_template = "<b>%{x}</b><br>" + \
                            f"{y_title}: %{{y:.2f}}<br>" + \
                            "Number of visits: %{customdata}<br>"
                fig = px.bar(day_tips, **fig_params)
                fig.update_traces(hovertemplate=hover_template)

            else:
                fig = px.bar(day_tips, **fig_params)

            fig.update_layout(
                showlegend=False,
                autosize=True,
                margin=dict(l=50, r=30, t=30, b=50)
    )
            return fig
            
#-------Cálculos reactivos y efectos-------

#Función reactiva para filtrar los datos según entradas del usuario
@reactive.calc
def tips_data():
    bill = input.total_bill() #Obtener rango de facturas seleccionado
    idx1=tips.total_bill.between(bill[0], bill[1]) #Filtrar por factura
    idx2=tips.time.isin(input.time())#Filtrar por momento
    return tips[idx1 & idx2] #Devolver datos filtrados
#Efecto reactivo para reestablecer filtros cuando se hace clic en el botón
@reactive.effect
@reactive.event(input.reset)#Activar cuando se haga clic en reset

def _():
    ui.update_slider("total_bill", value=bill_rng) #Restablecer el control deslizante
    ui.update_checkbox_group("time", selected=["Lunch", "Dinner"]) #Restablecer casillas
