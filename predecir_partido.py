def predecir_partido(local, visitante):
    pl, glf, glc = forma_equipo(local)
    pv, gvf, gvc = forma_equipo(visitante)

    ventaja_local = 1.15  # peso por jugar en casa

    fuerza_local = (pl + glf - glc) * ventaja_local
    fuerza_visitante = (pv + gvf - gvc)

    total = fuerza_local + fuerza_visitante

    prob_local = fuerza_local / total
    prob_visitante = fuerza_visitante / total
    prob_empate = 1 - (prob_local + prob_visitante)

    print("\n📊 ANÁLISIS DEL PARTIDO")
    print(f"{local} vs {visitante}")

    print("\n🔹 PROBABILIDADES 1X2")
    print(f"Victoria local: {prob_local:.2%}")
    print(f"Empate: {prob_empate:.2%}")
    print(f"Victoria visitante: {prob_visitante:.2%}")

    # GOLES
    media_goles = (glf + gvf) / 10
    print("\n🔹 GOLES")
    print(f"Media esperada de goles: {media_goles:.2f}")
    print("Over 2.5" if media_goles > 2.5 else "Under 2.5")

    # BTTS
    btts = (glf > 4 and gvf > 4)
    print("\n🔹 AMBOS MARCAN")
    print("Sí" if btts else "No")
