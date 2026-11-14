# Практическая работа №3. SQL запросы 
### Задача 3.1. 
> Для сотрудников, зарплата которых больше 1200 выведите столбец, который должен содержать полное имя сотрудника, зарплату и несколько звездочек (*), по одной звездочке на каждые $1000 зарплаты.

**Запрос:**
```sql
SELECT first_name, last_name, salary, repeat('*', (salary / 1000)::int) AS stars FROM employees WHERE salary > 1200
```
### Задача 3.2.
>Выведите названия городов (city), в которых 4-я буква t, а последняя е.

**Запрос:**
```sql
SELECT city from locations WHERE city LIKE '___t%e'
```
### Задача 3.3.
>Вывести данные о товарах, название которых содержит слово AMD и не содержит слово RYZEN. Предусмотреть то, что эти слова в названии товара могут быть представлены в разных регистрах.

**Запрос:**
```sql
SELECT product_name from products
    WHERE LOWER(product_name) LIKE '%amd%'
    AND LOWER(product_name) NOT LIKE '%ryzen%';
```
### Задача 3.4.
>Вывести названия товаров, первое слово которых состоит из 7 символов.

**Запрос:**
```sql
SELECT product_name FROM products WHERE product_name LIKE '_______ %' OR product_name LIKE '_______'
```
### Задача 3.5.
>Выведите названия отделов, которые состоят более чем из одного слова.

**Запрос:**
```sql
SELECT department_name from departments WHERE department_name LIKE '% %'
```
### Задача 3.6.
>Вывести данные о сотрудниках, которые были приняты на работу 21 апреля.

**Запрос:**
```sql
SELECT * from employees WHERE to_char(hire_date, 'MM-DD') = '04-21'
```
### Задача 3.7.
>Вывести даты текущего месяца, которые выпадают на воскресенье.

**Запрос:**
```sql
SELECT d::date AS sunday_date
    FROM generate_series(
        date_trunc('month', CURRENT_DATE),
        date_trunc('month', CURRENT_DATE) + interval '1 month' - interval '1 day',
        interval '1 day'
    ) AS d
    WHERE EXTRACT(dow FROM d) = 0;
```
### Задача 3.8.
>Вывести данные о сотрудниках и размере премии (bonus), которую они должны получить. Размер премии зависит от количества лет, которые проработал сотрудник: bonus = 1000 х количество лет.

**Запрос:**
```sql
SELECT first_name, last_name, hire_date,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date)) AS experience,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date)) * 1000 AS bonus
    FROM employees;
```
### Задача 3.9.
>Вывести данные о размере премии сотрудников, которые работают в отделе 30. Размер премии равен зарплате с учетом комиссионных, если сотрудник получает комиссионные, либо зарплате, умноженной на 1.2, если сотрудник не получает комиссионные.

**Запрос:**
```sql
SELECT employee_id, first_name, last_name, salary, commission_pct,
    CASE WHEN commission_pct IS NOT NULL THEN (salary * (1 + commission_pct)) - salary
         ELSE (salary * 0.2)
    END AS bonus
    FROM employees
    WHERE department_id = 30;
```
### Задача 3.10.
>Вывести данные об отделах, названия которых состоят более чем из одного слова. Результат выполнения запроса должен содержать: department_id, department_name, второе слово в названии отдела.

**Запрос:**
```sql
SELECT department_id, department_name, split_part(trim(department_name), ' ', 2) AS second_word
    FROM departments
    WHERE trim(department_name) LIKE '% %';
```
## Агрегатные функции
### Задача 4.1. 
>Определить средний размер комиссионных.

**Запрос:**
```sql
SELECT AVG(commission_pct) AS avg_commission FROM employees;
-- Задача 4.2. Найти количество товаров, в названии которых есть слово CORE.
SELECT COUNT(*) AS core_products
    FROM products
    WHERE LOWER(product_name) LIKE '%core%';
```
### Задача 4.3. 
>Вывести номера менеджеров и суммарную зарплату их подчиненных, имеющих нечетный рейтинг.

**Запрос:**
```sql
SELECT manager_id, SUM(salary) AS total_salary
    FROM employees
    WHERE manager_id IS NOT NULL AND MOD(rating_e, 2) = 1
    GROUP BY manager_id
    ORDER BY manager_id;
```
### Задача 4.4. 
>Вывести количество заказов, которые клиент 46 оформил в течение каждого года.

**Запрос:**
```sql
SELECT EXTRACT(YEAR FROM order_date) AS year, COUNT(*) AS orders_count
    FROM orders
    WHERE customer_id = 46
    GROUP BY EXTRACT(YEAR FROM order_date)
    ORDER BY year;
```
### Задача 4.5. 
>Вывести количество заказов, оформленных за каждый месяц 2019 года.

**Запрос:**
```sql
SELECT EXTRACT(MONTH FROM order_date) AS month, COUNT(*) AS orders_count
    FROM orders
    WHERE EXTRACT(YEAR FROM order_date) = 2019
    GROUP BY EXTRACT(MONTH FROM order_date)
    ORDER BY month;
```
### Задача 4.6. 
>Определить номера товаров, по которым было совершено меньше 10 продаж. Продажа - это строка в таблице Order_items.

**Запрос:**
```sql
SELECT product_id, COUNT(*) AS sales_count
    FROM order_items
    GROUP BY product_id
    HAVING COUNT(*) < 10
    ORDER BY product_id;
```
### Задача 4.7. 
>Вывести номера отделов, в которых более 5 ме-неджеров. Менеджером является сотрудник, который руководит другими сотрудниками. Ero employee_id содержится в столбце manager_id других сотрудников.

**Запрос:**
```sql
SELECT department_id, COUNT(DISTINCT employee_id) AS managers_count
    FROM employees
    WHERE employee_id IN (SELECT manager_id FROM employees WHERE manager_id IS NOT NULL)
    GROUP BY department_id
    HAVING COUNT(DISTINCT employee_id) > 5
    ORDER BY department_id;
### Задача 4.8. 
>Для заказов вывести номера товаров в заказе, их количество, общую стоимость каждого товара и всего заказа Вывести эти данные только для заказов, у которых order_id <10```

**Запрос:**
```sql
SELECT order_id, product_id, quantity,
    quantity * unit_price AS item_total,
    SUM(quantity * unit_price) OVER (PARTITION BY order_id) AS order_total
    FROM order_items
    WHERE order_id < 10
    ORDER BY order_id, product_id;
```
### Задача 4.9. 
>Вывести количество заказов, оформленных в тече-ние каждого года, и количество заказов, которые оформил каждый клиент. Вывести только те строки, в которых количество заказов >4.

**Запрос:**
```sql
SELECT EXTRACT(YEAR FROM order_date) AS year, customer_id, COUNT(*) AS orders_count
    FROM orders
    GROUP BY GROUPING SETS ((EXTRACT(YEAR FROM order_date)), (customer_id))
    HAVING COUNT(*) > 4
    ORDER BY year NULLS LAST, customer_id NULLS LAST;
```
### Задача 4.10. 
>Для каждого отдела вывести суммарную зарплату сотрудников за весь период их работы.

**Запрос:**
```sql
SELECT department_id,
    SUM(salary * EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date))) AS total_salary
    FROM employees
    GROUP BY department_id
    ORDER BY department_id;
```