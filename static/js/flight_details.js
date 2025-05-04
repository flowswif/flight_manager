$(document).ready(function() {
    // Calculate Flight Time

    

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
    document.getElementById("downloadExcel").addEventListener("click", function () {
        window.location.href = "/download_excel"; // URL должен соответствовать маршруту на сервере
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



