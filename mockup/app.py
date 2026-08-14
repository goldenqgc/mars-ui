"""MARS NetHub — static UI mockup server.

Per task spec:
- Pure FastAPI + Jinja2Templates.
- All data is hardcoded in source — no DB, no real auth.
- Used only to validate visual/interactive decisions before the real build.
"""
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="MARS NetHub Mockup", version="0.0.0-mockup")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# --- Fake data ----------------------------------------------------------------

NOW = datetime(2026, 6, 30, 14, 28, 0)


def _ago(mins: int) -> str:
    return (NOW - timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")


SWITCHES = [
    # Each switch's map has TWO distinct coordinates:
    #   - map_center + map_zoom  : where the iframe view is centered and how zoomed
    #   - pin_latlng             : where MazeMap would put its pin (different from center)
    # Keeping these separate gives the pin a meaningful position rather than
    # always sitting at the iframe center. We do NOT include `sharepoi=` in
    # the URL — the default `sharepoitype=point` errors out on this campus,
    # and the alternative `identifier` auto-opens the info card. So MazeMap
    # draws nothing; the custom SVG pin overlay in switch_detail.html
    # renders the building marker at the projected pixel offset using
    # `pin_latlng`.
    {
        "id": 1,  "name": "sw-core-01",     "ip": "10.0.1.1",   "model": "Cisco Catalyst 9300",  "status": "UP",      "last_seen": _ago(0),
        "pin_poi": "BLD01_2_C5",
        "campus": "bonduniversity", "campusid": 388, "zlevel": 1,        "map_center": "153.417500,-28.074200", "map_zoom": 17,
        "pin_latlng": "153.416973,-28.073765",    },
    {
        "id": 2,  "name": "sw-core-02",     "ip": "10.0.1.2",   "model": "Cisco Catalyst 9300",  "status": "UP",      "last_seen": _ago(1),
        "pin_poi": "BLD01_2_C5",
        "campus": "bonduniversity", "campusid": 388, "zlevel": 1,        "map_center": "153.417500,-28.074200", "map_zoom": 17,
        "pin_latlng": "153.417180,-28.073520",    },
    {
        "id": 3,  "name": "sw-agg-floor-3", "ip": "10.0.3.1",   "model": "Huawei S5735-S",        "status": "WARNING", "last_seen": _ago(2),
        "campus": "bonduniversity", "campusid": 388, "zlevel": 2,        "map_center": "153.417500,-28.074200", "map_zoom": 17,
        "pin_latlng": "153.418200,-28.074600",    },
    {
        "id": 4,  "name": "sw-agg-floor-7", "ip": "10.0.7.1",   "model": "Huawei S5735-S",        "status": "UP",      "last_seen": _ago(0),
        "campus": "bonduniversity", "campusid": 388, "zlevel": 2,        "map_center": "153.417500,-28.074200", "map_zoom": 17,
        "pin_latlng": "153.418800,-28.075100",    },
    {
        "id": 5,  "name": "sw-edge-room-A", "ip": "10.1.1.1",   "model": "H3C S5560X",            "status": "UP",      "last_seen": _ago(1),
        "campus": "bonduniversity", "campusid": 388, "zlevel": 2,        "map_center": "153.417500,-28.074200", "map_zoom": 17,
        "pin_latlng": "153.416400,-28.075800",    },
    {
        "id": 6,  "name": "sw-edge-room-B", "ip": "10.1.2.1",   "model": "H3C S5560X",            "status": "DOWN",    "last_seen": _ago(45),
        "campus": "bonduniversity", "campusid": 388, "zlevel": 2,        "map_center": "153.417500,-28.074200", "map_zoom": 17,
        "pin_latlng": "153.416200,-28.075200",    },
    {
        "id": 7,  "name": "sw-edge-room-C", "ip": "10.1.3.1",   "model": "H3C S5560X",            "status": "UNKNOWN", "last_seen": _ago(180),
        "campus": "bonduniversity", "campusid": 388, "zlevel": 2,        "map_center": "153.417500,-28.074200", "map_zoom": 17,
        "pin_latlng": "153.415800,-28.076000",    },
    {"id": 8,  "name": "sw-dmz-01",      "ip": "172.16.1.1", "model": "Cisco Catalyst 9500",  "status": "UP",      "last_seen": _ago(0),   "map_url": ""},
    {"id": 9,  "name": "sw-dmz-02",      "ip": "172.16.1.2", "model": "Cisco Catalyst 9500",  "status": "WARNING", "last_seen": _ago(8),   "map_url": ""},
    {"id": 10, "name": "sw-iac-mgmt-01", "ip": "10.20.1.1",  "model": "Arista 7050",           "status": "UP",      "last_seen": _ago(0),   "map_url": ""},
    {"id": 11, "name": "sw-iac-mgmt-02", "ip": "10.20.1.2",  "model": "Arista 7050",           "status": "UP",      "last_seen": _ago(0),   "map_url": ""},
    {"id": 12, "name": "sw-lab-01",      "ip": "10.99.1.1",  "model": "TP-LINK TL-ST5008",    "status": "DOWN",    "last_seen": _ago(360), "map_url": ""},
]

# Logs cover several operation types + both success / failed / partial results.
LOGS = [
    {"time": _ago(3),    "actor": "admin",       "device_id": 1,  "device": "sw-core-01",     "action": "reboot",         "action_label": "Reboot",        "result": "success", "note": "Canary upgrade rehearsal"},
    {"time": _ago(12),   "actor": "ops-zhang",   "device_id": 8,  "device": "sw-dmz-01",      "action": "config_apply",   "action_label": "Config push",   "result": "success", "note": "Add ACL 200"},
    {"time": _ago(15),   "actor": "ops-zhang",   "device_id": 8,  "device": "sw-dmz-01",      "action": "config_apply",   "action_label": "Config push",   "result": "failed",  "note": "Validation failed: vlan does not exist"},
    {"time": _ago(27),   "actor": "net-auto",    "device_id": 2,  "device": "sw-core-02",     "action": "config_apply",   "action_label": "Config push",   "result": "success", "note": "Ansible auto patrol script"},
    {"time": _ago(34),   "actor": "admin",       "device_id": 6,  "device": "sw-edge-room-B", "action": "reboot",         "action_label": "Reboot",        "result": "failed",  "note": "SSH timeout 3 times"},
    {"time": _ago(48),   "actor": "admin",       "device_id": 3,  "device": "sw-agg-floor-3", "action": "reboot",         "action_label": "Reboot",        "result": "success", "note": "Resolved after fan alarm"},
    {"time": _ago(60),   "actor": "admin",       "device_id": 0,  "device": "—",              "action": "login",          "action_label": "Sign in",       "result": "success", "note": "From 10.0.0.42"},
    {"time": _ago(60),   "actor": "ops-zhang",   "device_id": 0,  "device": "—",              "action": "login",          "action_label": "Sign in",       "result": "failed",  "note": "Wrong password 5 times"},
    {"time": _ago(75),   "actor": "ops-zhang",   "device_id": 0,  "device": "5 devices",      "action": "bulk",           "action_label": "Bulk",          "result": "partial", "note": "Bulk reboot of 5: 4 ok 1 failed"},
    {"time": _ago(95),   "actor": "net-auto",    "device_id": 10, "device": "sw-iac-mgmt-01", "action": "config_apply",   "action_label": "Config push",   "result": "success", "note": "SNMP community rotation"},
    {"time": _ago(120),  "actor": "ops-zhang",   "device_id": 11, "device": "sw-iac-mgmt-02", "action": "reboot",         "action_label": "Reboot",        "result": "success", "note": "Routine reboot before hardware upgrade"},
    {"time": _ago(150),  "actor": "admin",       "device_id": 9,  "device": "sw-dmz-02",      "action": "reboot",         "action_label": "Reboot",        "result": "success", "note": "Patch upgrade"},
    {"time": _ago(220),  "actor": "admin",       "device_id": 4,  "device": "sw-agg-floor-7", "action": "config_apply",   "action_label": "Config push",   "result": "failed",  "note": "Diff validation cancelled by user"},
    {"time": _ago(360),  "actor": "net-auto",    "device_id": 0,  "device": "—",              "action": "login",          "action_label": "Sign in",       "result": "success", "note": "service account"},
    {"time": _ago(720),  "actor": "admin",       "device_id": 12, "device": "sw-lab-01",      "action": "reboot",         "action_label": "Reboot",        "result": "failed",  "note": "Device unreachable"},
]


def device_logs(device_id: int):
    return [l for l in LOGS if l["device_id"] == device_id][:5] or [
        {"time": _ago(60), "actor": "admin", "action": "Heartbeat sync", "result": "success", "note": "No per-device activity yet"},
    ]


def build_map_url(sw: dict) -> str:
    """Build a MazeMap share URL from a switch's per-device map fields.

    The map has TWO distinct coordinates by design:
      - center / zoom: where the iframe view is centered (campus overview)
      - sharepoi       : where MazeMap's pin is placed (specific building)

    For switches whose `pin_poi` is a known-valid MazeMap POI id (we
    only have one verified real id, `BLD01_2_C5`, so only the two
    sw-core-* switches use it), we include `sharepoi=...` +
    `sharepoitype=identifier` so MazeMap draws its own pin at the
    building's location (not the iframe center). For all other switches
    `pin_poi` is empty → we omit `sharepoi` → MazeMap draws nothing
    (we don't have valid POI ids for the other buildings) and our
    custom SVG pin overlay in switch_detail.html handles the marker
    using `pin_latlng` + the projected pixel offset.

    Note: `sharepoitype=identifier` auto-opens the info card on load
    (it's the only verified-real type we know). The card is dismissable
    by the user; if we want to suppress it later, we'll need to find a
    different `sharepoitype` value or drop `sharepoi` entirely.
    """
    parts = [
        "https://use.mazemap.com/#v=1",
        f"config={sw.get('campus', 'bonduniversity')}",
        f"campusid={sw.get('campusid', 388)}",
        f"zlevel={sw.get('zlevel', 1)}",
        f"center={sw['map_center']}",
        f"zoom={sw['map_zoom']}",
    ]
    pin_poi = (sw.get("pin_poi") or "").strip()
    if pin_poi:
        # Only known-valid id is BLD01_2_C5 (for the two sw-core switches).
        # Use `identifier` (MazeMap's only verified real type); card
        # auto-opens on load — user dismisses.
        parts.append("sharepoitype=identifier")
        parts.append(f"sharepoi={pin_poi}")
    return "&".join(parts)


def pin_offset_px(pin_latlng: str, center_latlng: str, zoom: int) -> tuple[int, int]:
    """Return (dx, dy) pixel offset of the pin relative to the iframe
    center, using the standard Web Mercator projection (which MazeMap /
    mapbox-gl use). dx>0 means pin is right of center; dy>0 means pin is
    below center.

    At zoom z the world is 256 * 2**z pixels wide; a tile (x, y) coord is:
        x = (lng + 180) / 360 * 2**z
        y = (1 - asinh(tan(lat)) / pi) / 2 * 2**z
    So (pin_x - center_x) * 256 = horizontal pixel offset.
    """
    import math
    plng, plat = (float(s) for s in pin_latlng.split(","))
    clng, clat = (float(s) for s in center_latlng.split(","))

    def tile(lat, lng, z):
        x = (lng + 180) / 360 * (2 ** z)
        s = math.sin(math.radians(lat))
        y = (1 - math.log((1 + s) / (1 - s)) / 2 / math.pi) / 2 * (2 ** z)
        return x, y

    cx, cy = tile(clat, clng, zoom)
    px, py = tile(plat, plng, zoom)
    return int(round((px - cx) * 256)), int(round((py - cy) * 256))


# ---- Fake per-switch port data -----------------------------------------------
# Each switch has 48 ports (4 modules × 12 ports). Mostly up. VLANs are
# distributed so the user sees varied numbers on the page. Last 2 ports of
# each module are uplinks (trunk / 10G); the rest are access ports (1G).
# Description is sparsely populated to make some rows visually distinct.
# All values are deterministic given (device_id, port#) so refreshes are
# stable.

VLAN_POOL   = [10, 20, 30, 40, 100]      # cycles for normal ports
TRUNK_VLANS = [10, 20, 30]               # VLANs trunks carry

# VLANs the operator is *allowed* to change a port to. Real project would
# derive this from the device's VLAN DB; mockup uses a fixed list so the
# per-port VLAN dropdown and the bulk-VLAN toolbar stay in sync.
ALLOWED_VLANS = [1, 10, 20, 30, 40, 99, 100, 200, 300, 400, 666, 999]

DESCRIPTION_SAMPLES = {                   # pre-fills a few port descriptions
    5:  "uplink-to-core-01",
    6:  "uplink-to-core-02",
    17: "server rack 1",
    18: "server rack 2",
    31: "printer-floor-3",
    44: "mgmt",
}


def device_ports(device_id: int):
    """Return 48 ports for the given switch. Stable per (device_id, port#)."""
    ports = []
    seed = (device_id * 7) % 31            # deterministic distribution
    for module in range(1, 5):            # modules 1..4
        for p in range(1, 13):           # ports 1..12 per module
            num = (module - 1) * 12 + p
            is_trunk = p in (11, 12)
            status  = "down" if (seed + num) % 23 == 0 else "up"
            if is_trunk:
                vlan = TRUNK_VLANS[(seed + num) % len(TRUNK_VLANS)]
            else:
                vlan = VLAN_POOL[(seed + num) % len(VLAN_POOL)]
            # PoE: on for module 1 (PoE-capable switches usually have it
            # distributed across ports), off otherwise.
            poe = (module == 1 and p % 3 == 0)
            ports.append({
                "num":         num,
                "name":        f"Gi1/{num}",
                "module":      module,
                "status":      status,
                "vlan":        vlan,
                "mode":        "trunk" if is_trunk else "access",
                "speed":       "10G" if is_trunk else "1G",
                "poe":         poe,
                "description": DESCRIPTION_SAMPLES.get(num, ""),
            })
    return ports


# --- Tailwind config exposed to the template via window.tailwind.config -------

TAILWIND_CONFIG = {
    "content": ["./templates/**/*.html"],
    "theme": {
        "extend": {
            "colors": {
                "border": "hsl(var(--border) / <alpha-value>)",
                "input": "hsl(var(--input) / <alpha-value>)",
                "ring": "hsl(var(--ring) / <alpha-value>)",
                "background": "hsl(var(--background) / <alpha-value>)",
                "foreground": "hsl(var(--foreground) / <alpha-value>)",
                "primary": {
                    "DEFAULT": "hsl(var(--primary) / <alpha-value>)",
                    "foreground": "hsl(var(--primary-foreground) / <alpha-value>)",
                },
                "secondary": {
                    "DEFAULT": "hsl(var(--secondary) / <alpha-value>)",
                    "foreground": "hsl(var(--secondary-foreground) / <alpha-value>)",
                },
                "destructive": {
                    "DEFAULT": "hsl(var(--destructive) / <alpha-value>)",
                    "foreground": "hsl(var(--destructive-foreground) / <alpha-value>)",
                },
                "muted": {
                    "DEFAULT": "hsl(var(--muted) / <alpha-value>)",
                    "foreground": "hsl(var(--muted-foreground) / <alpha-value>)",
                },
                "accent": {
                    "DEFAULT": "hsl(var(--accent) / <alpha-value>)",
                    "foreground": "hsl(var(--accent-foreground) / <alpha-value>)",
                },
                "popover": {
                    "DEFAULT": "hsl(var(--popover) / <alpha-value>)",
                    "foreground": "hsl(var(--popover-foreground) / <alpha-value>)",
                },
                "card": {
                    "DEFAULT": "hsl(var(--card) / <alpha-value>)",
                    "foreground": "hsl(var(--card-foreground) / <alpha-value>)",
                },
                "success": "hsl(var(--success) / <alpha-value>)",
                "warning": "hsl(var(--warning) / <alpha-value>)",
                "chart-1": "hsl(var(--chart-1) / <alpha-value>)",
                "chart-2": "hsl(var(--chart-2) / <alpha-value>)",
                "chart-3": "hsl(var(--chart-3) / <alpha-value>)",
                "chart-4": "hsl(var(--chart-4) / <alpha-value>)",
                "chart-5": "hsl(var(--chart-5) / <alpha-value>)",
            },
            "borderRadius": {
                "lg": "var(--radius)",
                "md": "calc(var(--radius) - 2px)",
                "sm": "calc(var(--radius) - 4px)",
                "xl": "calc(var(--radius) + 4px)",
            },
            "fontFamily": {
                "sans": ['Inter', 'Inter Variable', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI',
                        'Roboto', 'Helvetica Neue', 'Arial',
                        'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB',
                        'Noto Sans SC', 'Noto Sans CJK SC', 'Source Han Sans SC',
                        'WenQuanYi Micro Hei', 'sans-serif'],
            },
        }
    },
}


def render(request: Request, template_name: str, context: dict) -> HTMLResponse:
    ctx = {"tailwind_config": TAILWIND_CONFIG, **context}
    return templates.TemplateResponse(request, template_name, ctx)


# --- Routes -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return render(request, "pages/login.html", {})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render(request, "pages/login.html", {})


@app.post("/login", response_class=HTMLResponse)
def login_submit(request: Request):
    # Mockup: any submit returns success, just nudge user to /switches.
    return HTMLResponse(
        '<span class="text-success text-sm">Signed in, redirecting…</span>'
        '<meta http-equiv="refresh" content="0; url=/switches" />'
    )


@app.get("/switches", response_class=HTMLResponse)
def switches_list(
    request: Request,
    q: str = "",
    status: str = "ALL",
    sort: str = "name",
    dir: str = "asc",
    demo_empty: int = 0,
):
    # Filter the hardcoded list by q (matches name OR ip, case-insensitive)
    # and status (exact match). Sort by name | ip | status | last_seen, with
    # direction. Mockup logic only — real project will hit the device registry.
    rows = SWITCHES
    if q:
        qn = q.strip().lower()
        rows = [s for s in rows if qn in s["name"].lower() or qn in s["ip"]]
    if status != "ALL":
        rows = [s for s in rows if s["status"] == status]
    sort_key = {
        "name":      lambda s: s["name"].lower(),
        "ip":        lambda s: s["ip"],
        "status":    lambda s: s["status"],
        "last_seen": lambda s: s["last_seen"],
    }.get(sort, lambda s: s["name"].lower())
    rows = sorted(rows, key=sort_key, reverse=(dir == "desc"))
    return render(request, "pages/switches_list.html", {
        "query": q,
        "selected_status": status,
        "selected_sort": sort,
        "selected_dir": dir,
        "switches": rows,
        "demo_empty": demo_empty,
    })


@app.get("/switches/{device_id}", response_class=HTMLResponse)
def switch_detail(request: Request, device_id: int):
    sw = next((s for s in SWITCHES if s["id"] == device_id), None)
    if not sw:
        sw = {**SWITCHES[0], "name": "Unknown device", "ip": "—", "model": "—", "status": "UNKNOWN",
              "serial": "—", "location": "—", "uptime": "—", "last_seen": "—", "map_url": ""}
    sw = {**sw,
          "serial": "FOC1234X5AB",
          "location": "Building B floor 3 · rack A07",
          "uptime": "12d 4h 32m"}
    # Build the MazeMap share URL from the per-switch map fields. If
    # the switch has no map_center / pin_latlng (e.g. unknown-device
    # fallback), produce an empty string so the location row falls back
    # to a plain text label.
    if sw.get("map_center") and sw.get("pin_latlng") and sw.get("map_zoom"):
        sw = {**sw, "map_url": build_map_url(sw)}
    else:
        sw = {**sw, "map_url": ""}
    return render(request, "pages/switch_detail.html", {
        "sw": sw,
        "device_logs": device_logs(device_id),
        "ports": device_ports(device_id),
        "allowed_vlans": ALLOWED_VLANS,
    })


# ---- Mockup write endpoints (return small HTML fragments; real persistence
# is stubbed out — UI just gets a "saved" toast back).
# ----------------------------------------------------------------------

@app.post("/switches/{device_id}/reboot")
def reboot(device_id: int):
    return HTMLResponse("")


@app.post("/switches/{device_id}/preview-config")
def preview_config(device_id: int):
    return HTMLResponse(
        '<div class="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">'
        'Diff snippet (mockup — see the Previewed tab for the static text).'
        '</div>'
    )


@app.post("/switches/{device_id}/apply-config")
def apply_config(device_id: int):
    return HTMLResponse("")


@app.post("/switches/bulk-reboot")
def bulk_reboot():
    return HTMLResponse(
        '<div class="rounded-md border border-success/30 bg-success/10 px-4 py-3 text-sm text-success">'
        'Bulk reboot request submitted (mockup).'
        '</div>'
    )


@app.get("/switches/poll", response_class=HTMLResponse)
def poll(request: Request):
    """htmx poll endpoint — returns the same table body. Fine for mockup."""
    return render(request, "_partials/switch_table_body.html", {"switches": SWITCHES})


@app.get("/logs", response_class=HTMLResponse)
def logs(
    request: Request,
    date_from: str = "2026-06-01",
    date_to: str = "2026-06-30",
    actor: str = "ALL",
    action: str = "ALL",
):
    rows = LOGS
    if actor != "ALL":
        rows = [l for l in rows if l["actor"] == actor]
    if action != "ALL":
        rows = [l for l in rows if l["action"] == action]
    return render(request, "pages/logs.html", {
        "logs": rows,
        "date_from": date_from,
        "date_to": date_to,
        "selected_actor": actor,
        "selected_action": action,
    })


@app.post("/switches/{device_id}/ports/bulk-apply")
async def ports_bulk_apply(device_id: int, request: Request):
    """Apply a batch of staged cell edits in one shot.

    Body: JSON-encoded `{"<port_num>": {"vlan": 100, "description": "...", "poe": true}, ...}`.
    Returns: HTML success fragment ready to swap into the apply-result slot.

    NOTE: this route is declared BEFORE the per-port route so the literal
    `bulk-apply` segment matches here, not as `port_num` (int parse).
    """
    form = await request.form()
    raw = form.get("payload", "{}")
    try:
        import json as _json
        changes = _json.loads(raw) if isinstance(raw, str) else dict(raw)
    except Exception:
        changes = {}

    # Real project would commit each change to the device / DB. Mockup
    # just counts + returns success.
    n_ports = len(changes)
    n_fields = sum(len(v) if isinstance(v, dict) else 1 for v in changes.values())
    return HTMLResponse(
        f'<div class="rounded-md border border-success/30 bg-success/10 px-4 py-3 text-sm text-success">'
        f'Applied <span class="font-semibold">{n_fields}</span> change(s) across '
        f'<span class="font-semibold">{n_ports}</span> port(s) on device #{device_id} (mockup).'
        '</div>'
    )


@app.post("/switches/{device_id}/ports/{port_num}")
def port_update(device_id: int, port_num: int, vlan: int = 0, mode: str = "access", description: str = ""):
    """Stub: real project would persist to the device. Mockup returns the
    update action's success toast for hx-swap into the row's bulk-result slot."""
    return HTMLResponse(
        '<div class="rounded-md border border-success/30 bg-success/10 px-3 py-2 text-xs text-success">'
        f'Port Gi1/{port_num} saved (VLAN {vlan}, {mode}).'
        '</div>'
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)
