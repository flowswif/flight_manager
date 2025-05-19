from app.domain.models import FlightCalculation

class FlightCalculatorService:
    def __init__(self, calculation: FlightCalculation):
        self.calculation = calculation

    def calculate_total(self):
        return self.calculation.calculate_total_cost()
