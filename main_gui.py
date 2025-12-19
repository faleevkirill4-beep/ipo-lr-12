import dearpygui.dearpygui as dpg
import json
import csv
from datetime import datetime
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем наши классы
try:
    from transport.Client import Client
    from transport.Vehicle import Vehicle
    from transport.TransportCompany import TransportCompany
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    # Создаем заглушки для тестирования
    class Client:
        def __init__(self, name, cargo_weight, is_vip=False):
            self.name = name
            self.cargo_weight = cargo_weight
            self.is_vip = is_vip
    
    class Vehicle:
        def __init__(self, vehicle_id, capacity, vehicle_type="Грузовик"):
            self.vehicle_id = vehicle_id
            self.capacity = capacity
            self.current_load = 0
            self.vehicle_type = vehicle_type
            self.clients_list = []
    
    class TransportCompany:
        def __init__(self, name):
            self.name = name
            self.vehicles = []
            self.clients = []

class TransportCompanyGUI:
    def __init__(self):
        self.company = TransportCompany("Транспортная Компания")
        self.current_edit_client_index = None
        self.current_edit_vehicle_index = None
        self.distribution_results = []
        
        # Инициализация DPG
        dpg.create_context()
        
        # Настройка темы
        self.setup_theme()
        
        # Создание интерфейса
        self.create_main_window()
        self.create_client_window()
        self.create_vehicle_window()
        self.create_about_window()
        self.create_export_window()
        
        # Показать главное окно
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
    
    def setup_theme(self):
        """Настройка темы приложения"""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (70, 70, 70, 150))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (80, 80, 80, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (60, 60, 60, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (40, 40, 40, 255))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (220, 220, 0, 255))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
        
        dpg.bind_theme(global_theme)
    
    def create_main_window(self):
        """Создание главного окна"""
        with dpg.window(label="Транспортная Компания", tag="main_window", width=1200, height=800):
            
            # Меню
            with dpg.menu_bar():
                with dpg.menu(label="Файл"):
                    dpg.add_menu_item(label="Экспорт результатов", callback=lambda: self.show_export_window())
                    dpg.add_separator()
                    dpg.add_menu_item(label="Выход", callback=lambda: dpg.stop_dearpygui())
                
                with dpg.menu(label="Справка"):
                    dpg.add_menu_item(label="О программе", callback=lambda: dpg.show_item("about_window"))
            
            # Панель управления
            with dpg.group(horizontal=True):
                dpg.add_button(label="Добавить клиента", callback=lambda: self.show_client_window(), width=150, height=40)
                dpg.add_button(label="Добавить транспорт", callback=lambda: self.show_vehicle_window(), width=150, height=40)
                dpg.add_button(label="Распределить грузы", callback=self.optimize_distribution, width=150, height=40)
                dpg.add_button(label="Удалить выделенное", callback=self.delete_selected, width=150, height=40)
                dpg.add_button(label="Очистить все", callback=self.clear_all, width=150, height=40)
            
            dpg.add_spacer(height=10)
            
            # Таблицы данных
            with dpg.group(horizontal=True):
                # Таблица клиентов
                with dpg.child_window(width=580, height=500):
                    dpg.add_text("Клиенты", color=(255, 255, 0))
                    self.clients_table = dpg.add_table(
                        header_row=True,
                        policy=dpg.mvTable_SizingFixedFit,
                        borders_innerH=True,
                        borders_outerH=True,
                        borders_innerV=True,
                        borders_outerV=True
                    )
                    dpg.add_table_column(label="Имя", parent=self.clients_table, width_fixed=True, width=200)
                    dpg.add_table_column(label="Вес груза (кг)", parent=self.clients_table, width_fixed=True, width=150)
                    dpg.add_table_column(label="VIP", parent=self.clients_table, width_fixed=True, width=100)
                    
                    # Контекстное меню для таблицы клиентов
                    with dpg.popup(parent=self.clients_table, mousebutton=dpg.mvMouseButton_Right, modal=False):
                        dpg.add_menu_item(label="Редактировать", callback=lambda: self.edit_client())
                        dpg.add_menu_item(label="Удалить", callback=lambda: self.delete_selected())
                
                dpg.add_spacer(width=10)
                
                # Таблица транспорта
                with dpg.child_window(width=580, height=500):
                    dpg.add_text("Транспортные средства", color=(255, 255, 0))
                    self.vehicles_table = dpg.add_table(
                        header_row=True,
                        policy=dpg.mvTable_SizingFixedFit,
                        borders_innerH=True,
                        borders_outerH=True,
                        borders_innerV=True,
                        borders_outerV=True
                    )
                    dpg.add_table_column(label="ID", parent=self.vehicles_table, width_fixed=True, width=150)
                    dpg.add_table_column(label="Тип", parent=self.vehicles_table, width_fixed=True, width=150)
                    dpg.add_table_column(label="Вместимость", parent=self.vehicles_table, width_fixed=True, width=150)
                    dpg.add_table_column(label="Загрузка", parent=self.vehicles_table, width_fixed=True, width=150)
                    
                    # Контекстное меню для таблицы транспорта
                    with dpg.popup(parent=self.vehicles_table, mousebutton=dpg.mvMouseButton_Right, modal=False):
                        dpg.add_menu_item(label="Редактировать", callback=lambda: self.edit_vehicle())
                        dpg.add_menu_item(label="Удалить", callback=lambda: self.delete_selected())
            
            dpg.add_spacer(height=10)
            
            # Статусная строка
            self.status_bar = dpg.add_text("Готов к работе", color=(0, 255, 0))
            
            # Результаты распределения
            with dpg.collapsing_header(label="Результаты распределения", default_open=False):
                self.results_table = dpg.add_table(
                    header_row=True,
                    policy=dpg.mvTable_SizingFixedFit
                )
                dpg.add_table_column(label="Клиент", parent=self.results_table)
                dpg.add_table_column(label="Вес груза", parent=self.results_table)
                dpg.add_table_column(label="Транспорт", parent=self.results_table)
                dpg.add_table_column(label="Загрузка", parent=self.results_table)
    
    def create_client_window(self):
        """Окно добавления/редактирования клиента"""
        with dpg.window(label="Клиент", tag="client_window", width=400, height=350, show=False, modal=True):
            dpg.add_text("Данные клиента")
            
            # Поля для ввода
            dpg.add_input_text(label="Имя клиента##client", tag="client_name", width=300)
            dpg.add_tooltip(dpg.last_item(), "Только буквы, минимум 2 символа")
            
            dpg.add_input_float(label="Вес груза (кг)##client", tag="client_weight", width=300, min_value=0, max_value=10000, format="%.2f")
            dpg.add_tooltip(dpg.last_item(), "Положительное число, не более 10000 кг")
            
            dpg.add_checkbox(label="VIP статус##client", tag="client_vip")
            
            # Кнопки
            with dpg.group(horizontal=True):
                dpg.add_button(label="Сохранить", tag="client_save", callback=self.save_client, width=100, height=40)
                dpg.add_button(label="Отмена", callback=lambda: dpg.hide_item("client_window"), width=100, height=40)
    
    def create_vehicle_window(self):
        """Окно добавления/редактирования транспортного средства"""
        with dpg.window(label="Транспортное средство", tag="vehicle_window", width=400, height=400, show=False, modal=True):
            dpg.add_text("Данные транспорта")
            
            # Поля для ввода
            dpg.add_input_text(label="ID транспорта##vehicle", tag="vehicle_id", width=300)
            
            dpg.add_combo(label="Тип транспорта##vehicle", tag="vehicle_type", items=["Грузовик", "Поезд", "Фура", "Контейнеровоз"], width=300)
            
            dpg.add_input_float(label="Грузоподъемность (кг)##vehicle", tag="vehicle_capacity", width=300, min_value=1, max_value=50000, format="%.2f")
            dpg.add_tooltip(dpg.last_item(), "Положительное число, не более 50000 кг")
            
            # Кнопки
            with dpg.group(horizontal=True):
                dpg.add_button(label="Сохранить", tag="vehicle_save", callback=self.save_vehicle, width=100, height=40)
                dpg.add_button(label="Отмена", callback=lambda: dpg.hide_item("vehicle_window"), width=100, height=40)
    
    def create_about_window(self):
        """Окно 'О программе'"""
        with dpg.window(label="О программе", tag="about_window", width=400, height=300, show=False, modal=True):
            dpg.add_text("Лабораторная работа по курсу 'Программирование'", color=(255, 255, 0))
            dpg.add_text("Тема: Транспортная компания", color=(200, 200, 255))
            dpg.add_separator()
            dpg.add_text("Номер ЛР: IPO-LR-...")
            dpg.add_text("Вариант: Индивидуальный")
            dpg.add_text("Разработчик: [Ваше ФИО]")
            dpg.add_separator()
            dpg.add_text("© 2024 Все права защищены")
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="Закрыть", callback=lambda: dpg.hide_item("about_window"), width=100, height=40)
    
    def create_export_window(self):
        """Окно экспорта результатов"""
        with dpg.window(label="Экспорт результатов", tag="export_window", width=500, height=300, show=False, modal=True):
            dpg.add_text("Экспорт результатов распределения грузов")
            dpg.add_separator()
            
            dpg.add_radio_button(label="Формат файла", items=["JSON", "CSV", "TXT"], tag="export_format", default_value="JSON")
            
            dpg.add_input_text(label="Имя файла", tag="export_filename", default_value=f"distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="Экспортировать", callback=self.export_results, width=120, height=40)
                dpg.add_button(label="Отмена", callback=lambda: dpg.hide_item("export_window"), width=120, height=40)
    
    def show_client_window(self, edit_index=None):
        """Показать окно клиента"""
        self.current_edit_client_index = edit_index
        
        if edit_index is not None and edit_index < len(self.company.clients):
            client = self.company.clients[edit_index]
            dpg.set_value("client_name", client.name)
            dpg.set_value("client_weight", client.cargo_weight)
            dpg.set_value("client_vip", client.is_vip)
        else:
            dpg.set_value("client_name", "")
            dpg.set_value("client_weight", 0.0)
            dpg.set_value("client_vip", False)
        
        dpg.show_item("client_window")
        dpg.focus_item("client_name")
    
    def show_vehicle_window(self, edit_index=None):
        """Показать окно транспортного средства"""
        self.current_edit_vehicle_index = edit_index
        
        if edit_index is not None and edit_index < len(self.company.vehicles):
            vehicle = self.company.vehicles[edit_index]
            dpg.set_value("vehicle_id", vehicle.vehicle_id)
            dpg.set_value("vehicle_type", getattr(vehicle, 'vehicle_type', 'Грузовик'))
            dpg.set_value("vehicle_capacity", vehicle.capacity)
        else:
            dpg.set_value("vehicle_id", "")
            dpg.set_value("vehicle_type", "Грузовик")
            dpg.set_value("vehicle_capacity", 1000.0)
        
        dpg.show_item("vehicle_window")
        dpg.focus_item("vehicle_id")
    
    def show_export_window(self):
        """Показать окно экспорта"""
        if not self.distribution_results:
            self.show_error("Нет данных для экспорта. Сначала выполните распределение грузов.")
            return
        
        dpg.show_item("export_window")
    
    def validate_client_data(self, name, weight):
        """Валидация данных клиента"""
        if not name or len(name.strip()) < 2:
            return False, "Имя клиента должно содержать минимум 2 символа"
        
        if not name.replace(" ", "").isalpha():
            return False, "Имя клиента должно содержать только буквы"
        
        if weight <= 0:
            return False, "Вес груза должен быть положительным числом"
        
        if weight > 10000:
            return False, "Вес груза не может превышать 10000 кг"
        
        return True, ""
    
    def validate_vehicle_data(self, vehicle_id, capacity):
        """Валидация данных транспортного средства"""
        if not vehicle_id.strip():
            return False, "ID транспорта не может быть пустым"
        
        if capacity <= 0:
            return False, "Грузоподъемность должна быть положительным числом"
        
        # Проверка на уникальность ID
        for i, vehicle in enumerate(self.company.vehicles):
            if i != self.current_edit_vehicle_index and vehicle.vehicle_id == vehicle_id:
                return False, f"Транспорт с ID '{vehicle_id}' уже существует"
        
        return True, ""
    
    def save_client(self):
        """Сохранение клиента"""
        name = dpg.get_value("client_name").strip()
        weight = dpg.get_value("client_weight")
        is_vip = dpg.get_value("client_vip")
        
        # Валидация
        is_valid, error_msg = self.validate_client_data(name, weight)
        if not is_valid:
            self.show_error(error_msg)
            return
        
        try:
            if self.current_edit_client_index is not None:
                # Редактирование существующего клиента
                self.company.clients[self.current_edit_client_index] = Client(name, weight, is_vip)
                self.update_status(f"Клиент '{name}' обновлен")
            else:
                # Добавление нового клиента
                client = Client(name, weight, is_vip)
                self.company.clients.append(client)
                self.update_status(f"Клиент '{name}' добавлен")
            
            self.update_clients_table()
            dpg.hide_item("client_window")
            
        except Exception as e:
            self.show_error(f"Ошибка при сохранении клиента: {str(e)}")
    
    def save_vehicle(self):
        """Сохранение транспортного средства"""
        vehicle_id = dpg.get_value("vehicle_id").strip()
        vehicle_type = dpg.get_value("vehicle_type")
        capacity = dpg.get_value("vehicle_capacity")
        
        # Валидация
        is_valid, error_msg = self.validate_vehicle_data(vehicle_id, capacity)
        if not is_valid:
            self.show_error(error_msg)
            return
        
        try:
            if self.current_edit_vehicle_index is not None:
                # Редактирование существующего транспорта
                vehicle = self.company.vehicles[self.current_edit_vehicle_index]
                vehicle.vehicle_id = vehicle_id
                vehicle.capacity = capacity
                vehicle.vehicle_type = vehicle_type
                self.update_status(f"Транспорт '{vehicle_id}' обновлен")
            else:
                # Добавление нового транспорта
                vehicle = Vehicle(vehicle_id, capacity)
                vehicle.vehicle_type = vehicle_type  # Добавляем тип транспорта
                self.company.vehicles.append(vehicle)
                self.update_status(f"Транспорт '{vehicle_id}' добавлен")
            
            self.update_vehicles_table()
            dpg.hide_item("vehicle_window")
            
        except Exception as e:
            self.show_error(f"Ошибка при сохранении транспорта: {str(e)}")
    
    def optimize_distribution(self):
        """Оптимизация распределения грузов"""
        if not self.company.clients:
            self.show_error("Нет клиентов для распределения")
            return
        
        if not self.company.vehicles:
            self.show_error("Нет транспортных средств для распределения")
            return
        
        try:
            # Выполняем распределение
            self.company.optimize_cargo_distribution()
            
            # Собираем результаты
            self.distribution_results = []
            for vehicle in self.company.vehicles:
                if hasattr(vehicle, 'clients_list') and vehicle.clients_list:
                    for client in vehicle.clients_list:
                        self.distribution_results.append({
                            'client': client.name,
                            'weight': client.cargo_weight,
                            'vehicle': vehicle.vehicle_id,
                            'load': f"{vehicle.current_load}/{vehicle.capacity}"
                        })
            
            # Обновляем таблицы
            self.update_clients_table()
            self.update_vehicles_table()
            self.update_results_table()
            
            self.update_status("Распределение грузов выполнено успешно")
            
        except Exception as e:
            self.show_error(f"Ошибка при распределении грузов: {str(e)}")
    
    def export_results(self):
        """Экспорт результатов в файл"""
        if not self.distribution_results:
            self.show_error("Нет данных для экспорта")
            return
        
        filename = dpg.get_value("export_filename")
        format_type = dpg.get_value("export_format")
        
        if not filename:
            filename = f"distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            if format_type == "JSON":
                filename = filename if filename.endswith('.json') else filename + '.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    export_data = {
                        'company': self.company.name,
                        'timestamp': datetime.now().isoformat(),
                        'results': self.distribution_results,
                        'vehicles': [{
                            'id': v.vehicle_id,
                            'type': getattr(v, 'vehicle_type', 'Не указан'),
                            'capacity': v.capacity,
                            'current_load': v.current_load
                        } for v in self.company.vehicles],
                        'clients': [{
                            'name': c.name,
                            'weight': c.cargo_weight,
                            'is_vip': c.is_vip
                        } for c in self.company.clients]
                    }
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            elif format_type == "CSV":
                filename = filename if filename.endswith('.csv') else filename + '.csv'
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Клиент', 'Вес груза (кг)', 'Транспорт', 'Загрузка'])
                    for result in self.distribution_results:
                        writer.writerow([
                            result['client'],
                            result['weight'],
                            result['vehicle'],
                            result['load']
                        ])
            
            else:  # TXT
                filename = filename if filename.endswith('.txt') else filename + '.txt'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Отчет о распределении грузов\n")
                    f.write(f"Компания: {self.company.name}\n")
                    f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for vehicle in self.company.vehicles:
                        f.write(f"Транспорт: {vehicle.vehicle_id} ({getattr(vehicle, 'vehicle_type', 'Не указан')})\n")
                        f.write(f"Загрузка: {vehicle.current_load}/{vehicle.capacity} кг\n")
                        if hasattr(vehicle, 'clients_list') and vehicle.clients_list:
                            f.write("Клиенты:\n")
                            for client in vehicle.clients_list:
                                f.write(f"  - {client.name}: {client.cargo_weight} кг {'(VIP)' if client.is_vip else ''}\n")
                        f.write("\n")
            
            self.update_status(f"Результаты экспортированы в файл: {filename}")
            dpg.hide_item("export_window")
            
        except Exception as e:
            self.show_error(f"Ошибка при экспорте: {str(e)}")
    
    def update_clients_table(self):
        """Обновление таблицы клиентов"""
        dpg.delete_item(self.clients_table, children_only=True)
        
        for i, client in enumerate(self.company.clients):
            with dpg.table_row(parent=self.clients_table):
                dpg.add_text(client.name)
                dpg.add_text(f"{client.cargo_weight:.2f}")
                dpg.add_text("✓" if client.is_vip else "✗")
    
    def update_vehicles_table(self):
        """Обновление таблицы транспортных средств"""
        dpg.delete_item(self.vehicles_table, children_only=True)
        
        for i, vehicle in enumerate(self.company.vehicles):
            with dpg.table_row(parent=self.vehicles_table):
                dpg.add_text(vehicle.vehicle_id)
                dpg.add_text(getattr(vehicle, 'vehicle_type', 'Грузовик'))
                dpg.add_text(f"{vehicle.capacity:.2f}")
                dpg.add_text(f"{vehicle.current_load:.2f}")
    
    def update_results_table(self):
        """Обновление таблицы результатов"""
        dpg.delete_item(self.results_table, children_only=True)
        
        for result in self.distribution_results:
            with dpg.table_row(parent=self.results_table):
                dpg.add_text(result['client'])
                dpg.add_text(f"{result['weight']:.2f}")
                dpg.add_text(result['vehicle'])
                dpg.add_text(result['load'])
    
    def update_status(self, message, is_error=False):
        """Обновление статусной строки"""
        color = (255, 0, 0) if is_error else (0, 255, 0)
        dpg.set_value(self.status_bar, message)
        dpg.bind_item_theme(self.status_bar, self.create_color_theme(color))
    
    def create_color_theme(self, color):
        """Создание темы с определенным цветом"""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, color)
        return theme
    
    def show_error(self, message):
        """Показать сообщение об ошибке"""
        with dpg.window(label="Ошибка", modal=True, show=True, tag="error_modal", no_title_bar=False):
            dpg.add_text(message, color=(255, 0, 0))
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="OK", width=100, callback=lambda: dpg.delete_item("error_modal"))
    
    def delete_selected(self):
        """Удаление выделенных элементов"""
        # В реальном приложении здесь должна быть логика определения выбранных строк
        # Для примера удалим последний элемент из каждого списка
        if self.company.clients:
            client = self.company.clients.pop()
            self.update_status(f"Клиент '{client.name}' удален")
            self.update_clients_table()
        
        if self.company.vehicles:
            vehicle = self.company.vehicles.pop()
            self.update_status(f"Транспорт '{vehicle.vehicle_id}' удален")
            self.update_vehicles_table()
    
    def clear_all(self):
        """Очистка всех данных"""
        self.company.clients.clear()
        self.company.vehicles.clear()
        self.distribution_results.clear()
        
        self.update_clients_table()
        self.update_vehicles_table()
        dpg.delete_item(self.results_table, children_only=True)
        
        self.update_status("Все данные очищены")
    
    def edit_client(self):
        """Редактирование клиента (по двойному щелчку)"""
        # В реальном приложении здесь должна быть логика определения выбранной строки
        # Для примера редактируем первого клиента
        if self.company.clients:
            self.show_client_window(0)
    
    def edit_vehicle(self):
        """Редактирование транспорта (по двойному щелчку)"""
        # В реальном приложении здесь должна быть логика определения выбранной строки
        # Для примера редактируем первый транспорт
        if self.company.vehicles:
            self.show_vehicle_window(0)
    
    def run(self):
        """Запуск главного цикла"""
        dpg.start_dearpygui()
        dpg.destroy_context()

# Запуск приложения
if __name__ == "__main__":
    # Проверка наличия необходимых модулей
    try:
        import dearpygui.dearpygui as dpg
    except ImportError:
        print("Ошибка: Dear PyGui не установлен.")
        print("Установите его ")
        exit(1)
    
    app = TransportCompanyGUI()
    app.run()