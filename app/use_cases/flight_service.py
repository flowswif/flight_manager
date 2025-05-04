# Глобальная переменная для хранения последнего курса
import requests
from xml.etree import ElementTree as ET

last_usd_to_rub_rate = None
def calculate_flight_time(distance, speed):
    try:
        distance = float(distance)
        speed = float(speed)
        if speed > 0:
            return distance / speed
    except ValueError:
        return None
    return None

def get_usd_to_rub_rate():
    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    response = requests.get(url)
    if response.status_code == 200:
        xml_data = ET.fromstring(response.content)
        for currency in xml_data.findall("Valute"):
            if currency.find("CharCode").text == "USD":
                return float(currency.find("Value").text.replace(",", "."))
    return None

def calculate_fuel_consumption(time, consumption):
    try:
        time = float(time)
        consumption = float(consumption)
        if consumption > 0:
            return time * consumption
    except ValueError:
        return None
    return None

def calculate_refueled_fuel(initial_fuel, fuel_consumption, residual_fuel):
    try:
        initial_fuel = float(initial_fuel)
        fuel_consumption = float(fuel_consumption)
        residual_fuel = float(residual_fuel)
        return fuel_consumption + residual_fuel - initial_fuel
    except ValueError:
        return None

def calculate_landing_fuel_residual(initial_fuel, fuel_consumption, refueled_fuel):
    try:
        initial_fuel = float(initial_fuel)
        fuel_consumption = float(fuel_consumption)
        refueled_fuel = float(refueled_fuel)
        return refueled_fuel + initial_fuel - fuel_consumption
    except ValueError:
        return None

def calculate_takeoff_weight(initial_fuel, empty_weight, refueled_fuel, commercial_load):
    try:
        initial_fuel = float(initial_fuel)
        empty_weight = float(empty_weight)
        refueled_fuel = float(refueled_fuel)
        commercial_load = float(commercial_load)
        return refueled_fuel + initial_fuel + empty_weight + commercial_load
    except ValueError:
        return None

def calculate_takeoff_overweight(max_takeoff_weight, takeoff_weight):
    try:
        max_takeoff_weight = float(max_takeoff_weight)
        takeoff_weight = float(takeoff_weight)
        return max(0, takeoff_weight - max_takeoff_weight)
    except ValueError:
        return None

def calculate_landing_weight(takeoff_weight, fuel_consumption):
    try:
        takeoff_weight = float(takeoff_weight)
        fuel_consumption = float(fuel_consumption)
        return takeoff_weight - fuel_consumption
    except ValueError:
        return None

def calculate_landing_overweight(max_landing_weight, landing_weight):
    try:
        max_landing_weight = float(max_landing_weight)
        landing_weight = float(landing_weight)
        return max(0, landing_weight - max_landing_weight)
    except ValueError:
        return None

def calculate_aircraft_rent_cost(flight_time, price_per_hour_usd):
    try:
        flight_time = float(flight_time)
        price_per_hour_usd = float(price_per_hour_usd)
        return flight_time * price_per_hour_usd
    except ValueError:
        return None

def calculate_fuel_cost(fuel_price_per, refueled_fuel):
    try:
        fuel_price_per = float(fuel_price_per)
        refueled_fuel = float(refueled_fuel)
        return fuel_price_per * refueled_fuel
    except ValueError:
        return None

def calculate_catering_price_per_meal(crew_count, price_per_serving, catering_count):
    try:
        crew_count = float(crew_count)
        price_per_serving = float(price_per_serving)
        catering_count = float(catering_count)
        return crew_count * price_per_serving * catering_count
    except ValueError:
        return None

def calculate_navigation_fees(distance):
    try:
        distance = float(distance)
        return distance * 1.2
    except ValueError:
        return None

def calculate_total_cost(aircraft_rent_cost, fuel_cost, takeoff_landing_cost, maintenance_cost, parking_cost, catering_price_per_meal, crew_daily_allowance, support_cost, navigation_fees, accommodation_cost, miscellaneous_cost):
    try:
        # Преобразование строк в числа с плавающей запятой
        costs = [
            float(aircraft_rent_cost), 
            float(fuel_cost), 
            float(takeoff_landing_cost), 
            float(maintenance_cost), 
            float(parking_cost), 
            float(catering_price_per_meal), 
            float(crew_daily_allowance), 
            float(support_cost), 
            float(navigation_fees), 
            float(accommodation_cost), 
            float(miscellaneous_cost)
        ]
        
        return sum(costs)
    
    except ValueError:
        # В случае ошибки преобразования, возвращаем None
        return None

def calculate_declared_flight_price(total_cost):
    try:
        total_cost = float(total_cost)
        return total_cost * 1.2
    except ValueError:
        return None

def calculate_declared_flight_price_rub(declared_flight_price):
    try:
        declared_flight_price = float(declared_flight_price)
        usd_to_rub_rate = get_usd_to_rub_rate()
        if usd_to_rub_rate:
            return declared_flight_price * usd_to_rub_rate
    except ValueError:
        return None
    return None