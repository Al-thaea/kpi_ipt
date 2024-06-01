from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, CheckboxGroup, Button
import numpy as np
from scipy.signal import butter, filtfilt
import sys
import subprocess

# Функція для генерації гармоніки
def harmonic(t, amplitude, frequency, phase):
    return amplitude * np.sin(2 * np.pi * frequency * t + phase)

# Функція для генерації шуму
def create_noise(t, noise_mean, noise_covariance):
    return np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))

# Функція для генерації гармоніки зі шумом
def harmonic_with_noise(t, amplitude, frequency, phase=0, noise_mean=0, noise_covariance=0.1, noise=None):
    harmonic_signal = harmonic(t, amplitude, frequency, phase)
    if noise is not None:
        return harmonic_signal + noise
    else:
        global noise_g
        noise_g = create_noise(t, noise_mean, noise_covariance)
        return harmonic_signal + noise_g



# Функція для застосування фільтра до сигналу
def moving_avg(data, window_size):
    moving_avg = []
    window_size = int(window_size)
    for i in range(len(data)):
        if i < window_size:
            avg = np.mean(data[:i+1])
        else:
            avg = np.mean(data[i-window_size+1:i+1])
        moving_avg.append(avg)
    return moving_avg


# Початкові значення параметрів
init_amplitude = 1.0
init_frequency = 1.0
init_phase = 0.0
init_noise_mean = 0.0
init_noise_covariance = 0.1
noise_g = None

# Генерація часового проміжку
t = np.linspace(0, 10, 1000)
sampling_frequency = 1 / (t[1] - t[0])

# Створення графічного інтерфейсу
plot = figure(title="Harmonic Signal with Noise", x_axis_label='Time', y_axis_label='Amplitude', width=1250, height=500, sizing_mode="fixed")
plot.background_fill_color = "whitesmoke"
plot.border_fill_color = "lightgrey"

# Генерація гармоніки
harmonic_line = plot.line(t, harmonic(t, init_amplitude, init_frequency, init_phase), line_width=2, color='darkorange', line_dash='dotted', legend_label='Harmonic line')
# Генерація гармоніки зі шумом
with_noise_line = plot.line(t, harmonic_with_noise(t, init_amplitude, frequency=init_frequency,
                                                   phase=init_phase, noise_mean=initial_noise_mean,
                                                   noise_covariance=initial_noise_covariance,noise=None), 
                                                   line_width=2, color='skyblue', legend_label='Signal with noise')

# Застосування  фільтру
filtered_signal = moving_avg(with_noise_line.data_source.data['y'],sampling_frequency)
# Побудова фільтрованого сигналу
l_filtered = plot.line(t, filtered_signal, line_width=2, color='darkgreen', legend_label='Filtered Signal')

# Створення слайдерів
slider_color = 'lightgrey'

s_amplitude = Slider(title="Amplitude", value=init_amplitude, start=0.1, end=10.0, step=0.1,  bar_color=slider_color)
s_frequency = Slider(title="Frequency", value=init_frequency, start=0.1, end=10.0, step=0.1,  bar_color=slider_color)
s_phase = Slider(title="Phase", value=init_phase, start=0.0, end=2 * np.pi, step=0.1, bar_color=slider_color)
s_noise_mean = Slider(title="Noise Mean", value=initial_noise_mean, start=-1.0, end=1.0, step=0.1, bar_color=slider_color)
s_noise_covariance = Slider(title="Noise Covariance", value=initial_noise_covariance, start=0.0, end=1.0, step=0.1, bar_color=slider_color)
s_cutoff_frequency = Slider(title="window_size", value=3, start=1, end=35.0, step=1, bar_color=slider_color)

# Створення чекбоксу для відображення шуму
cb_show_noise = CheckboxGroup(labels=['Show Noise'], active=[0])
# Створення кнопки "Перегенерувати шум"
button_regenerate_noise = Button(label='Regenerate Noise')
# Створення кнопки "Reset"
button_reset = Button(label='Reset')

# Функція, яка оновлює графіки при зміні параметрів
def update(attrname, old, new):
    amplitude = s_amplitude.value
    frequency = s_frequency.value
    phase = s_phase.value

    noise_mean = s_noise_mean.value
    noise_covariance = s_noise_covariance.value

    global initial_noise_mean, initial_noise_covariance, noise_g
    
    if initial_noise_covariance != noise_covariance or initial_noise_mean != noise_mean:
        initial_noise_mean = noise_mean
        initial_noise_covariance = noise_covariance
        noise_g = create_noise(t, noise_mean, noise_covariance)


    show_noise = bool(new)
    harmonic_line.data_source.data['y'] = harmonic(t, amplitude, frequency, phase)
    with_noise_line.data_source.data['y'] = harmonic_with_noise(t, amplitude, frequency, phase,
                                                                noise_mean, noise_covariance, noise_g)
    with_noise_line.visible = show_noise

    cutoff_frequency = s_cutoff_frequency.value
    filtered_signal = moving_avg(with_noise_line.data_source.data['y'], cutoff_frequency)
    l_filtered.data_source.data['y'] = filtered_signal

# Функція, яка оновлює шум
def regenerate_noise():
    with_noise_line.data_source.data['y'] = harmonic_with_noise(t, s_amplitude.value, s_frequency.value, s_phase.value,
                                                                s_noise_mean.value, s_noise_covariance.value)
# Функція для скидання параметрів
def reset_params():
    s_amplitude.value = init_amplitude
    s_frequency.value = init_frequency
    s_phase.value = init_phase
    s_noise_mean.value = 0.0
    s_noise_covariance.value = 0.1
    s_cutoff_frequency.value = 3
    cb_show_noise.active = [0]
    regenerate_noise()

s_amplitude.on_change('value', update)
s_frequency.on_change('value', update)
s_phase.on_change('value', update)
s_noise_mean.on_change('value', update)
s_noise_covariance.on_change('value', update)
s_cutoff_frequency.on_change('value', update)

cb_show_noise.on_change('active', update)
button_regenerate_noise.on_click(regenerate_noise)
button_reset.on_click(reset_params)

layout = column(plot, 
                row(s_amplitude, s_frequency),
                row(s_phase, s_noise_mean),
                row(s_noise_covariance, s_cutoff_frequency),
                row(cb_show_noise, button_regenerate_noise, button_reset),
                sizing_mode='stretch_width',  align='center')

# Зміна кольору фону всього макету
layout.background = "whitesmoke"
curdoc().add_root(layout)

# Запуск сервера Bokeh
if __name__ == "__main__":
    with open("lab5_bokeh.py", "w", encoding="utf-8") as f:
         f.write(__import__("inspect").getsource(sys.modules[__name__]))
    subprocess.run(["bokeh", "serve", "--show", "lab5_bokeh.py"])
