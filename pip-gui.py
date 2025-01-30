import wx
import subprocess
import threading

class PipGUI(wx.Frame):
    def __init__(self, *args, **kw):
        super(PipGUI, self).__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):
        # Головний контейнер для розміщення елементів
        main_panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Заголовок у верхній частині вікна
        title = wx.StaticText(main_panel, label="Пакетний менеджер PIP для Python", style=wx.ALIGN_CENTER)
        title.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(title, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Горизонтальний контейнер для основного вмісту
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Лівий фрейм для списку встановлених пакетів
        left_panel = wx.Panel(main_panel)
        vbox_left = wx.BoxSizer(wx.VERTICAL)

        btn_list = wx.Button(left_panel, label='Оновити список пакетів')
        btn_list.Bind(wx.EVT_BUTTON, self.OnListPackages)
        vbox_left.Add(btn_list, flag=wx.EXPAND | wx.ALL, border=10)

        # wx.ListBox для відображення пакетів
        self.package_listbox = wx.ListBox(left_panel, style=wx.LB_SINGLE)
        vbox_left.Add(self.package_listbox, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        left_panel.SetSizer(vbox_left)

        # Правий фрейм для введення даних та сповіщень
        right_panel = wx.Panel(main_panel)
        vbox_right = wx.BoxSizer(wx.VERTICAL)

        # Поле для введення назви пакету
        self.package_input = wx.TextCtrl(right_panel)
        vbox_right.Add(self.package_input, flag=wx.EXPAND | wx.ALL, border=10)

        # Кнопка для встановлення пакету
        btn_install = wx.Button(right_panel, label='Встановити пакет')
        btn_install.Bind(wx.EVT_BUTTON, self.OnInstallPackage)
        vbox_right.Add(btn_install, flag=wx.EXPAND | wx.ALL, border=10)

        # Кнопка для отримання інформації про пакет
        btn_info = wx.Button(right_panel, label='Інформація про пакет')
        btn_info.Bind(wx.EVT_BUTTON, self.OnPackageInfo)
        vbox_right.Add(btn_info, flag=wx.EXPAND | wx.ALL, border=10)

        # Кнопка для вилучення пакету
        btn_uninstall = wx.Button(right_panel, label='Вилучити обраний пакет')
        btn_uninstall.Bind(wx.EVT_BUTTON, self.OnUninstallPackage)
        vbox_right.Add(btn_uninstall, flag=wx.EXPAND | wx.ALL, border=10)

        # Фрейм для сповіщень
        self.output = wx.TextCtrl(right_panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox_right.Add(self.output, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        right_panel.SetSizer(vbox_right)

        # Розміщення лівої та правої панелей у головному контейнері
        hbox.Add(left_panel, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        hbox.Add(right_panel, proportion=2, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(hbox, proportion=1, flag=wx.EXPAND)

        # Напис у нижній частині вікна
        footer = wx.StaticText(main_panel, label="Розроблено за допомогою DeepSeek", style=wx.ALIGN_CENTER)
        footer.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        vbox.Add(footer, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        main_panel.SetSizer(vbox)

        self.SetTitle('Pip GUI')
        self.SetSize((800, 600))
        self.Centre()

        # Завантажити список пакетів при запуску
        self.UpdatePackageList()

    def UpdatePackageList(self):
        """Оновити список пакетів у ListBox"""
        try:
            result = subprocess.run(['pip', 'list', '--format=freeze'], capture_output=True, text=True)
            packages = result.stdout.splitlines()
            self.package_listbox.Clear()
            for package in packages:
                self.package_listbox.Append(package.split('==')[0])  # Додаємо лише назви пакетів
        except Exception as e:
            self.output.AppendText(f"Помилка при оновленні списку пакетів: {str(e)}\n")

    def OnListPackages(self, event):
        """Оновити список пакетів"""
        self.UpdatePackageList()

    def OnPackageInfo(self, event):
        """Обробник натискання кнопки 'Інформація про пакет'"""
        selected_package = self.package_listbox.GetStringSelection()
        if selected_package:
            self.ShowPackageInfo(selected_package)
        else:
            self.output.AppendText("Виберіть пакет зі списку для отримання інформації.\n")

    def ShowPackageInfo(self, package_name):
        """Показати інформацію про обраний пакет"""
        try:
            result = subprocess.run(['pip', 'show', package_name], capture_output=True, text=True)
            if result.returncode == 0:
                self.output.SetValue(result.stdout)  # Вивести інформацію у вікно сповіщень
            else:
                self.output.SetValue(f"Інформація про пакет '{package_name}' не знайдена.\n")
        except Exception as e:
            self.output.SetValue(f"Помилка при отриманні інформації про пакет: {str(e)}\n")

    def OnInstallPackage(self, event):
        """Встановити пакет"""
        package_name = self.package_input.GetValue()
        if package_name:
            threading.Thread(target=self.CheckPackageExistence, args=(package_name, self.InstallPackageThread)).start()
        else:
            self.output.AppendText("Введіть назву пакету для встановлення.\n")

    def OnUninstallPackage(self, event):
        """Вилучити обраний пакет"""
        selected_package = self.package_listbox.GetStringSelection()
        if selected_package:
            threading.Thread(target=self.CheckPackageInstalled, args=(selected_package, self.UninstallPackageThread)).start()
        else:
            self.output.AppendText("Виберіть пакет зі списку для вилучення.\n")

    def CheckPackageExistence(self, package_name, callback):
        """Перевірка, чи існує пакет у репозиторії"""
        try:
            process = subprocess.run(['pip', 'search', package_name], capture_output=True, text=True)
            if "ERROR" in process.stdout or "No match found" in process.stdout:
                wx.CallAfter(self.output.AppendText, f"Пакет '{package_name}' не знайдено.\n")
            else:
                wx.CallAfter(self.output.AppendText, f"Пакет '{package_name}' знайдено. Починаю встановлення...\n")
                callback(package_name)
        except Exception as e:
            wx.CallAfter(self.output.AppendText, f"Помилка при пошуку пакету: {str(e)}\n")

    def CheckPackageInstalled(self, package_name, callback):
        """Перевірка, чи встановлений пакет"""
        try:
            process = subprocess.run(['pip', 'show', package_name], capture_output=True, text=True)
            if "WARNING: Package(s) not found" in process.stdout or not process.stdout.strip():
                wx.CallAfter(self.output.AppendText, f"Пакет '{package_name}' не встановлено.\n")
            else:
                wx.CallAfter(self.output.AppendText, f"Пакет '{package_name}' знайдено. Починаю вилучення...\n")
                callback(package_name)
        except Exception as e:
            wx.CallAfter(self.output.AppendText, f"Помилка при перевірці пакету: {str(e)}\n")

    def InstallPackageThread(self, package_name):
        """Поток для встановлення пакету"""
        try:
            process = subprocess.Popen(['pip', 'install', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    wx.CallAfter(self.output.AppendText, output)
            process.stdout.close()
            process.wait()
            wx.CallAfter(self.UpdatePackageList)  # Оновити список після встановлення
        except Exception as e:
            wx.CallAfter(self.output.AppendText, f"Помилка: {str(e)}\n")

    def UninstallPackageThread(self, package_name):
        """Поток для вилучення пакету"""
        try:
            process = subprocess.Popen(['pip', 'uninstall', '-y', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    wx.CallAfter(self.output.AppendText, output)
            process.stdout.close()
            process.wait()
            wx.CallAfter(self.UpdatePackageList)  # Оновити список після вилучення
        except Exception as e:
            wx.CallAfter(self.output.AppendText, f"Помилка: {str(e)}\n")

def main():
    app = wx.App(False)
    frame = PipGUI(None)
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
