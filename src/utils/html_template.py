html_template = """<!DOCTYPE html>
    <html lang="ru" class="dark">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sugarscape Analytics Dashboard</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
    tailwind.config = {{
    darkMode: 'class',
    theme: {{
    extend: {{
    colors: {{
    slate: {{ 950: '#020617' }}
    }}
    }}
    }}
    }}
    </script>
    
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    
    <style>
    body {{ overflow-x: hidden; }}
    .chart-container {{ width: 100%; height: 400px; }}
    </style>
    </head>
    <body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 font-sans antialiased">

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
        <header class="flex justify-between items-center mb-8 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
        <h1 class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-emerald-500 bg-clip-text text-transparent">
        Sugarscape Core
        </h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Интерактивный аналитический отчет</p>
        </div>
        <button id="theme-toggle" class="p-2 rounded-lg bg-white dark:bg-slate-800 shadow-md hover:shadow-lg transition-all focus:outline-none ring-2 ring-blue-500/20">
        <span id="theme-icon">🌙</span>
        </button>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
        <p class="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">Финальная популяция</p>
        <p id="kpi-agents" class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-2">--</p>
        </div>
        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
        <p class="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">Медиана благосостояния</p>
        <p id="kpi-welfare" class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-2">--</p>
        </div>
        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
        <p class="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">Коэффициент Джини</p>
        <p id="kpi-gini" class="text-2xl font-bold text-red-600 dark:text-red-400 mt-2">--</p>
        </div>
        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
        <p class="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">Всего шагов</p>
        <p id="kpi-steps" class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-2">--</p>
        </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 col-span-1 lg:col-span-2">
        <h3 class="text-lg font-semibold mb-4">Динамика популяции и демографии</h3>
        <div id="chart-population" class="chart-container"></div>
        </div>

        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
        <h3 class="text-lg font-semibold mb-4">Общие ресурсы (Сахар/Специи)</h3>
        <div id="chart-resources" class="chart-container"></div>
        </div>

        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
        <h3 class="text-lg font-semibold mb-4">Благосостояние и Неравенство</h3>
        <div id="chart-welfare" class="chart-container"></div>
        </div>

        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
        <h3 class="text-lg font-semibold mb-4">Рыночные цены (Exchange Rates)</h3>
        <div id="chart-prices" class="chart-container"></div>
        </div>

        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
        <h3 class="text-lg font-semibold mb-4">Распределение богатства (Final Step)</h3>
        <div id="chart-distribution" class="chart-container"></div>
        </div>
        </div>

        <!-- AI CHAT WIDGET START -->
        <div id="ai-chat-widget" class="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-2 hidden">
        <!-- Окно чата -->
        <div id="chat-window" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-2xl w-80 h-96 flex flex-col overflow-hidden transition-all duration-300 transform translate-y-4 opacity-0 scale-95 pointer-events-none">
        <div class="p-3 bg-gradient-to-r from-blue-600 to-emerald-500 text-white font-semibold flex justify-between items-center cursor-pointer select-none" onclick="toggleChat()">
        <span>🤖 AI Аналитик</span>
        <button class="hover:bg-white/20 rounded p-1">✕</button>
        </div>
        <div id="chat-messages" class="flex-1 overflow-y-auto p-3 space-y-2 text-sm bg-slate-50 dark:bg-slate-950">
        <div class="text-center text-slate-400 text-xs mt-10 italic">Задайте вопрос о симуляции...</div>
        </div>
        <div class="p-2 border-t border-slate-200 dark:border-slate-700 flex gap-2 bg-white dark:bg-slate-900">
        <input type="text" id="chat-input" placeholder="Почему упала популяция?" 
        class="flex-1 bg-slate-100 dark:bg-slate-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white placeholder-slate-400"
        onkeydown="if(event.key==='Enter') sendChat()">
        <button onclick="sendChat()" class="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-3 py-2 text-sm font-bold transition-colors">➤</button>
        </div>
        </div>
        <!-- Кнопка открытия -->
        <button onclick="toggleChat()" class="bg-gradient-to-r from-blue-600 to-emerald-500 text-white p-3 rounded-full shadow-lg hover:scale-110 transition-transform active:scale-95">
        💬
        </button>
        </div>
                
        <footer class="mt-12 text-center text-xs text-slate-400 dark:text-slate-600">
        Generated by Simulation Core • Powered by Plotly & Tailwind
        </footer>
        </div>

    <script>
        const rawData = __DATA_JSON__;

        const toggleBtn = document.getElementById('theme-toggle');
        const iconSpan = document.getElementById('theme-icon');
        const htmlEl = document.documentElement;
        let isDark = true;

        function updateChartsTheme() {{
        // Используем "плоские" ключи для надежного обновления вложенных осей Plotly
        const layoutUpdates = {{
        paper_bgcolor: isDark ? 'rgba(0,0,0,0)' : 'rgba(255,255,255,0)',
        plot_bgcolor: isDark ? 'rgba(0,0,0,0)' : 'rgba(255,255,255,0)',
        'font.color': isDark ? '#e2e8f0' : '#1e293b',
        'xaxis.gridcolor': isDark ? '#334155' : '#cbd5e1',
        'yaxis.gridcolor': isDark ? '#334155' : '#cbd5e1',
        'yaxis2.gridcolor': isDark ? '#334155' : '#cbd5e1'
        }};
        
        ['chart-population', 'chart-resources', 'chart-welfare', 'chart-prices', 'chart-distribution'].forEach(id => {{
        if(document.getElementById(id)) {{
        Plotly.relayout(id, layoutUpdates);
        }}
        }});
        }}

        toggleBtn.addEventListener('click', () => {{
        isDark = !isDark;
        if(isDark) {{
        htmlEl.classList.add('dark');
        iconSpan.textContent = '🌙';
        }} else {{
        htmlEl.classList.remove('dark');
        iconSpan.textContent = '☀️';
        }}
        updateChartsTheme();
        }});

        function getBaseLayout(title) {{
        return {{
        title: {{ text: title, font: {{ size: 16 }} }},
        margin: {{ l: 50, r: 20, t: 40, b: 40 }},
        showlegend: true,
        legend: {{ orientation: 'h', y: -0.2 }},
        autosize: true,
        responsive: true
        }};
        }}

        function renderPopulationChart() {{
        const traceAgents = {{
        x: rawData.steps, y: rawData.agents, type: 'scatter', mode: 'lines+markers',
        name: 'Популяция', line: {{ color: '#3b82f6', width: 2 }}, marker: {{ size: 4 }}
        }};
        
            const traceBirths = {{
            x: rawData.steps, y: rawData.births, type: 'bar', name: 'Рождения',
            marker: {{ color: 'rgba(16, 185, 129, 0.6)' }}, visible: false
            }};
            
            const traceDeaths = {{
            x: rawData.steps, y: rawData.deaths.map(d => -d), type: 'bar', name: 'Смерти',
            marker: {{ color: 'rgba(239, 68, 68, 0.6)' }}, visible: false
            }};

            const layout = getBaseLayout('Динамика популяции');
            layout.yaxis = {{ title: 'Количество агентов' }};
            layout.yaxis2 = {{ title: 'Естественное движение', overlaying: 'y', side: 'right', rangemode: 'tozero' }};
            
            Plotly.newPlot('chart-population', [traceAgents, traceBirths, traceDeaths], layout);
            }}

        function renderResourcesChart() {{
        const traceSugar = {{ x: rawData.steps, y: rawData.sugar, type: 'scatter', mode: 'lines', name: 'Сахар', line: {{ color: '#f59e0b', width: 2 }} }};
        const traceSpicy = {{ x: rawData.steps, y: rawData.spicy, type: 'scatter', mode: 'lines', name: 'Специи', line: {{ color: '#ef4444', width: 2 }} }};
        Plotly.newPlot('chart-resources', [traceSugar, traceSpicy], getBaseLayout('Запасы ресурсов'));
        }}

        function renderWelfareChart() {{
        const traceWelfare = {{ x: rawData.steps, y: rawData.welfare, type: 'scatter', mode: 'lines', name: 'Медиана благосостояния', line: {{ color: '#10b981', width: 2 }} }};
        const traceGini = {{ x: rawData.steps, y: rawData.gini, type: 'scatter', mode: 'lines', name: 'Коэфф. Джини', line: {{ color: '#8b5cf6', dash: 'dashdot', width: 2 }}, yaxis: 'y2' }};

            const layout = getBaseLayout('Благосостояние и Неравенство');
            // ЗАЩИТА: Если массив пустой, Math.max вернет -Infinity и сломает график
            const maxWelfare = rawData.welfare.length > 0 ? Math.max(...rawData.welfare) : 100;
            layout.yaxis = {{ title: 'Уровень жизни', range: [0, maxWelfare * 1.1] }};
            layout.yaxis2 = {{ title: 'Неравенство (0-1)', overlaying: 'y', side: 'right', range: [0, 1] }};
            
            Plotly.newPlot('chart-welfare', [traceWelfare, traceGini], layout);
            }}

        function renderPricesChart() {{
        const validIndices = rawData.price_sugar.map((v, i) => v > 0 ? i : null).filter(i => i !== null);
        if(validIndices.length === 0) {{
        document.getElementById('chart-prices').innerHTML = '<div class="flex items-center justify-center h-full text-slate-400">Нет данных о торгах</div>';
        return;
        }}

            const filteredSteps = validIndices.map(i => rawData.steps[i]);
            const filteredSugarP = validIndices.map(i => rawData.price_sugar[i]);
            const filteredSpiceP = validIndices.map(i => rawData.price_spice[i]);

            const traceSugarPrice = {{ x: filteredSteps, y: filteredSugarP, type: 'scatter', mode: 'lines+markers', name: 'Цена Сахара (в Специях)', line: {{ color: '#f59e0b', width: 2 }}, marker: {{ size: 6 }} }};
            const traceSpicePrice = {{ x: filteredSteps, y: filteredSpiceP, type: 'scatter', mode: 'lines+markers', name: 'Цена Специй (в Сахаре)', line: {{ color: '#ef4444', width: 2, dash: 'dot' }}, marker: {{ size: 6 }} }};

            Plotly.newPlot('chart-prices', [traceSugarPrice, traceSpicePrice], getBaseLayout('Обменные курсы'));
            }}

        function renderDistributionChart() {{
            if(!rawData.final_wealth_dist || rawData.final_wealth_dist.length === 0) {{
                 document.getElementById('chart-distribution').innerHTML = '<div class="flex items-center justify-center h-full text-slate-400">Нет данных</div>';
                return;
            }}

            const traceHist = {{ 
                x: rawData.final_wealth_dist, 
                type: 'histogram', 
                histnorm: 'probability density', 
                marker: {{ color: '#3b82f6', opacity: 0.7 }}, 
                nbinsx: 30 
            }};
            
            // Получаем базовый лейаут
            const layout = getBaseLayout('Гистограмма распределения благосостояния');
            
            // Безопасно добавляем подписи осей, проверяя существование объектов
            // Для histogram Plotly часто сам управляет осями, поэтому лучше использовать merge или проверку
            if (!layout.xaxis) layout.xaxis = {};
            if (!layout.yaxis) layout.yaxis = {};
            
            layout.xaxis.title = 'Уровень благосостояния';
            layout.yaxis.title = 'Плотность вероятности';
            layout.showlegend = false;

            try {
                Plotly.newPlot('chart-distribution', [traceHist], layout);
            } catch (e) {
                console.error("Error rendering distribution chart:", e);
                document.getElementById('chart-distribution').innerHTML = '<div class="text-red-500 p-4">Ошибка отрисовки графика распределения.</div>';
            }
        }}

        // --- AI CHAT WIDGET LOGIC ---
        function toggleChat() {{
            const widget = document.getElementById('ai-chat-widget');
            const chatWindow = document.getElementById('chat-window');
            widget.classList.remove('hidden');
            
            const isHidden = chatWindow.classList.contains('pointer-events-none');
            if (isHidden) {{
                chatWindow.classList.remove('pointer-events-none', 'opacity-0', 'scale-95', 'translate-y-4');
                document.getElementById('chat-input').focus();
            }} else {{
                chatWindow.classList.add('pointer-events-none', 'opacity-0', 'scale-95', 'translate-y-4');
            }}
        }}

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = wsProtocol + '//' + window.location.host + '/ws';
        let ws = null;
        let currentAiDiv = null;

        function initWebSocket() {{
            ws = new WebSocket(wsUrl);
            ws.onopen = () => console.log('✅ AI WebSocket connected');
            
            ws.onmessage = (event) => {{
                const data = event.data;
                if (data === '[DONE]') {{
                    currentAiDiv = null;
                    return;
                }}
                if (data.startsWith('[ERROR]')) {{
                    if (currentAiDiv) currentAiDiv.innerHTML = '<span class="text-red-500">' + data + '</span>';
                    currentAiDiv = null;
                    return;
                }}
                if (currentAiDiv) {{
                    if (currentAiDiv.textContent === '...') currentAiDiv.textContent = '';
                    currentAiDiv.textContent += data;
                    document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
                }}
            }};
            
            ws.onclose = () => {{
                console.log('🔌 AI WebSocket closed. Reconnecting in 3s...');
                setTimeout(initWebSocket, 3000);
            }};
            
            ws.onerror = (err) => {{
                console.error('❌ AI WebSocket error:', err);
                ws.close();
            }};
        }}

        function sendChat() {{
            if (!ws || ws.readyState !== WebSocket.OPEN) {{
                alert('Соединение с AI-сервером не установлено. Подождите...');
                return;
            }}
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;
            
            const messagesDiv = document.getElementById('chat-messages');
            
            // Сообщение пользователя
            const userWrap = document.createElement('div');
            userWrap.className = 'flex justify-end mb-2';
            userWrap.innerHTML = '<div class="bg-blue-600 text-white rounded-lg px-3 py-2 max-w-[80%] break-words">' + message + '</div>';
            messagesDiv.appendChild(userWrap);
            
            input.value = '';
            
            // Плейсхолдер ответа AI
            const aiWrap = document.createElement('div');
            aiWrap.className = 'flex justify-start mb-2';
            const aiDiv = document.createElement('div');
            aiDiv.className = 'bg-slate-200 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-lg px-3 py-2 max-w-[80%] whitespace-pre-wrap break-words';
            aiDiv.textContent = '...';
            aiWrap.appendChild(aiDiv);
            messagesDiv.appendChild(aiWrap);
            
            currentAiDiv = aiDiv;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            ws.send(JSON.stringify({{message: message}}));
        }}

        window.onload = () => {{
        // ЗАЩИТА: Безопасное обновление KPI без падения на .toFixed()
        if(rawData.agents && rawData.agents.length > 0) {{
        document.getElementById('kpi-agents').textContent = rawData.agents[rawData.agents.length - 1] || 0;
        const lastWelfare = rawData.welfare.length > 0 ? rawData.welfare[rawData.welfare.length - 1] : 0;
        const lastGini = rawData.gini.length > 0 ? rawData.gini[rawData.gini.length - 1] : 0;
        
                document.getElementById('kpi-welfare').textContent = lastWelfare.toFixed(2);
                document.getElementById('kpi-gini').textContent = lastGini.toFixed(3);
                document.getElementById('kpi-steps').textContent = rawData.steps.length;
                }}

            renderPopulationChart();
            renderResourcesChart();
            renderWelfareChart();
            renderPricesChart();
            renderDistributionChart();
            
            updateChartsTheme();
            initWebSocket();
            }};
            </script>
            </body>
            </html>"""