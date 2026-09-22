CREATE TABLE nam (
    u_id SERIAL PRIMARY KEY,
    n_val VARCHAR(50) NOT NULL
);

CREATE TABLE fam (
    u_id SERIAL PRIMARY KEY,
    f_val VARCHAR(50) NOT NULL
);

CREATE TABLE otc (
    u_id SERIAL PRIMARY KEY,
    o_val VARCHAR(50) NOT NULL
);

CREATE TABLE street (
    u_id SERIAL PRIMARY KEY,
    s_val VARCHAR(50) NOT NULL
);
CREATE TABLE people (
    u_id SERIAL PRIMARY KEY,
    fam INT REFERENCES fam(u_id),
    nam INT REFERENCES nam(u_id),
    otc INT REFERENCES otc(u_id),
    street INT REFERENCES street(u_id),
    bldn VARCHAR(5),
    bldn_k VARCHAR(5),
    appr INT,
    telef_n VARCHAR(30)
);