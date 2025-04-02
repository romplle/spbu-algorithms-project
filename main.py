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


def calculate_critical_rate(K0, P, C_delivery, T_delivery, tax, customs_fee, n, T):
    """
    Вычисляет критическую банковскую ставку r_кр, при которой сделка безубыточна.
    
    K0 - начальная стоимость сервера ($)
    P - стоимость продажи сервера ($)
    C_delivery - стоимость доставки ($)
    T_delivery - время доставки
    n - количество начислений процентов в год (по умолчанию 1)
    T - время до продажи в годах
    """

    C_dop = C_delivery + ((P + C_delivery) * tax) + customs_fee
    # print(C_dop)
    if P <= C_dop:  # Проверка на возможность прибыли
        return None  # Если выручка не покрывает затраты, смысла нет
    
    return n * (((P - C_dop) / K0) ** (1 / (n * (T + T_delivery / 12))) - 1)


def monte_carlo_simulation(n_simulations=100000):
    # Фиксированные параметры
    K0 = 3000         # Начальная стоимость сервера ($)
    P = 400_000       # Стоимость продажи сервера (₽)
    C_aviation = 120  # Стоимость авиадоставки ($)
    C_sea = 50        # Стоимость морской доставки ($)
    n = 12            # Начисление процентов раз в год
    tax = 0.2         # Налог
    T = 0.5           # Время до продажи в годах

    # Средний курс 87.5 руб., стандартное отклонение 5 руб.
    usd_rate_first = np.random.normal(loc=87.5, scale=2.5)
    usd_rate_second = np.random.normal(loc=87.5, scale=2.5)

    K0 *= usd_rate_first
    C_aviation *= usd_rate_second
    C_sea *= usd_rate_second
    
    critical_rates_avia = []
    critical_rates_sea = []
    
    for _ in range(n_simulations):
        T_aviation = np.random.normal(loc=2, scale=0.5) / 52  # Среднее 2 недели, стандартное отклонение 0.5 недели
        T_sea = np.random.normal(loc=12, scale=2) / 52        # Среднее 12 недель, стандартное отклонение 2 недели
        
        customs_fee = get_customs_fee(P)
        
        r_crit_avia = calculate_critical_rate(K0, P, C_aviation, T_aviation, tax, customs_fee, n, T)
        r_crit_sea = calculate_critical_rate(K0, P, C_sea, T_sea, tax, customs_fee, n, T)
        
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
