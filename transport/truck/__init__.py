from Vehicle import Vehicle

class Truck(Vehicle):

     def __init__(self,vihicle_id:str,capacity:float,clients_list:list,color:str,current_load = 0):
          self.color = color 
          super().__init__(vihicle_id,capacity,clients_list,current_load)