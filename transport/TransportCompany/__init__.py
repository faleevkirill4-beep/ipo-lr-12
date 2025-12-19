from ..Vehicle import Vehicle
from ..Client import Client

class TransportCompany:

    def __init__(self,name):
        self.name = name
        self.vehicles = []
        self.clients = [] 

    def add_vehicle(self,vehicle):
         if not isinstance(vehicle, Vehicle):
            raise TypeError(f"Введено некорректное название транспортного средства: {vehicle}")
         for number_vehicle in self.vehicles:
             if number_vehicle == vehicle.vihicle_id:
                 raise TypeError(f"Введено некорректное название транспортного средства: {vehicle}")
             if number_vehicle == vehicle.vihicle_id:
                 raise TypeError(f"введенное ID уже существует")
             self.vehicles.append(vehicle)
             self.clients += vehicle.clients_list
             return print(f"В компанию {self.name} добавлено новое транспортное средство {vehicle}")

    def list_vehicles(self):
        return self.vehicles
    
    def list_clients(self):
        return self.clients
    
    def add_client(self,client):
        if not isinstance(client, Client):
            raise TypeError(f"Введено некорректное имя клиента: {client}")
        for number_client in self.clients:
            if number_client == client:
                raise TypeError(f"клиент уже существует")
        self.clients.append(client)
        return print(f"Клиент {client} добавлен в компанию {self.name} ")
    
    def optimize_cargo_distribution(self,):
        # Разделяем клиентов на VIP и обычных
        vip_clients = [client for client in self.clients if client.is_vip]
        regular_clients = [client for client in self.clients if not client.is_vip]

        sorted_vip_clients = sorted(vip_clients, key=lambda c: c.cargo_weight, reverse=True)
        sorted_regular_clients = sorted(regular_clients, key=lambda c: c.cargo_weight, reverse=True)
        sorted_clients = sorted_vip_clients + sorted_regular_clients

        valid_s_clients = [client for client in sorted_clients if client.cargo_weight > 0]

        sorted_vehicles = sorted(self.vehicles, key=lambda w: w.capacity, reverse=True)

        assigned_clients = 0  # счетчик распределенных клиентов

        for clnt in valid_s_clients:
            for vehicl in sorted_vehicles:
                available_w = vehicl.capacity - vehicl.current_load
                if available_w >= clnt.cargo_weight:
                    vehicl.current_load += clnt.cargo_weight
                    clnt.cargo_weight = 0
                    assigned_clients += 1
                    break

        if assigned_clients != len(valid_s_clients):
            return print(f"Не удалось поместить все грузы в транспорт")
        elif assigned_clients == len(valid_s_clients):
            return print("Загрузка товаров прошла успешно")