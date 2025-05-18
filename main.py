import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ критической ставки")
        self.root.state('zoomed')
        
        # Основной фрейм
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая часть (параметры и результаты)
        left_frame = tk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        # Параметры алгоритма
        param_frame = tk.Frame(left_frame)
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        params = [
            ("Начальная стоимость сервера ($):", "3000"),
            ("Стоимость продажи сервера (₽):", "400000"),
            ('Вес сервера (кг)', '50'),
            ('Длина сервера (см)', '100'),
            ('Ширина сервера (см)', '50'),
            ('Высота сервера (см)', '10'),
            ("Количество начислений процентов в год:", "12"),
            ("Время до продажи в годах:", "0.5"),
            ("Текущий курс доллара (₽):", "85"),
            ("Количество итераций:", "10000")
        ]
        
        self.entries = {}
        for text, default in params:
            tk.Label(param_frame, text=text).pack(anchor='w')
            entry = tk.Entry(param_frame)
            entry.insert(0, default)
            entry.pack(fill=tk.X)
            self.entries[text.split(":")[0]] = entry
        
        # Выбор налоговой схемы
        tk.Label(param_frame, text="Налоговая схема:").pack(anchor='w')
        self.tax_scheme = ttk.Combobox(param_frame, values=["INDIVIDUAL", "OSNO", "USN"])
        self.tax_scheme.set("OSNO")
        self.tax_scheme.pack(fill=tk.X)
        
        # Кнопки
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(button_frame, text="Рассчитать", command=self.run_analysis).pack(fill=tk.X)
        tk.Button(button_frame, text="Очистить", command=self.clear_results).pack(fill=tk.X)

        # Поле результата
        self.result_text = tk.Text(left_frame, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Правая часть (графики)
        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Холсты для графиков
        self.canvas_avia = None
        self.canvas_sea = None
        self.canvas_compare = None

    def calculate_shipping(self, method, weight, length, width, height):
        volume_weight = (length * width * height) / 5000

        if method == 'sea':
            volume_m3 = (length * width * height) / 6_000_000
            chargeable = max(weight / 1000, volume_m3)
            return 105 * chargeable
        else:
            chargeable = max(weight, volume_weight)
            return 2.7 * chargeable

    def get_customs_fee(self, value_rub):
        """ Возвращает сумму таможенного сбора в зависимости от стоимости товара в рублях """
        if value_rub <= 200_000:
            return 1_067
        elif value_rub <= 450_000:
            return 2_134
        elif value_rub <= 1_200_000:
            return 4_269
        elif value_rub <= 2_700_000:
            return 11_746
        elif value_rub <= 4_200_000:
            return 16_524
        elif value_rub <= 5_500_000:
            return 21_344
        elif value_rub <= 7_000_000:
            return 27_540
        else:
            return 30_000

    def calculate_critical_rate(self, buying_price, selling_price, delivery_price, delivery_time, tax_scheme, n, T):
        """
        Вычисляет критическую банковскую ставку r_кр, при которой сделка безубыточна.
        
        buying_price - начальная стоимость сервера (₽)
        selling_price - стоимость продажи сервера (₽)
        delivery_price - стоимость доставки (₽)
        delivery_time - время доставки
        tax_scheme - система налогообложения
        n - количество начислений процентов в год (по умолчанию 12)
        T - время до продажи в годах
        """

        customs_fee = self.get_customs_fee(buying_price + delivery_price)

        customs_tax = (buying_price + delivery_price + customs_fee) * 0.20
        total_cost = buying_price + delivery_price + customs_tax

        tax = self.calculate_tax(selling_price, tax_scheme, customs_tax, total_cost)
        # print("tax", tax, " customs_tax", customs_tax)
        # quit()

        additional_costs = delivery_price + tax

        # Проверка на возможность прибыли
        if selling_price <= additional_costs:
            return None
        
        return n * (((selling_price - additional_costs) / buying_price) ** (1 / (n * (T + delivery_time / 12))) - 1)
    
    def calculate_tax(self, selling_price, tax_scheme, customs_tax, total_cost):
        """
        Расчёт налогов
        
        selling_price - стоимость продажи сервера (₽)
        tax_scheme - система налогообложения
        customs_tax - таможенный НДС (₽)
        total_cost - стоимость сервера + стоимость доставки + таможенный НДС (₽)
        """
    
        if tax_scheme == "INDIVIDUAL":
            profit_tax = max(0, selling_price - total_cost) * 0.13
            return customs_tax + profit_tax
        elif tax_scheme == "OSNO":
            customs_tax_payable = max(0, selling_price * 0.20 - customs_tax)
            profit_tax = max(0, selling_price - total_cost) * 0.20
            return customs_tax_payable + profit_tax
        elif tax_scheme == "USN":
            usn6_tax = selling_price * 0.06
            usn15_tax = max(0, selling_price - total_cost) * 0.15
            return customs_tax + (usn6_tax if usn6_tax < usn15_tax else usn15_tax)

    def run_analysis(self):
        """Запуск анализа и отображение результатов"""
        try:
            # Получаем параметры из интерфейса
            params = {
                'buying_price': float(self.entries["Начальная стоимость сервера ($)"].get()),
                'selling_price': float(self.entries["Стоимость продажи сервера (₽)"].get()),
                'weight': float(self.entries["Вес сервера (кг)"].get()),
                'length': float(self.entries["Длина сервера (см)"].get()),
                'width': float(self.entries["Ширина сервера (см)"].get()),
                'height': float(self.entries["Высота сервера (см)"].get()),
                'n': int(self.entries["Количество начислений процентов в год"].get()),
                'T': float(self.entries["Время до продажи в годах"].get()),
                'usd_rate': float(self.entries["Текущий курс доллара (₽)"].get()),
                'n_simulations': int(self.entries["Количество итераций"].get()),
                'tax_scheme': self.tax_scheme.get()
            }

            # Запуск симуляции
            results_avia, results_sea = self.monte_carlo_simulation(params)
            
            # Очистка предыдущих результатов
            self.clear_results()
            
            # Вывод статистики
            self.print_stats(results_avia, results_sea)
            
            # Построение графиков
            self.plot_results(results_avia, results_sea)
            
        except ValueError as e:
            self.result_text.insert(tk.END, f"Ошибка ввода данных: {str(e)}\n")

    def monte_carlo_simulation(self, params):
        """Метод Монте-Карло"""
        critical_rates_avia = []
        critical_rates_sea = []
        
        for _ in range(params['n_simulations']):
            delivery_price_avia = self.calculate_shipping('air', params['weight'], params['length'], params['width'], params['height'])
            delivery_price_sea = self.calculate_shipping('sea', params['weight'], params['length'], params['width'], params['height'])

            usd1 = np.random.normal(params['usd_rate'], 2.5)
            usd2 = np.random.normal(params['usd_rate'], 2.5)
            
            buying_price = params['buying_price'] * usd1
            delivery_avia = delivery_price_avia * usd2
            delivery_sea = delivery_price_sea * usd2
            
            time_avia = max(0.01, np.random.normal(2, 0.5)) / 52
            time_sea = max(0.01, np.random.normal(12, 2)) / 52
            
            rate_avia = self.calculate_critical_rate(
                buying_price, params['selling_price'], delivery_avia,
                time_avia, params['tax_scheme'], params['n'], params['T']
            )
            
            rate_sea = self.calculate_critical_rate(
                buying_price, params['selling_price'], delivery_sea,
                time_sea, params['tax_scheme'], params['n'], params['T']
            )
            
            if rate_avia and 0 < rate_avia < 1:
                critical_rates_avia.append(rate_avia)
            if rate_sea and 0 < rate_sea < 1:
                critical_rates_sea.append(rate_sea)
        
        return critical_rates_avia, critical_rates_sea

    def print_stats(self, rates_avia, rates_sea):
        """Вывод статистики в текстовое поле"""
        def get_stats(rates, name):
            if not rates:
                return f"{name}: Нет подходящих значений\n"
            
            return (
                f"{name}:\n"
                f"Средняя ставка: {np.mean(rates):.2%}\n"
                f"Медианная ставка: {np.median(rates):.2%}\n"
                f"Минимальная ставка: {np.min(rates):.2%}\n"
                f"Максимальная ставка: {np.max(rates):.2%}\n\n"
            )
        
        self.result_text.insert(tk.END, get_stats(rates_avia, "Авиаперевозка"))
        self.result_text.insert(tk.END, get_stats(rates_sea, "Морская перевозка"))

    def plot_results(self, rates_avia, rates_sea):
        """Построение графиков"""
        # Очистка предыдущих графиков
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Верхний фрейм для первых двух графиков
        top_frame = tk.Frame(self.right_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)
        
        # Нижний фрейм для третьего графика
        bottom_frame = tk.Frame(self.right_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # График 1: Авиаперевозка
        if rates_avia:
            fig1 = plt.Figure(figsize=(5, 4))
            ax1 = fig1.add_subplot(111)
            ax1.hist(rates_avia, bins=50, color='red', edgecolor='black', density=True)
            ax1.axvline(np.mean(rates_avia), color='darkred', linestyle='--', label=f'Средняя: {np.mean(rates_avia):.2%}')
            ax1.set_title('Авиаперевозка')
            ax1.set_xlabel('Критическая банковская ставка')
            ax1.set_ylabel('Плотность вероятности')
            ax1.legend()
            ax1.grid(True)
            
            canvas1 = FigureCanvasTkAgg(fig1, top_frame)
            canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.canvas_avia = canvas1

        
        # График 2: Морская перевозка
        if rates_sea:
            fig2 = plt.Figure(figsize=(5, 4))
            ax2 = fig2.add_subplot(111)
            ax2.hist(rates_sea, bins=50, color='blue', edgecolor='black', density=True)
            ax2.axvline(np.mean(rates_sea), color='darkblue', linestyle='--', label=f'Средняя: {np.mean(rates_sea):.2%}')
            ax2.set_title('Морская перевозка')
            ax2.set_xlabel('Критическая банковская ставка')
            ax2.set_ylabel('Плотность вероятности')
            ax2.legend()
            ax2.grid(True)
            
            canvas2 = FigureCanvasTkAgg(fig2, top_frame)
            canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.canvas_sea = canvas2

        # График 3: Сравнение авиаперевозка и морской перевозки
        if rates_avia and rates_sea:
            fig3 = plt.Figure(figsize=(10, 5))
            ax3 = fig3.add_subplot(111)
            ax3.hist(rates_avia, bins=50, color='red', alpha = 0.5, edgecolor='black', density=True, label='Авиа')
            ax3.hist(rates_sea, bins=50, color='blue', alpha = 0.5, edgecolor='black', density=True, label='Море')
            ax3.axvline(np.mean(rates_avia), color='darkred', linestyle='--')
            ax3.axvline(np.mean(rates_sea), color='darkblue', linestyle='--')
            ax3.set_title('Авиаперевозка vs Морская перевозка')
            ax3.set_xlabel('Критическая банковская ставка')
            ax3.set_ylabel('Плотность вероятности')
            ax3.legend()
            ax3.grid(True)
            
            canvas3 = FigureCanvasTkAgg(fig3, bottom_frame)
            canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.canvas_compare = canvas3

    def clear_results(self):
        """Очистка результатов"""
        self.result_text.delete(1.0, tk.END)
        for widget in self.right_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
