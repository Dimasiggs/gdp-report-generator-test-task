## Как запустить проект
```bash
# Установка зависимостей
pip install -r requirements.txt

# Пример запуска генерации отчета
python main.py --files data/economic1.csv data/economic2.csv --report average-gdp
```

## Как запустить тесты
```bash
python pytest
```

## Структура проект
```
data/                 # Тестовые данные
src/
├── main.py           
├── schemas.py        # Pydantic модели данных
├── interfaces.py     # Протоколы (интерфейсы)
├── services.py       # Бизнес-логика и сервисы
tests/
├── test_schemas.py   # Тесты моделей
├── test_services.py  # Тесты сервисов
main.py               # Точка входа
requirements.txt
.gitignore

```


## Формат входных данных
```
country,year,gdp,gdp_growth,inflation,unemployment,population,continent
United States,2023,25462,2.1,3.4,3.7,339,North America
United States,2022,23315,2.1,8.0,3.6,338,North America
United States,2021,22994,5.9,4.7,5.3,337,North America
```

## Формат выходных данных (в консоли)
```
+-----+----------------+----------+
|   № | country        |      gdp |
+=====+================+==========+
|   1 | United States  | 23923.7  |
+-----+----------------+----------+
|   2 | China          | 17810.3  |
+-----+----------------+----------+
```
