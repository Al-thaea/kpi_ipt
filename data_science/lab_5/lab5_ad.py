import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
import numpy as np
from scipy.signal import butter, filtfilt


# Функція для генерації гармоніки
def harmonic(t, amplitude, frequency, phase):
    return amplitude * np.sin(2 * np.pi * frequency * t + phase)

# Функція для генерації шуму
def create_noise(t, noise_mean, noise_covariance):
    return np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))

# Функція для генерації гармоніки зі шумом
def harmonic_with_noise(t, amplitude, frequency, phase=0, noise_mean=0, noise_covariance=0.1, show_noise=None, noise=None):
    harmonic_signal = harmonic(t, amplitude, frequency, phase)
    if noise is not None and show_noise:
        return harmonic_signal + noise
    elif show_noise:
        global noise_g
        noise_g =  create_noise(t, noise_mean, noise_covariance)
        return harmonic_signal + noise_g
    else:
        return 



# Функція для створення фільтра Нижчих частот
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

# Функція для застосування фільтра до сигналу
def lowpass_filter(data, cutoff_freq, fs, order=5):
    b, a = butter_lowpass(cutoff_freq, fs, order=order)
    y = filtfilt(b, a, data)
    return y



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
fig, ax = plt.subplots()
fig.set_facecolor('whitesmoke')
ax.grid()
ax.set_facecolor('lightgray')
ax.set_ylim(-5, 5)
plt.subplots_adjust(left=0.12, bottom=0.45, top=0.95)



# Генерація гармоніки
harmonic_line, = ax.plot(t, harmonic(t, init_amplitude, init_frequency, init_phase), lw=2, color='indianred', linestyle=':', label='Harmonic Signal')
# Генерація гармоніки зі шумом
with_noise_line, = ax.plot(t, harmonic_with_noise(t, init_amplitude, frequency=init_frequency, 
                                                  phase=init_phase, noise_mean=init_noise_mean, noise_covariance=init_noise_covariance, 
                                                  show_noise=True, noise=None), lw=2, color='violet',label='Noise Signal')
# Застосування низькочастотного фільтру
filtered_signal = lowpass_filter(with_noise_line.get_ydata(), 3, sampling_frequency, order=5)
# Побудова фільтрованого сигналу
l_filtered, = ax.plot(t, filtered_signal, lw=2, color='blue', label='Filtered Signal')
ax.legend()

# Створення слайдерів
axcolor = 'lightsteelblue'
slider_color = 'paleturquoise'

ax_amplitude = plt.axes([0.12, 0.35, 0.65, 0.03], facecolor=axcolor)
ax_frequency = plt.axes([0.12, 0.3, 0.65, 0.03], facecolor=axcolor)
ax_phase = plt.axes([0.12, 0.25, 0.65, 0.03], facecolor=axcolor)
ax_noise_mean = plt.axes([0.12, 0.2, 0.65, 0.03], facecolor=axcolor)
ax_noise_covariance = plt.axes([0.12, 0.15, 0.65, 0.03], facecolor=axcolor)

s_amplitude = Slider(ax_amplitude, 'Amplitude', 0.1, 5.0, valinit=init_amplitude, color='yellow')
s_frequency = Slider(ax_frequency, 'Frequency', 0.1, 5.0, valinit=init_frequency, color=slider_color)
s_phase = Slider(ax_phase, 'Phase', 0.0, 2 * np.pi, valinit=init_phase, color=slider_color)
s_noise_mean = Slider(ax_noise_mean, 'Noise Mean', -1.0, 1.0, valinit=init_noise_mean, color=slider_color)
s_noise_covariance = Slider(ax_noise_covariance, 'Noise Covariance', 0.0, 1.0, valinit=init_noise_covariance, color=slider_color)

# Створення слайдера для налаштування частоти зрізу фільтра
ax_cutoff_frequency = plt.axes([0.12, 0.1, 0.65, 0.03], facecolor=axcolor)
s_cutoff_frequency = Slider(ax_cutoff_frequency, 'Cutoff Frequency', 0.1, 10.0, valinit=3, color=slider_color)

# Створення чекбоксу для відображення шуму
rax = plt.axes([0.83, 0.35, 0.1, 0.04], facecolor=axcolor)
cb_show_noise = CheckButtons(rax, ['Show Noise'], [True])
# Створення кнопки "Перегенерувати шум"
button_regenerate_noise = Button(plt.axes([0.83, 0.275, 0.1, 0.04]), 'Regenerate Noise', color=axcolor, hovercolor='lavenderblush')
# Створення кнопки "Reset"
button_reset = Button(plt.axes([0.83, 0.125, 0.1, 0.04]), 'Reset', color=axcolor, hovercolor='palegoldenrod')

# Функція, яка оновлює графіки при зміні параметрів
def update(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val

    harmonic_line.set_ydata(harmonic(t, amplitude, frequency, phase))
    with_noise_line.set_ydata(harmonic_with_noise(t, amplitude, frequency, phase, noise=noise_g, show_noise=cb_show_noise.get_status()[0]))

    cutoff_frequency = s_cutoff_frequency.val
    filtered_signal = lowpass_filter(with_noise_line.get_ydata(), cutoff_frequency, sampling_frequency)
    l_filtered.set_ydata(filtered_signal)    
    fig.canvas.draw_idle()

# Відповідає за відображення  шуму
def update_chb(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val

    harmonic_line.set_ydata(harmonic(t, amplitude, frequency, phase))
    with_noise_line.set_ydata(harmonic_with_noise(t, amplitude, frequency, phase, noise=noise_g, show_noise=cb_show_noise.get_status()[0]))
    fig.canvas.draw_idle()

# Функція, яка оновлює параметри шуму
def update_noise(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val
    noise_mean = s_noise_mean.val
    noise_covariance = s_noise_covariance.val
    harmonic_line.set_ydata(harmonic(t, amplitude, frequency, phase))
    with_noise_line.set_ydata(harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, cb_show_noise.get_status()[0]))

    cutoff_frequency = s_cutoff_frequency.val
    filtered_signal = lowpass_filter(with_noise_line.get_ydata(), cutoff_frequency, sampling_frequency)
    l_filtered.set_ydata(filtered_signal)
    fig.canvas.draw_idle()
    
# Перегенерація шуму
def regenerate_noise(event):
    with_noise_line.set_ydata(harmonic_with_noise(t, s_amplitude.val, s_frequency.val, s_phase.val, s_noise_mean.val, s_noise_covariance.val, show_noise=True))
    fig.canvas.draw_idle()


# Відновлення початкових параметрів
def reset(event):
    s_amplitude.reset()
    s_frequency.reset()
    s_phase.reset()
    s_noise_mean.reset()
    s_noise_covariance.reset()
    s_cutoff_frequency.reset()
    cb_show_noise.set_active(0)
    regenerate_noise(event)

# Функція, яка оновлює відфільтрований сигнал при зміні коефіцієнта
def update_filter(val):
    cutoff_frequency = s_cutoff_frequency.val
    filtered_signal = lowpass_filter(with_noise_line.get_ydata(), cutoff_frequency, sampling_frequency)
    l_filtered.set_ydata(filtered_signal)
    fig.canvas.draw_idle()


s_amplitude.on_changed(update)
s_frequency.on_changed(update)
s_phase.on_changed(update)
s_noise_mean.on_changed(update_noise)
s_noise_covariance.on_changed(update_noise)
s_cutoff_frequency.on_changed(update_filter)


cb_show_noise.on_clicked(update_chb)
button_regenerate_noise.on_clicked(regenerate_noise)
button_reset.on_clicked(reset)



plt.show()
