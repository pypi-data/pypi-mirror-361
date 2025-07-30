# iLaplace/methods/talbot.py

from mpmath import invertlaplace

def invert_laplace_talbot(f_s, t_val, degree=8):
    try:
        return float(invertlaplace(f_s, t_val, method='talbot', degree=degree))
    except Exception as e:
        raise RuntimeError(f"خطا در محاسبه لاپلاس معکوس با روش Talbot: {e}")
