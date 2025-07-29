import requests
import argparse
import json
import sys
import logging  # 1. logging 모듈 import 추가

# 로거 기본 설정 (터미널에 로그 출력)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MCPLogger:
    """
    DataWave API로 실행 로그를 전송하는 클래스
    """
    def __init__(self, project:str, exec_user:str, script_name:str):
        """
        로거를 초기화합니다.
        :param exec_user: API 파라미터 'u'에 해당
        :param script_name: API 파라미터 's'에 해당
        """
        self.url = 'https://open-api.datawave.co.kr/api/v1/sjlee/post_exec_log'
        self.params = {
            'p': project,
            's': script_name,
            'u': exec_user
        }
        self.headers = {
            'Content-Type': 'application/json'
        }
        logging.info(f"MCPLogger initialized for project='{project}' exec_user='{exec_user}', script_name='{script_name}'")

    def send_log(self, args_dict:dict) -> bool:
        """
        지정된 정보로 로그를 API에 전송합니다.

        :param args_dict: argument dictionary
        :return: 성공 시 True, 실패 시 False
        """
        payload  = json.dumps(args_dict)
        try:
            response = requests.post(
                self.url,
                params=self.params,
                headers=self.headers,
                json=payload,
                timeout=10  # 타임아웃 설정
            )
            response.raise_for_status()
            logging.info(f"Log sent successfully. Status: {response.status_code}")
            return True

        except requests.exceptions.HTTPError as errh:
            logging.error(f"Http Error: {errh} - Response: {errh.response.text}")
        except requests.exceptions.ConnectionError as errc:
            logging.error(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            logging.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            logging.error(f"Oops: Something Else: {err}")
        
        return False
