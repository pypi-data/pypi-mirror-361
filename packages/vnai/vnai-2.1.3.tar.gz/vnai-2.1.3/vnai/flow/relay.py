_U='execution_time'
_T='manual'
_S='success'
_R='is_exceeded'
_Q='source'
_P='function'
_O='last_sync_time'
_N='sync_interval'
_M='buffer_size'
_L='webhook_url'
_K='value'
_J='sync_count'
_I='machine_id'
_H='data'
_G=False
_F=None
_E='timestamp'
_D='api_requests'
_C='rate_limits'
_B='function_calls'
_A=True
import time,threading,json,random,requests
from datetime import datetime
from pathlib import Path
from typing import Dict,List,Any,Optional
class Conduit:
	_instance=_F;_lock=threading.Lock()
	def __new__(cls,webhook_url=_F,buffer_size=50,sync_interval=300):
		with cls._lock:
			if cls._instance is _F:cls._instance=super(Conduit,cls).__new__(cls);cls._instance._initialize(webhook_url,buffer_size,sync_interval)
			return cls._instance
	def _initialize(self,webhook_url,buffer_size,sync_interval):
		self.webhook_url=webhook_url;self.buffer_size=buffer_size;self.sync_interval=sync_interval;self.buffer={_B:[],_D:[],_C:[]};self.lock=threading.Lock();self.last_sync_time=time.time();self.sync_count=0;self.failed_queue=[];self.home_dir=Path.home();self.project_dir=self.home_dir/'.vnstock';self.project_dir.mkdir(exist_ok=_A);self.data_dir=self.project_dir/_H;self.data_dir.mkdir(exist_ok=_A);self.config_path=self.data_dir/'relay_config.json'
		try:from vnai.scope.profile import inspector;self.machine_id=inspector.fingerprint()
		except:self.machine_id=self._generate_fallback_id()
		self._load_config();self._start_periodic_sync()
	def _generate_fallback_id(self)->str:
		try:import platform,hashlib,uuid;system_info=platform.node()+platform.platform()+platform.processor();return hashlib.md5(system_info.encode()).hexdigest()
		except:import uuid;return str(uuid.uuid4())
	def _load_config(self):
		if self.config_path.exists():
			try:
				with open(self.config_path,'r')as f:config=json.load(f)
				if not self.webhook_url and _L in config:self.webhook_url=config[_L]
				if _M in config:self.buffer_size=config[_M]
				if _N in config:self.sync_interval=config[_N]
				if _O in config:self.last_sync_time=config[_O]
				if _J in config:self.sync_count=config[_J]
			except:pass
	def _save_config(self):
		config={_L:self.webhook_url,_M:self.buffer_size,_N:self.sync_interval,_O:self.last_sync_time,_J:self.sync_count}
		try:
			with open(self.config_path,'w')as f:json.dump(config,f)
		except:pass
	def _start_periodic_sync(self):
		def periodic_sync():
			while _A:time.sleep(self.sync_interval);self.dispatch('periodic')
		sync_thread=threading.Thread(target=periodic_sync,daemon=_A);sync_thread.start()
	def add_function_call(self,record):
		if not isinstance(record,dict):record={_K:str(record)}
		with self.lock:self.buffer[_B].append(record);self._check_triggers(_B)
	def add_api_request(self,record):
		if not isinstance(record,dict):record={_K:str(record)}
		with self.lock:self.buffer[_D].append(record);self._check_triggers(_D)
	def add_rate_limit(self,record):
		if not isinstance(record,dict):record={_K:str(record)}
		with self.lock:self.buffer[_C].append(record);self._check_triggers(_C)
	def _check_triggers(self,record_type:str):
		current_time=time.time();should_trigger=_G;trigger_reason=_F;total_records=sum(len(buffer)for buffer in self.buffer.values())
		if total_records>=self.buffer_size:should_trigger=_A;trigger_reason='buffer_full'
		elif record_type==_C and self.buffer[_C]and any(item.get(_R)for item in self.buffer[_C]if isinstance(item,dict)):should_trigger=_A;trigger_reason='rate_limit_exceeded'
		elif record_type==_B and self.buffer[_B]and any(not item.get(_S)for item in self.buffer[_B]if isinstance(item,dict)):should_trigger=_A;trigger_reason='function_error'
		else:
			time_factor=min(1.,(current_time-self.last_sync_time)/(self.sync_interval/2))
			if random.random()<.05*time_factor:should_trigger=_A;trigger_reason='random_time_weighted'
		if should_trigger:threading.Thread(target=self.dispatch,args=(trigger_reason,),daemon=_A).start()
	def queue(self,package,priority=_F):
		H='packages';G='commercial';F='system_info';E='rate_limit';D='free';C='system';B='type';A='segment'
		try:from vnai.scope.promo import ContentManager;is_paid=ContentManager().is_paid_user;segment_val='paid'if is_paid else D
		except Exception:segment_val=D
		def ensure_segment(d):
			if not isinstance(d,dict):return d
			d=dict(d)
			if A not in d:d[A]=segment_val
			return d
		if isinstance(package,dict)and A not in package:package[A]=segment_val
		if isinstance(package,dict)and isinstance(package.get(_H),dict):
			if A not in package[_H]:package[_H][A]=segment_val
		if not package:return _G
		if not isinstance(package,dict):self.add_function_call(ensure_segment({'message':str(package)}));return _A
		if _E not in package:package[_E]=datetime.now().isoformat()
		if B in package:
			package_type=package[B];data=package.get(_H,{})
			if isinstance(data,dict)and C in data:
				machine_id=data[C].get(_I);data.pop(C)
				if machine_id:data[_I]=machine_id
			if package_type==_P:self.add_function_call(ensure_segment(data))
			elif package_type=='api_request':self.add_api_request(ensure_segment(data))
			elif package_type==E:self.add_rate_limit(ensure_segment(data))
			elif package_type==F:self.add_function_call({B:F,G:data.get(G),H:data.get(H),_E:package.get(_E)})
			elif package_type=='metrics':
				metrics_data=data
				for(metric_type,metrics_list)in metrics_data.items():
					if isinstance(metrics_list,list):
						if metric_type==_P:
							for item in metrics_list:self.add_function_call(ensure_segment(item))
						elif metric_type==E:
							for item in metrics_list:self.add_rate_limit(ensure_segment(item))
						elif metric_type=='request':
							for item in metrics_list:self.add_api_request(ensure_segment(item))
			elif isinstance(data,dict)and data is not package:self.add_function_call(ensure_segment(data))
			else:self.add_function_call(ensure_segment(package))
		else:self.add_function_call(ensure_segment(package))
		if priority=='high':self.dispatch('high_priority')
		return _A
	def dispatch(self,reason=_T):
		if not self.webhook_url:return _G
		with self.lock:
			if all(len(records)==0 for records in self.buffer.values()):return _G
			data_to_send={_B:self.buffer[_B].copy(),_D:self.buffer[_D].copy(),_C:self.buffer[_C].copy()};self.buffer={_B:[],_D:[],_C:[]};self.last_sync_time=time.time();self.sync_count+=1;self._save_config()
		try:from vnai.scope.profile import inspector;environment_info=inspector.examine();machine_id=environment_info.get(_I,self.machine_id)
		except:environment_info={_I:self.machine_id};machine_id=self.machine_id
		payload={'analytics_data':data_to_send,'metadata':{_E:datetime.now().isoformat(),_I:machine_id,_J:self.sync_count,'trigger_reason':reason,'environment':environment_info,'data_counts':{_B:len(data_to_send[_B]),_D:len(data_to_send[_D]),_C:len(data_to_send[_C])}}};success=self._send_data(payload)
		if not success:
			with self.lock:
				self.failed_queue.append(payload)
				if len(self.failed_queue)>10:self.failed_queue=self.failed_queue[-10:]
		return success
	def _send_data(self,payload):
		if not self.webhook_url:return _G
		try:response=requests.post(self.webhook_url,json=payload,timeout=5);return response.status_code==200
		except:return _G
	def retry_failed(self):
		if not self.failed_queue:return 0
		with self.lock:to_retry=self.failed_queue.copy();self.failed_queue=[]
		success_count=0
		for payload in to_retry:
			if self._send_data(payload):success_count+=1
			else:
				with self.lock:self.failed_queue.append(payload)
		return success_count
	def configure(self,webhook_url):
		with self.lock:self.webhook_url=webhook_url;self._save_config();return _A
conduit=Conduit()
def track_function_call(function_name,source,execution_time,success=_A,error=_F,args=_F):
	record={_P:function_name,_Q:source,_U:execution_time,_E:datetime.now().isoformat(),_S:success}
	if error:record['error']=error
	if args:
		sanitized_args={}
		if isinstance(args,dict):
			for(key,value)in args.items():
				if isinstance(value,(str,int,float,bool)):sanitized_args[key]=value
				else:sanitized_args[key]=str(type(value))
		else:sanitized_args={_K:str(args)}
		record['args']=sanitized_args
	conduit.add_function_call(record)
def track_rate_limit(source,limit_type,limit_value,current_usage,is_exceeded):record={_Q:source,'limit_type':limit_type,'limit_value':limit_value,'current_usage':current_usage,_R:is_exceeded,_E:datetime.now().isoformat(),'usage_percentage':current_usage/limit_value*100 if limit_value>0 else 0};conduit.add_rate_limit(record)
def track_api_request(endpoint,source,method,status_code,execution_time,request_size=0,response_size=0):record={'endpoint':endpoint,_Q:source,'method':method,'status_code':status_code,_U:execution_time,_E:datetime.now().isoformat(),'request_size':request_size,'response_size':response_size};conduit.add_api_request(record)
def configure(webhook_url):return conduit.configure(webhook_url)
def sync_now():return conduit.dispatch(_T)
def retry_failed():return conduit.retry_failed()