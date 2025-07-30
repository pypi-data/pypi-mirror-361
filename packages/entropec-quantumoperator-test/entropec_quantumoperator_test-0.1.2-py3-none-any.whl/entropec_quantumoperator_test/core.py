import requests
import time
from typing import Dict, Optional, Any

class DMRGClient:
    """
    DMRG计算任务客户端，用于提交任务和获取结果
    
    Attributes:
        api_base (str): API基础URL
        submit_url (str): 提交任务的URL
        result_url (str): 获取结果的URL
        timeout (int): 请求超时时间(秒)
        retry_interval (int): 结果轮询间隔(秒)
    """
    
    def __init__(
        self, 
        api_base: str = "http://192.168.124.22:12805",
        timeout: int = 10,
        retry_interval: int = 5

    ):
        """
        初始化DMRG客户端
        
        Args:
            api_base: API基础URL
            timeout: 请求超时时间(秒)
            retry_interval: 结果轮询间隔(秒)
        """
        self.api_base = api_base
        self.submit_url = f"{self.api_base}/run_task"
        self.result_url = f"{self.api_base}/get_result"
        self.timeout = timeout
        self.retry_interval = retry_interval

    def submit_job(
        self, 
        task_id: str, 
        program: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        提交DMRG计算任务
        
        Args:
            task_id: 任务标识符
            params: 计算参数配置
            
        Returns:
            服务器响应的JSON数据
            
        Raises:
            requests.RequestException: 网络请求异常
        """
        params = {"program": program, "params": params}
        print(f"提交任务 {task_id}...")
        try:
            response = requests.post(
                f"{self.submit_url}?filename={task_id}",
                json=params,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            response.raise_for_status()
            print(f"响应 [{response.status_code}]: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"提交失败: {str(e)}")
            raise

    def fetch_result(
        self, 
        task_id: str, 
        max_retries: Optional[int] = None
    ) -> str:
        """
        获取DMRG计算结果
        
        Args:
            task_id: 任务标识符
            max_retries: 最大重试次数，None表示无限重试
            
        Returns:
            计算结果文本
            
        Raises:
            requests.RequestException: 网络请求异常
            TimeoutError: 超过最大重试次数仍未获取结果
        """
        print(f"\n获取结果 {task_id}...")
        retries = 0
        
        while max_retries is None or retries < max_retries:
            try:
                response = requests.get(
                    self.result_url,
                    params={"task_id": task_id},
                    timeout=self.timeout
                )
                response.raise_for_status()
                print(f"结果获取成功:\n{response.text}")
                return response.text
            except requests.RequestException:
                retries += 1
                if max_retries is not None and retries >= max_retries:
                    raise TimeoutError(f"超过最大重试次数({max_retries})，未获取到结果")
                print(f"结果未就绪，{self.retry_interval}秒后重试...")
                time.sleep(self.retry_interval)
                
        raise TimeoutError("未获取到结果")