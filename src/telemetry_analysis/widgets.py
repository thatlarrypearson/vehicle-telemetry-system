# telemetry-analysis/telemetry_analysis/widgets.py
#
# UI widgets for Jupyter Notebooks

import time

# Anaconda 'base' environment:
#   conda install -n base ipywidgets
# Local environment:
#   pip install ipywidgets
#   conda install ipywidgets
import ipywidgets as widgets
from IPython.display import display

# https://github.com/Kirill888/jupyter-ui-poll
# python -m pip install jupyter-ui-poll
from jupyter_ui_poll import ui_events

from private.vehicles import vehicles

vehicle_names = [vehicles[vin]['name'] for vin in vehicles]
name_to_vin = {vehicle['name']: vin for vin, vehicle in vehicles.items()}
selected_names = None

ui_done = False

def select_vin_dialog(title="Select Vehicle By Name", verbose=True)->list:
    """
    Select vehicles by name from the list of vehicle names and return a list of selected VINs.
    """
    global vehicle_names
    global name_to_vin
    checkboxes = [widgets.Checkbox(description=name) for name in vehicle_names]
    checkbox_container = widgets.VBox(children=checkboxes)
    selection_button = widgets.Button(description='Select vehicles...')
    title_container = widgets.Label(value=title)

    def handle_selection(btn):
        global ui_done
        global selected_names
        ui_done = True
        selected_names = [checkbox.description for checkbox in checkboxes if checkbox.value]
        btn.description = '👍'
        return selected_names

    selection_button.on_click(handle_selection)

    display(title_container)
    display(checkbox_container)
    display(selection_button)

    # Wait for user to press the select button
    with ui_events() as poll:
        while ui_done is False:
            poll(10)          # React to UI events (upto 10 at a time)
            if verbose:
                print('.', end='')
            time.sleep(1.0)

    if verbose:
        print(" DONE!")

    return [name_to_vin[name] for name in selected_names]


