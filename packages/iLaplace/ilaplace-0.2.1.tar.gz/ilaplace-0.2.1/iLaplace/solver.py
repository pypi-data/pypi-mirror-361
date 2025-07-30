# iLaplace/solver.py

from iLaplace.methods.talbot import invert_laplace_talbot

def invert_laplace(f_s, t_val, method="talbot", degree=8):
    if not callable(f_s):
        raise TypeError("f_s باید تابعی از s باشد (مثلاً lambda s: 1 / (s+1))")

    if not isinstance(t_val, (int, float)):
        raise TypeError("t_val باید عددی (int یا float) باشد")

    if t_val < 0:
        raise ValueError("t_val نباید منفی باشد؛ زمان باید مثبت یا صفر باشد.")

    if method == "talbot":
        return invert_laplace_talbot(f_s, t_val, degree=degree)
    else:
        raise ValueError(f"روش '{method}' پشتیبانی نمی‌شود.")
