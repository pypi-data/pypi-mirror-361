_L='minimal'
_K='warnings'
_J='api_requests'
_I='last_error_time'
_H='startup_time'
_G='standard'
_F='function_calls'
_E='peak_memory'
_D='errors'
_C=True
_B=None
_A='execution_times'
import time,threading,json,os
from datetime import datetime
from pathlib import Path
class Tracker:
	_instance=_B;_lock=threading.Lock()
	def __new__(cls):
		with cls._lock:
			if cls._instance is _B:cls._instance=super(Tracker,cls).__new__(cls);cls._instance._initialize()
			return cls._instance
	def _initialize(self):self.metrics={_H:datetime.now().isoformat(),_F:0,_J:0,_D:0,_K:0};self.performance_metrics={_A:[],_I:_B,_E:0};self.privacy_level=_G;self.home_dir=Path.home();self.project_dir=self.home_dir/'.vnstock';self.project_dir.mkdir(exist_ok=_C);self.data_dir=self.project_dir/'data';self.data_dir.mkdir(exist_ok=_C);self.metrics_path=self.data_dir/'usage_metrics.json';self.privacy_config_path=self.project_dir/'config'/'privacy.json';os.makedirs(os.path.dirname(self.privacy_config_path),exist_ok=_C);self._load_metrics();self._load_privacy_settings();self._start_background_collector()
	def _load_metrics(self):
		if self.metrics_path.exists():
			try:
				with open(self.metrics_path,'r')as f:stored_metrics=json.load(f)
				for(key,value)in stored_metrics.items():
					if key in self.metrics:self.metrics[key]=value
			except:pass
	def _save_metrics(self):
		try:
			with open(self.metrics_path,'w')as f:json.dump(self.metrics,f)
		except:pass
	def _load_privacy_settings(self):
		if self.privacy_config_path.exists():
			try:
				with open(self.privacy_config_path,'r')as f:settings=json.load(f);self.privacy_level=settings.get('level',_G)
			except:pass
	def setup_privacy(self,level=_B):
		privacy_levels={_L:'Essential system data only',_G:'Performance metrics and errors','enhanced':'Detailed operation analytics'}
		if level is _B:level=_G
		if level not in privacy_levels:raise ValueError(f"Invalid privacy level: {level}. Choose from {', '.join(privacy_levels.keys())}")
		self.privacy_level=level
		with open(self.privacy_config_path,'w')as f:json.dump({'level':level},f)
		return level
	def get_privacy_level(self):return self.privacy_level
	def _start_background_collector(self):
		def collect_metrics():
			while _C:
				try:
					import psutil;current_process=psutil.Process();memory_info=current_process.memory_info();memory_usage=memory_info.rss/1048576
					if memory_usage>self.performance_metrics[_E]:self.performance_metrics[_E]=memory_usage
					self._save_metrics()
				except:pass
				time.sleep(300)
		thread=threading.Thread(target=collect_metrics,daemon=_C);thread.start()
	def record(self,event_type,data=_B):
		A='execution_time'
		if self.privacy_level==_L and event_type!=_D:return _C
		if event_type in self.metrics:self.metrics[event_type]+=1
		else:self.metrics[event_type]=1
		if event_type==_D:self.performance_metrics[_I]=datetime.now().isoformat()
		if event_type==_F and data and A in data:
			self.performance_metrics[_A].append(data[A])
			if len(self.performance_metrics[_A])>100:self.performance_metrics[_A]=self.performance_metrics[_A][-100:]
		if self.metrics[_F]%100==0 or event_type==_D:self._save_metrics()
		return _C
	def get_metrics(self):
		avg_execution_time=0
		if self.performance_metrics[_A]:avg_execution_time=sum(self.performance_metrics[_A])/len(self.performance_metrics[_A])
		output=self.metrics.copy();output.update({'avg_execution_time':avg_execution_time,'peak_memory_mb':self.performance_metrics[_E],'uptime':(datetime.now()-datetime.fromisoformat(self.metrics[_H])).total_seconds(),'privacy_level':self.privacy_level});return output
	def reset(self):self.metrics={_H:datetime.now().isoformat(),_F:0,_J:0,_D:0,_K:0};self.performance_metrics={_A:[],_I:_B,_E:0};self._save_metrics();return _C
tracker=Tracker()
def record(event_type,data=_B):return tracker.record(event_type,data)