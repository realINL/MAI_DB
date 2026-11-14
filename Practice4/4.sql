-- Задача 4.1. Определить средний размер комиссионных.
SELECT AVG(commission_pct) AS avg_commission FROM employees;
-- Задача 4.2. Найти количество товаров, в названии которых есть слово CORE.
SELECT COUNT(*) AS core_products
    FROM products
    WHERE LOWER(product_name) LIKE '%core%';
-- Задача 4.3. Вывести номера менеджеров и суммарную зарплату их подчиненных, имеющих нечетный рейтинг.
SELECT manager_id, SUM(salary) AS total_salary
    FROM employees
    WHERE manager_id IS NOT NULL AND MOD(rating_e, 2) = 1
    GROUP BY manager_id
    ORDER BY manager_id;
-- Задача 4.4. Вывести количество заказов, которые клиент 46 оформил в течение каждого года.
SELECT EXTRACT(YEAR FROM order_date) AS year, COUNT(*) AS orders_count
    FROM orders
    WHERE customer_id = 46
    GROUP BY EXTRACT(YEAR FROM order_date)
    ORDER BY year;
-- Задача 4.5. Вывести количество заказов, оформленных за каждый месяц 2019 года.
SELECT EXTRACT(MONTH FROM order_date) AS month, COUNT(*) AS orders_count
    FROM orders
    WHERE EXTRACT(YEAR FROM order_date) = 2019
    GROUP BY EXTRACT(MONTH FROM order_date)
    ORDER BY month;
-- Задача 4.6. Определить номера товаров, по которым было совершено меньше 10 продаж. Продажа - это строка в таблице Order_items.
SELECT product_id, COUNT(*) AS sales_count
    FROM order_items
    GROUP BY product_id
    HAVING COUNT(*) < 10
    ORDER BY product_id;
-- Задача 4.7. Вывести номера отделов, в которых более 5 ме-неджеров. Менеджером является сотрудник, который руководит другими сотрудниками. Ero employee_id содержится в столбце manager_id других сотрудников.
SELECT department_id, COUNT(DISTINCT employee_id) AS managers_count
    FROM employees
    WHERE employee_id IN (SELECT manager_id FROM employees WHERE manager_id IS NOT NULL)
    GROUP BY department_id
    HAVING COUNT(DISTINCT employee_id) > 5
    ORDER BY department_id;
-- Задача 4.8. Для заказов вывести номера товаров в заказе, их количество, общую стоимость каждого товара и всего заказа Вывести эти данные только для заказов, у которых order_id <10
SELECT order_id, product_id, quantity,
    quantity * unit_price AS item_total,
    SUM(quantity * unit_price) OVER (PARTITION BY order_id) AS order_total
    FROM order_items
    WHERE order_id < 10
    ORDER BY order_id, product_id;
-- Задача 4.9. Вывести количество заказов, оформленных в тече-ние каждого года, и количество заказов, которые оформил каждый клиент. Вывести только те строки, в которых количество заказов >4.
SELECT EXTRACT(YEAR FROM order_date) AS year, customer_id, COUNT(*) AS orders_count
    FROM orders
    GROUP BY GROUPING SETS ((EXTRACT(YEAR FROM order_date)), (customer_id))
    HAVING COUNT(*) > 4
    ORDER BY year NULLS LAST, customer_id NULLS LAST;
-- Задача 4.10. Для каждого отдела вывести суммарную зарплату сотрудников за весь период их работы.
SELECT department_id,
    SUM(salary * EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date))) AS total_salary
    FROM employees
    GROUP BY department_id
    ORDER BY department_id;