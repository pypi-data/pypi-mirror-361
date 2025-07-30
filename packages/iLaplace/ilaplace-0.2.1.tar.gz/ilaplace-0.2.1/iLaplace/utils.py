# iLaplace/utils.py

def validate_callable(func):
    if not callable(func):
        raise TypeError("ورودی باید یک تابع callable باشد.")

def validate_positive_number(value, name="value"):
    if not (isinstance(value, (int, float)) and value > 0):
        raise ValueError(f"{name} باید یک عدد مثبت باشد.")

def prepare_time_array(t_start, t_end, num_points):
    if t_start < 0:
        raise ValueError("t_start باید بزرگتر یا مساوی صفر باشد.")
    if t_end <= t_start:
        raise ValueError("t_end باید بزرگتر از t_start باشد.")
    if num_points <= 1:
        raise ValueError("num_points باید بزرگتر از 1 باشد.")

    step = (t_end - t_start) / (num_points_
