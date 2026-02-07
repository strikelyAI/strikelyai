def estado_forma(df, equipo, local=True, n=5):
    if local:
        partidos = df[df["HomeTeam"] == equipo].tail(n)
        gf = partidos["FTHG"].sum()
        gc = partidos["FTAG"].sum()
        res = ["W" if r.FTHG > r.FTAG else "D" if r.FTHG == r.FTAG else "L"
               for r in partidos.itertuples()]
    else:
        partidos = df[df["AwayTeam"] == equipo].tail(n)
        gf = partidos["FTAG"].sum()
        gc = partidos["FTHG"].sum()
        res = ["W" if r.FTAG > r.FTHG else "D" if r.FTAG == r.FTHG else "L"
               for r in partidos.itertuples()]

    return {
        "PJ": len(partidos),
        "V": res.count("W"),
        "E": res.count("D"),
        "D": res.count("L"),
        "GF": gf,
        "GC": gc,
        "racha": res
    }
