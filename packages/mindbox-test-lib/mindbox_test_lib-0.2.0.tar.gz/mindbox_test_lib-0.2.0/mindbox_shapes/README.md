# Mindbox Shapes

Библиотека создана в качестве тестового задания компании 'Mindbox'.

Репозиторий находится [здесь](https://github.com/SivikGosh/test_mindbox_lib).

## Работа с библиотекой

В текущей реализации существует 2 фигуры, круг **(Circle)** и треугольник **(Triangle)**.

Примеры использования фигур:

```python
from mindbox_shapes import Circle

circle = Circle(radius=10.0)

area = circle.area()  # получить площадь круга
```

```python
from mindbox_shapes import Triangle

triangle = Triangle(a=10.0, b=20.0, c=30.0)

area = triangle.area()  # получить площадь треугольника

triangle.is_right()  # проверка, является ли треугольник равносторонним
```

## Сборка для разработчика

Для загрузки библиотеки с инструментами для разработки использовать команду:

```bash
$ pip install mindbox-test-lib[dev]
```

Для загрузки библиотеки с инструментами для тестирования кода:

```bash
$ pip install mindbox-test-lib[test]
```

### [!] Каталог библиотеки переименован, при загрузке код будет доступен в папке 'mindbox_shapes'
