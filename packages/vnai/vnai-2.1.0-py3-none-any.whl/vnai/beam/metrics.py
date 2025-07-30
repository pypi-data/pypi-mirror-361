_K='success'
_J='buffer_size'
_I='request'
_H='rate_limit'
_G='execution_time'
_F='timestamp'
_E=False
_D='error'
_C=True
_B=None
_A='function'
import sys,time,threading
from datetime import datetime
import hashlib,json
class Collector:
	_instance=_B;_lock=threading.Lock()
	def __new__(cls):
		with cls._lock:
			if cls._instance is _B:cls._instance=super(Collector,cls).__new__(cls);cls._instance._initialize()
			return cls._instance
	def _initialize(self):self.metrics={_A:[],_H:[],_I:[],_D:[]};self.thresholds={_J:50,'error_threshold':.1,'performance_threshold':5.};self.function_count=0;self.colab_auth_triggered=_E;self.max_metric_length=200;self._last_record_time={};self.min_interval_per_type=.5
	def record(self,metric_type,data,priority=_B):
		A='high'
		if not isinstance(data,dict):data={'value':str(data)}
		if _F not in data:data[_F]=datetime.now().isoformat()
		if metric_type!='system_info':data.pop('system',_B);from vnai.scope.profile import inspector;data['machine_id']=inspector.fingerprint()
		now=time.time();last_time=self._last_record_time.get(metric_type,0)
		if now-last_time<self.min_interval_per_type and priority!=A:return
		self._last_record_time[metric_type]=now;data_hash=hashlib.md5(json.dumps(data,sort_keys=_C).encode()).hexdigest()
		if data_hash in self._recent_hashes and priority!=A:return
		self._recent_hashes.append(data_hash)
		if metric_type in self.metrics:
			self.metrics[metric_type].append(data)
			if len(self.metrics[metric_type])>self.max_metric_length:self.metrics[metric_type]=self.metrics[metric_type][-self.max_metric_length:]
		else:self.metrics[_A].append(data)
		if metric_type==_A:
			self.function_count+=1
			if self.function_count>10 and not self.colab_auth_triggered and'google.colab'in sys.modules:self.colab_auth_triggered=_C;threading.Thread(target=self._trigger_colab_auth,daemon=_C).start()
		if sum(len(metric_list)for metric_list in self.metrics.values())>=self.thresholds[_J]:self._send_metrics()
		if priority==A or metric_type==_D:self._send_metrics()
	def _trigger_colab_auth(self):
		try:from vnai.scope.profile import inspector;inspector.get_or_create_user_id()
		except:pass
	def _send_metrics(self):
		C='vnai';B='source';A='unknown';from vnai.flow.relay import track_function_call,track_rate_limit,track_api_request
		for(metric_type,data_list)in self.metrics.items():
			if not data_list:continue
			for data in data_list:
				try:
					if metric_type==_A:track_function_call(function_name=data.get(_A,A),source=data.get(B,C),execution_time=data.get(_G,0),success=data.get(_K,_C),error=data.get(_D),args=data.get('args'))
					elif metric_type==_H:track_rate_limit(source=data.get(B,C),limit_type=data.get('limit_type',A),limit_value=data.get('limit_value',0),current_usage=data.get('current_usage',0),is_exceeded=data.get('is_exceeded',_E))
					elif metric_type==_I:track_api_request(endpoint=data.get('endpoint',A),source=data.get(B,C),method=data.get('method','GET'),status_code=data.get('status_code',200),execution_time=data.get(_G,0),request_size=data.get('request_size',0),response_size=data.get('response_size',0))
				except Exception as e:continue
			self.metrics[metric_type]=[]
	def get_metrics_summary(self):return{metric_type:len(data_list)for(metric_type,data_list)in self.metrics.items()}
collector=Collector()
def capture(module_type=_A):
	def decorator(func):
		def wrapper(*args,**kwargs):
			start_time=time.time();success=_E;error=_B
			try:result=func(*args,**kwargs);success=_C;return result
			except Exception as e:error=str(e);raise
			finally:execution_time=time.time()-start_time;collector.record(module_type,{_A:func.__name__,_G:execution_time,_K:success,_D:error,_F:datetime.now().isoformat(),'args':str(args)[:100]if args else _B})
		return wrapper
	return decorator