$(document).ready(function() {
    // Calculate Flight Time
    $("input[name='distance_km'], input[name='speed_kmh']").on("input", function() {
        var distance = parseFloat($("input[name='distance_km']").val());
        var speed = parseFloat($("input[name='speed_kmh']").val());
    
        if (distance > 0 && speed > 0) {
            $.ajax({
                url: '/calculate_flight_time',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    distance: distance,
                    speed: speed
                }),
                success: function(response) {
                    if (response.flight_time !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#flight_time_h')
                            .val(response.flight_time.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете времени полета.");
                }
            });
        } else {
            $('#flight_time_h').val('').trigger('input'); // Обнуляем значение и триггерим изменение
        }
    });
    

    // Calculate Fuel Consumption
    $("input[name='flight_time_h'], input[name='fuel_consumption_per_hour_t']").on("input", function() {
        var time = parseFloat($("input[name='flight_time_h']").val());
        var consumption = parseFloat($("input[name='fuel_consumption_per_hour_t']").val());

        if (!isNaN(time) && !isNaN(consumption) && time > 0 && consumption > 0) {
            $.ajax({
                url: '/calculate_fuel_consumption',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    time: time,
                    consumption: consumption
                }),
                success: function(response) {
                    if (response.fuel_consumption !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#fuel_consumption_t')
                            .val(response.fuel_consumption.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете времени полета.");
                }
            });
        } else {
            $('#fuel_consumption_t').val('').trigger('input');
        }
    });

    $("input[name='initial_fuel_t'], input[name='fuel_consumption_t'], input[name='required_residual_fuel_t']").on("input", function() {
        var initial_fuel = parseFloat($("input[name='initial_fuel_t']").val());
        var fuel_consumption = parseFloat($("input[name='fuel_consumption_t']").val());
        var residual_fuel = parseFloat($("input[name='required_residual_fuel_t']").val());

        if (!isNaN(initial_fuel) && !isNaN(fuel_consumption) && !isNaN(residual_fuel) && initial_fuel > 0 && fuel_consumption > 0 && residual_fuel > 0) {
            $.ajax({
                url: '/calculate_refueled_fuel',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    initial_fuel: initial_fuel,
                    fuel_consumption: fuel_consumption,
                    residual_fuel: residual_fuel
                }),
                success: function(response) {
                    if (response.refueled_fuel !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#refueled_fuel_t')
                            .val(response.refueled_fuel.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете времени полета.");
                }
                
            });
        } else {
            $('#refueled_fuel_t').val('');
        }
    });


    $("input[name='initial_fuel_t'], input[name='fuel_consumption'], input[name='refueled_fuel_t']").on("input", function() {
        var initial_fuel = parseFloat($("input[name='initial_fuel_t']").val());
        var fuel_consumption = parseFloat($("input[name='fuel_consumption_t']").val());
        var refueled_fuel = parseFloat($("input[name='refueled_fuel_t']").val());
        console.log("Отправляем данные:", {
            initial_fuel: initial_fuel,
            fuel_consumption: fuel_consumption,
            refueled_fuel: refueled_fuel
        });
        

        if (!isNaN(initial_fuel) && !isNaN(fuel_consumption) && !isNaN(refueled_fuel) && initial_fuel > 0 && fuel_consumption > 0 && refueled_fuel > 0) {
            $.ajax({
                url: '/calculate_landing_fuel_residual',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    initial_fuel: initial_fuel,
                    fuel_consumption: fuel_consumption,
                    refueled_fuel: refueled_fuel
                }),
                success: function(response) {
                    if (response.landing_fuel_residual !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#landing_fuel_residual_t')
                            .val(response.landing_fuel_residual.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете расхода топлива.");
                }
            });
        } else {
            $('#landing_fuel_residual_t').val('');
        }
    });
    // calculate_takeoff_weight (Взлетный вес, т)
    $("input[name='initial_fuel_t'], input[name='empty_weight_t'], input[name='refueled_fuel_t'], input[name='max_commercial_load']").on("input", function() {
        var initial_fuel = parseFloat($("input[name='initial_fuel_t']").val());
        var empty_weight = parseFloat($("input[name='empty_weight_t']").val());
        var refueled_fuel = parseFloat($("input[name='refueled_fuel_t']").val());
        var commercial_load = parseFloat($("input[name='max_commercial_load']").val());
        console.log("Отправляем данные:", {
            commercial_load: commercial_load,
            initial_fuel: initial_fuel,
            empty_weight: empty_weight,
            refueled_fuel: refueled_fuel

        });
        

        if (!isNaN(initial_fuel) && !isNaN(empty_weight) && !isNaN(refueled_fuel) && !isNaN(commercial_load)) {
            $.ajax({
                url: '/calculate_takeoff_weight',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    commercial_load: commercial_load,
                    initial_fuel: initial_fuel,
                    empty_weight : empty_weight,
                    refueled_fuel: refueled_fuel
                }),
                success: function(response) {
                    if (response.takeoff_weight !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#takeoff_weight_t')
                            .val(response.takeoff_weight.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете расхода топлива.");
                }
            });
        } else {
            $('#takeoff_weight_t').val('');
        }
    });

    // calculate_takeoff_overweight (Перегрузка на взлете, т)
    $("input[name='max_takeoff_weight_t'], input[name='takeoff_weight_t']").on("input", function() {
        var takeoff_weight = parseFloat($("input[name='takeoff_weight_t']").val());
        var max_takeoff_weight = parseFloat($("input[name='max_takeoff_weight_t']").val());

        console.log("Отправляем данные:", {
            takeoff_weight: takeoff_weight,
            max_takeoff_weight: max_takeoff_weight
        });

        if (!isNaN(takeoff_weight) && !isNaN(max_takeoff_weight)) {
            $.ajax({
                url: '/calculate_takeoff_overweight',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    takeoff_weight: takeoff_weight,
                    max_takeoff_weight: max_takeoff_weight
                }),
                success: function(response) {
                    if (response.takeoff_overweight !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#takeoff_overweight_t')
                            .val(response.takeoff_overweight.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете перегрузки на взлете.");
                }
            });
        } else {
            $('#takeoff_overweight_t').val('');
        }
    });

    $("input[name='takeoff_weight_t'], input[name='fuel_consumption_t']").on("input", function() {
        var takeoff_weight = parseFloat($("input[name='takeoff_weight_t']").val());
        var fuel_consumption = parseFloat($("input[name='fuel_consumption_t']").val());

        console.log("Отправляем данные:", {
            takeoff_weight: takeoff_weight,
            fuel_consumption: fuel_consumption
        });

        if (!isNaN(takeoff_weight) && !isNaN(fuel_consumption)) {
            $.ajax({
                url: '/calculate_landing_weight',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    takeoff_weight: takeoff_weight,
                    fuel_consumption: fuel_consumption
                }),
                success: function(response) {
                    if (response.landing_weight !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#landing_weight_t')
                            .val(response.landing_weight.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете перегрузки на взлете.");
                }
            });
        } else {
            $('#landing_weight_t').val('');
        }
    });

    // calculate_landing_overweight (Перегрузка на посадке, т)
    $("input[name='landing_weight_t'], input[name='max_landing_weight_t']").on("input", function() {
        var landing_weight = parseFloat($("input[name='landing_weight_t']").val());
        var max_landing_weight = parseFloat($("input[name='max_landing_weight_t']").val());

        console.log("Отправляем данные:", {
            landing_weight: landing_weight,
            max_landing_weight: max_landing_weight
        });

        if (!isNaN(landing_weight) && !isNaN(max_landing_weight)) {
            $.ajax({
                url: '/calculate_landing_overweight',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    landing_weight: landing_weight,
                    max_landing_weight: max_landing_weight
                }),
                success: function(response) {
                    if (response.landing_overweight !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#landing_overweight_t')
                            .val(response.landing_overweight.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете перегрузки на взлете.");
                }
            });
        } else {
            $('#landing_overweight_t').val('');
        }
    });

    // aircraft_rent_cost (Аренда ВС)
    $("input[name='flight_time_h'], input[name='price_per_hour_usd']").on("input", function() {
        var flight_time = parseFloat($("input[name='flight_time_h']").val());
        var price_per_hour_usd = parseFloat($("input[name='price_per_hour_usd']").val());

        console.log("Отправляем данные:", {
            flight_time: flight_time,
            price_per_hour_usd: price_per_hour_usd
        });

        if (!isNaN(flight_time) && !isNaN(price_per_hour_usd)) {
            $.ajax({
                url: '/calculate_aircraft_rent_cost',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    flight_time: flight_time,
                    price_per_hour_usd: price_per_hour_usd
                }),
                success: function(response) {
                    if (response.aircraft_rent_cost !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#aircraft_rent_cost')
                            .val(response.aircraft_rent_cost.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете перегрузки на взлете.");
                }
            });
        } else {
            $('#aircraft_rent_cost').val('');
        }
    });

    // fuel_cost (Цена заправки, $)
    $("input[name='fuel_price_per_t'], input[name='refueled_fuel_t']").on("input", function() {
        var fuel_price_per = parseFloat($("input[name='fuel_price_per_t']").val());
        var refueled_fuel = parseFloat($("input[name='refueled_fuel_t']").val());

        console.log("Отправляем данные:", {
            fuel_price_per: fuel_price_per,
            refueled_fuel: refueled_fuel
        });

        if (!isNaN(fuel_price_per) && !isNaN(refueled_fuel)) {
            $.ajax({
                url: '/calculate_fuel_cost',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    fuel_price_per: fuel_price_per,
                    refueled_fuel: refueled_fuel
                }),
                success: function(response) {
                    if (response.fuel_cost !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#fuel_cost')
                            .val(response.fuel_cost.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете перегрузки на взлете.");
                }
            });
        } else {
            $('#fuel_cost').val('');
        }
    });

    // catering_price_per_meal (Цена питания, $)
    $("input[name='crew_count'], input[name='price_per_serving'], input[name='catering_count']").on("input", function() {
        var crew_count = parseFloat($("input[name='crew_count']").val());
        var price_per_serving = parseFloat($("input[name='price_per_serving']").val());
        var catering_count = parseFloat($("input[name='catering_count']").val());


        console.log("Отправляем данные:", {
            crew_count: crew_count,
            price_per_serving: price_per_serving,
            catering_count: catering_count
        });

        if (!isNaN(crew_count) && !isNaN(price_per_serving) && !isNaN(catering_count)) {
            $.ajax({
                url: '/calculate_catering_price_per_meal',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    crew_count: crew_count,
                    price_per_serving: price_per_serving,
                    catering_count: catering_count
                }),
                success: function(response) {
                    if (response.catering_price_per_meal !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#catering_price_per_meal')
                            .val(response.catering_price_per_meal.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете перегрузки на взлете.");
                }
            });
        } else {
            $('#catering_price_per_meal').val('');
        }
    });

    // navigation_fees (Трассовые аэронавигационные сборы, $)
    $("input[name='distance_km']").on("input", function() {
        var distance = parseFloat($("input[name='distance_km']").val());


        console.log("Отправляем данные:", {
            distance: distance,
        });

        if (!isNaN(distance)) {
            $.ajax({
                url: '/calculate_navigation_fees',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    distance: distance,

                }),
                success: function(response) {
                    if (response.navigation_fees !== undefined) {
                        // Установить значение поля и триггерить событие input
                        $('#navigation_fees')
                            .val(response.navigation_fees.toFixed(2))
                            .trigger('input'); // Триггер события для дальнейших расчетов
                    } else {
                        alert("Ошибка: данные не получены.");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Ошибка AJAX:", error);
                    alert("Ошибка при расчете перегрузки на взлете.");
                }
            });
        } else {
            $('#navigation_fees').val('');
        }
    });

    $("input[name='aircraft_rent_cost'], input[name='fuel_cost'], input[name='takeoff_landing_cost'], input[name='maintenance_cost'], input[name='parking_cost'], input[name='catering_price_per_meal'], input[name='crew_daily_allowance'], input[name='support_cost'], input[name='navigation_fees'], input[name='accommodation_cost'], input[name='miscellaneous_cost']").on("input", function() {
        var aircraft_rent_cost = parseFloat($("input[name='aircraft_rent_cost']").val()) || 0;
        var fuel_cost = parseFloat($("input[name='fuel_cost']").val()) || 0;
        var takeoff_landing_cost = parseFloat($("input[name='takeoff_landing_cost']").val()) || 0;
        var maintenance_cost = parseFloat($("input[name='maintenance_cost']").val()) || 0;
        var parking_cost = parseFloat($("input[name='parking_cost']").val()) || 0;
        var catering_price_per_meal = parseFloat($("input[name='catering_price_per_meal']").val()) || 0;
        var crew_daily_allowance = parseFloat($("input[name='crew_daily_allowance']").val()) || 0;
        var support_cost = parseFloat($("input[name='support_cost']").val()) || 0;
        var navigation_fees = parseFloat($("input[name='navigation_fees']").val()) || 0;
        var accommodation_cost = parseFloat($("input[name='accommodation_cost']").val()) || 0;
        var miscellaneous_cost = parseFloat($("input[name='miscellaneous_cost']").val()) || 0;
    
        console.log("Отправляем данные:", {
            aircraft_rent_cost,
            fuel_cost,
            takeoff_landing_cost,
            maintenance_cost,
            parking_cost,
            catering_price_per_meal,
            crew_daily_allowance,
            support_cost,
            navigation_fees,
            accommodation_cost,
            miscellaneous_cost
        });
    
        $.ajax({
            url: '/calculate_total_cost',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                aircraft_rent_cost,
                fuel_cost,
                takeoff_landing_cost,
                maintenance_cost,
                parking_cost,
                catering_price_per_meal,
                crew_daily_allowance,
                support_cost,
                navigation_fees,
                accommodation_cost,
                miscellaneous_cost
            }),
            success: function(response) {
                if (response.total_cost !== undefined) {
                    $('#total_cost')
                        .val(response.total_cost.toFixed(2))
                        .trigger('input');
                } else {
                    alert("Ошибка: данные не получены.");
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка AJAX:", error);
                alert("Ошибка при расчете перегрузки на взлете.");
            }
        });
    });
    
    $("input[name='total_cost']").on("input", function() {
        var total_cost = parseFloat($("input[name='total_cost']").val()) || 0;

    
        console.log("Отправляем данные:", {
            total_cost,
        });
    
        $.ajax({
            url: '/calculate_declared_flight_price',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                total_cost

            }),
            success: function(response) {
                if (response.declared_flight_price !== undefined) {
                    $('#declared_flight_price')
                        .val(response.declared_flight_price.toFixed(2))
                        .trigger('input');
                } else {
                    alert("Ошибка: данные не получены.");
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка AJAX:", error);
                alert("Ошибка при расчете перегрузки на взлете.");
            }
        });
    });

    $("input[name='declared_flight_price']").on("input", function() {
        var declared_flight_price = parseFloat($("input[name='declared_flight_price']").val()) || 0;

    
        console.log("Отправляем данные:", {
            declared_flight_price,
        });
    
        $.ajax({
            url: '/calculate_declared_flight_price_rub',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                declared_flight_price

            }),
            success: function(response) {
                if (response.declared_flight_price_rub !== undefined) {
                    $('#declared_flight_price_rub')
                        .val(response.declared_flight_price_rub.toFixed(2))
                        .trigger('input');
                } else {
                    alert("Ошибка: данные не получены.");
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка AJAX:", error);
                alert("Ошибка при расчете перегрузки на взлете.");
            }
        });
    });

    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();  // Отключаем стандартную отправку
    
        const formData = new FormData(this);
        console.log("Отправляемые данные:", Object.fromEntries(formData));
    
        fetch('/add', {
            method: 'POST',
            body: formData
        }).then(response => response.text()).then(console.log);
    });

    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener("blur", function () {
            if (this.value.trim() === "") {
                this.value = 0;
            }
        });
    });

    

    // Функция для получения данных
    function fetchData() {
        $.ajax({
            url: '/get_usd_to_rub_rate',
            type: 'POST',
            success: function(response) {
                if (response['Курс USD'] !== undefined) {
                    $('#usd-rate').text('Курс USD: ' + response['Курс USD'].toFixed(2) + ' руб.');
                } else if (response['Курс USD (последний сохраненный)'] !== undefined) {
                    $('#usd-rate').text('Курс USD (последний сохраненный): ' + response['Курс USD (последний сохраненный)'].toFixed(2) + ' руб.');
                } else {
                    $('#usd-rate').text("Ошибка: курс USD не найден.");
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка AJAX:", error);
                $('#usd-rate').text("Ошибка при получении данных о курсе USD.");
            }
        });
    }

    // Вызовем функцию для получения данных при загрузке страницы
    fetchData();
    document.addEventListener('keydown', function(event) {
        if (event.key === "Escape") {
            window.history.back();  // Возврат назад в истории браузера
        }
    });


    
});

function toggleSummary() {
    const summaryBox = document.getElementById("summaryBox");
    const toggleBtn = document.getElementById("toggleBtn");
    summaryBox.classList.toggle("collapsed");
    
    if (summaryBox.classList.contains("collapsed")) {
        toggleBtn.textContent = "Развернуть";
    } else {
        toggleBtn.textContent = "Свернуть";
    }
}

function syncRoute() {
    let route1 = document.getElementById("route_airports_1");
    let route2 = document.getElementById("route_airports_2");

    route1.addEventListener("input", function() {
        route2.value = route1.value;
    });

    route2.addEventListener("input", function() {
        route1.value = route2.value;
    });
}

syncRoute();