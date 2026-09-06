-- Employee Compensation Service - seed data

SET IDENTITY_INSERT dbo.Department ON;
INSERT INTO dbo.Department (DepartmentID, DepartmentName, Location) VALUES
    (1, 'Engineering', 'Mumbai'),
    (2, 'Sales',        'Bangalore'),
    (3, 'HR',           'Mumbai'),
    (4, 'Finance',      'Pune');
SET IDENTITY_INSERT dbo.Department OFF;

SET IDENTITY_INSERT dbo.Employee ON;
INSERT INTO dbo.Employee (EmployeeID, FirstName, LastName, DepartmentID, Salary, Bonus, HireDate) VALUES
    (1,  'Aditi',     'Sharma',  1, 1200000.00, 150000.00, '2022-01-10'),
    (2,  'Rohan',     'Mehta',   1,  950000.00, NULL,       '2023-03-15'),
    (3,  'Priya',     'Nair',    1, 1100000.00,  90000.00, '2021-07-01'),
    (4,  'Karan',     'Verma',   1,  800000.00, NULL,       '2024-02-20'),
    (5,  'Simran',    'Kaur',    2,  700000.00, 900000.00, '2020-05-05'),
    (6,  'Arjun',     'Rao',     2,  650000.00, 480000.00, '2019-11-11'),
    (7,  'Neha',      'Joshi',   2,  600000.00, NULL,       '2023-09-09'),
    (8,  'Fatima',    'Sheikh',  3,  550000.00,  20000.00, '2022-08-01'),
    (9,  'Vikram',    'Desai',   3,  500000.00, NULL,       '2023-01-01'),
    (10, 'Ananya',    'Iyer',    4, 1300000.00, 200000.00, '2018-04-01'),
    (11, 'Siddharth', 'Kapoor',  4,  900000.00, 150000.00, '2021-12-12'),
    (12, 'Meera',     'Pillai',  4,  850000.00, NULL,       '2022-06-06');
SET IDENTITY_INSERT dbo.Employee OFF;

