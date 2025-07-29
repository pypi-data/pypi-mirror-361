from nicegui import ui
import pons
import json

ui.markdown("## PONS - Python Opportunistic Network Simulator")


def on_btn_run_click():
    print(
        "Run simulation with {} nodes for {} seconds".format(
            nodes.value, duration.value
        )
    )
    moves = pons.generate_randomwaypoint_movement(
        duration.value,
        nodes.value,
        world_w.value,
        world_h.value,
        max_pause=max_pause.value,
        min_speed=min_speed.value,
        max_speed=max_speed.value,
    )
    net = pons.NetworkSettings("WIFI", range=netrange.value)

    if routing.value == 1:
        router = pons.routing.EpidemicRouter(capacity=100)
    elif routing.value == 2:
        router = pons.routing.SprayAndWaitRouter(capacity=100)
    elif routing.value == 3:
        router = pons.routing.DirectDeliveryRouter(capacity=100)

    sim_nodes = pons.generate_nodes(nodes.value, net=[net], router=router)
    config = {"movement_logger": False, "peers_logger": False}
    msggenconfig = {
        "type": "single",
        "interval": 30,
        "src": (0, nodes.value),
        "dst": (0, nodes.value),
        "size": 100,
        "id": "M",
        "ttl": 3600,
    }

    netsim = pons.NetSim(
        duration.value,
        (world_w.value, world_h.value),
        sim_nodes,
        moves,
        config=config,
        msggens=[msggenconfig],
    )

    netsim.setup()

    # cProfile.run("netsim.run()")
    log.clear()
    netsim.run()
    log.push(json.dumps(netsim.net_stats, indent=4))
    log.push(json.dumps(netsim.routing_stats, indent=4))
    print(json.dumps(netsim.net_stats, indent=4))
    print(json.dumps(netsim.routing_stats, indent=4))

    rows = [{"key": k, "value": v} for k, v in netsim.routing_stats.items()]
    tbl_msgstats.clear()
    for r in rows:
        tbl_msgstats.add_rows(r)
    # tbl_msgstats.update()

    tabs.value = tab_results


with ui.tabs().classes("w-full") as tabs:
    tab_cfg = ui.tab("Config")
    tab_results = ui.tab("Results")
tabs = ui.tab_panels(tabs, value=tab_cfg).classes("w-full")
with tabs:
    with ui.tab_panel(tab_cfg):
        with ui.row():
            with ui.card():
                ui.markdown("**General**")
                # with ui.row():
                ui.label("Simulation duration:")
                duration = ui.slider(min=600, max=3600 * 2, value=3600, step=600).props(
                    "label-always"
                )

                ui.label("World:")
                with ui.row():
                    world_w = ui.number(
                        label="Width (m)", value=1000, format="%i", step=100
                    )
                    world_h = ui.number(
                        label="Height (m)", value=1000, format="%i", step=100
                    )

            with ui.card():
                ui.markdown("**Nodes**")
                # with ui.row():
                ui.label("Num:")
                nodes = ui.slider(min=2, max=40, value=10).props("label-always")

                routing = ui.select(
                    {1: "Epidemic", 2: "Spray'n'Wait", 3: "Direct Delivery"},
                    value=1,
                    label="Routing",
                )

                netrange = ui.number(
                    label="Network Range (m)", value=80, format="%i", step=1
                )

                ui.label("Movement:")
                with ui.row():
                    min_speed = ui.number(
                        label="Min Speed (m/s)", value=0.5, format="%.2f"
                    )
                    max_speed = ui.number(
                        label="Max Speed (m/s)", value=1.5, format="%.2f"
                    )
                    max_pause = ui.number(
                        label="Max Pause (s)", value=60, format="%.2f"
                    )

        ui.button("Run!", on_click=on_btn_run_click)

    with ui.tab_panel(tab_results):
        columns = [
            {
                "name": "key",
                "label": "Property",
                "field": "key",
                "required": True,
                "align": "left",
            },
            {
                "name": "val",
                "label": "Value",
                "field": "value",
                "sortable": False,
                "required": True,
            },
        ]
        rows = [
            {"key": "Alice", "value": 18},
            {"key": "Bob", "value": 21},
            {"key": "Carol", "value": 22},
        ]
        tbl_msgstats = ui.table(columns=columns, rows=[], row_key="value")
ui.run()

log = ui.log(max_lines=40).classes("w-full h-60")
