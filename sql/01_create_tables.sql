-- Employee Compensation Service Database Schema
IF OBJECT_ID('dbo.Employee', 'U') IS NOT NULL DROP TABLE dbo.Employee;
IF OBJECT_ID('dbo.Department', 'U') IS NOT NULL DROP TABLE dbo.Department;

-- Department Table
CREATE TABLE dbo.Department (
    DepartmentID    INT             NOT NULL IDENTITY(1,1) PRIMARY KEY,
    DepartmentName  VARCHAR(100)    NOT NULL,
    Location        VARCHAR(100)    NULL
);

-- Employee Table
CREATE TABLE dbo.Employee (
    EmployeeID      INT             NOT NULL IDENTITY(1,1) PRIMARY KEY,
    FirstName       VARCHAR(50)     NOT NULL,
    LastName        VARCHAR(50)     NOT NULL,
    DepartmentID    INT             NOT NULL,
    Salary          DECIMAL(12,2)   NOT NULL,
    Bonus           DECIMAL(12,2)   NULL,   -- NULL = no bonus awarded
    HireDate        DATE            NULL,
    CONSTRAINT FK_Employee_Department
        FOREIGN KEY (DepartmentID) REFERENCES dbo.Department(DepartmentID),
    CONSTRAINT CK_Employee_Salary_NonNegative CHECK (Salary >= 0),
    CONSTRAINT CK_Employee_Bonus_NonNegative CHECK (Bonus IS NULL OR Bonus >= 0)
);

-- Speeds up "list employees by department" and the department-level report.
CREATE INDEX IX_Employee_DepartmentID ON dbo.Employee(DepartmentID);
