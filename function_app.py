import azure.functions as func

from functions.create_employee import bp as create_employee_bp
from functions.delete_employee import bp as delete_employee_bp
from functions.get_employee import bp as get_employee_bp
from functions.list_employees import bp as list_employees_bp
from functions.reports.bonus_percentage import bp as bonus_percentage_bp
from functions.reports.departments_bonus_exceeds_avg_salary import (
    bp as departments_bonus_exceeds_avg_salary_bp,
)
from functions.reports.employees_ranked_by_bonus import bp as employees_ranked_by_bonus_bp
from functions.reports.employees_without_bonus import bp as employees_without_bonus_bp
from functions.reports.highest_salary_employee import bp as highest_salary_employee_bp
from functions.reports.total_bonus import bp as total_bonus_bp
from functions.update_employee import bp as update_employee_bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Part A - CRUD
app.register_functions(create_employee_bp)
app.register_functions(get_employee_bp)
app.register_functions(list_employees_bp)
app.register_functions(update_employee_bp)
app.register_functions(delete_employee_bp)

# Part B - compensation reporting
app.register_functions(total_bonus_bp)
app.register_functions(employees_without_bonus_bp)
app.register_functions(bonus_percentage_bp)
app.register_functions(departments_bonus_exceeds_avg_salary_bp)
app.register_functions(employees_ranked_by_bonus_bp)
app.register_functions(highest_salary_employee_bp)
