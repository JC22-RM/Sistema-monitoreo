from flask import Flask, render_template, request, redirect
from smartolt import obtener_onus
from datetime import datetime

app = Flask(__name__)


def tiempo_transcurrido(fecha_texto):

    if not fecha_texto:
        return "Sin dato"

    try:

        fecha = datetime.strptime(
            fecha_texto,
            "%Y-%m-%d %H:%M:%S"
        )

        ahora = datetime.now()

        diferencia = ahora - fecha

        dias = diferencia.days

        horas = diferencia.seconds // 3600

        minutos = (diferencia.seconds % 3600) // 60

        if dias >= 7:
            return f"{dias // 7} semana(s)"

        elif dias > 0:
            return f"{dias} día(s)"

        elif horas > 0:
            return f"{horas} hora(s)"

        else:
            return f"{minutos} min"

    except:
        return "Sin dato"


# ==========================
# LOGIN
# ==========================

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/validar", methods=["POST"])
def validar():

    usuario = request.form.get("usuario")
    password = request.form.get("password")

    if usuario == "admin" and password == "123456":
        return redirect("/dashboard")

    return render_template(
        "login.html",
        error="❌ Usuario o contraseña incorrectos"
    )


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ==========================
# MONITOREO
# ==========================

@app.route("/monitoreo")
def monitoreo():

    onus = obtener_onus()

    total_onus = len(onus)

    online = len([
        o for o in onus
        if o.get("status") == "Online"
    ])

    offline = len([
        o for o in onus
        if o.get("status") == "Offline"
    ])

    los = len([
        o for o in onus
        if o.get("status") == "LOS"
    ])

    power_fail = len([
        o for o in onus
        if o.get("status") == "Power fail"
    ])

    grupos = {}

    for onu in onus:

        estado = onu.get("status")

        if estado not in [
            "LOS",
            "Power fail",
            "Offline"
        ]:
            continue

        clave = (
            onu.get("olt_id"),
            onu.get("board"),
            onu.get("port"),
            estado
        )

        if clave not in grupos:

            grupos[clave] = {
                "olt": onu.get("olt_id"),
                "board": onu.get("board"),
                "port": onu.get("port"),
                "zona": onu.get("zone_id"),
                "estado": estado,
                "cantidad": 0,
                "tiempo": tiempo_transcurrido(
                    onu.get("last_status_change")
                )
            }

        grupos[clave]["cantidad"] += 1

    incidencias = sorted(
        grupos.values(),
        key=lambda x: x["cantidad"],
        reverse=True
    )

    return render_template(
        "monitoreo.html",
        total_onus=total_onus,
        online=online,
        offline=offline,
        los=los,
        power_fail=power_fail,
        incidencias=incidencias
    )


# ==========================
# DIAGNOSTICO IA
# ==========================

@app.route("/diagnostico")
def diagnostico():
    return render_template("diagnostico.html")


# ==========================
# HISTORIAL
# ==========================

@app.route("/historial")
def historial():
    return render_template("historial.html")


# ==========================
# REPORTES
# ==========================

@app.route("/reportes")
def reportes():
    return render_template("reportes.html")


# ==========================
# USUARIOS
# ==========================

@app.route("/usuarios")
def usuarios():
    return render_template("usuarios.html")


# ==========================
# CONFIGURACION
# ==========================

@app.route("/configuracion")
def configuracion():
    return render_template("configuracion.html")


# ==========================
# EJECUCION
# ==========================

if __name__ == "__main__":
    app.run(debug=True)