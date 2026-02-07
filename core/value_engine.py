def validar_cuota(txt):
    try:
        q = float(txt.replace(",", "."))
        if q < 1.20 or q > 50:
            return None
        return q
    except:
        return None

def calcular_value(prob, cuota):
    return prob * cuota - 1
