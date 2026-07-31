from jz_pwm2 import JZPWM2

PORT = "COM5"  # Linux: например /dev/ttyUSB0

with JZPWM2(PORT) as pwm:
    pwm.set_frequency(1, 100)
    pwm.set_duty(1, 25)
    pwm.set_frequency(2, 25_000)
    pwm.set_duty(2, 75)
