WITH
-- 1. Заполняем фамилии и забираем их ID
inserted_fam AS (
    INSERT INTO fam (f_val)
    VALUES ('Иванов'), ('Петров'), ('Сидоров'), ('Кузнецов'), ('Смирнов')
    RETURNING u_id, f_val
),
-- 2. Заполняем имена и забираем их ID
inserted_nam AS (
    INSERT INTO nam (n_val)
    VALUES ('Иван'), ('Пётр'), ('Сидор'), ('Алексей'), ('Дмитрий')
    RETURNING u_id, n_val
),
-- 3. Заполняем отчества и забираем их ID
inserted_otc AS (
    INSERT INTO otc (o_val)
    VALUES ('Иванович'), ('Петрович'), ('Сидорович'), ('Николаевич'), ('Сергеевич')
    RETURNING u_id, o_val
),
-- 4. Заполняем улицы и забираем их ID
inserted_street AS (
    INSERT INTO street (s_val)
    VALUES ('Ленина'), ('Пушкина'), ('Садовая'), ('Новая'), ('Лесная')
    RETURNING u_id, s_val
)

-- 5. Вставляем 5 строк в финальную таблицу people, сопоставляя нужные ID
INSERT INTO people (fam, nam, otc, street, bldn, bldn_k, appr, telef_n)
VALUES
    (
        (SELECT u_id FROM inserted_fam WHERE f_val = 'Иванов'),
        (SELECT u_id FROM inserted_nam WHERE n_val = 'Иван'),
        (SELECT u_id FROM inserted_otc WHERE o_val = 'Иванович'),
        (SELECT u_id FROM inserted_street WHERE s_val = 'Ленина'),
        '10', 'А', 45, '+79991112233'
    ),
    (
        (SELECT u_id FROM inserted_fam WHERE f_val = 'Петров'),
        (SELECT u_id FROM inserted_nam WHERE n_val = 'Пётр'),
        (SELECT u_id FROM inserted_otc WHERE o_val = 'Петрович'),
        (SELECT u_id FROM inserted_street WHERE s_val = 'Пушкина'),
        '25', NULL, 12, '+79994445566'
    ),
    (
        (SELECT u_id FROM inserted_fam WHERE f_val = 'Сидоров'),
        (SELECT u_id FROM inserted_nam WHERE n_val = 'Сидор'),
        (SELECT u_id FROM inserted_otc WHERE o_val = 'Сидорович'),
        (SELECT u_id FROM inserted_street WHERE s_val = 'Садовая'),
        '5', '2', 118, '+79997778899'
    ),
    (
        (SELECT u_id FROM inserted_fam WHERE f_val = 'Кузнецов'),
        (SELECT u_id FROM inserted_nam WHERE n_val = 'Алексей'),
        (SELECT u_id FROM inserted_otc WHERE o_val = 'Николаевич'),
        (SELECT u_id FROM inserted_street WHERE s_val = 'Новая'),
        '14', NULL, 3, '+79990001122'
    ),
    (
        (SELECT u_id FROM inserted_fam WHERE f_val = 'Смирнов'),
        (SELECT u_id FROM inserted_nam WHERE n_val = 'Дмитрий'),
        (SELECT u_id FROM inserted_otc WHERE o_val = 'Сергеевич'),
        (SELECT u_id FROM inserted_street WHERE s_val = 'Лесная'),
        '88', 'Б', 9, '+79993334455'
    );


INSERT INTO people (f_val, n_val, o_val, s_val, bldn, bldn_k, appr, telef_n)
VALUES ( 'Иванов', 'Олег', 'Иванович', 'Дубосековская', '25', 'k5', 422, '88005553535'),
       ('Петров', 'Андрей', 'Иванович', 'Дубосековская', '26', 'k5', 44, '88005553536'),
       ('Степанов', 'Петр', 'Васильевич', 'Дубосековская', '32', 'k1', 12, '88005553537')
