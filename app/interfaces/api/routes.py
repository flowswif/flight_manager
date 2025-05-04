from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, send_file
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from xml.etree import ElementTree as ET
import secrets
import smtplib
from email.mime.text import MIMEText
import ssl
import pandas as pd
from werkzeug.security import generate_password_hash
from datetime import datetime
import logging
from app.interfaces.repo.mysql_repo import create_connection

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def register_routes(app):
    app.secret_key = 'secretkey'
    @app.route('/')
    def home():
        if 'loggedin' not in session:
            return redirect(url_for('login'))

        role = session.get('role', 'guest')  # По умолчанию роль 'guest'

        conn = create_connection()
        cur = conn.cursor()

        search_query = request.args.get('search_query', '')  # Поиск по ключевым словам

        try:
            query = "SELECT * FROM flights WHERE 1=1"
            params = []

            if search_query:
                query += " AND (aircraft LIKE %s OR route_countries LIKE %s OR route_airports LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

            cur.execute(query, params)
            flights = cur.fetchall()
        except Exception as e:
            flash(f"Ошибка при получении данных: {str(e)}", "danger")
            flights = []
        finally:
            cur.close()
            conn.close()

        return render_template('index.html', username=session['username'], role=role, flights=flights, search_query=search_query)

    @app.route('/accounts')
    def accounts():
        if 'loggedin' not in session:
            return redirect(url_for('login'))

        user_id = session.get('id')  # Получаем ID текущего пользователя
        role = session.get('role', 'guest')

        conn = create_connection()
        cur = conn.cursor()

        user = None
        users = []  # Список всех пользователей (только для админов)

        try:
            # Получаем данные о текущем пользователе
            query = "SELECT id, username, email, password FROM accounts WHERE id = %s"
            cur.execute(query, (user_id,))
            user = cur.fetchone()

            # Если админ, загружаем также всех пользователей
            if role == 'admin':
                query = "SELECT id, username, email, role, registration_date, password FROM accounts"
                cur.execute(query)
                users = cur.fetchall()
                
        except Exception as e:
            flash(f"Ошибка при получении данных: {str(e)}", "danger")
        finally:
            cur.close()
            conn.close()

        return render_template('accounts.html', user=user, users=users, role=role)

    @app.route('/aircrafts')
    def aircrafts():
        if 'loggedin' not in session:
            return redirect(url_for('login'))

        role = session.get('role', 'guest')

        conn = create_connection()
        cur = conn.cursor()

        search_query = request.args.get('search_query', '')

        try:
            query = """
                SELECT aircraft, aircraft_type, crew_count, max_takeoff_weight_t, 
                    max_landing_weight_t, empty_weight_t, total_fuel_weight_t
                FROM aircrafts
                WHERE 1=1
            """
            params = []

            if search_query:
                query += " AND (aircraft LIKE %s OR aircraft_type LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            cur.execute(query, params)
            aircrafts = cur.fetchall()
        except Exception as e:
            flash(f"Ошибка при получении данных: {str(e)}", "danger")
            aircrafts = []
        finally:
            cur.close()
            conn.close()

        return render_template(
            'crud_aircrafts/aircraft.html',
            username=session['username'],
            role=role,
            aircrafts=aircrafts,
            search_query=search_query
        )
        


    @app.route('/aircrafts/add', methods=['GET', 'POST'])
    def add_aircraft():
        if 'loggedin' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            aircraft = request.form['aircraft']
            aircraft_type = request.form['aircraft_type']
            crew_count = request.form['crew_count']
            max_takeoff_weight_t = request.form['max_takeoff_weight_t']
            max_landing_weight_t = request.form['max_landing_weight_t']
            empty_weight_t = request.form['empty_weight_t']
            total_fuel_weight_t = request.form['total_fuel_weight_t']

            conn = create_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO aircrafts (aircraft, aircraft_type, crew_count, max_takeoff_weight_t, max_landing_weight_t, empty_weight_t, total_fuel_weight_t)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (aircraft, aircraft_type, crew_count, max_takeoff_weight_t, max_landing_weight_t, empty_weight_t, total_fuel_weight_t))
                conn.commit()
                flash('Самолет успешно добавлен!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f"Ошибка при добавлении самолета: {str(e)}", 'danger')
            finally:
                cur.close()
                conn.close()
            return redirect(url_for('aircrafts'))

        return render_template('crud_aircrafts/add_aircraft.html')

    @app.route('/aircrafts/edit/<string:aircraft>', methods=['GET', 'POST'])
    def edit_aircraft(aircraft):
        if 'loggedin' not in session:
            return redirect(url_for('login'))

        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM aircrafts WHERE aircraft = %s", (aircraft,))
        aircraft_data = cur.fetchone()

        if request.method == 'POST':
            aircraft_type = request.form['aircraft_type']
            crew_count = request.form['crew_count']
            max_takeoff_weight_t = request.form['max_takeoff_weight_t']
            max_landing_weight_t = request.form['max_landing_weight_t']
            empty_weight_t = request.form['empty_weight_t']
            total_fuel_weight_t = request.form['total_fuel_weight_t']

            try:
                cur.execute("""
                    UPDATE aircrafts
                    SET aircraft_type = %s, crew_count = %s, max_takeoff_weight_t = %s, max_landing_weight_t = %s, empty_weight_t = %s, total_fuel_weight_t = %s
                    WHERE aircraft = %s
                """, (aircraft_type, crew_count, max_takeoff_weight_t, max_landing_weight_t, empty_weight_t, total_fuel_weight_t, aircraft))
                conn.commit()
                flash('Данные самолета обновлены!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f"Ошибка при обновлении данных: {str(e)}", 'danger')
            finally:
                cur.close()
                conn.close()
            return redirect(url_for('aircrafts'))

        cur.close()
        conn.close()

        return render_template('crud_aircrafts/edit_aircraft.html', aircraft=aircraft_data)

    @app.route('/aircrafts/delete/<string:aircraft>')
    def delete_aircraft(aircraft):
        if 'loggedin' not in session:
            return redirect(url_for('login'))

        conn = create_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM aircrafts WHERE aircraft = %s", (aircraft,))
            conn.commit()
            flash('Самолет удален!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f"Ошибка при удалении самолета: {str(e)}", 'danger')
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('aircrafts'))

    @app.route('/update_role/<int:id>', methods=['POST'])
    def update_role(id):
        if 'loggedin' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))

        conn = create_connection()
        cur = conn.cursor()
        accounts = None  # Инициализация переменной

        try:
            # Получение данных из формы
            new_role = request.form.get('role')

            # Обновление роли пользователя
            cur.execute("""
                UPDATE accounts 
                SET role = %s
                WHERE id = %s
            """, (new_role, id))
            conn.commit()
            flash(f"Роль пользователя обновлена на {new_role}", "success")
        except Exception as e:
            import logging
            logging.error(f"Ошибка при обновлении роли: {str(e)}")
            flash(f"Ошибка при обновлении роли: {str(e)}", "danger")
        finally:
            cur.close()
            conn.close()

        # Отображение формы редактирования
        try:
            cur = conn.cursor()  # Создаем новый курсор
            cur.execute("SELECT * FROM accounts WHERE id = %s", (id,))
            accounts = cur.fetchone()
        except Exception as e:
            print(f"Error fetching flight details: {e}")
            accounts = None
        finally:
            cur.close()
            if conn and conn.open:
                conn.close()

        return redirect(url_for('accounts', accounts=accounts))

    @app.route('/delete_user/<int:id>', methods=['POST'])
    def delete_user(id):
        if 'loggedin' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))

        conn = create_connection()
        cur = conn.cursor()

        try:
            cur.execute("DELETE FROM accounts WHERE id = %s", (id,))
            conn.commit()
            flash(f"Пользователь с ID {id} удалён", "success")
        except Exception as e:
            flash(f"Ошибка при удалении пользователя: {str(e)}", "danger")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('accounts'))

    # Добавление рейса
    @app.route('/add', methods=['GET', 'POST'])
    def add_flight():
        if 'loggedin' in session and session['role'] == 'admin':
            conn = create_connection()
            cur = conn.cursor()

            if request.method == 'POST':
                # Получение данных из формы
                flight_data = {
                    'date': request.form.get('date'),
                    'aircraft': request.form.get('aircraft'),
                    'route_countries': request.form.get('route_countries'),
                    'route_airports': request.form.get('route_airports'),
                    'max_commercial_load': request.form.get('max_commercial_load'),
                    'flight_cost': request.form.get('flight_cost'),
                    'calculation_date': request.form.get('calculation_date'),
                    'aircraft_type': request.form.get('aircraft_type')
                }
                calculation_data = {
                    'distance_km': request.form.get('distance_km'),
                    'speed_kmh': request.form.get('speed_kmh'),
                    'flight_time_h': request.form.get('flight_time_h'),
                    'fuel_consumption_per_hour_t': request.form.get('fuel_consumption_per_hour_t'),
                    'fuel_consumption_t': request.form.get('fuel_consumption_t'),
                    'required_residual_fuel_t': request.form.get('required_residual_fuel_t'),
                    'refueled_fuel_t': request.form.get('refueled_fuel_t'),
                    'landing_fuel_residual_t': request.form.get('landing_fuel_residual_t'),
                    'takeoff_weight_t': request.form.get('takeoff_weight_t'),
                    'takeoff_overweight_t': request.form.get('takeoff_overweight_t'),
                    'landing_weight_t': request.form.get('landing_weight_t'),
                    'landing_overweight_t': request.form.get('landing_overweight_t'),
                    'aircraft_rent_cost': request.form.get('aircraft_rent_cost'),
                    'fuel_price_per_t': request.form.get('fuel_price_per_t'),
                    'fuel_cost': request.form.get('fuel_cost'),
                    'takeoff_landing_cost': request.form.get('takeoff_landing_cost'),
                    'maintenance_cost': request.form.get('maintenance_cost'),
                    'parking_cost': request.form.get('parking_cost'),
                    'catering_count': request.form.get('catering_count'),
                    'catering_price_per_meal': request.form.get('catering_price_per_meal'),
                    'crew_daily_allowance': request.form.get('crew_daily_allowance'),
                    'support_cost': request.form.get('support_cost'),
                    'navigation_fees': request.form.get('navigation_fees'),
                    'accommodation_cost': request.form.get('accommodation_cost'),
                    'miscellaneous_cost': request.form.get('miscellaneous_cost'),
                    'total_cost': request.form.get('total_cost'),
                    'declared_flight_price': request.form.get('declared_flight_price'),
                    'crew_count': request.form.get('crew_count'),
                    'max_takeoff_weight_t': request.form.get('max_takeoff_weight_t'),
                    'max_landing_weight_t': request.form.get('max_landing_weight_t'),
                    'empty_weight_t': request.form.get('empty_weight_t'),
                    'total_fuel_weight_t': request.form.get('total_fuel_weight_t'),
                    'performed_by': session['username'],
                    'initial_fuel_t': request.form.get('initial_fuel_t'),
                    'price_per_hour_usd': request.form.get('price_per_hour_usd'),
                    'note': request.form.get('note'),
                    'price_per_serving': request.form.get('price_per_serving'),
                    'declared_flight_price_rub': request.form.get('declared_flight_price_rub')
                }

                        # Рассчитать flight_time_h
                if calculation_data['distance_km'] and calculation_data['speed_kmh']:
                    calculation_data['flight_time_h'] = calculate_flight_time(
                        calculation_data['distance_km'], calculation_data['speed_kmh']
                    )
                if calculation_data['flight_time_h'] and calculation_data['fuel_consumption_per_hour_t']:
                    calculation_data['fuel_consumption_t'] = calculate_fuel_consumption(
                        calculation_data['flight_time_h'], calculation_data['fuel_consumption_per_hour_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['fuel_consumption_t'] and calculation_data['required_residual_fuel_t']:
                    calculation_data['refueled_fuel_t'] = calculate_refueled_fuel(
                        calculation_data['initial_fuel_t'], calculation_data['fuel_consumption_t'], calculation_data['required_residual_fuel_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['fuel_consumption_t'] and calculation_data['refueled_fuel_t']:
                    calculation_data['landing_fuel_residual_t'] = calculate_landing_fuel_residual(
                        calculation_data['initial_fuel_t'], calculation_data['fuel_consumption_t'], calculation_data['refueled_fuel_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['refueled_fuel_t'] and calculation_data['empty_weight_t'] and flight_data['max_commercial_load']:
                    calculation_data['takeoff_weight_t'] = calculate_takeoff_weight(
                        calculation_data['initial_fuel_t'], calculation_data['refueled_fuel_t'], calculation_data['empty_weight_t'], flight_data['max_commercial_load']
                    )
                if calculation_data['max_takeoff_weight_t'] and calculation_data['takeoff_weight_t']:
                    calculation_data['takeoff_overweight_t'] = calculate_takeoff_overweight(
                        calculation_data['max_takeoff_weight_t'], calculation_data['takeoff_weight_t']
                    )   
                if calculation_data['takeoff_weight_t'] and calculation_data['fuel_consumption_t']:
                    calculation_data['landing_weight_t'] = calculate_landing_weight(
                        calculation_data['takeoff_weight_t'], calculation_data['fuel_consumption_t']
                    ) 
                if calculation_data['max_landing_weight_t'] and calculation_data['landing_weight_t']:
                    calculation_data['landing_overweight_t'] = calculate_landing_overweight(
                        calculation_data['max_landing_weight_t'], calculation_data['landing_weight_t']
                    )
                if calculation_data['price_per_hour_usd'] and calculation_data['flight_time_h']:
                    calculation_data['aircraft_rent_cost'] = calculate_aircraft_rent_cost(
                        calculation_data['price_per_hour_usd'], calculation_data['flight_time_h']
                    )  
                if calculation_data['fuel_price_per_t'] and calculation_data['refueled_fuel_t']:
                    calculation_data['fuel_cost'] = calculate_fuel_cost(
                        calculation_data['fuel_price_per_t'], calculation_data['refueled_fuel_t']
                    )  
                if calculation_data['crew_count'] and calculation_data['price_per_serving'] and calculation_data['catering_count']:
                    calculation_data['catering_price_per_meal'] = calculate_catering_price_per_meal(
                        calculation_data['crew_count'], calculation_data['price_per_serving'], calculation_data['catering_count']
                    )      
                if calculation_data['distance_km']:
                    calculation_data['navigation_fees'] = calculate_navigation_fees(
                        calculation_data['distance_km'] 
                    )   
                if calculation_data['aircraft_rent_cost'] and calculation_data['fuel_cost'] and calculation_data['takeoff_landing_cost'] and calculation_data['maintenance_cost'] and calculation_data['parking_cost'] and calculation_data['catering_price_per_meal'] and calculation_data['crew_daily_allowance'] and calculation_data['support_cost'] and calculation_data['navigation_fees'] and calculation_data['accommodation_cost'] and calculation_data['miscellaneous_cost']:
                    calculation_data['total_cost'] = calculate_total_cost(
                        calculation_data['aircraft_rent_cost'], calculation_data['fuel_cost'], calculation_data['takeoff_landing_cost'], calculation_data['maintenance_cost'], calculation_data['parking_cost'], calculation_data['catering_price_per_meal'], calculation_data['crew_daily_allowance'], calculation_data['support_cost'], calculation_data['navigation_fees'], calculation_data['accommodation_cost'], calculation_data['miscellaneous_cost']
                    )
                if calculation_data['total_cost']:
                    calculation_data['declared_flight_price'] = calculate_declared_flight_price(
                        calculation_data['total_cost']
                    )
                if calculation_data['declared_flight_price']:
                    calculation_data['declared_flight_price_rub'] = calculate_declared_flight_price_rub(
                        calculation_data['declared_flight_price']
                    )
                flight_data['flight_cost'] = calculation_data['total_cost']

                try:
                    # Добавление рейса
                    cur.execute("""
                        INSERT INTO flights (date, aircraft, route_countries, route_airports,
                                            max_commercial_load, flight_cost, calculation_date, aircraft_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(flight_data.values()))

                    flight_id = cur.lastrowid  # Получение ID добавленного рейса

                    # Добавление данных калькуляции
                    cur.execute("""
                        INSERT INTO flight_calculations (flight_id, distance_km, speed_kmh, flight_time_h,
                                                        fuel_consumption_per_hour_t, fuel_consumption_t,
                                                        required_residual_fuel_t, refueled_fuel_t,
                                                        landing_fuel_residual_t, takeoff_weight_t,
                                                        takeoff_overweight_t, landing_weight_t, landing_overweight_t,
                                                        aircraft_rent_cost, fuel_price_per_t, fuel_cost,
                                                        takeoff_landing_cost, maintenance_cost, parking_cost,
                                                        catering_count, catering_price_per_meal, crew_daily_allowance,
                                                        support_cost, navigation_fees, accommodation_cost,
                                                        miscellaneous_cost, total_cost, declared_flight_price,
                                                        crew_count, max_takeoff_weight_t, max_landing_weight_t,
                                                        empty_weight_t, total_fuel_weight_t, performed_by,
                                                        initial_fuel_t, price_per_hour_usd, note, price_per_serving, declared_flight_price_rub)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (flight_id, *calculation_data.values()))

                    conn.commit()
                    return redirect(url_for('home'))
                except Exception as e:
                    print(f"Error adding flight and calculations: {e}")
                    conn.rollback()
                finally:
                    cur.close()
                    conn.close()


            return render_template('crud/add_flight.html')
        # Перенесено выше — создание соединения перед выполнением SQL-запроса
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT aircraft FROM aircrafts")
        aircrafts = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return redirect(url_for('home'), aircrafts=aircrafts)

    @app.route('/get_aircraft_info')
    def get_aircraft_info():
        aircraft_name = request.args.get('aircraft')
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT aircraft_type, crew_count, max_takeoff_weight_t, max_landing_weight_t, empty_weight_t, total_fuel_weight_t
            FROM aircrafts
            WHERE aircraft = %s
        """, (aircraft_name,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        return jsonify(result)



    # Расчет для времени в полете (расстояние (км) / скорость ВС (км/ч))
    @app.route('/calculate_flight_time', methods=['POST'])
    def calculate_flight_time():
        data = request.get_json()
        distance = data.get('distance') # расстояние (км)
        speed = data.get('speed') # скорость ВС (км/ч)
        if distance and speed and speed > 0:
            flight_time = distance / speed # формула
            return jsonify({"flight_time": flight_time})
        return jsonify({"error": "Invalid input"}), 400 
    # Вывод курса доллара к рублю через ЦБР xml
    @app.route('/get_usd_to_rub_rate', methods=['POST'])
    def get_usd_to_rub_rate():
        global last_usd_to_rub_rate
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            xml_data = ET.fromstring(response.content)
            for currency in xml_data.findall("Valute"):
                if currency.find("CharCode").text == "USD":
                    last_usd_to_rub_rate = float(currency.find("Value").text.replace(",", "."))
                    return jsonify({"Курс USD": last_usd_to_rub_rate})
            return jsonify({"error": "USD rate not found"}), 404
        except (requests.RequestException, ET.ParseError):
            if last_usd_to_rub_rate is not None:
                return jsonify({"Курс USD (последний сохраненный)": last_usd_to_rub_rate})
            return jsonify({"error": "Failed to fetch data from CBR and no saved rate"}), 500

    @app.route('/calculate_fuel_consumption', methods=['POST'])
    def calculate_fuel_consumption():
        data = request.get_json()
        time = data.get('time')
        consumption = data.get('consumption')
        if time and consumption and consumption > 0:
            fuel_consumption = time * consumption
            return jsonify({"fuel_consumption": fuel_consumption})
        return jsonify({"error": "Invalid input"}), 400
    # Расчет 
    @app.route('/calculate_refueled_fuel', methods=['POST'])
    def calculate_refueled_fuel():
        data = request.get_json()
        initial_fuel = data.get('initial_fuel')
        fuel_consumption = data.get('fuel_consumption')
        residual_fuel = data.get('residual_fuel')
        if initial_fuel and fuel_consumption and residual_fuel:
            refueled_fuel = fuel_consumption + residual_fuel - initial_fuel
            return jsonify({"refueled_fuel": refueled_fuel})
        return jsonify({"error": "Invalid input"}), 400

    @app.route('/calculate_landing_fuel_residual', methods=['POST'])
    def calculate_landing_fuel_residual():
        data = request.get_json()
        print("Received data for landing_fuel_residual:", data)
        initial_fuel = data.get('initial_fuel')
        fuel_consumption = data.get('fuel_consumption')
        refueled_fuel = data.get('refueled_fuel')
        if initial_fuel and fuel_consumption and refueled_fuel:
            landing_fuel_residual = refueled_fuel + initial_fuel - fuel_consumption
            return jsonify({"landing_fuel_residual": landing_fuel_residual})
        print("Invalid input for landing_fuel_residual")
        return jsonify({"error": "Invalid input"}), 400

    @app.route('/calculate_takeoff_weight', methods=['POST'])
    def calculate_takeoff_weight():
        data = request.get_json()
        initial_fuel = data.get('initial_fuel')
        empty_weight = data.get('empty_weight')
        refueled_fuel = data.get('refueled_fuel')
        commercial_load = data.get('commercial_load')
        if initial_fuel and empty_weight and refueled_fuel and commercial_load:
            takeoff_weight = refueled_fuel + initial_fuel + empty_weight + commercial_load
            return jsonify({"takeoff_weight": takeoff_weight})
        return jsonify({"error": "Invalid input"}), 400

    @app.route('/calculate_takeoff_overweight', methods=['POST'])
    def calculate_takeoff_overweight():
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        try:
            max_takeoff_weight = float(data.get('max_takeoff_weight', 0))
            takeoff_weight = float(data.get('takeoff_weight', 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid data format"}), 400

        if max_takeoff_weight < 0 or takeoff_weight < 0:
            return jsonify({"error": "Weights must be greater than 0"}), 400

        if takeoff_weight < max_takeoff_weight:
            return jsonify({"takeoff_overweight": 0})  # Возвращаем JSON, а не просто 0
        
        return jsonify({"takeoff_overweight": takeoff_weight - max_takeoff_weight})  # Исправлен расчет

    @app.route('/calculate_landing_weight', methods=['POST'])
    def calculate_landing_weight():
        data = request.get_json()
        takeoff_weight = data.get('takeoff_weight')
        fuel_consumption = data.get('fuel_consumption')
        if takeoff_weight and fuel_consumption:
            landing_weight = takeoff_weight - fuel_consumption
            return jsonify({"landing_weight": landing_weight})
        return jsonify({"error": "Invalid input"}), 400

    @app.route('/calculate_landing_overweight', methods=['POST'])
    def calculate_landing_overweight():
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        try:
            max_landing_weight = float(data.get('max_landing_weight', 0))
            landing_weight = float(data.get('landing_weight', 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid data format"}), 400

        if max_landing_weight < 0 or landing_weight < 0:
            return jsonify({"error": "Weights must be greater than 0"}), 400

        if landing_weight < max_landing_weight:
            return jsonify({"landing_overweight": 0})  # Возвращаем JSON, а не просто 0
        
        return jsonify({"landing_overweight": landing_weight - max_landing_weight})  # Исправлен расчет

    @app.route('/calculate_aircraft_rent_cost', methods=['POST'])
    def calculate_aircraft_rent_cost():
        data = request.get_json()
        flight_time = data.get('flight_time')
        price_per_hour_usd = data.get('price_per_hour_usd')
        if price_per_hour_usd and flight_time:
            aircraft_rent_cost = price_per_hour_usd * flight_time
            return jsonify({"aircraft_rent_cost": aircraft_rent_cost})
        return jsonify({"error": "Invalid input"}), 400

    @app.route('/calculate_fuel_cost', methods=['POST'])
    def calculate_fuel_cost():
        data = request.get_json()
        fuel_price_per = data.get('fuel_price_per')
        refueled_fuel = data.get('refueled_fuel')
        if fuel_price_per and refueled_fuel:
            fuel_cost = fuel_price_per * refueled_fuel
            return jsonify({"fuel_cost": fuel_cost})
        return jsonify({"error": "Invalid input"}), 400

    @app.route('/calculate_catering_price_per_meal', methods=['POST'])
    def calculate_catering_price_per_meal():
        data = request.get_json()
        crew_count = data.get('crew_count')
        price_per_serving = data.get('price_per_serving')
        catering_count= data.get('catering_count')
        if price_per_serving and crew_count and catering_count:
            catering_price_per_meal = crew_count * price_per_serving * catering_count
            return jsonify({"catering_price_per_meal": catering_price_per_meal})
        return jsonify({"error": "Invalid input"}), 400

    @app.route('/calculate_navigation_fees', methods=['POST'])
    def calculate_navigation_fees():
        data = request.get_json()
        distance = data.get('distance')
        if distance:
            navigation_fees = distance * 1.2
            return jsonify({"navigation_fees": navigation_fees})
        return jsonify({"error": "Invalid input"}), 400

    @app.route('/calculate_total_cost', methods=['POST'])
    def calculate_total_cost():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Нет данных"}), 400

        # Используем .get() с `0` по умолчанию, чтобы избежать ошибок
        try:
            aircraft_rent_cost = float(data.get('aircraft_rent_cost', 0))
            fuel_cost = float(data.get('fuel_cost', 0))
            takeoff_landing_cost = float(data.get('takeoff_landing_cost', 0))
            maintenance_cost = float(data.get('maintenance_cost', 0))
            parking_cost = float(data.get('parking_cost', 0))
            catering_price_per_meal = float(data.get('catering_price_per_meal', 0))
            crew_daily_allowance = float(data.get('crew_daily_allowance', 0))
            support_cost = float(data.get('support_cost', 0))
            navigation_fees = float(data.get('navigation_fees', 0))
            accommodation_cost = float(data.get('accommodation_cost', 0))
            miscellaneous_cost = float(data.get('miscellaneous_cost', 0))

            total_cost = (
                aircraft_rent_cost + fuel_cost + takeoff_landing_cost +
                maintenance_cost + parking_cost + catering_price_per_meal +
                crew_daily_allowance + support_cost + navigation_fees +
                accommodation_cost + miscellaneous_cost
            )

            return jsonify({"total_cost": total_cost})

        except ValueError:
            return jsonify({"error": "Некорректные данные"}), 400

    @app.route('/calculate_declared_flight_price', methods=['POST'])
    def calculate_declared_flight_price():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Нет данных"}), 400

        # Используем .get() с `0` по умолчанию, чтобы избежать ошибок
        try:
            total_cost = float(data.get('total_cost', 0))

            declared_flight_price = (
                total_cost * 1.2
            )

            return jsonify({"declared_flight_price": declared_flight_price})

        except ValueError:
            return jsonify({"error": "Некорректные данные"}), 400

    @app.route('/calculate_declared_flight_price_rub', methods=['POST'])
    def calculate_declared_flight_price_rub():
        global last_usd_to_rub_rate
        data = request.get_json()

        if not data:
            return jsonify({"error": "Нет данных"}), 400

        try:
            declared_flight_price = float(data.get('declared_flight_price', 0))

            # Получаем курс USD -> RUB
            url = "https://www.cbr.ru/scripts/XML_daily.asp"
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                xml_data = ET.fromstring(response.content)
                for currency in xml_data.findall("Valute"):
                    if currency.find("CharCode").text == "USD":
                        last_usd_to_rub_rate = float(currency.find("Value").text.replace(",", "."))
                        break
                else:
                    return jsonify({"error": "Курс USD не найден"}), 404
            except (requests.RequestException, ET.ParseError):
                if last_usd_to_rub_rate is None:
                    return jsonify({"error": "Ошибка запроса к ЦБР и нет сохраненного курса"}), 500

            # Используем последний успешный курс
            declared_flight_price_rub = declared_flight_price * last_usd_to_rub_rate

            return jsonify({"declared_flight_price_rub": declared_flight_price_rub})

        except ValueError:
            return jsonify({"error": "Некорректные данные"}), 400

    # Редактирование
    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit_flight(id):
        if 'loggedin' in session and session['role'] == 'admin':
            conn = create_connection()
            cur = conn.cursor()
            if request.method == 'POST':
                # Получение данных из формы
                flight_data = {
                    'date': request.form.get('date'),
                    'aircraft': request.form.get('aircraft'),
                    'route_countries': request.form.get('route_countries'),
                    'route_airports': request.form.get('route_airports'),
                    'max_commercial_load': request.form.get('max_commercial_load'),
                    'flight_cost': request.form.get('flight_cost'),
                    'calculation_date': request.form.get('calculation_date'),
                    'aircraft_type': request.form.get('aircraft_type')
                }
                calculation_data = {
                    'distance_km': request.form.get('distance_km'), # Расстояние между пунктами взлета и посадки
                    'speed_kmh': request.form.get('speed_kmh'), # Скорость ВС
                    'flight_time_h': request.form.get('flight_time_h'), # Время в пути ВС
                    'fuel_consumption_per_hour_t': request.form.get('fuel_consumption_per_hour_t'),
                    'fuel_consumption_t': request.form.get('fuel_consumption_t'),
                    'required_residual_fuel_t': request.form.get('required_residual_fuel_t'),
                    'refueled_fuel_t': request.form.get('refueled_fuel_t'),
                    'landing_fuel_residual_t': request.form.get('landing_fuel_residual_t'),
                    'takeoff_weight_t': request.form.get('takeoff_weight_t'),
                    'takeoff_overweight_t': request.form.get('takeoff_overweight_t'),
                    'landing_weight_t': request.form.get('landing_weight_t'),
                    'landing_overweight_t': request.form.get('landing_overweight_t'),
                    'aircraft_rent_cost': request.form.get('aircraft_rent_cost'),
                    'fuel_price_per_t': request.form.get('fuel_price_per_t'),
                    'fuel_cost': request.form.get('fuel_cost'),
                    'takeoff_landing_cost': request.form.get('takeoff_landing_cost'),
                    'maintenance_cost': request.form.get('maintenance_cost'),
                    'parking_cost': request.form.get('parking_cost'),
                    'catering_count': request.form.get('catering_count'),
                    'catering_price_per_meal': request.form.get('catering_price_per_meal'),
                    'crew_daily_allowance': request.form.get('crew_daily_allowance'),
                    'support_cost': request.form.get('support_cost'),
                    'navigation_fees': request.form.get('navigation_fees'),
                    'accommodation_cost': request.form.get('accommodation_cost'),
                    'miscellaneous_cost': request.form.get('miscellaneous_cost'),
                    'total_cost': request.form.get('total_cost'),
                    'declared_flight_price': request.form.get('declared_flight_price'),
                    'crew_count': request.form.get('crew_count'),
                    'max_takeoff_weight_t': request.form.get('max_takeoff_weight_t'),
                    'max_landing_weight_t': request.form.get('max_landing_weight_t'),
                    'empty_weight_t': request.form.get('empty_weight_t'),
                    'total_fuel_weight_t': request.form.get('total_fuel_weight_t'),
                    'performed_by': request.form.get('performed_by'),
                    'initial_fuel_t': request.form.get('initial_fuel_t'),
                    'price_per_hour_usd': request.form.get('price_per_hour_usd'),
                    'note': request.form.get('note'),
                    'price_per_serving': request.form.get('price_per_serving'),
                    'declared_flight_price_rub':  request.form.get('declared_flight_price_rub')
                }
                if calculation_data['distance_km'] and calculation_data['speed_kmh']:
                    calculation_data['flight_time_h'] = calculate_flight_time(
                        calculation_data['distance_km'], calculation_data['speed_kmh']
                    )
                if calculation_data['flight_time_h'] and calculation_data['fuel_consumption_per_hour_t']:
                    calculation_data['fuel_consumption_t'] = calculate_fuel_consumption(
                        calculation_data['flight_time_h'], calculation_data['fuel_consumption_per_hour_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['fuel_consumption_t'] and calculation_data['required_residual_fuel_t']:
                    calculation_data['refueled_fuel_t'] = calculate_refueled_fuel(
                        calculation_data['initial_fuel_t'], calculation_data['fuel_consumption_t'], calculation_data['required_residual_fuel_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['fuel_consumption_t'] and calculation_data['refueled_fuel_t']:
                    calculation_data['landing_fuel_residual_t'] = calculate_landing_fuel_residual(
                        calculation_data['initial_fuel_t'], calculation_data['fuel_consumption_t'], calculation_data['refueled_fuel_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['refueled_fuel_t'] and calculation_data['empty_weight_t'] and flight_data['max_commercial_load']:
                    calculation_data['takeoff_weight_t'] = calculate_takeoff_weight(
                        calculation_data['initial_fuel_t'], calculation_data['refueled_fuel_t'], calculation_data['empty_weight_t'], flight_data['max_commercial_load']
                    )
                if calculation_data['max_takeoff_weight_t'] and calculation_data['takeoff_weight_t']:
                    calculation_data['takeoff_overweight_t'] = calculate_takeoff_overweight(
                        calculation_data['max_takeoff_weight_t'], calculation_data['takeoff_weight_t']
                    )   
                if calculation_data['takeoff_weight_t'] and calculation_data['fuel_consumption_t']:
                    calculation_data['landing_weight_t'] = calculate_landing_weight(
                        calculation_data['takeoff_weight_t'], calculation_data['fuel_consumption_t']
                    ) 
                if calculation_data['max_landing_weight_t'] and calculation_data['landing_weight_t']:
                    calculation_data['landing_overweight_t'] = calculate_landing_overweight(
                        calculation_data['max_landing_weight_t'], calculation_data['landing_weight_t']
                    )
                if calculation_data['price_per_hour_usd'] and calculation_data['flight_time_h']:
                    calculation_data['aircraft_rent_cost'] = calculate_aircraft_rent_cost(
                        calculation_data['price_per_hour_usd'], calculation_data['flight_time_h']
                    )  
                if calculation_data['fuel_price_per_t'] and calculation_data['refueled_fuel_t']:
                    calculation_data['fuel_cost'] = calculate_fuel_cost(
                        calculation_data['fuel_price_per_t'], calculation_data['refueled_fuel_t']
                    )  
                if calculation_data['crew_count'] and calculation_data['price_per_serving'] and calculation_data['catering_count']:
                    calculation_data['catering_price_per_meal'] = calculate_catering_price_per_meal(
                        calculation_data['crew_count'], calculation_data['price_per_serving'], calculation_data['catering_count']
                    )      
                if calculation_data['distance_km']:
                    calculation_data['navigation_fees'] = calculate_navigation_fees(
                        calculation_data['distance_km'] 
                    )   
                if calculation_data['aircraft_rent_cost'] and calculation_data['fuel_cost'] and calculation_data['takeoff_landing_cost'] and calculation_data['maintenance_cost'] and calculation_data['parking_cost'] and calculation_data['catering_price_per_meal'] and calculation_data['crew_daily_allowance'] and calculation_data['support_cost'] and calculation_data['navigation_fees'] and calculation_data['accommodation_cost'] and calculation_data['miscellaneous_cost']:
                    calculation_data['total_cost'] = calculate_total_cost(
                        calculation_data['aircraft_rent_cost'], calculation_data['fuel_cost'], calculation_data['takeoff_landing_cost'], calculation_data['maintenance_cost'], calculation_data['parking_cost'], calculation_data['catering_price_per_meal'], calculation_data['crew_daily_allowance'], calculation_data['support_cost'], calculation_data['navigation_fees'], calculation_data['accommodation_cost'], calculation_data['miscellaneous_cost']
                    )
                if calculation_data['total_cost']:
                    calculation_data['declared_flight_price'] = calculate_declared_flight_price(
                        calculation_data['total_cost']
                    )
                if calculation_data['declared_flight_price']:
                    calculation_data['declared_flight_price_rub'] = calculate_declared_flight_price_rub(
                        calculation_data['declared_flight_price']
                    )
                flight_data['flight_cost'] = calculation_data['total_cost']
                
                try:
                    # Обновление данных рейса
                    cur.execute("""
                        UPDATE flights 
                        SET date = %s, aircraft = %s, route_countries = %s, route_airports = %s, 
                            max_commercial_load = %s, flight_cost = %s, calculation_date = %s, aircraft_type = %s
                        WHERE id = %s
                    """, (*flight_data.values(), id))
                    calculation_data['flight_id'] = id

                    #print(f"Updating flight with id: {id}")  
                    #print(f"Flight data: {flight_data}")  
                    #print(f"Checking for existing calculation with id: {id}")  
                    # Проверка существования записи в flight_calculations
                    cur.execute("SELECT * FROM flight_calculations WHERE flight_id = %s", (id,))
                    calculation_exists = cur.fetchone()
                    if calculation_exists:
                        # Обновление данных калькуляции
                        cur.execute("""
                            UPDATE flight_calculations
                            SET distance_km = %(distance_km)s, speed_kmh = %(speed_kmh)s, flight_time_h = %(flight_time_h)s,
                                fuel_consumption_per_hour_t = %(fuel_consumption_per_hour_t)s,
                                fuel_consumption_t = %(fuel_consumption_t)s,
                                required_residual_fuel_t = %(required_residual_fuel_t)s,
                                refueled_fuel_t = %(refueled_fuel_t)s, landing_fuel_residual_t = %(landing_fuel_residual_t)s,
                                takeoff_weight_t = %(takeoff_weight_t)s, takeoff_overweight_t = %(takeoff_overweight_t)s,
                                landing_weight_t = %(landing_weight_t)s, landing_overweight_t = %(landing_overweight_t)s,
                                aircraft_rent_cost = %(aircraft_rent_cost)s, fuel_price_per_t = %(fuel_price_per_t)s,
                                fuel_cost = %(fuel_cost)s, takeoff_landing_cost = %(takeoff_landing_cost)s,
                                maintenance_cost = %(maintenance_cost)s, parking_cost = %(parking_cost)s,
                                catering_count = %(catering_count)s, catering_price_per_meal = %(catering_price_per_meal)s,
                                crew_daily_allowance = %(crew_daily_allowance)s, support_cost = %(support_cost)s,
                                navigation_fees = %(navigation_fees)s, accommodation_cost = %(accommodation_cost)s,
                                miscellaneous_cost = %(miscellaneous_cost)s, total_cost = %(total_cost)s,
                                declared_flight_price = %(declared_flight_price)s, crew_count = %(crew_count)s,
                                max_takeoff_weight_t = %(max_takeoff_weight_t)s, max_landing_weight_t = %(max_landing_weight_t)s,
                                empty_weight_t = %(empty_weight_t)s, total_fuel_weight_t = %(total_fuel_weight_t)s, performed_by = %(performed_by)s, 
                                initial_fuel_t = %(initial_fuel_t)s, price_per_hour_usd = %(price_per_hour_usd)s, note = %(note)s, price_per_serving = %(price_per_serving)s, declared_flight_price_rub = %(declared_flight_price_rub)s
                            WHERE flight_id = %(flight_id)s
                        """, {**calculation_data, 'flight_id': id})
                    else:
                        # Создание новой записи в калькуляции
                        cur.execute("""
                            INSERT INTO flight_calculations (flight_id, distance_km, speed_kmh, flight_time_h, 
                                                        fuel_consumption_per_hour_t, fuel_consumption_t,
                                                        required_residual_fuel_t, refueled_fuel_t,
                                                        landing_fuel_residual_t, takeoff_weight_t, 
                                                        takeoff_overweight_t, landing_weight_t, landing_overweight_t,
                                                        aircraft_rent_cost, fuel_price_per_t, fuel_cost,
                                                        takeoff_landing_cost, maintenance_cost, parking_cost,
                                                        catering_count, catering_price_per_meal, crew_daily_allowance,
                                                        support_cost, navigation_fees, accommodation_cost,
                                                        miscellaneous_cost, total_cost, declared_flight_price,
                                                        crew_count, max_takeoff_weight_t, max_landing_weight_t,
                                                        empty_weight_t, total_fuel_weight_t, performed_by,
                                                        initial_fuel_t, price_per_hour_usd, note, price_per_serving, declared_flight_price_rub)
                        VALUES (%(flight_id)s, %(distance_km)s, %(speed_kmh)s, %(flight_time_h)s,
                                %(fuel_consumption_per_hour_t)s, %(fuel_consumption_t)s,
                                %(required_residual_fuel_t)s, %(refueled_fuel_t)s,
                                %(landing_fuel_residual_t)s, %(takeoff_weight_t)s,
                                %(takeoff_overweight_t)s, %(landing_weight_t)s, %(landing_overweight_t)s,
                                %(aircraft_rent_cost)s, %(fuel_price_per_t)s, %(fuel_cost)s,
                                %(takeoff_landing_cost)s, %(maintenance_cost)s, %(parking_cost)s,
                                %(catering_count)s, %(catering_price_per_meal)s, %(crew_daily_allowance)s,
                                %(support_cost)s, %(navigation_fees)s, %(accommodation_cost)s,
                                %(miscellaneous_cost)s, %(total_cost)s, %(declared_flight_price)s,
                                %(crew_count)s, %(max_takeoff_weight_t)s, %(max_landing_weight_t)s,
                                %(empty_weight_t)s, %(total_fuel_weight_t)s, %(performed_by)s,
                                %(initial_fuel_t)s, %(price_per_hour_usd)s, %(note)s, %(price_per_serving)s, %(declared_flight_price_rub)s)
                        """, {**calculation_data, 'flight_id': id})

                    conn.commit()
                    return redirect(url_for('home'))
                except Exception as e:
                    print(f"Error updating flight and calculations: {e}")
                finally:
                    cur.close()
                    conn.close()

            # Отображение формы редактирования
            try:
                cur.execute("SELECT * FROM flights WHERE id = %s", (id,))
                flight = cur.fetchone()

                cur.execute("SELECT * FROM flight_calculations WHERE flight_id = %s", (id,))
                calculations = cur.fetchone()
            except Exception as e:
                print(f"Error fetching flight details: {e}")
                flight = None
                calculations = None
            finally:
                cur.close()
                if conn and conn.open:
                    conn.close()

            
            if flight:
                return render_template('crud/edit_flight.html', flight=flight, calculations=calculations)
            else:
                return "Flight not found", 404

        # Перенесено выше — создание соединения перед выполнением SQL-запроса
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT aircraft FROM aircrafts")
        aircrafts = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return redirect(url_for('home'), aircrafts=aircrafts)

    # Копирование
    @app.route('/copy/<int:id>', methods=['GET', 'POST'])
    def copy_flight(id):
        if 'loggedin' in session and session['role'] == 'admin':
            conn = create_connection()
            cur = conn.cursor()
            if request.method == 'POST':
                # Получение данных из формы
                flight_data = {
                    'date': request.form.get('date'),
                    'aircraft': request.form.get('aircraft'),
                    'route_countries': request.form.get('route_countries'),
                    'route_airports': request.form.get('route_airports'),
                    'max_commercial_load': request.form.get('max_commercial_load'),
                    'flight_cost': request.form.get('flight_cost'),
                    'calculation_date': request.form.get('calculation_date'),
                    'aircraft_type': request.form.get('aircraft_type')
                }
                calculation_data = {
                    'distance_km': request.form.get('distance_km'), # Расстояние между пунктами взлета и посадки
                    'speed_kmh': request.form.get('speed_kmh'), # Скорость ВС
                    'flight_time_h': request.form.get('flight_time_h'), # Время в пути ВС
                    'fuel_consumption_per_hour_t': request.form.get('fuel_consumption_per_hour_t'),
                    'fuel_consumption_t': request.form.get('fuel_consumption_t'),
                    'required_residual_fuel_t': request.form.get('required_residual_fuel_t'),
                    'refueled_fuel_t': request.form.get('refueled_fuel_t'),
                    'landing_fuel_residual_t': request.form.get('landing_fuel_residual_t'),
                    'takeoff_weight_t': request.form.get('takeoff_weight_t'),
                    'takeoff_overweight_t': request.form.get('takeoff_overweight_t'),
                    'landing_weight_t': request.form.get('landing_weight_t'),
                    'landing_overweight_t': request.form.get('landing_overweight_t'),
                    'aircraft_rent_cost': request.form.get('aircraft_rent_cost'),
                    'fuel_price_per_t': request.form.get('fuel_price_per_t'),
                    'fuel_cost': request.form.get('fuel_cost'),
                    'takeoff_landing_cost': request.form.get('takeoff_landing_cost'),
                    'maintenance_cost': request.form.get('maintenance_cost'),
                    'parking_cost': request.form.get('parking_cost'),
                    'catering_count': request.form.get('catering_count'),
                    'catering_price_per_meal': request.form.get('catering_price_per_meal'),
                    'crew_daily_allowance': request.form.get('crew_daily_allowance'),
                    'support_cost': request.form.get('support_cost'),
                    'navigation_fees': request.form.get('navigation_fees'),
                    'accommodation_cost': request.form.get('accommodation_cost'),
                    'miscellaneous_cost': request.form.get('miscellaneous_cost'),
                    'total_cost': request.form.get('total_cost'),
                    'declared_flight_price': request.form.get('declared_flight_price'),
                    'crew_count': request.form.get('crew_count'),
                    'max_takeoff_weight_t': request.form.get('max_takeoff_weight_t'),
                    'max_landing_weight_t': request.form.get('max_landing_weight_t'),
                    'empty_weight_t': request.form.get('empty_weight_t'),
                    'total_fuel_weight_t': request.form.get('total_fuel_weight_t'),
                    'performed_by': request.form.get('performed_by'),
                    'initial_fuel_t': request.form.get('initial_fuel_t'),
                    'price_per_hour_usd': request.form.get('price_per_hour_usd'),
                    'note': request.form.get('note'),
                    'price_per_serving': request.form.get('price_per_serving'),
                    'declared_flight_price_rub':  request.form.get('declared_flight_price_rub')
                }
                if calculation_data['distance_km'] and calculation_data['speed_kmh']:
                    calculation_data['flight_time_h'] = calculate_flight_time(
                        calculation_data['distance_km'], calculation_data['speed_kmh']
                    )
                if calculation_data['flight_time_h'] and calculation_data['fuel_consumption_per_hour_t']:
                    calculation_data['fuel_consumption_t'] = calculate_fuel_consumption(
                        calculation_data['flight_time_h'], calculation_data['fuel_consumption_per_hour_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['fuel_consumption_t'] and calculation_data['required_residual_fuel_t']:
                    calculation_data['refueled_fuel_t'] = calculate_refueled_fuel(
                        calculation_data['initial_fuel_t'], calculation_data['fuel_consumption_t'], calculation_data['required_residual_fuel_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['fuel_consumption_t'] and calculation_data['refueled_fuel_t']:
                    calculation_data['landing_fuel_residual_t'] = calculate_landing_fuel_residual(
                        calculation_data['initial_fuel_t'], calculation_data['fuel_consumption_t'], calculation_data['refueled_fuel_t']
                    )
                if calculation_data['initial_fuel_t'] and calculation_data['refueled_fuel_t'] and calculation_data['empty_weight_t'] and flight_data['max_commercial_load']:
                    calculation_data['takeoff_weight_t'] = calculate_takeoff_weight(
                        calculation_data['initial_fuel_t'], calculation_data['refueled_fuel_t'], calculation_data['empty_weight_t'], flight_data['max_commercial_load']
                    )
                if calculation_data['max_takeoff_weight_t'] and calculation_data['takeoff_weight_t']:
                    calculation_data['takeoff_overweight_t'] = calculate_takeoff_overweight(
                        calculation_data['max_takeoff_weight_t'], calculation_data['takeoff_weight_t']
                    )   
                if calculation_data['takeoff_weight_t'] and calculation_data['fuel_consumption_t']:
                    calculation_data['landing_weight_t'] = calculate_landing_weight(
                        calculation_data['takeoff_weight_t'], calculation_data['fuel_consumption_t']
                    ) 
                if calculation_data['max_landing_weight_t'] and calculation_data['landing_weight_t']:
                    calculation_data['landing_overweight_t'] = calculate_landing_overweight(
                        calculation_data['max_landing_weight_t'], calculation_data['landing_weight_t']
                    )
                if calculation_data['price_per_hour_usd'] and calculation_data['flight_time_h']:
                    calculation_data['aircraft_rent_cost'] = calculate_aircraft_rent_cost(
                        calculation_data['price_per_hour_usd'], calculation_data['flight_time_h']
                    )  
                if calculation_data['fuel_price_per_t'] and calculation_data['refueled_fuel_t']:
                    calculation_data['fuel_cost'] = calculate_fuel_cost(
                        calculation_data['fuel_price_per_t'], calculation_data['refueled_fuel_t']
                    )  
                if calculation_data['crew_count'] and calculation_data['price_per_serving'] and calculation_data['catering_count']:
                    calculation_data['catering_price_per_meal'] = calculate_catering_price_per_meal(
                        calculation_data['crew_count'], calculation_data['price_per_serving'], calculation_data['catering_count']
                    )      
                if calculation_data['distance_km']:
                    calculation_data['navigation_fees'] = calculate_navigation_fees(
                        calculation_data['distance_km'] 
                    )   
                if calculation_data['aircraft_rent_cost'] and calculation_data['fuel_cost'] and calculation_data['takeoff_landing_cost'] and calculation_data['maintenance_cost'] and calculation_data['parking_cost'] and calculation_data['catering_price_per_meal'] and calculation_data['crew_daily_allowance'] and calculation_data['support_cost'] and calculation_data['navigation_fees'] and calculation_data['accommodation_cost'] and calculation_data['miscellaneous_cost']:
                    calculation_data['total_cost'] = calculate_total_cost(
                        calculation_data['aircraft_rent_cost'], calculation_data['fuel_cost'], calculation_data['takeoff_landing_cost'], calculation_data['maintenance_cost'], calculation_data['parking_cost'], calculation_data['catering_price_per_meal'], calculation_data['crew_daily_allowance'], calculation_data['support_cost'], calculation_data['navigation_fees'], calculation_data['accommodation_cost'], calculation_data['miscellaneous_cost']
                    )
                if calculation_data['total_cost']:
                    calculation_data['declared_flight_price'] = calculate_declared_flight_price(
                        calculation_data['total_cost']
                    )
                if calculation_data['declared_flight_price']:
                    calculation_data['declared_flight_price_rub'] = calculate_declared_flight_price_rub(
                        calculation_data['declared_flight_price']
                    )
                flight_data['flight_cost'] = calculation_data['total_cost']
                
                try:
                    # Обновление данных рейса
                    cur.execute("""
                        UPDATE flights 
                        SET date = %s, aircraft = %s, route_countries = %s, route_airports = %s, 
                            max_commercial_load = %s, flight_cost = %s, calculation_date = %s, aircraft_type = %s
                        WHERE id = %s
                    """, (*flight_data.values(), id))
                    calculation_data['flight_id'] = id
                    print(f"Updating flight with id: {id}")  
                    print(f"Flight data: {flight_data}")  
                    print(f"Checking for existing calculation with id: {id}")  
                    # Проверка существования записи в flight_calculations
                    cur.execute("SELECT * FROM flight_calculations WHERE flight_id = %s", (id,))
                    calculation_exists = cur.fetchone()

                    # Создание новой записи в калькуляции
                    cur.execute("""
                        INSERT INTO flight_calculations (flight_id, distance_km, speed_kmh, flight_time_h, 
                                                    fuel_consumption_per_hour_t, fuel_consumption_t,
                                                    required_residual_fuel_t, refueled_fuel_t,
                                                    landing_fuel_residual_t, takeoff_weight_t, 
                                                    takeoff_overweight_t, landing_weight_t, landing_overweight_t,
                                                    aircraft_rent_cost, fuel_price_per_t, fuel_cost,
                                                    takeoff_landing_cost, maintenance_cost, parking_cost,
                                                    catering_count, catering_price_per_meal, crew_daily_allowance,
                                                    support_cost, navigation_fees, accommodation_cost,
                                                    miscellaneous_cost, total_cost, declared_flight_price,
                                                    crew_count, max_takeoff_weight_t, max_landing_weight_t,
                                                    empty_weight_t, total_fuel_weight_t, performed_by,
                                                    initial_fuel_t, price_per_hour_usd, note, price_per_serving, declared_flight_price_rub)
                    VALUES (%(flight_id)s, %(distance_km)s, %(speed_kmh)s, %(flight_time_h)s,
                            %(fuel_consumption_per_hour_t)s, %(fuel_consumption_t)s,
                            %(required_residual_fuel_t)s, %(refueled_fuel_t)s,
                            %(landing_fuel_residual_t)s, %(takeoff_weight_t)s,
                            %(takeoff_overweight_t)s, %(landing_weight_t)s, %(landing_overweight_t)s,
                            %(aircraft_rent_cost)s, %(fuel_price_per_t)s, %(fuel_cost)s,
                            %(takeoff_landing_cost)s, %(maintenance_cost)s, %(parking_cost)s,
                            %(catering_count)s, %(catering_price_per_meal)s, %(crew_daily_allowance)s,
                            %(support_cost)s, %(navigation_fees)s, %(accommodation_cost)s,
                            %(miscellaneous_cost)s, %(total_cost)s, %(declared_flight_price)s,
                            %(crew_count)s, %(max_takeoff_weight_t)s, %(max_landing_weight_t)s,
                            %(empty_weight_t)s, %(total_fuel_weight_t)s, %(performed_by)s,
                            %(initial_fuel_t)s, %(price_per_hour_usd)s, %(note)s, %(price_per_serving)s, %(declared_flight_price_rub)s)
                    """, {**calculation_data, 'flight_id': id})

                    conn.commit()
                    return redirect(url_for('home'))
                except Exception as e:
                    print(f"Error updating flight and calculations: {e}")
                finally:
                    cur.close()
                    conn.close()

            # Отображение формы редактирования
            try:
                cur.execute("SELECT * FROM flights WHERE id = %s", (id,))
                flight = cur.fetchone()

                cur.execute("SELECT * FROM flight_calculations WHERE flight_id = %s", (id,))
                calculations = cur.fetchone()
            except Exception as e:
                print(f"Error fetching flight details: {e}")
                flight = None
                calculations = None
            finally:
                cur.close()
                if conn and conn.open:
                    conn.close()


            if flight:
                return render_template('crud/copy_flight.html', flight=flight, calculations=calculations)
            else:
                return "Flight not found", 404

        return redirect(url_for('home'))

    @app.route('/delete/<int:id>')
    def delete_flight(id):
        if 'loggedin' in session and session['role'] == 'admin':
            conn = create_connection()
            cur = conn.cursor()
            try:
                # Удаление связанных записей перед удалением основного рейса
                cur.execute("DELETE FROM flight_calculations WHERE flight_id = %s", (id,))
                cur.execute("DELETE FROM flights WHERE id = %s", (id,))
                conn.commit()
            except pymysql.MySQLError as e:
                print(f"Error deleting flight: {e}")
                conn.rollback()  # Откат изменений в случае ошибки
            finally:
                cur.close()
                conn.close()

        return redirect(url_for('home'))

    @app.route("/download_excel/<int:id>")
    def download_excel(id):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        
        conn = create_connection()
        cur = conn.cursor()
        
        try:
            # Получаем данные из БД
            query = """
                SELECT 
                    f.date, f.aircraft, f.route_countries, f.route_airports, 
                    f.max_commercial_load, f.flight_cost, f.calculation_date, 
                    f.aircraft_type, fc.distance_km, fc.speed_kmh, fc.flight_time_h, 
                    fc.fuel_consumption_per_hour_t, fc.fuel_consumption_t, 
                    fc.required_residual_fuel_t, fc.refueled_fuel_t, 
                    fc.landing_fuel_residual_t, fc.takeoff_weight_t, 
                    fc.takeoff_overweight_t, fc.landing_weight_t, 
                    fc.landing_overweight_t, fc.aircraft_rent_cost, 
                    fc.fuel_price_per_t, fc.fuel_cost, fc.takeoff_landing_cost, 
                    fc.maintenance_cost, fc.parking_cost, fc.catering_count, 
                    fc.catering_price_per_meal, fc.crew_daily_allowance, 
                    fc.support_cost, fc.navigation_fees, fc.accommodation_cost, 
                    fc.miscellaneous_cost, fc.total_cost, fc.declared_flight_price, 
                    fc.crew_count, fc.max_takeoff_weight_t, fc.max_landing_weight_t, 
                    fc.empty_weight_t, fc.total_fuel_weight_t, fc.performed_by, 
                    fc.initial_fuel_t, fc.price_per_hour_usd, fc.note, 
                    fc.price_per_serving, fc.declared_flight_price_rub 
                FROM flights f
                LEFT JOIN flight_calculations fc ON f.id = fc.flight_id
                WHERE f.id = %s
            """
            cur.execute(query, (id,))
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            
            if not data:
                return "Нет данных для отчета", 404
            
            # Создаем DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Преобразуем даты в строковый формат ДД.ММ.ГГГГ
            date_columns = ['date', 'calculation_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = df.loc[0, col].strftime('%d.%m.%Y') if col in df.columns and pd.notna(df.loc[0, col]) else 'Unknown'
            
            # Получаем название листа Excel из route_airports
            sheet_name = df.loc[0, 'route_airports'] if 'route_airports' in df.columns else 'Рейсы'
            sheet_name = sheet_name[:31]  # Ограничение Excel на длину имени листа
            
            # Получаем имя файла из route_airports + calculation_date
            route_airports = df.loc[0, 'route_airports'] if 'route_airports' in df.columns else 'Unknown'
            calculation_date = df.loc[0, 'calculation_date'] if 'calculation_date' in df.columns else 'Unknown'
            filename = f"{route_airports}_{calculation_date}.xlsx".replace(" ", "_")
            
            # Переименование столбцов на русский
            column_mapping = {
                "date": "Дата рейса",
                "aircraft": "Самолет",
                "route_countries": "Страны маршрута",
                "route_airports": "Аэропорты маршрута",
                "max_commercial_load": "Максимальная коммерческая загрузка",
                "flight_cost": "Стоимость рейса",
                "calculation_date": "Дата расчета",
                "aircraft_type": "Тип самолета",
                "distance_km": "Дистанция (км)",
                "speed_kmh": "Скорость (км/ч)",
                "flight_time_h": "Время полета (ч)",
                "fuel_consumption_per_hour_t": "Потребление топлива в час (т)",
                "fuel_consumption_t": "Общее потребление топлива (т)",
                "required_residual_fuel_t": "Требуемый остаток топлива (т)",
                "refueled_fuel_t": "Заправленное топливо (т)",
                "landing_fuel_residual_t": "Остаток топлива при посадке (т)",
                "takeoff_weight_t": "Взлетный вес (т)",
                "takeoff_overweight_t": "Перегрузка при взлете (т)",
                "landing_weight_t": "Посадочный вес (т)",
                "landing_overweight_t": "Перегрузка при посадке (т)",
                "aircraft_rent_cost": "Стоимость аренды самолета",
                "fuel_price_per_t": "Цена топлива за тонну",
                "fuel_cost": "Стоимость топлива",
                "takeoff_landing_cost": "Стоимость взлета/посадки",
                "maintenance_cost": "Стоимость техобслуживания",
                "parking_cost": "Стоимость стоянки",    
                "catering_count": "Количество питания",
                "catering_price_per_meal": "Цена за порцию",
                "crew_daily_allowance": "Суточные экипажа",
                "support_cost": "Стоимость поддержки",
                "navigation_fees": "Навигационные сборы",
                "accommodation_cost": "Стоимость проживания",
                "miscellaneous_cost": "Прочие расходы",
                "total_cost": "Общая стоимость",
                "declared_flight_price": "Заявленная стоимость рейса",
                "crew_count": "Количество экипажа",
                "max_takeoff_weight_t": "Максимальный взлетный вес (т)",
                "max_landing_weight_t": "Максимальный посадочный вес (т)",
                "empty_weight_t": "Пустой вес (т)",
                "total_fuel_weight_t": "Общий вес топлива (т)",
                "performed_by": "Выполнено",
                "initial_fuel_t": "Начальный запас топлива (т)",
                "price_per_hour_usd": "Цена за час (USD)",
                "note": "Примечание",
                "price_per_serving": "Цена за обслуживание",
                "declared_flight_price_rub": "Заявленная стоимость (RUB)"
            }
            df.rename(columns=column_mapping, inplace=True)
            
            # Сохраняем в Excel
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            writer.close()
            
            return send_file(filename, as_attachment=True, download_name=filename)
        
        except Exception as e:
            print(f"Ошибка генерации отчета: {e}")
            return "Ошибка генерации отчета", 500
        finally:
            cur.close()
            conn.close()
    # Вывод деталей рейса - просто их просмотр
    @app.route('/flight/<int:id>', methods=['GET', 'POST'])
    def flight_details(id):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        role = session.get('role', 'guest')  # По умолчанию роль 'guest', если ключ отсутствует

        conn = create_connection()
        cur = conn.cursor()

        try:
            # Получение данных рейса
            cur.execute("SELECT * FROM flights WHERE id = %s", (id,))
            flight = cur.fetchone()

            # Получение данных калькуляции, если они существуют
            cur.execute("SELECT * FROM flight_calculations WHERE flight_id = %s", (id,))
            calculations = cur.fetchone()
        except Exception as e:
            print(f"Error fetching flight details: {e}")
            flight = None
            calculations = None
        finally:
            cur.close()
            conn.close()

        if not flight:
            return "Flight not found", 404

        if request.method == 'POST' and session.get('role') == 'admin':
            # Если администратор, обработать редактирование калькуляции
            try:
                # Получение данных из формы
                calculation_data = {
                    'distance_km': request.form.get('distance_km'),
                    'speed_kmh': request.form.get('speed_kmh'),
                    'flight_time_h': request.form.get('flight_time_h'),
                    'fuel_consumption_per_hour_t': request.form.get('fuel_consumption_per_hour_t'),
                    'fuel_consumption_t': request.form.get('fuel_consumption_t'),
                    'required_residual_fuel_t': request.form.get('required_residual_fuel_t'),
                    'refueled_fuel_t': request.form.get('refueled_fuel_t'),
                    'landing_fuel_residual_t': request.form.get('landing_fuel_residual_t'),
                    'takeoff_weight_t': request.form.get('takeoff_weight_t'),
                    'takeoff_overweight_t': request.form.get('takeoff_overweight_t'),
                    'landing_weight_t': request.form.get('landing_weight_t'),
                    'landing_overweight_t': request.form.get('landing_overweight_t'),
                    'aircraft_rent_cost': request.form.get('aircraft_rent_cost'),
                    'fuel_price_per_t': request.form.get('fuel_price_per_t'),
                    'fuel_cost': request.form.get('fuel_cost'),
                    'takeoff_landing_cost': request.form.get('takeoff_landing_cost'),
                    'maintenance_cost': request.form.get('maintenance_cost'),
                    'parking_cost': request.form.get('parking_cost'),
                    'catering_count': request.form.get('catering_count'),
                    'catering_price_per_meal': request.form.get('catering_price_per_meal'),
                    'crew_daily_allowance': request.form.get('crew_daily_allowance'),
                    'support_cost': request.form.get('support_cost'),
                    'navigation_fees': request.form.get('navigation_fees'),
                    'accommodation_cost': request.form.get('accommodation_cost'),
                    'miscellaneous_cost': request.form.get('miscellaneous_cost'),
                    'total_cost': request.form.get('total_cost'),
                    'declared_flight_price': request.form.get('declared_flight_price'),
                    'crew_count': request.form.get('crew_count'),
                    'max_takeoff_weight_t': request.form.get('max_takeoff_weight_t'),
                    'max_landing_weight_t': request.form.get('max_landing_weight_t'),
                    'empty_weight_t': request.form.get('empty_weight_t'),
                    'total_fuel_weight_t': request.form.get('total_fuel_weight_t'),
                    'performed_by': request.form.get('performed_by'),
                    'initial_fuel_t': request.form.get('initial_fuel_t'),
                    'price_per_hour_usd': request.form.get('price_per_hour_usd'),
                    'note': request.form.get('note'),
                    'price_per_serving': request.form.get('price_per_serving'),
                    'declared_flight_price_rub': request.form.get('declared_flight_price_rub')
                }

                conn = create_connection()
                cur = conn.cursor()

                # Обновление или создание записи в таблице flight_calculations
                if calculations:
                    cur.execute("""
                        UPDATE flight_calculations
                        SET distance_km = %(distance_km)s, speed_kmh = %(speed_kmh)s, flight_time_h = %(flight_time_h)s,
                            fuel_consumption_per_hour_t = %(fuel_consumption_per_hour_t)s,
                            fuel_consumption_t = %(fuel_consumption_t)s,
                            required_residual_fuel_t = %(required_residual_fuel_t)s,
                            refueled_fuel_t = %(refueled_fuel_t)s, landing_fuel_residual_t = %(landing_fuel_residual_t)s,
                            takeoff_weight_t = %(takeoff_weight_t)s, takeoff_overweight_t = %(takeoff_overweight_t)s,
                            landing_weight_t = %(landing_weight_t)s, landing_overweight_t = %(landing_overweight_t)s,
                            aircraft_rent_cost = %(aircraft_rent_cost)s, fuel_price_per_t = %(fuel_price_per_t)s,
                            fuel_cost = %(fuel_cost)s, takeoff_landing_cost = %(takeoff_landing_cost)s,
                            maintenance_cost = %(maintenance_cost)s, parking_cost = %(parking_cost)s,
                            catering_count = %(catering_count)s, catering_price_per_meal = %(catering_price_per_meal)s,
                            crew_daily_allowance = %(crew_daily_allowance)s, support_cost = %(support_cost)s,
                            navigation_fees = %(navigation_fees)s, accommodation_cost = %(accommodation_cost)s,
                            miscellaneous_cost = %(miscellaneous_cost)s, total_cost = %(total_cost)s,
                            declared_flight_price = %(declared_flight_price)s, crew_count = %(crew_count)s,
                            max_takeoff_weight_t = %(max_takeoff_weight_t)s, max_landing_weight_t = %(max_landing_weight_t)s,
                            empty_weight_t = %(empty_weight_t)s, total_fuel_weight_t = %(total_fuel_weight_t)s, performed_by = %(performed_by)s, 
                            initial_fuel_t = %(initial_fuel_t)s, price_per_hour_usd = %(price_per_hour_usd)s, note = %(note)s, price_per_serving = %(price_per_serving)s,
                            declared_flight_price_rub = %(declared_flight_price_rub)s
                        WHERE flight_id = %(flight_id)s
                    """, {**calculation_data, 'flight_id': id})
                else:
                    cur.execute("""
                        INSERT INTO flight_calculations (flight_id, distance_km, speed_kmh, flight_time_h, 
                                                        fuel_consumption_per_hour_t, fuel_consumption_t,
                                                        required_residual_fuel_t, refueled_fuel_t,
                                                        landing_fuel_residual_t, takeoff_weight_t, 
                                                        takeoff_overweight_t, landing_weight_t, landing_overweight_t,
                                                        aircraft_rent_cost, fuel_price_per_t, fuel_cost,
                                                        takeoff_landing_cost, maintenance_cost, parking_cost,
                                                        catering_count, catering_price_per_meal, crew_daily_allowance,
                                                        support_cost, navigation_fees, accommodation_cost,
                                                        miscellaneous_cost, total_cost, declared_flight_price,
                                                        crew_count, max_takeoff_weight_t, max_landing_weight_t,
                                                        empty_weight_t, total_fuel_weight_t, performed_by,
                                                        initial_fuel_t, price_per_hour_usd, note, price_per_serving
                                                        declared_flight_price_rub)
                        VALUES (%(flight_id)s, %(distance_km)s, %(speed_kmh)s, %(flight_time_h)s,
                                %(fuel_consumption_per_hour_t)s, %(fuel_consumption_t)s,
                                %(required_residual_fuel_t)s, %(refueled_fuel_t)s,
                                %(landing_fuel_residual_t)s, %(takeoff_weight_t)s,
                                %(takeoff_overweight_t)s, %(landing_weight_t)s, %(landing_overweight_t)s,
                                %(aircraft_rent_cost)s, %(fuel_price_per_t)s, %(fuel_cost)s,
                                %(takeoff_landing_cost)s, %(maintenance_cost)s, %(parking_cost)s,
                                %(catering_count)s, %(catering_price_per_meal)s, %(crew_daily_allowance)s,
                                %(support_cost)s, %(navigation_fees)s, %(accommodation_cost)s,
                                %(miscellaneous_cost)s, %(total_cost)s, %(declared_flight_price)s,
                                %(crew_count)s, %(max_takeoff_weight_t)s, %(max_landing_weight_t)s,
                                %(empty_weight_t)s, %(total_fuel_weight_t)s, %(performed_by)s,
                                %(initial_fuel_t)s, %(price_per_hour_usd)s, %(note)s, %(price_per_serving)s,
                                %(declared_flight_price_rub)s)
                    """, {**calculation_data, 'flight_id': id})
                conn.commit()
            except Exception as e:
                print(f"Error updating calculations: {e}")
            finally:
                cur.close()
                conn.close()
            return redirect(url_for('flight_details', id=id))

        return render_template(
            'crud/flight_details.html',
            flight=flight,
            role=role,
            calculations=calculations,
            is_admin=(session.get('role') == 'admin')
        )

    def send_verification_email(email, token):
        verification_link = f"http://127.0.0.1:5003/verify/{token}"
        msg = MIMEText(f"Для подтверждения email перейдите по ссылке: {verification_link}")
        msg["Subject"] = "Подтверждение email"
        msg["From"] = "support@airroute.ru"
        msg["To"] = email

        smtp_server = "mail.hosting.reg.ru"
        smtp_port = 465
        email_account = "support@airroute.ru"
        password = "nW5uV1dP3gaG8hF3"

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(email_account, password)
                server.sendmail(email_account, email, msg.as_string())
            print("Письмо успешно отправлено!")
        except Exception as e:
            print(f"Ошибка при отправке: {e}")


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        logger.debug("Запрос на регистрацию получен")
        text = ''
        if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form.get('role', 'user')

            logger.debug(f"Данные для регистрации: username={username}, email={email}, role={role}")

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            verification_token = secrets.token_urlsafe(16)
            registration_date = datetime.now()
            is_active = True

            conn = create_connection()
            cur = conn.cursor()

            try:
                cur.execute("SELECT * FROM accounts WHERE username = %s OR email = %s", (username, email))
                account = cur.fetchone()

                if account:
                    text = "Account already exists!"
                    logger.warning("Пользователь уже существует")
                else:
                    cur.execute("""
                        INSERT INTO accounts 
                        (username, email, password, role, email_verification_token, email_verified, registration_date, is_active) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (username, email, hashed_password, role, verification_token, False, registration_date, is_active))

                    conn.commit()
                    logger.debug("Пользователь успешно зарегистрирован")

                    send_verification_email(email, verification_token)
                    logger.debug("Письмо с подтверждением отправлено")

                    text = "Учетная запись создана! Пожалуйста, проверьте свою электронную почту, чтобы подтвердить свою учетную запись."

            except Exception as e:
                logger.error(f"Ошибка при регистрации: {e}")
                text = "An error occurred, please try again later."
            finally:
                cur.close()
                conn.close()

        return render_template('auth/register.html', text=text)


    @app.route('/verify/<token>', methods=['GET'])
    def verify_email(token):
        conn = create_connection()
        cur = conn.cursor()
        try:
            # Логируем токен для отладки
            logger.debug(f"Токен для верификации: {token}")

            cur.execute("SELECT id FROM accounts WHERE email_verification_token = %s", (token,))
            user = cur.fetchone()
            logger.debug(f"Результат запроса: {user}")

            if not user:
                logger.warning("Пользователь с таким токеном не найден")
                return "Неверный или устаревший токен.", 400
            user_id = user['id']
            logger.debug(f"Найден пользователь с ID: {user_id}")

            # Обновляем статус подтверждения email
            cur.execute("UPDATE accounts SET email_verified = TRUE, email_verification_token = NULL WHERE id = %s", (user_id,))
            conn.commit()
            logger.debug("Email успешно подтвержден")

            return "Email успешно подтвержден! Теперь вы можете войти в систему."
        except Exception as e:
            # Логируем тип исключения и его текст
            logger.error(f"Тип исключения: {type(e)}")
            logger.error(f"Ошибка при верификации email: {str(e)}")
            return f"Ошибка: {str(e)}", 500
        finally:
            cur.close()
            conn.close()


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']

            # Подключение к базе данных
            conn = create_connection()
            cur = conn.cursor()

            try:
                # Получение данных пользователя
                cur.execute('SELECT * FROM accounts WHERE username = %s', (username,))
                user = cur.fetchone()

                if user:
                    if not user['email_verified']:
                        msg = 'You need to verify your email before logging in!'
                    elif check_password_hash(user['password'], password):
                        session['loggedin'] = True
                        session['id'] = user['id']
                        session['username'] = user['username']
                        session['role'] = user['role']
                        return redirect(url_for('home'))
                    else:
                        msg = 'Неверное имя пользователя/пароль!'
                else:
                    msg = 'Неверное имя пользователя/пароль!'
            except Exception as e:
                print(f"Error: {e}")
                msg = 'Произошла ошибка, пожалуйста, повторите попытку.'
            finally:
                cur.close()
                conn.close()
        elif request.method == 'POST':
            msg = 'Пожалуйста, заполните форму!'

        return render_template('auth/login.html', text=msg)

    def send_reset_email(email, token):
        reset_link = f"http://127.0.0.1:5003/reset/{token}"
        msg = MIMEText(f"Для восстановления пароля перейдите по ссылке: {reset_link}")
        msg["Subject"] = "Восстановление пароля"
        msg["From"] = "support@airroute.ru"
        msg["To"] = email
        # Использование SSL-соединения с портом 465
        smtp_server = "mail.hosting.reg.ru"  # Замените на правильный SMTP сервер
        smtp_port = 465  # Порт для SSL
        email_account = "support@airroute.ru"
        password = "nW5uV1dP3gaG8hF3"  # Ваш пароль от почтового ящика

        try:
            # Создание SSL контекста и подключение через SSL
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(email_account, password)  # Логин на сервере
                server.sendmail(email_account, email, msg.as_string())  # Отправка письма
            print("Письмо успешно отправлено!")
        except Exception as e:
            print(f"Ошибка при отправке: {e}")

    @app.route('/restore', methods=['GET', 'POST'])
    def restore_password():
        email = request.form.get('email')
        if request.method == 'POST':

            conn = create_connection()
            cur = conn.cursor()

            try:
                cur.execute("SELECT id FROM accounts WHERE email = %s", (email,))
                user = cur.fetchone()

                if not user:
                    return "Такого email нет в системе!", 400
                
                token = secrets.token_urlsafe(16)
                cur.execute("UPDATE accounts SET reset_token = %s WHERE email = %s", (token, email))
                conn.commit()

                send_reset_email(email, token)
                return "Ссылка для восстановления отправлена на вашу почту."

            except Exception as e:
                return f"Ошибка: {e}", 500
            finally:
                cur.close()
                conn.close()

        return render_template('auth/restore.html', email=email)

    @app.route('/reset/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        conn = create_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT id FROM accounts WHERE reset_token = %s", (token,))
            user = cur.fetchone()

            if not user:
                return "Неверная или устаревшая ссылка.", 400

            if request.method == 'POST':
                new_password = request.form.get('password')
                if len(new_password) < 8:  # Пример проверки длины пароля
                    return "Пароль должен содержать минимум 8 символов", 400
                
                hashed_password = generate_password_hash(new_password)

                cur.execute("""
                    UPDATE accounts 
                    SET password = %(hashed_password)s, reset_token = NULL
                    WHERE id = %(user_id)s
                    """, {'hashed_password': hashed_password, 'user_id': user['id']})
                conn.commit()

                return redirect(url_for('login'))

        except Exception as e:
            print(f"Ошибка при сбросе пароля для токена {token}: {e}")
            return f"Ошибка: {e}", 500
        finally:
            cur.close()
            conn.close()

        return render_template('auth/reset_password.html', token=token)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))