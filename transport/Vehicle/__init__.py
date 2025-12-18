from Client import Client

class Vehicle:

    def __init__(self,vihicle_id:str,capacity:float,clients_list:list,current_load = 0):
            self.vihicle_id = vihicle_id
            self.capacity = capacity
            self.current_load = current_load
            self.clients_list = clients_list  if clients_list is not None else []


    def load_cargo(self, client):
        if not isinstance(client,Client):
            raise TypeError(f"Получено: {type(client)}, не соответствует валидации")
        self.current_load += client.cargo_weight
        if self.current_load <=self.capacity:
             self.clients_list.append(client)
             return print(f"Клиент {client} добавлен в список клиентов")
        else:
             return print(f"Произошла перегрузка транспортного средства, допустимый обьем: {self.capacity} | загрузка: {self.current_load} ")
    
    def __str__(self):
         string = f"ID транспорта: {self.vihicle_id} || грузоподьемность: {self.capacity} || загруженный вес транспорта: {self.current_load}"
         return string