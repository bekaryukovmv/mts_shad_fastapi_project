# from unittest import TestCase
# import unittest


# Тестирование с помощью обычных функций и http-клиента
# def test_get_book():
#     response = requests.get("url")
#     assert response.status_code == 200, "Wrong code"
#     assert response.json() == {
#         "books": [
#             {"title": "Wrong Code", "author": "Robert Martin", "pages": 104, "year": 2007},
#         ]
#     }


# Пример написания теста с помощью Юниттеста
# https://docs.python.org/3/library/unittest.html
# class TestBooks(TestCase):
#     def setUp(self):
#         # метод выполняемый перед каждым тестом
#         # например, можно заполнить БД
#         pass

#     def tearDown(self):
#         pass

#     def test_get_book(self):
#         response = requests.get("url")
#         self.assertEqual(response.status_code, 200)
#         assert response.json() == {
#             "books": [
#                 {"title": "Wrong Code", "author": "Robert Martin", "pages": 104, "year": 2007},
#             ]
#         }

# if __name__ == '__main__':
#     unittest.main()
