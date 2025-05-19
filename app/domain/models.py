class Aircraft:
    def __init__(self, id, aircraft_type, crew_count, max_takeoff_weight_t,
                 max_landing_weight_t, empty_weight_t, total_fuel_weight_t):
        self.id = id
        self.aircraft_type = aircraft_type
        self.crew_count = crew_count
        self.max_takeoff_weight_t = max_takeoff_weight_t
        self.max_landing_weight_t = max_landing_weight_t
        self.empty_weight_t = empty_weight_t
        self.total_fuel_weight_t = total_fuel_weight_t


class Account:
    def __init__(self, id, username, email, role, is_active):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active


class Flight:
    def __init__(self, id, date, aircraft_id, route_countries, route_airports,
                 max_commercial_load, flight_cost, calculation_date, aircraft_type, account_id):
        self.id = id
        self.date = date
        self.aircraft_id = aircraft_id
        self.route_countries = route_countries
        self.route_airports = route_airports
        self.max_commercial_load = max_commercial_load
        self.flight_cost = flight_cost
        self.calculation_date = calculation_date
        self.aircraft_type = aircraft_type
        self.account_id = account_id


class FlightCalculation:
    def __init__(self, flight_id, distance_km, speed_kmh, fuel_consumption_per_hour_t,
                 fuel_price_per_t, aircraft_rent_cost, takeoff_landing_cost,
                 maintenance_cost, parking_cost, catering_count, catering_price_per_meal,
                 crew_daily_allowance, support_cost, navigation_fees,
                 accommodation_cost, miscellaneous_cost, declared_flight_price):
        self.flight_id = flight_id
        self.distance_km = distance_km
        self.speed_kmh = speed_kmh
        self.fuel_consumption_per_hour_t = fuel_consumption_per_hour_t
        self.fuel_price_per_t = fuel_price_per_t
        self.aircraft_rent_cost = aircraft_rent_cost
        self.takeoff_landing_cost = takeoff_landing_cost
        self.maintenance_cost = maintenance_cost
        self.parking_cost = parking_cost
        self.catering_count = catering_count
        self.catering_price_per_meal = catering_price_per_meal
        self.crew_daily_allowance = crew_daily_allowance
        self.support_cost = support_cost
        self.navigation_fees = navigation_fees
        self.accommodation_cost = accommodation_cost
        self.miscellaneous_cost = miscellaneous_cost
        self.declared_flight_price = declared_flight_price

    def calculate_total_cost(self):
        fuel_cost = self.fuel_consumption_per_hour_t * self.fuel_price_per_t
        catering_total = self.catering_count * self.catering_price_per_meal
        return (
            fuel_cost +
            self.aircraft_rent_cost +
            self.takeoff_landing_cost +
            self.maintenance_cost +
            self.parking_cost +
            catering_total +
            self.crew_daily_allowance +
            self.support_cost +
            self.navigation_fees +
            self.accommodation_cost +
            self.miscellaneous_cost
        )
