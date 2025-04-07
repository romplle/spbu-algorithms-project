import numpy as np
import matplotlib.pyplot as plt

def get_customs_fee(value_rub):
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


def calculate_critical_rate(buying_price, selling_price, delivery_price, delivery_time, tax_scheme, n, T):
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

    customs_fee = get_customs_fee(buying_price + delivery_price)

    customs_tax = (buying_price + delivery_price + customs_fee) * 0.20
    total_cost = buying_price + delivery_price + customs_tax

    tax = calculate_tax(selling_price, tax_scheme, customs_tax, total_cost)
    # print("tax", tax, " customs_tax", customs_tax)
    # quit()

    additional_costs = delivery_price + tax

    # Проверка на возможность прибыли
    if selling_price <= additional_costs:
        return None
    
    return n * (((selling_price - additional_costs) / buying_price) ** (1 / (n * (T + delivery_time / 12))) - 1)


def calculate_tax(selling_price, tax_scheme, customs_tax, total_cost):
    """
    Расчёт налогов
    
    selling_price - стоимость продажи сервера (₽)
    tax_scheme - система налогообложения
    customs_tax - таможенный НДС (₽)
    total_cost - стоимость сервера + стоимость доставки + таможенный НДС (₽)
    """
    
    if tax_scheme == "INDIVIDUAL":
        profit_tax = max(0, selling_price - total_cost * 0.13)
        return customs_tax + profit_tax
    
    elif tax_scheme == "OSNO":
        customs_tax_payable  = max(0, selling_price * 0.20 - customs_tax)
        profit_tax = max(0, selling_price - total_cost) * 0.20
        return customs_tax_payable + profit_tax
    
    elif tax_scheme == "USN":
        usn6_tax = selling_price * 0.06
        usn15_tax = max(0, selling_price - total_cost) * 0.15
        
        if usn6_tax < usn15_tax:
            return customs_tax + usn6_tax
        else:
            return customs_tax + usn15_tax


def monte_carlo_simulation(n_simulations=1_000_000, tax_scheme="OSNO"):
    """
    Метод Монте-Карло
    
    n_simulations - количество итераций метода Монте-Карло
    tax_scheme - система налогообложения
    """
    
    # Фиксированные параметры
    buying_price = 3000         # Начальная стоимость сервера ($)
    selling_price = 400_000     # Стоимость продажи сервера (₽)
    delivery_price_avia = 120   # Стоимость авиадоставки ($)
    delivery_price_sea = 50     # Стоимость морской доставки ($)
    n = 12                      # Начисление процентов раз в год
    T = 0.5                     # Время до продажи в годах
    usd_rate_now = 87.5         # Текущий курс доллара (₽)

    usd_rate_first = np.random.normal(loc=usd_rate_now, scale=2.5)
    usd_rate_second = np.random.normal(loc=usd_rate_now, scale=2.5)

    # usd_rate_first = np.random.uniform(85, 92.5)
    # usd_rate_second = np.random.uniform(85, 92.5)

    buying_price *= usd_rate_first
    delivery_price_avia *= usd_rate_second
    delivery_price_sea *= usd_rate_second
    
    critical_rates_avia = []
    critical_rates_sea = []
    
    for _ in range(n_simulations):
        delivery_time_avia = np.random.normal(loc=2, scale=0.5) / 52  # Среднее 2 недели, стандартное отклонение 0.5 недели
        delivery_time_sea = np.random.normal(loc=12, scale=2) / 52    # Среднее 12 недель, стандартное отклонение 2 недели
        
        r_crit_avia = calculate_critical_rate(buying_price, selling_price, delivery_price_avia, delivery_time_avia, tax_scheme, n, T)
        r_crit_sea = calculate_critical_rate(buying_price, selling_price, delivery_price_sea, delivery_time_sea, tax_scheme, n, T)
        
        if r_crit_avia is not None and 0 < r_crit_avia < 1:
            critical_rates_avia.append(r_crit_avia)

        if r_crit_sea is not None and 0 < r_crit_sea < 1:
            critical_rates_sea.append(r_crit_sea)

    # Вывод статистики
    def print_stats(rates, method):
        if rates:
            print(f"\n{method} доставка:")
            print(f"Средняя критическая ставка: {np.mean(rates):.2%}")
            print(f"Медианная критическая ставка: {np.median(rates):.2%}")
            print(f"Минимальная ставка: {np.min(rates):.2%}")
            print(f"Максимальная ставка: {np.max(rates):.2%}")
        else:
            print(f"\n{method} доставка: Нет подходящих значений.")

    print_stats(critical_rates_avia, "Авиаперевозка")
    print_stats(critical_rates_sea, "Морская перевозка")

    # График 1: Авиационная доставка
    plt.figure(figsize=(12, 6))
    plt.hist(critical_rates_avia, bins=50, color='red', edgecolor='black', density=True)
    plt.axvline(np.mean(critical_rates_avia), color='darkred', linestyle='--', label=f'Средняя: {np.mean(critical_rates_avia):.2%}')
    plt.title('Распределение критических банковских ставок (Авиаперевозка)')
    plt.xlabel('Критическая банковская ставка')
    plt.ylabel('Плотность вероятности')
    plt.legend()
    plt.grid(True)
    plt.show()

    # График 2: Морская доставка
    plt.figure(figsize=(12, 6))
    plt.hist(critical_rates_sea, bins=50, color='blue', edgecolor='black', density=True)
    plt.axvline(np.mean(critical_rates_sea), color='darkblue', linestyle='--', label=f'Средняя: {np.mean(critical_rates_sea):.2%}')
    plt.title('Распределение критических банковских ставок (Морская перевозка)')
    plt.xlabel('Критическая банковская ставка')
    plt.ylabel('Плотность вероятности')
    plt.legend()
    plt.grid(True)
    plt.show()

    # График 3: Сравнение авиа и морской доставки
    plt.figure(figsize=(12, 6))
    plt.hist(critical_rates_avia, bins=10, color='red', edgecolor='black', density=True, label='Авиаперевозка')
    plt.hist(critical_rates_sea, bins=10, color='blue', edgecolor='black', density=True, label='Морская перевозка')
    
    plt.axvline(np.mean(critical_rates_avia), color='darkred', linestyle='--', label=f'Средняя (авиа): {np.mean(critical_rates_avia):.2%}')
    plt.axvline(np.mean(critical_rates_sea), color='darkblue', linestyle='--', label=f'Средняя (море): {np.mean(critical_rates_sea):.2%}')
        
    plt.title('Сравнение критических банковских ставок\nАвиаперевозка vs Морская перевозка')
    plt.xlabel('Критическая банковская ставка')
    plt.ylabel('Плотность вероятности')
    plt.legend()
    plt.grid(True)
    plt.show()

monte_carlo_simulation()
