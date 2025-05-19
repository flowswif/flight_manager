import requests
from xml.etree import ElementTree as ET

from app.domain.models import FlightCalculation
from app.services.flight_calculator import FlightCalculatorService


class FlightComputationService:
    def __init__(self):
        self.last_usd_to_rub_rate = None

    def run_calculation(self, flight_data):
        calculation = FlightCalculation(**flight_data)
        service = FlightCalculatorService(calculation)
        return service.calculate_total()

    def get_usd_to_rub_rate(self):
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        response = requests.get(url)
        if response.status_code == 200:
            xml_data = ET.fromstring(response.content)
            for currency in xml_data.findall("Valute"):
                if currency.find("CharCode").text == "USD":
                    return float(currency.find("Value").text.replace(",", "."))
        return None

    def calculate_flight_time(self, distance, speed):
        try:
            return float(distance) / float(speed) if float(speed) > 0 else None
        except ValueError:
            return None

    def calculate_fuel_consumption(self, time, consumption):
        try:
            return float(time) * float(consumption)
        except ValueError:
            return None

    def calculate_refueled_fuel(self, initial_fuel, fuel_consumption, residual_fuel):
        try:
            return float(fuel_consumption) + float(residual_fuel) - float(initial_fuel)
        except ValueError:
            return None

    def calculate_landing_fuel_residual(self, initial_fuel, fuel_consumption, refueled_fuel):
        try:
            return float(refueled_fuel) + float(initial_fuel) - float(fuel_consumption)
        except ValueError:
            return None

    def calculate_takeoff_weight(self, initial_fuel, empty_weight, refueled_fuel, commercial_load):
        try:
            return sum(map(float, [initial_fuel, empty_weight, refueled_fuel, commercial_load]))
        except ValueError:
            return None

    def calculate_takeoff_overweight(self, max_takeoff_weight, takeoff_weight):
        try:
            return max(0, float(takeoff_weight) - float(max_takeoff_weight))
        except ValueError:
            return None

    def calculate_landing_weight(self, takeoff_weight, fuel_consumption):
        try:
            return float(takeoff_weight) - float(fuel_consumption)
        except ValueError:
            return None

    def calculate_landing_overweight(self, max_landing_weight, landing_weight):
        try:
            return max(0, float(landing_weight) - float(max_landing_weight))
        except ValueError:
            return None

    def calculate_aircraft_rent_cost(self, flight_time, price_per_hour_usd):
        try:
            return float(flight_time) * float(price_per_hour_usd)
        except ValueError:
            return None

    def calculate_fuel_cost(self, fuel_price_per, refueled_fuel):
        try:
            return float(fuel_price_per) * float(refueled_fuel)
        except ValueError:
            return None

    def calculate_catering_price(self, crew_count, price_per_serving, catering_count):
        try:
            return float(crew_count) * float(price_per_serving) * float(catering_count)
        except ValueError:
            return None

    def calculate_navigation_fees(self, distance):
        try:
            return float(distance) * 1.2
        except ValueError:
            return None

    def calculate_total_cost(self, *costs):
        try:
            return sum(map(float, costs))
        except ValueError:
            return None

    def calculate_declared_flight_price(self, total_cost):
        try:
            return float(total_cost) * 1.2
        except ValueError:
            return None

    def calculate_declared_price_rub(self, declared_price_usd):
        try:
            rate = self.get_usd_to_rub_rate()
            return float(declared_price_usd) * rate if rate else None
        except ValueError:
            return None
