"""
canonical_schema.py
--------------------
This is the heart of the "dataset-agnostic" design.

Instead of every part of the system (dashboard, analytics, ML model)
referring to raw column names like "Salary" or "PerformanceScore"
(which change from one HR file to another), everything talks to
these CANONICAL_FIELDS instead.

When a new CSV comes in, schema_mapper.py maps its real columns to
these canonical names once. After that, nothing else in the app
needs to know or care what the original file's columns were called.

To support a new field system-wide: add it here once, then it's
automatically available to the mapper, the dashboard, and the model.
"""

CANONICAL_FIELDS = {
    "employee_id": {
        "aliases": ["empid", "employee_id", "emp_id", "id", "staff_id", "emp_no"],
        "dtype": "string",
        "required": True,
        "description": "Unique identifier for the employee",
    },
    "employee_name": {
        "aliases": ["employee_name", "name", "full_name", "emp_name"],
        "dtype": "string",
        "required": False,
        "description": "Employee full name",
    },
    "department": {
        "aliases": ["department", "dept", "dept_name", "division"],
        "dtype": "string",
        "required": True,
        "description": "Department / team the employee belongs to",
    },
    "position": {
        "aliases": ["position", "job_title", "title", "role"],
        "dtype": "string",
        "required": False,
        "description": "Job title / position",
    },
    "salary": {
        "aliases": ["salary", "pay_rate", "monthly_salary", "annual_salary", "wage"],
        "dtype": "float",
        "required": True,
        "description": "Compensation figure (whatever period the source uses)",
    },
    "employment_status": {
        "aliases": ["employment_status", "emp_status", "status", "active_status"],
        "dtype": "string",
        "required": False,
        "description": "e.g. Active, Terminated, On Leave",
    },
    "hire_date": {
        "aliases": ["date_of_hire", "hire_date", "start_date", "joining_date"],
        "dtype": "date",
        "required": False,
        "description": "Date the employee was hired",
    },
    "termination_date": {
        "aliases": ["date_of_termination", "termination_date", "end_date", "leaving_date"],
        "dtype": "date",
        "required": False,
        "description": "Date the employee left, if applicable",
    },
    "termination_reason": {
        "aliases": ["term_reason", "termination_reason", "reason_for_leaving"],
        "dtype": "string",
        "required": False,
        "description": "Why the employee left, if applicable",
    },
    "performance_score": {
        "aliases": ["performance_score", "perf_score", "performance_rating", "rating"],
        "dtype": "string",
        "required": False,
        "description": "Categorical or numeric performance rating",
    },
    "engagement_score": {
        "aliases": ["engagement_survey", "engagement_score", "engagement_rating"],
        "dtype": "float",
        "required": False,
        "description": "Engagement survey score",
    },
    "satisfaction_score": {
        "aliases": ["emp_satisfaction", "satisfaction_score", "satisfaction_rating"],
        "dtype": "float",
        "required": False,
        "description": "Employee satisfaction score",
    },
    "absences": {
        "aliases": ["absences", "absence_count", "days_absent"],
        "dtype": "int",
        "required": False,
        "description": "Number of absence days",
    },
    "days_late": {
        "aliases": ["dayslatelast30", "days_late", "late_count", "tardiness"],
        "dtype": "int",
        "required": False,
        "description": "Days late in a recent period",
    },
    "special_projects_count": {
        "aliases": ["special_projects_count", "projects_count", "num_projects"],
        "dtype": "int",
        "required": False,
        "description": "Number of special projects the employee worked on",
    },
    "manager_name": {
        "aliases": ["manager_name", "manager", "supervisor"],
        "dtype": "string",
        "required": False,
        "description": "Name of the employee's manager",
    },
    "gender": {
        "aliases": ["sex", "gender"],
        "dtype": "string",
        "required": False,
        "description": "Employee gender, if present in source data",
    },
    "recruitment_source": {
        "aliases": ["recruitment_source", "source", "hiring_source"],
        "dtype": "string",
        "required": False,
        "description": "Channel through which the employee was recruited",
    },
}


def normalize(text: str) -> str:
    """Lowercase and strip separators so 'Days Late Last 30' and
    'DaysLateLast30' both normalize to the same comparable string."""
    return "".join(ch for ch in text.lower() if ch.isalnum())
