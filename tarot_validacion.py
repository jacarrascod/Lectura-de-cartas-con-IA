import os
import pandas as pd
import streamlit as st

RUTA_BBDD = "bbdd_user.csv"
DORSO_PATH = "cards\\Dorso.png"
CARPETA_CARTAS = "cards"

# Validar correo electrónico
def validar_email(correo):
    import re
    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(patron, correo) is not None

# Verificar imagen
def verificar_imagen(ruta):
    return os.path.exists(ruta)

# Guardar datos del usuario
def guardar_datos_usuario(nombre, correo, carta):
    if not os.path.exists(RUTA_BBDD):
        df = pd.DataFrame(columns=["nombre_usuario", "email_usuario", "carta_que_le_toco"])
    else:
        df = pd.read_csv(RUTA_BBDD, delimiter=";")

    nuevo_usuario = pd.DataFrame({
        "nombre_usuario": [nombre],
        "email_usuario": [correo],
        "carta_que_le_toco": [carta]
    })
    df = pd.concat([df, nuevo_usuario], ignore_index=True)
    df.to_csv(RUTA_BBDD, sep=";", index=False)

# Verificar si un usuario ya está registrado
def verificar_usuario(correo):
    if os.path.exists(RUTA_BBDD):
        df = pd.read_csv(RUTA_BBDD, delimiter=";")
        usuario = df[df["email_usuario"] == correo]
        if not usuario.empty:
            return usuario.iloc[0]["carta_que_le_toco"]
    return None

# Cargar datos del tarot
def cargar_tarot():
    data_path = "cartas_bdd.csv"
    if os.path.exists(data_path):
        return pd.read_csv(data_path, delimiter=";")
    else:
        st.error("No se encontró el archivo de datos del tarot.")
        return None

# Función principal de la aplicación
def main():
    st.title("\u2728 Lectura de Tarot \u2728")
    tarot_data = cargar_tarot()

    if tarot_data is not None:
        if "cartas_seleccionadas" not in st.session_state:
            st.session_state["cartas_seleccionadas"] = []
            st.session_state["cartas_volteadas"] = [False, False, False]
            st.session_state["cartas_mostradas"] = [True, True, True]
            st.session_state["card_chosen"] = None
            st.session_state["nombre"] = ""
            st.session_state["correo"] = ""
            st.session_state["show_form"] = True
            st.session_state["email_valido"] = False
            st.session_state["carta_seleccionada"] = False

        if st.session_state["show_form"]:
            st.write("Por favor ingresa tu nombre y dirección de correo:")

            nombre = st.text_input("Nombre", value=st.session_state["nombre"])
            correo = st.text_input("Correo electrónico", value=st.session_state["correo"])

            if correo and not validar_email(correo):
                st.error("Email inválido, ingresa un email válido.")
                st.session_state["email_valido"] = False
            else:
                st.session_state["email_valido"] = True

            if nombre and correo and st.session_state["email_valido"]:
                habilitar_boton = True
            else:
                habilitar_boton = False

            if st.button("Consultar el tarot", disabled=not habilitar_boton):
                st.session_state["nombre"] = nombre
                st.session_state["correo"] = correo
                carta_asignada = verificar_usuario(correo)

                if carta_asignada:
                    st.session_state["cartas_seleccionadas"] = tarot_data[
                        tarot_data["codigo"] == carta_asignada
                    ][["codigo", "carta_esp", "descrip", "como_afecta_year"]].to_dict(orient="records")
                    st.session_state["cartas_volteadas"] = [True]
                    st.session_state["cartas_mostradas"] = [True]
                    st.session_state["card_chosen"] = carta_asignada
                    st.session_state["carta_seleccionada"] = True
                else:
                    seleccionadas = tarot_data.sample(3)
                    st.session_state["cartas_seleccionadas"] = seleccionadas[
                        ["codigo", "carta_esp", "descrip", "como_afecta_year"]
                    ].to_dict(orient="records")
                    st.session_state["cartas_volteadas"] = [False, False, False]
                    st.session_state["cartas_mostradas"] = [True, True, True]
                    st.session_state["card_chosen"] = None
                    st.session_state["carta_seleccionada"] = False

                st.session_state["show_form"] = False
                st.rerun()

        if not st.session_state["show_form"]:
            if not st.session_state["carta_seleccionada"]:
                st.subheader("Elige una carta para verla")

            cols = st.columns(3)
            for i, carta in enumerate(st.session_state["cartas_seleccionadas"]):
                with cols[i]:
                    if st.session_state["cartas_mostradas"][i]:
                        if not st.session_state["cartas_volteadas"][i]:
                            if st.button(f"Voltear carta {i+1}", key=f"voltear_{i}"):
                                st.session_state["cartas_volteadas"][i] = True
                                st.session_state["cartas_mostradas"] = [False, False, False]
                                st.session_state["cartas_mostradas"][i] = True
                                st.session_state["card_chosen"] = carta["codigo"]
                                st.session_state["carta_seleccionada"] = True
                                st.rerun()

                            if verificar_imagen(DORSO_PATH):
                                st.image(DORSO_PATH, use_container_width=True, caption=f"Carta {i+1}")

            if st.session_state["card_chosen"]:
                carta_seleccionada = next(
                    c for c in st.session_state["cartas_seleccionadas"] if c["codigo"] == st.session_state["card_chosen"]
                )
                cols = st.columns([2, 2])

                with cols[0]:
                    ruta_carta = os.path.join(CARPETA_CARTAS, f"{carta_seleccionada['codigo']}.png")
                    if verificar_imagen(ruta_carta):
                        st.image(ruta_carta, width=int(300 * 0.7))

                with cols[1]:
                    st.markdown(f"### **{carta_seleccionada['carta_esp']}**")
                    st.write(f"**Descripción:** {carta_seleccionada['descrip']}")
                    st.write(f"**¿Cómo afecta este año?:** {carta_seleccionada['como_afecta_year']}")

                if not verificar_usuario(st.session_state["correo"]):
                    guardar_datos_usuario(
                        st.session_state["nombre"], st.session_state["correo"], st.session_state["card_chosen"]
                    )

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
