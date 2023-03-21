from api1 import PetFriends
from settings import valid_email, valid_password, invalid_password, invalid_email
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """Получаем Api ключ"""
    status, result = pf.get_api_key(email, password)
    # проверяем статус и наличие ключа
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """Проверяем возможность получения списка питомцев с правильными данными"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key['key'], filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Харди', animal_type='хаски',
                                     age='4', pet_photo='image/husky.jpg'):
    """Проверяем, что можно добавить питомца с корректными данными"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Феликс", "пёс", "2", "images/husky.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_successful_add_new_pet_without_photo(name='Тень', animal_type='Собака', age=4):
    """Проверяем, что можно добавить питомца с корректными данными"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_pet_photo_with_valid_data(pet_photo='image/husky2.jpg'):
    """Проверяем возможность добавления фотографии питомца"""

    # Полный путь изображения питомца, который сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список непустой, то пробуем добавить фотографию
    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_of_pets(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем, что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
    else:
        # В случае пустого списка, выводим исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    """Проверяем, что запрос с неверным паролем возвращает ошибку 403"""
    status, result = pf.get_api_key(email, password) # проверяем статус и наличие ключа
    assert status == 403 # Сверяем полученный ответ с ожидаемым результатом
    assert 'This user wasn&#x27;t found in database' in result


def test_get_api_key_for_invalid_email(email=invalid_email, password=invalid_password):
    """Проверяем, что запрос api-ключа с неверным email возвращает ошибку 403"""
    status, result = pf.get_api_key(email, password)
    assert status == 403  # Сверяем полученный ответ с ожидаемым результатом
    assert "This user wasn&#x27;t  found in database" in result


def test_get_all_pets_with_invalid_key(filter=''):
    """Проверяем возможность получения списка питомцев с неправильным Api клюом"""
    auth_key = {'key': '12345'}
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403
    assert 'Please provide &#x27;auth_key&#x27; Header' in result


def test_add_new_pet_with_valid_data_with_invalid_key(name='Харди', animal_type='хаски',
                                     age='4', pet_photo='image/husky.jpg'):
    """Проверяем, что нельзя добавить питомца с корректными данными, но некорректным api ключом"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    auth_key = {'key': '12345'}

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 403
    assert 'Please provide &#x27;auth_key&#x27; Header' in result

def test_add_new_pet_with_invalid_name(name='Ха:рди', animal_type='хаски',
                                     age='4', pet_photo='image/husky.jpg'):
    """Проверяем, что нельзя добавить питомца с невалидным именем"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400

   # обнаружен баг, имя животного можно записать с символом ":"


def test_add_new_pet_with_invalid_age(name='Харди', animal_type='хаски',
                                     age='-4', pet_photo='image/husky.jpg'):
    """Проверяем, что нельзя добавить питомца с отрицательным значением возраста"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400
#     Обнаружен баг, сайт позволяет указать отрицательный возраст питомца


def test_add_new_pet_with_invalid_photo_format(name='Харди', animal_type='хаски',
                                     age='4', pet_photo='image/Husky3.docx'):
    """Проверяем, что нельзя добавить питомца с фотографией представленной в формате docx"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400
#     обнаружен баг, сат позволяет добавить питомца с фотографией форматом docx


def test_successful_add_new_pet_without_photo_with_invalid_age(name='Тень', animal_type='Собака', age=455):
    """Проверяем, что можно добавить питомца с корректными данными"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400
    #     Обнаружен баг, сайт позволяет указать нереальный возраст питомца.


def test_successful_add_new_pet_without_photo_with_invalid_animal_type(name='Тень', animal_type='Соб@ка', age=4):
    """Проверяем, что можно добавить питомца с корректными данными"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400
    #     Обнаружен баг, сайт позволяет указать вид животного со спецсимволом @.

def test_delete_self_pet_with_invalid_key():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Феликс", "пёс", "2", "images/husky.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    auth_key = {'key': '12345'}
    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 403




