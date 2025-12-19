from transport.TransportCompany import TransportCompany
from transport.Client import Client
from transport.Vehicle import Vehicle


company = TransportCompany("Транспортная компания")
while True:
    number = int(input('''Выберите номер пункта из меню:
        1. Вывести список транспортных средств
        2. Вывести список клиентов
        3. Добавить транспортное средство
        4. Добавить клиента
        5. Распределение грузов клиентов
        6. Выход из меню\n'''))
    
    if number == 1:
        vehicles = company.list_vehicles()  # получаем список
        if len(vehicles) == 0:
            print("\n| В компании пока нет транспортных средств | \n")
        else:
            print("\n=== Список транспортных средств ===")
            for vehicle in vehicles:  # перебираем и печатаем
                print(vehicle)
            print()


    if number == 2:
        clients1 = company.list_clients()  # получаем список
        if len(clients1) == 0:
            print("\n| У компании пока нет клиентов | \n")
        else:
            print("\n=== Список клиентов ===")
            for client1 in clients1:  # перебираем и печатаем
                print(client1)
            print()


    if number == 3:
        print("*Добавление транспортного средства*")
        veh_cl_list = []
        veh_id = input("Введите ID транспортного средства: ")
        veh_capacity = float(input("Введите вместимость (в тоннах): "))
        iter = int(input("Введите количество клиентов у транспортного ср-ва: "))
        for i in range(iter):
            cl_name = input("Введите имя клиента: ")
            cl_weight = float(input("Введите вес груза клиента: "))
            cl_isvip = input("Клиент вип? (True / False): ")
            if cl_isvip == 'True':
                cl_isvip = True
            elif cl_isvip == 'False': 
                cl_isvip = False
            else:
                raise TypeError("Введено неверное вип-значение")
            cl = Client(cl_name, cl_weight, cl_isvip)
            company.add_client(cl)
        veh_load = float(input("Введите загруженность транспортного ср-ва (в тоннах): "))
        new_vehicle = Vehicle( veh_id, veh_capacity, veh_cl_list, veh_load)
        company.add_vehicle(new_vehicle)



    if number == 4:
        cli_name = input("Введите имя клиента: ")
        cli_weight = float(input("Введите вес груза клиента: "))
        cli_isvip = input("Клиент вип? (True / False): ")
        if cli_isvip == 'True':
            cli_isvip = True
        elif cli_isvip == 'False': 
             cli_isvip = False
        else:
            raise TypeError("Введено неверное вип-значение")
        cli = Client(cli_name, cli_weight, cli_isvip)
        company.add_client(cli)
        
    if number == 5:
        company.optimize_cargo_distribution()
    if number == 6:
        break
    