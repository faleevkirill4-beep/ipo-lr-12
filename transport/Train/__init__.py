from Vehicle import Vehicle

class Train(Vehicle):

    def __init__(self,vihicle_id:str,capacity:float,clients_list:list,number_of_cars:int,current_load = 0):
        self.number_of_cars = number_of_cars
        super().__init__(vihicle_id,capacity,clients_list,current_load)