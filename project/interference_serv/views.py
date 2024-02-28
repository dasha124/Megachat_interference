import json
import requests
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
from math import *
from .static.ex_info import data0
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import random
import bitarray
import struct
import base64


def xor(X):
    return 0 if X.count('1') % 2 == 0 else 1




CALLBACK_URL = "http://192.168.207.1:8800/coding"

def codding(json_data):
    print('3')
    user = json_data["username"]
    time = json_data["time"]
    segment_num = json_data["payload"]["segment_num"]
    segment_cnt = json_data["payload"]["segment_cnt"]


    data = json_data["payload"]["data"]
    print(data)
    # из base64 в байты 
    decoded_bytes = base64.b64decode(data)
    data = decoded_bytes



    #data = data.encode("utf-8") # перевод строки данных в байты

    # print("_data0 =", data)
    #---------------------------------------------------------------------------------------------#
    bit_str = "".join(f"{byte:08b}" for byte in data)


    # кодирование Хемминогом [7,4]
    arr0 =[]
    bits_arr =[]
    for i in range(0, len(bit_str), 4):

        information_vector =  bit_str[i:i+4]
        arr0.append(information_vector)
        codded_vector = information_vector[:3] + str(xor([information_vector[i] for i in range(3)])) + \
                    information_vector[3] + str(xor([information_vector[i] for i in [0, 1, 3]])) + \
                    str(xor([information_vector[i] for i in [0, 2, 3]]))
        bits_arr.append(codded_vector)
    # print("----------bits-----------",bits_arr)


    # наложение ошибки
    random_number = random.randint(1, 10)
    if random_number == 1: #  вероятность ошибки = 10%
        print("Возникли помехи при передаче сообщения")
        random_position1 = random.randint(0, len(bits_arr)-1)
        random_position2 = random.randint(0, 6)
        word = bits_arr[random_position1]
        opposite_char = '0' if word[random_position2] == '1' else '1'
        updated_word = word[:(random_position2)] + opposite_char + word[random_position2+1:]
        bits_arr[random_position1] = updated_word
        # print(bits_arr)

        bits_arr2 = []
        for code_item in bits_arr:
            syndrome = str(xor([code_item[i] for i in [0, 1, 2, 3]])) + \
                    str(xor([code_item[i] for i in [0, 1, 4, 5]])) + \
                    str(xor([code_item[i] for i in [0, 2, 4, 6]]))
            if syndrome != '000':
                if code_item[7 - int(syndrome, 2)] == '0':
                    code_vector = code_item[:7 - int(syndrome, 2)] + '1' + code_item[7 - int(syndrome, 2) + 1:]
                else:
                    code_vector = code_item[:7 - int(syndrome, 2)] + '0' + code_item[7 - int(syndrome, 2) + 1:]
                bits_arr2.append(code_vector)
            else:
                bits_arr2.append(code_item)

        # print("bits_arr2 = ", bits_arr2)
        bits_arr = bits_arr2
    else:
        print("Помехи в канале передачи не возникли")
    
    # декодирование
    bits_arr3 =[]
    for item in bits_arr:
        bits_arr3.append(str(item[:3]+item[4]))

    if bits_arr3 == arr0:
        f = 0
    

    join_bits_arr = lambda bits_list: ''.join(bits_list)
    bit_string = join_bits_arr(bits_arr3)

    bit_array = bitarray.bitarray(bit_string)
    bytes_data = bit_array.tobytes()

    # байты в формат base64
    base64_data = base64.b64encode(bytes_data)
    
    data = str(base64_data)[2:]
    data = data[:-1]
    print(data, len(bytes_data))

    # вероятность отправки пакета
    if (random.randint(0,  10000) >  17) and (f==0):
        print("Пакет отправлен")
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
        print("============", answer)
        requests.post(CALLBACK_URL,  json=answer)
    else:
        if (random.randint(0,  10000) >  17) and (f!=0):
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
            requests.post(CALLBACK_URL,  json=answer) 

@csrf_exempt
def interference_serv(request):
    print("2")
    try:

        json_data = json.loads(request.body)
        print("-------------------------------------------", json_data)
        codding(json_data)
        return HttpResponse('Hello world!')
    
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON: {e}')
        return HttpResponse('Hello world!')

