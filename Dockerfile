# Використовуємо офіційний образ Python
FROM python:3.12-slim

# Встановлюємо залежності для Python та інші необхідні пакети
RUN apt-get update && apt-get install -y curl

# Встановлюємо Poetry для керування залежностями
RUN curl -sSL https://install.python-poetry.org | python3 -

# Встановлюємо змінні середовища для Poetry
ENV PATH="/root/.local/bin:$PATH"

# Створюємо директорію для застосунку
WORKDIR /app

# Копіюємо файли проєкту до контейнера
COPY . /app

# Встановлюємо залежності через Poetry
RUN poetry install

# Визначаємо команду для запуску CLI застосунку
ENTRYPOINT ["poetry", "run", "python", "hw-02.py"]

# Підтримка інтерактивного режиму
CMD ["/bin/bash"]
