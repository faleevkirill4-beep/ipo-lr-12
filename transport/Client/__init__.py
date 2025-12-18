class Client:

    def __init__(self,name:str,cargo_weight:float,is_vip:bool):

        self.name = name
        self.cargo_weight = cargo_weight
        self.is_vip = is_vip

    def __str__(self):
        return f"имя клиента: {self.name}\n вес груза: {self.cargo_weight}\n флаг VIP-статуса: {self.is_vip}"