create table bot_user (
  telegram_id bigint primary key
);

create table income_category (
  id integer primary key,
  name varchar(60) not null unique,
  ordering integer not null unique,
  category_type integer not null,
  check(category_type in (1))
);

create table expenses_category (
  id integer primary key,
  name varchar(60) not null unique,
  ordering integer not null unique,
  category_type integer not null,
  check(category_type in (2))
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

-- Daytime table sheet:
create table days (
  id integer primary key,
  month_number integer not null,
  timestamp datetime default current_timestamp,
  name varchar(50),
  payment_type integer not null,
  category_name integer not null,
  price integer,
  custom_comment text,
  -- here may depend on what is the type of cactegory: income || expenses:
  foreign key(category_name) references category_delegator(category_name),
  -- 0: income, 1: expense 
  check(payment_type in (0, 1))
);

create table category_delegator (
  category_name varchar(60) 
  -- foreign key(category_name_income) references income_category(name),
  -- foreign key(category_name_expense) references expenses_category(name)
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

insert into income_category (name, ordering, category_type) values
('Зарплата', 10, 1),
('Подработки', 20, 1),
('Инвестиции', 30, 1),
('Дополнительно', 40, 1);

insert into expenses_category (name, ordering, category_type) values
('Питание', 10, 2),
('Транспорт', 20, 2),
('Дом', 30, 2),
('Здоровье', 40, 2),
('Связь', 50, 2),
('Подарки', 60, 2),
('Одежда', 70, 2),
('Путешествия', 80, 2),
('Мелочь', 90, 2),
('Другое', 100, 2);

insert into category_delegator (category_name) select name from income_category;
insert into category_delegator (category_name) select name from expenses_category;
/*
(1, 'Зарплата', null),
(1, 'Подработки', null),
(1, 'Инвестиции', null),
(1, 'Дополнительно', null),
(2, null, 'Питание'),
(2, null, 'Транспорт'),
(2, null, 'Дом'),
(2, null, 'Здоровье'),
(2, null, 'Связь'),
(2, null, 'Подарки'),
(2, null, 'Одежда'),
(2, null, 'Путешествия'),
(2, null, 'Мелочь'),
(2, null, 'Другое');
*/
