from aplicacion.autenticacion.seguridad import cifrar_password, verificar_password


def test_cifrar_password_genera_hash_distinto_al_original():
    hash_resultante = cifrar_password("Admin123")

    assert hash_resultante != "Admin123"
    assert isinstance(hash_resultante, str)


def test_verificar_password_acepta_password_correcto():
    hash_resultante = cifrar_password("Admin123")

    assert verificar_password("Admin123", hash_resultante) is True


def test_verificar_password_rechaza_password_incorrecto():
    hash_resultante = cifrar_password("Admin123")

    assert verificar_password("ClaveIncorrecta", hash_resultante) is False


def test_cifrar_password_genera_hashes_distintos_para_mismo_password():
    hash_uno = cifrar_password("Admin123")
    hash_dos = cifrar_password("Admin123")

    assert hash_uno != hash_dos
