-- Объединение таблицы
-- SELECT people.u_id, fam.f_val, nam.n_val, otc.o_val, street.s_val, people.bldn, people.bldn_k, people.appr, people.telef_n
-- FROM people
--     JOIN fam ON people.fam = fam.u_id
--     JOIN nam ON people.nam = nam.u_id
--     JOIN otc ON people.otc = otc.u_id
--     JOIN street ON people.street = street.u_id

-- SELECT *
--     FROM people
--     cross JOIN fam
--     cross JOIN nam
--     cross JOIN otc
--     cross JOIN street

-- CREATE TABLE name (
--     name VARCHAR(50),
--     surname VARCHAR(50)
-- )
-- INSERT INTO name(name, surname) VALUES ('Иван', 'Иванов'), ('Петр', 'Петров')

SELECT n1.name, n2.surname
FROM name n1
CROSS JOIN name n2;
