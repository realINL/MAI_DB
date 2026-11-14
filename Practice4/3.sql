-- Задача 3.1. Для сотрудников, зарплата которых больше 1200 выведите столбец, который должен содержать полное имя сотрудника, зарплату и несколько звездочек (*), по одной звездочке на каждые $1000 зарплаты.
SELECT first_name, last_name, salary, repeat('*', (salary / 1000)::int) AS stars FROM employees WHERE salary > 1200
-- Задача 3.2. Выведите названия городов (city), в которых 4-я буква t, а последняя е.
SELECT city from locations WHERE city LIKE '___t%e'
-- Задача 3.3. Вывести данные о товарах, название которых содержит слово AMD и не содержит слово RYZEN. Предусмотреть то, что эти слова в названии товара могут быть представлены в разных регистрах.
SELECT product_name from products
    WHERE LOWER(product_name) LIKE '%amd%'
    AND LOWER(product_name) NOT LIKE '%ryzen%';
-- Задача 3.4. Вывести названия товаров, первое слово которых состоит из 7 символов.
SELECT product_name FROM products WHERE product_name LIKE '_______ %' OR product_name LIKE '_______'
-- Задача 3.5. Выведите названия отделов, которые состоят более чем из одного слова.
SELECT department_name from departments WHERE department_name LIKE '% %'
-- Задача 3.6. Вывести данные о сотрудниках, которые были приняты на работу 21 апреля.
SELECT * from employees WHERE to_char(hire_date, 'MM-DD') = '04-21'
-- Задача 3.7. Вывести даты текущего месяца, которые выпадают на воскресенье.
SELECT d::date AS sunday_date
    FROM generate_series(
        date_trunc('month', CURRENT_DATE),
        date_trunc('month', CURRENT_DATE) + interval '1 month' - interval '1 day',
        interval '1 day'
    ) AS d
    WHERE EXTRACT(dow FROM d) = 0;
-- Задача 3.8. Вывести данные о сотрудниках и размере премии (bonus), которую они должны получить. Размер премии зависит от количества лет, которые проработал сотрудник: bonus = 1000 х количество лет.
SELECT first_name, last_name, hire_date,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date)) AS experience,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date)) * 1000 AS bonus
    FROM employees;
-- Задача 3.9. Вывести данные о размере премии сотрудников, которые работают в отделе 30. Размер премии равен зарплате с учетом комиссионных, если сотрудник получает комиссионные, либо зарплате, умноженной на 1.2, если сотрудник не получает комиссионные.
SELECT employee_id, first_name, last_name, salary, commission_pct,
    CASE WHEN commission_pct IS NOT NULL THEN (salary * (1 + commission_pct)) - salary
         ELSE (salary * 0.2)
    END AS bonus
    FROM employees
    WHERE department_id = 30;
-- Задача 3.10. Вывести данные об отделах, названия которых состоят более чем из одного слова. Результат выполнения запроса должен содержать: department_id, department_name, второе слово в названии отдела.
SELECT department_id, department_name, split_part(trim(department_name), ' ', 2) AS second_word
    FROM departments
    WHERE trim(department_name) LIKE '% %';