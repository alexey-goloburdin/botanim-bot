create table bot_user (
  telegram_id bigint primary key
);

create table income_category (
  id integer primary key,
  name varchar(60) not null unique,
  ordering integer not null unique
);

create table expenses_category (
  id integer primary key,
  name varchar(60) not null unique,
  ordering integer not null unique
);

create table income (
  id integer primary key,
  amount integer,
  custom_comment text,
  category_id integer,
  ordering integer not null,
  timestamp datetime default current_timestamp,
  foreign key(category_id) references income_category(id),
  unique(category_id, ordering)
);

create table expenses (
  id integer primary key,
  amount integer,
  custom_comment text,
  category_id integer,
  ordering integer not null,
  timestamp datetime default current_timestamp,
  foreign key(category_id) references expenses_category(id),
  unique(category_id, ordering)
);

create table storage (
  id integer primary key,
  name varchar(100)
);

-- months with double period like 1/2 and 2/2
create table months (
  id integer primary key,
  name varchar(10) not null,
  ordering integer not null unique,
  which_half integer not null,
  check(which_half in (1, 2))
  -- foreign key(id) references income_category(id), ?
);

-- total sum, depends on what income | expenses category is, sums from monthes by it (category)
create table total_sum (
  id integer primary key,
  months_id integer not null,
  ordering integer not null,
  -- foreign key(months_id) references income_category(id),
  unique(months_id, ordering)
);

insert into months (name, ordering, which_half) values
('Январь', 10, 1),
('Январь', 15, 2),
('Февраль', 20, 1),
('Февраль', 25, 2),
('Март', 30, 1),
('Март', 35, 2),
('Апрель', 40, 1),
('Апрель', 45, 2),
('Май', 50, 1),
('Май', 55, 2),
('Июнь', 60, 1),
('Июнь', 65, 2),
('Июль', 70, 1),
('Июль', 75, 2),
('Август', 80, 1),
('Август', 85, 2),
('Сентябрь', 90, 1),
('Сентябрь', 95, 2),
('Октябрь', 100, 1),
('Октябрь', 105, 2),
('Ноябрь', 110, 1),
('Ноябрь', 115, 2),
('Декабрь', 120, 1),
('Декабрь', 125, 2);

insert into income_category (name, ordering) values
('Зарплата', 10),
('Подработки', 20),
('Инвестиции', 30),
('Дополнительно', 40);

insert into expenses_category (name, ordering) values
('Питание', 10),
('Транспорт', 20),
('Дом', 30),
('Здоровье', 40),
('Связь', 50),
('Подарки', 60),
('Одежда', 70),
('Путешествия', 80),
('Мелочь', 90),
('Другое', 100);
