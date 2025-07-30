_C='category'
_B=True
_A=None
import time,threading,json
from datetime import datetime
from pathlib import Path
class Buffer:
	_instance=_A;_lock=threading.Lock()
	def __new__(cls):
		with cls._lock:
			if cls._instance is _A:cls._instance=super(Buffer,cls).__new__(cls);cls._instance._initialize()
			return cls._instance
	def _initialize(self):self.data=[];self.lock=threading.Lock();self.max_size=1000;self.backup_interval=300;self.home_dir=Path.home();self.project_dir=self.home_dir/'.vnstock';self.project_dir.mkdir(exist_ok=_B);self.data_dir=self.project_dir/'data';self.data_dir.mkdir(exist_ok=_B);self.backup_path=self.data_dir/'buffer_backup.json';self._load_from_backup();self._start_backup_thread()
	def _load_from_backup(self):
		if self.backup_path.exists():
			try:
				with open(self.backup_path,'r')as f:backup_data=json.load(f)
				with self.lock:self.data=backup_data
			except:pass
	def _save_to_backup(self):
		with self.lock:
			if not self.data:return
			try:
				with open(self.backup_path,'w')as f:json.dump(self.data,f)
			except:pass
	def _start_backup_thread(self):
		def backup_task():
			while _B:time.sleep(self.backup_interval);self._save_to_backup()
		backup_thread=threading.Thread(target=backup_task,daemon=_B);backup_thread.start()
	def add(self,item,category=_A):
		A='timestamp'
		with self.lock:
			if isinstance(item,dict):
				if A not in item:item[A]=datetime.now().isoformat()
				if category:item[_C]=category
			self.data.append(item)
			if len(self.data)>self.max_size:self.data=self.data[-self.max_size:]
			if len(self.data)%100==0:self._save_to_backup()
			return len(self.data)
	def get(self,count=_A,category=_A):
		with self.lock:
			if category:filtered_data=[item for item in self.data if item.get(_C)==category]
			else:filtered_data=self.data.copy()
			if count:return filtered_data[:count]
			else:return filtered_data
	def clear(self,category=_A):
		with self.lock:
			if category:self.data=[item for item in self.data if item.get(_C)!=category]
			else:self.data=[]
			self._save_to_backup();return len(self.data)
	def size(self,category=_A):
		with self.lock:
			if category:return len([item for item in self.data if item.get(_C)==category])
			else:return len(self.data)
buffer=Buffer()