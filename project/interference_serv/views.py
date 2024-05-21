import json
import requests
# from rest_framework.response import Response
# from rest_framework import status
# from django.shortcuts import render
from django.http import HttpResponse
from math import *
from .static.ex_info import data0
# from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import random
import bitarray
import struct
import base64
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import CoreJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# в постмане дергаю свой метод, если к диме подключена, то все ок, иначе - ошибка подключпения


def xor(X):
    return 0 if X.count('1') % 2 == 0 else 1




CALLBACK_URL = "http://172.16.82.155:8800/coding"


def set_error(bits_arr):
    random_number = random.randint(1, 2)
    if random_number == 1: #  вероятность ошибки = 10%
        print("3. Наложение ошибки при передаче сообщения")
        print('\n')
        random_position1 = random.randint(0, len(bits_arr)-1)
        random_position2 = random.randint(0, 6)
        word = bits_arr[random_position1]
        opposite_char = '0' if word[random_position2] == '1' else '1'
        updated_word = word[:(random_position2)] + opposite_char + word[random_position2+1:]
        bits_arr[random_position1] = updated_word
        print("Исходный вектор =", word)
        print("Вектор с ошибкой в", 6 - random_position2+1, 'разряде =', updated_word)
        print('\n')
        # print(bits_arr)

        bits_arr2 = []
        cf = 0
        for code_item in bits_arr:
            syndrome = str(xor([code_item[i] for i in [0, 1, 2, 3]])) + \
                    str(xor([code_item[i] for i in [0, 1, 4, 5]])) + \
                    str(xor([code_item[i] for i in [0, 2, 4, 6]]))
            if cf == 0:
                print("Проверка вычисления синдрома ошибки для первого вектора:")
                print("Вектор =", code_item, "Синдром =", syndrome)
                cf = 1
            
            if syndrome != '000':
                if code_item[7 - int(syndrome, 2)] == '0':
                    code_vector = code_item[:7 - int(syndrome, 2)] + '1' + code_item[7 - int(syndrome, 2) + 1:]
                else:
                    code_vector = code_item[:7 - int(syndrome, 2)] + '0' + code_item[7 - int(syndrome, 2) + 1:]
                bits_arr2.append(code_vector)
                print("Поверка исправления вектора с помощью синдрома ошибки:")
                print("Синдром =", syndrome, "Вектор с ошибкой =", code_item, "Исправленный вектор =", code_vector)
            else:
                bits_arr2.append(code_item)

        bits_arr = bits_arr2
        return bits_arr
    else:
        print("3. Помехи в канале передачи не возникли")
        return bits_arr

def decoddinng(bits_arr):
    bits_arr3 = []
    cf = 0
    for item in bits_arr:
        bits_arr3.append(str(item[:3]+item[4]))
        if cf == 0:
            print("Проверка:")
            print("Исходный вектор =", item, "Декодированный вектор =", str(item[:3]+item[4]))
            cf = 1

    return bits_arr3
    
def send_data(user, time, data, segment_num, segment_cnt, f):
    print('\n')
    print("5. Этап отправки пакета")
    if (random.randint(0,  10000) >  17):
        F = 0
    else:
        F = 1
    if (F == 0) and (f==0):
        answer = {
        "username": user,
        "time": time,
        "payload": {
            "data": data,
            "status": "ok",
            "segment_num": segment_num,
            "segment_cnt": segment_cnt
        }
        }
        print("Отправляемые данные:")
        print(answer)
        try:
            response = requests.post(CALLBACK_URL, json=answer, timeout=7)
            response.raise_for_status()
            if response.status_code == 200:
                print("Данные успешно отправлены на транспортный уровень")
                print()
                # print("Отправляемые данные:")
                # print(answer)
            else:
                print(f"Ошибка при отправке данных. Код состояния: {response.status_code}")
        except requests.exceptions.Timeout as e:
            print("Ошибка подключения к транспортному уровню")
        except requests.exceptions.HTTPError as err:
            print(f"Ошибка HTTP: {err}")
    else:
        if (F == 0) and (f!=0):
            print("Пакет отправлен c ошибкой")
            answer = {
            "username": user,
            "time": time,
            "payload": {
                "data": None,
                "status": "error",
                "segment_num": segment_num,
                "segment_cnt": segment_cnt
            }
            }
            try:
                print("Отправленные данные:")
                print(answer)
                response = requests.post(CALLBACK_URL, json=answer)
                if response.status_code == 200:
                    print("Данные успешно отправлены на транспортный уровень")
                    # print()
                    # print("Отправляемые данные:")
                    # print(answer)
                else:
                    print(f"Ошибка при отправке данных. Код состояния: {response.status_code}")
            except requests.exceptions.Timeout as e:
                print("Ошибка подключения к транспортному уровню")
            except requests.exceptions.HTTPError as err:
                print(f"Ошибка HTTP: {err}")
        elif (F == 1):
            print("Потеря пакета") 



def codding(json_data):
    print('\n')
    print('2. Начало этапа кодирования')
    user = json_data["username"]
    time = json_data["time"]
    segment_num = json_data["payload"]["segment_num"]
    segment_cnt = json_data["payload"]["segment_cnt"]


    data = json_data["payload"]["data"]
    # print(data)
    # из base64 в байты 
    decoded_bytes = base64.b64decode(data)
    data = decoded_bytes


    #data = data.encode("utf-8") # перевод строки данных в байты

    # print("_data0 =", data)
    #---------------------------------------------------------------------------------------------#
    bit_str = "".join(f"{byte:08b}" for byte in data)

    # кодирование Хемминогом [7,4]
    print('\n')
    print("Проверка правильности кодирования кодом Хемминга [7,4] для первого вектора:")
    arr0 =[]
    bits_arr =[]
    for i in range(0, len(bit_str), 4):
        information_vector =  bit_str[i:i+4]
        arr0.append(information_vector)

        codded_vector = information_vector[:3] + str(xor([information_vector[i] for i in range(3)])) + \
                    information_vector[3] + str(xor([information_vector[i] for i in [0, 1, 3]])) + \
                    str(xor([information_vector[i] for i in [0, 2, 3]]))
        bits_arr.append(codded_vector)
        if i==0:
            print("Информационный вектор =", information_vector)
            print("Закодированный вектор =", codded_vector)
            print('\n')


    # наложение ошибки
    bits_arr = set_error(bits_arr)

    # декодирование
    print('\n')
    print("4. Декодирование")
    bits_arr3 = decoddinng(bits_arr)
    if bits_arr3 == arr0:
        f = 0
    

    join_bits_arr = lambda bits_list: ''.join(bits_list) # обединение строк в массиве в одну строку
    bit_string = join_bits_arr(bits_arr3)

    bit_array = bitarray.bitarray(bit_string)
    bytes_data = bit_array.tobytes()

    # байты в формат base64
    base64_data = base64.b64encode(bytes_data)
    
    data = str(base64_data)[2:]
    data = data[:-1]
    # print(data, len(bytes_data))

    # вероятность отправки пакета
    send_data(user, time, data, segment_num, segment_cnt, f)
    



schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        'time': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        'payload': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'data': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'segment_num': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'segment_cnt': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        },
        required=['data', 'segment_num', 'segment_cnt']),
    },
    required=['username','time', 'payload']
)

@csrf_exempt
@api_view(['POST'])
@swagger_auto_schema(request_body=schema)
def interference_serv(request):
    print("1. Начало работы канального уровня")
    try:

        json_data = json.loads(request.body)
        print("Данные, принятые с транспортного уровня:")
        print(json_data)
        codding(json_data)
        return HttpResponse('Hello world!')
    
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON: {e}')
        return HttpResponse('Hello world!')

