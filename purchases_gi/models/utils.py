

def redondear_cantidad_decimales(qty):
    """
    Funcion que redondea a 3 decimales las cantidades que tienen mas de 3.
    :param qty:
    :return:
    """
    new_qty = qty
    if qty:
        split_cantidad = str(qty).split(".")
        if len(split_cantidad[1]) > 3:
            new_qty = float("{0:.3f}".format(qty))
    return new_qty