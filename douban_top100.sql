USE database1;

CREATE TABLE IF NOT EXISTS douban_top100 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    director VARCHAR(255),
    year INT,
    rating FLOAT,
    genre VARCHAR(255),
    douban_url VARCHAR(255),
    cover_url VARCHAR(255)
);

TRUNCATE TABLE douban_top100;
SELECT * FROM douban_top100;
