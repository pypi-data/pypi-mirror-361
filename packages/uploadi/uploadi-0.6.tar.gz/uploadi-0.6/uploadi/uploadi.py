from argparse import ArgumentParser
import sys
import os

class CustomArgumentParser(ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Ошибка: {message}", file=sys.stderr)
        sys.exit(1)


def uploadi():
    # Получаем аргументы из командной строки
    parser = CustomArgumentParser(description="Код для загрузки проектов python на PyPI или TestPyPI")
    parser.add_argument('-t', action='store_true', help='Загрузка будет происходить на TestPyPI')
    parser.add_argument('-p', action='store_true', help='Загрузка будет происходить на PyPI')
    parser.add_argument('name_project', help='Название проекта')
    args = parser.parse_args()
    
    # Проверяем наличие одного из флагов
    # Если указагы оба флага или ни один
    if (args.t and args.p) or (not args.t and not args.p):
        print('Надо выбрать один флаг. -t или -p')
        return

    name_project = args.name_project


    # Выполняем выгрузку
    os.system('python setup.py sdist bdist_wheel')
    if args.t:
        os.system('twine upload --repository-url https://test.pypi.org/legacy/ dist/*')
    else:
        os.system('twine upload dist/*')
    os.system(f'rmdir /s /q build dist {name_project}.egg-info')


if __name__ == "__main__":
    uploadi()