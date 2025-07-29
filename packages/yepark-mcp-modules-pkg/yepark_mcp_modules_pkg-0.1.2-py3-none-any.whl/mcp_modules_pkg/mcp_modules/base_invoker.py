import subprocess
import asyncio
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import paramiko
import logging
import re
import os # os 모듈 추가
import sys # sys 모듈 추가

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class ExecutionResult:
    """스크립트 실행 결과"""
    success: bool
    command: str
    output: str = ""
    error: str = ""
    return_code: int = 0

class MCPFileInvoker(ABC):
    """MCP 파일 실행 추상화 클래스"""
    
    def __init__(self, base_path: str = "~/Project/mcp-cli",
                       remote_host: Optional[str] = None,
                       remote_user: Optional[str] = None,
                       remote_password: Optional[str] = None,
                       private_key_path: Optional[str] = None,
                       venv_path: Optional[str] = None): # venv_path 추가

        self.base_path = Path(base_path).expanduser()
        
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_password = remote_password
        self.private_key_path = private_key_path
        self.venv_path = Path(venv_path).expanduser() if venv_path else None # venv_path 처리

        if self.remote_host and self.remote_user:
            logger.info(f"Invoker가 원격 실행 모드로 초기화되었습니다. {self.remote_user}@{self.remote_host}")
        else:
            logger.info("Invoker가 로컬 실행 모드로 초기화되었습니다.")
        
        if self.venv_path:
            logger.info(f"가상 환경 경로가 설정되었습니다: {self.venv_path}")

    
    @abstractmethod
    def _build_command(self, script_path: str, parameters: Dict[str, Any]) -> List[str]:
        """
        주어진 스크립트 경로와 파라미터로 실행할 명령어를 구축합니다.
        각 Invoker 구현에서 구체화되어야 합니다.
        """
        pass

    async def execute_script(self, script_path: str, parameters: Dict[str, Any], 
                             timeout: int = 300) -> ExecutionResult:
        """
        스크립트 실행 (비동기)
        
        Args:
            script_path: 스크립트 파일 경로
            parameters: 스크립트 파라미터 (예: {'s': 'sheet_id', 'l': 'ko,jp,en'})
            timeout: 실행 타임아웃 (초)
        """
        # _build_command에서 이미 shell 명령어로 반환하므로, command_to_execute는 단일 문자열이 될 것임.
        cmd_list_for_execution = self._build_command(script_path, parameters)
        command_to_execute = ' '.join(cmd_list_for_execution)

        result = ExecutionResult(
            success=False,
            command=command_to_execute
        )

        if self.remote_host and self.remote_user:
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                connect_args = {
                    'hostname': self.remote_host,
                    'username': self.remote_user,
                    'timeout': timeout
                }
                if self.private_key_path:
                    try:
                        key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
                        connect_args['pkey'] = key
                    except Exception as e:
                        logger.error(f"SSH 프라이빗 키 로드 실패: {self.private_key_path}, 오류: {e}")
                        result.error = f"SSH 프라이빗 키 로드 실패: {self.private_key_path}, 오류: {e}"
                        return result
                elif self.remote_password:
                    connect_args['password'] = self.remote_password
                else:
                    result.error = "원격 서버 접속을 위한 비밀번호 또는 프라이빗 키가 제공되지 않았습니다."
                    return result
                
                await asyncio.to_thread(ssh_client.connect, **connect_args)
                logger.info(f"SSH 연결 성공: {self.remote_user}@{self.remote_host}")

                # exec_command returns stdin, stdout, stderr. Ensure they are read.
                # command_to_execute는 이미 shell 명령어를 포함하고 있으므로 그대로 전달.
                stdin, stdout, stderr = await asyncio.to_thread(
                    lambda: ssh_client.exec_command(command_to_execute, timeout=timeout)
                )
                
                output = stdout.read().decode('utf-8').strip()
                error = stderr.read().decode('utf-8').strip()

                return_code = await asyncio.to_thread(lambda: stdout.channel.recv_exit_status())

                result.success = (return_code == 0)
                result.output = output
                result.error = error
                result.return_code = return_code
                ssh_client.close()
                logger.info(f"SSH 연결 종료: {self.remote_user}@{self.remote_host}")

            except paramiko.AuthenticationException:
                result.error = "인증 실패: 사용자 이름 또는 비밀번호/키를 확인하세요"    
                logger.error(f"SSH 인증 실패: {self.remote_user}@{self.remote_host}", exc_info=True)
            except paramiko.SSHException as e:
                result.error = f"SSH 연결 또는 명령 실행 중 오류 발생: {str(e)}"
                logger.error(f"SSH 오류 ({self.remote_user}@{self.remote_host}): {e}", exc_info=True)
            except TimeoutError:
                result.error = f"원격 스크립트 실행 시간 초과 ({timeout}초)"
                logger.warning(f"원격 스크립트 실행 시간 초과 ({timeout}초) for {self.remote_user}@{self.remote_host}: {command_to_execute}")
            except Exception as e:
                result.error = f"원격 실행 중 예기치 않은 오류 발생: {str(e)}"
                logger.exception(f"원격 실행 중 예기치 않은 오류 발생 ({self.remote_user}@{self.remote_host})")
        else: # Local execution
            if script_path.startswith('~/'):
                full_path = Path(script_path).expanduser()
            else:
                full_path = self.base_path / script_path
            
            # Rebuild cmd for local execution, ensuring paths are correct.
            # _build_command가 이미 ['/bin/bash', '-c', 'command string'] 형태로 반환하므로, 
            # 이를 그대로 사용
            cmd = self._build_command(str(full_path), parameters)
            
            result = ExecutionResult(
                success=False,
                command=' '.join(cmd) # 결과 객체에 저장할 명령어도 문자열로
            )
        
            try:
                process = await asyncio.to_thread(
                    subprocess.run,
                    cmd, # cmd는 이미 ['/bin/bash', '-c', '...'] 형태
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False, 
                )
                
                result.success = process.returncode == 0
                result.output = process.stdout.strip()
                result.error = process.stderr.strip()
                result.return_code = process.returncode
                
            except subprocess.TimeoutExpired:
                result.error = f'스크립트 실행 시간 초과 ({timeout}초)'
                logger.warning(f"로컬 스크립트 실행 시간 초과: {full_path} (Timeout: {timeout}s)")
            except FileNotFoundError:
                # /bin/bash를 찾을 수 없는 경우 (거의 없겠지만)
                result.error = f'명령어 실행기를 찾을 수 없습니다: {cmd[0]}'
                logger.error(f"로컬 명령어 실행기를 찾을 수 없음: {cmd[0]}")
            except Exception as e:
                result.error = f'실행 중 오류 발생: {str(e)}'
                logger.exception(f"로컬 스크립트 실행 중 예기치 않은 오류 발생: {full_path}")
            
        return result
    
    async def invoke(self, script_path: str, parameters: Optional[Dict[str, Any]] = None, log_email: Optional[str] = None) -> ExecutionResult:
        """
        스크립트 실행을 위한 invoke 메서드.
        """
        # 전달된 parameters를 직접 수정하지 않기 위해 복사본 생성
        final_params = {**(parameters or {})}

        # log_email 인자가 제공되었고, *그리고* 기존 parameters에 'log_email' 키가 없을 경우에만 추가
        if log_email is not None and 'log_email' not in (parameters or {}):
            final_params['log_email'] = log_email
            
        # user_input이 아닌, 이미 파싱된 script_path와 parameters를 직접 받도록 변경
        return await self.execute_script(
            script_path,
            final_params
        )

class ShInvoker(MCPFileInvoker):
    def parse_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        parts = user_input.split(" ", 1)
        script_path = parts[0]
        parameters = {}
        if len(parts) > 1:
            param_str = parts[1]
            matches = re.findall(r'(--?\w+)\s+(".*?"|\S+)', param_str)
            for key_raw, value_raw in matches:
                key = key_raw.lstrip('-')
                value = value_raw.strip('"')
                parameters[key] = value
        logger.info(f"Parsed SH request: script_path={script_path}, parameters={parameters}")
        return {'script_path': script_path, 'parameters': parameters}

    def _build_command(self, script_path: str, parameters: Dict[str, Any]) -> List[str]:
        cmd_parts = ['sh', script_path]
        for key, value in parameters.items():
            # 값에 포함된 백슬래시와 작은따옴표를 이스케이프 처리합니다.
            # 이렇게 하면 괄호, 줄바꿈, 따옴표 등 모든 특수문자가 안전하게 처리됩니다.
            escaped_value = str(value).replace('\\', '\\\\').replace("'", "\\'")
            param_value = f"$'{escaped_value}'"
            # 키(key) 길이에 따라 하이픈을 동적으로 추가합니다.
            if len(key) == 1:
                cmd_parts.extend([f'-{key}', param_value])
            else:
                cmd_parts.extend([f'--{key}', param_value])
            
        # 모든 부분을 결합하여 /bin/bash -c 로 실행할 최종 명령어 문자열을 생성합니다.
        final_command = ' '.join(cmd_parts)
        
        return ['/bin/bash', '-c', final_command]

class PythonInvoker(MCPFileInvoker):
    def parse_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        parts = user_input.split(" ", 1)
        script_path = parts[0]
        parameters = {}
        if len(parts) > 1:
            param_str = parts[1]
            matches = re.findall(r'(--?\w+)\s+(".*?"|\S+)', param_str)
            for key_raw, value_raw in matches:
                key = key_raw.lstrip('-')
                value = value_raw.strip('"')
                parameters[key] = value
        logger.info(f"Parsed Python request: script_path={script_path}, parameters={parameters}")
        return {'script_path': script_path, 'parameters': parameters}

    def _is_venv_active(self) -> bool:
        """
        현재 셸 세션에서 가상 환경이 활성화되어 있는지 확인합니다.
        VIRTUAL_ENV 환경 변수와 sys.prefix를 사용합니다.
        """
        # 현재 프로세스가 가상 환경 내에서 실행 중인지 확인
        if hasattr(sys, 'real_prefix') and sys.prefix != sys.real_prefix:
            # sys.real_prefix가 존재하고 sys.prefix와 다르면 가상 환경 내부로 판단.
            # 이 경우, 현재 가상 환경의 경로가 self.venv_path와 일치하는지도 확인.
            return self.venv_path and Path(sys.prefix).resolve() == self.venv_path.resolve()
        
        # VIRTUAL_ENV 환경 변수 확인 (외부 셸 환경에서 활성화된 경우)
        # 즉, 이 Invoker를 호출한 셸이 가상 환경을 활성화했는지 확인
        if 'VIRTUAL_ENV' in os.environ and self.venv_path:
            return Path(os.environ['VIRTUAL_ENV']).resolve() == self.venv_path.resolve()
        return False

    def _build_command(self, script_path: str, parameters: Dict[str, Any]) -> List[str]:
        python_executable = 'python' # 기본 파이썬 실행 파일
        activate_cmd = ""

        # 가상 환경 경로가 지정되어 있다면
        if self.venv_path:
            # 가상 환경이 이미 활성화되어 있는지 확인
            if self._is_venv_active():
                #logger.info(f"가상 환경 '{self.venv_path}'이(가) 이미 활성화되어 있습니다. 스크립트를 바로 실행합니다.")
                # 활성화된 가상 환경의 python 실행 파일을 사용
                python_executable = str(self.venv_path / 'bin' / 'python')
            else:
                # 가상 환경이 활성화되어 있지 않다면 활성화 스크립트 확인
                activate_script_path = self.venv_path / 'bin' / 'activate'
                if activate_script_path.exists():
                    activate_cmd = f"source {activate_script_path} && "
                    # activate 스크립트가 PATH를 설정해주므로 'python'만 써도 되지만,
                    # 명시적으로 가상 환경 내의 python 실행 파일을 지정하는 것이 더 안전함.
                    python_executable = str(self.venv_path / 'bin' / 'python') 
                    logger.info(f"가상 환경 '{self.venv_path}'을(를) 활성화합니다.")
                else:
                    logger.warning(f"지정된 가상 환경 경로 '{self.venv_path}'에 'activate' 스크립트를 찾을 수 없습니다. 전역 Python으로 실행합니다.")
        else:
            logger.info("가상 환경 경로가 지정되지 않았습니다. 전역 Python으로 실행합니다.")
        
        # 명령어 구성 시작
        cmd_parts = [activate_cmd + python_executable, script_path]

        for key, value in parameters.items():
            if len(key) == 1:
                cmd_parts.extend([f'-{key}', f'"{str(value)}"'])
            else:
                cmd_parts.extend([f'--{key}', f'"{str(value)}"'])
        
        # 모든 부분을 결합하여 전체 명령 문자열 생성
        full_command_str = ' '.join(cmd_parts)
        
        # 전체 명령 문자열을 /bin/bash -c "..." 로 감싸서 반환
        return ['/bin/bash', '-c', full_command_str] 
