from pycamp_bot.models import Pycampista


if __name__ == "__main__":
    admin = input("Ingresá tu Alias de Telegram para ser admin: ")

    pycampistas = Pycampista.filter(username=admin)
    if pycampistas.count() == 1:
        pycampista = pycampistas[0]
        pycampista.is_admin = True
        pycampista.save()
        print('\033[1;32mEl usuario {} fue habilitado como admin!\033[0m'.format(admin))
    else:
        print('\033[1;31mEl usuario ingresado no existe!\033[0m')
