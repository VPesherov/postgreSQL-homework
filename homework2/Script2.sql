
CREATE TABLE IF NOT EXISTS employees (
	employee_id SERIAL primary key not null,
	name varchar(100) not null
);

CREATE TABLE IF NOT EXISTS deparments (
	department_id SERIAL primary key not null,
	name varchar(100) not null
);


CREATE TABLE IF NOT EXISTS deparment_staff (
	employee_id integer not null references employees(employee_id),
	department_id integer not null references deparments(department_id),
	boss_id integer null references employees(employee_id),
	constraint pk1 primary key (employee_id, department_id)
);