_G='resource_type'
_F=False
_E=True
_D=None
_C='default'
_B='hour'
_A='min'
import time,functools,threading
from collections import defaultdict
from datetime import datetime
class RateLimitExceeded(Exception):
	def __init__(self,resource_type,limit_type=_A,current_usage=_D,limit_value=_D,retry_after=_D):
		self.resource_type=resource_type;self.limit_type=limit_type;self.current_usage=current_usage;self.limit_value=limit_value;self.retry_after=retry_after;message=f"Bạn đã gửi quá nhiều request tới {resource_type}. "
		if retry_after:message+=f"Vui lòng thử lại sau {round(retry_after)} giây."
		else:message+='Vui lòng thêm thời gian chờ giữa các lần gửi request.'
		super().__init__(message)
class Guardian:
	_instance=_D;_lock=threading.Lock()
	def __new__(cls):
		with cls._lock:
			if cls._instance is _D:cls._instance=super(Guardian,cls).__new__(cls);cls._instance._initialize()
			return cls._instance
	def _initialize(self):self.resource_limits=defaultdict(lambda:defaultdict(int));self.usage_counters=defaultdict(lambda:defaultdict(list));self.resource_limits[_C]={_A:60,_B:3000};self.resource_limits['TCBS']={_A:60,_B:3000};self.resource_limits['VCI']={_A:60,_B:3000};self.resource_limits['MBK']={_A:600,_B:36000};self.resource_limits['MAS.ext']={_A:600,_B:36000};self.resource_limits['VCI.ext']={_A:600,_B:36000};self.resource_limits['FMK.ext']={_A:600,_B:36000};self.resource_limits['VND.ext']={_A:600,_B:36000};self.resource_limits['CAF.ext']={_A:600,_B:36000};self.resource_limits['SPL.ext']={_A:600,_B:36000};self.resource_limits['VDS.ext']={_A:600,_B:36000};self.resource_limits['FAD.ext']={_A:600,_B:36000}
	def verify(self,operation_id,resource_type=_C):
		E='is_exceeded';D='current_usage';C='limit_value';B='limit_type';A='rate_limit';current_time=time.time();limits=self.resource_limits.get(resource_type,self.resource_limits[_C]);minute_cutoff=current_time-60;self.usage_counters[resource_type][_A]=[t for t in self.usage_counters[resource_type][_A]if t>minute_cutoff];minute_usage=len(self.usage_counters[resource_type][_A]);minute_exceeded=minute_usage>=limits[_A]
		if minute_exceeded:from vnai.beam.metrics import collector;collector.record(A,{_G:resource_type,B:_A,C:limits[_A],D:minute_usage,E:_E},priority='high');raise RateLimitExceeded(resource_type=resource_type,limit_type=_A,current_usage=minute_usage,limit_value=limits[_A],retry_after=60-current_time%60)
		hour_cutoff=current_time-3600;self.usage_counters[resource_type][_B]=[t for t in self.usage_counters[resource_type][_B]if t>hour_cutoff];hour_usage=len(self.usage_counters[resource_type][_B]);hour_exceeded=hour_usage>=limits[_B];from vnai.beam.metrics import collector;collector.record(A,{_G:resource_type,B:_B if hour_exceeded else _A,C:limits[_B]if hour_exceeded else limits[_A],D:hour_usage if hour_exceeded else minute_usage,E:hour_exceeded})
		if hour_exceeded:raise RateLimitExceeded(resource_type=resource_type,limit_type=_B,current_usage=hour_usage,limit_value=limits[_B],retry_after=3600-current_time%3600)
		self.usage_counters[resource_type][_A].append(current_time);self.usage_counters[resource_type][_B].append(current_time);return _E
	def usage(self,resource_type=_C):current_time=time.time();limits=self.resource_limits.get(resource_type,self.resource_limits[_C]);minute_cutoff=current_time-60;hour_cutoff=current_time-3600;self.usage_counters[resource_type][_A]=[t for t in self.usage_counters[resource_type][_A]if t>minute_cutoff];self.usage_counters[resource_type][_B]=[t for t in self.usage_counters[resource_type][_B]if t>hour_cutoff];minute_usage=len(self.usage_counters[resource_type][_A]);hour_usage=len(self.usage_counters[resource_type][_B]);minute_percentage=minute_usage/limits[_A]*100 if limits[_A]>0 else 0;hour_percentage=hour_usage/limits[_B]*100 if limits[_B]>0 else 0;return max(minute_percentage,hour_percentage)
	def get_limit_status(self,resource_type=_C):E='reset_in_seconds';D='remaining';C='percentage';B='limit';A='usage';current_time=time.time();limits=self.resource_limits.get(resource_type,self.resource_limits[_C]);minute_cutoff=current_time-60;hour_cutoff=current_time-3600;minute_usage=len([t for t in self.usage_counters[resource_type][_A]if t>minute_cutoff]);hour_usage=len([t for t in self.usage_counters[resource_type][_B]if t>hour_cutoff]);return{_G:resource_type,'minute_limit':{A:minute_usage,B:limits[_A],C:minute_usage/limits[_A]*100 if limits[_A]>0 else 0,D:max(0,limits[_A]-minute_usage),E:60-current_time%60},'hour_limit':{A:hour_usage,B:limits[_B],C:hour_usage/limits[_B]*100 if limits[_B]>0 else 0,D:max(0,limits[_B]-hour_usage),E:3600-current_time%3600}}
guardian=Guardian()
class CleanErrorContext:
	_last_message_time=0;_message_cooldown=5
	def __enter__(self):return self
	def __exit__(self,exc_type,exc_val,exc_tb):
		if exc_type is RateLimitExceeded:
			current_time=time.time()
			if current_time-CleanErrorContext._last_message_time>=CleanErrorContext._message_cooldown:print(f"\n⚠️ {str(exc_val)}\n");CleanErrorContext._last_message_time=current_time
			import sys;sys.exit(f"Rate limit exceeded. {str(exc_val)} Process terminated.");return _F
		return _F
def optimize(resource_type=_C,loop_threshold=10,time_window=5,ad_cooldown=150,content_trigger_threshold=3,max_retries=2,backoff_factor=2,debug=_F):
	if callable(resource_type):func=resource_type;return _create_wrapper(func,_C,loop_threshold,time_window,ad_cooldown,content_trigger_threshold,max_retries,backoff_factor,debug)
	if loop_threshold<2:raise ValueError(f"loop_threshold must be at least 2, got {loop_threshold}")
	if time_window<=0:raise ValueError(f"time_window must be positive, got {time_window}")
	if content_trigger_threshold<1:raise ValueError(f"content_trigger_threshold must be at least 1, got {content_trigger_threshold}")
	if max_retries<0:raise ValueError(f"max_retries must be non-negative, got {max_retries}")
	if backoff_factor<=0:raise ValueError(f"backoff_factor must be positive, got {backoff_factor}")
	def decorator(func):return _create_wrapper(func,resource_type,loop_threshold,time_window,ad_cooldown,content_trigger_threshold,max_retries,backoff_factor,debug)
	return decorator
def _create_wrapper(func,resource_type,loop_threshold,time_window,ad_cooldown,content_trigger_threshold,max_retries,backoff_factor,debug):
	call_history=[];last_ad_time=0;consecutive_loop_detections=0;session_displayed=_F;session_start_time=time.time();session_timeout=1800
	@functools.wraps(func)
	def wrapper(*args,**kwargs):
		E='timestamp';D='environment';C='error';B='function';A='loop';nonlocal last_ad_time,consecutive_loop_detections,session_displayed,session_start_time;current_time=time.time();content_triggered=_F
		if current_time-session_start_time>session_timeout:session_displayed=_F;session_start_time=current_time
		retries=0
		while _E:
			call_history.append(current_time)
			while call_history and current_time-call_history[0]>time_window:call_history.pop(0)
			loop_detected=len(call_history)>=loop_threshold
			if debug and loop_detected:print(f"[OPTIMIZE] Đã phát hiện vòng lặp cho {func.__name__}: {len(call_history)} lần gọi trong {time_window}s")
			if loop_detected:
				consecutive_loop_detections+=1
				if debug:print(f"[OPTIMIZE] Số lần phát hiện vòng lặp liên tiếp: {consecutive_loop_detections}/{content_trigger_threshold}")
			else:consecutive_loop_detections=0
			should_show_content=consecutive_loop_detections>=content_trigger_threshold and current_time-last_ad_time>=ad_cooldown and not session_displayed
			if should_show_content:
				last_ad_time=current_time;consecutive_loop_detections=0;content_triggered=_E;session_displayed=_E
				if debug:print(f"[OPTIMIZE] Đã kích hoạt nội dung cho {func.__name__}")
				try:
					from vnai.scope.promo import manager
					try:from vnai.scope.profile import inspector;environment=inspector.examine().get(D,_D);manager.present_content(environment=environment,context=A)
					except ImportError:manager.present_content(context=A)
				except ImportError:print(f"Phát hiện vòng lặp: Hàm '{func.__name__}' đang được gọi trong một vòng lặp")
				except Exception as e:
					if debug:print(f"[OPTIMIZE] Lỗi khi hiển thị nội dung: {str(e)}")
			try:
				with CleanErrorContext():guardian.verify(func.__name__,resource_type)
			except RateLimitExceeded as e:
				from vnai.beam.metrics import collector;collector.record(C,{B:func.__name__,C:str(e),'context':'resource_verification',_G:resource_type,'retry_attempt':retries},priority='high')
				if not session_displayed:
					try:
						from vnai.scope.promo import manager
						try:from vnai.scope.profile import inspector;environment=inspector.examine().get(D,_D);manager.present_content(environment=environment,context=A);session_displayed=_E;last_ad_time=current_time
						except ImportError:manager.present_content(context=A);session_displayed=_E;last_ad_time=current_time
					except Exception:pass
				if retries<max_retries:
					wait_time=backoff_factor**retries;retries+=1
					if hasattr(e,'retry_after')and e.retry_after:wait_time=min(wait_time,e.retry_after)
					if debug:print(f"[OPTIMIZE] Đã đạt giới hạn tốc độ cho {func.__name__}, thử lại sau {wait_time} giây (lần thử {retries}/{max_retries})")
					time.sleep(wait_time);continue
				else:raise
			start_time=time.time();success=_F;error=_D
			try:result=func(*args,**kwargs);success=_E;return result
			except Exception as e:error=str(e);raise
			finally:
				execution_time=time.time()-start_time
				try:
					from vnai.beam.metrics import collector;collector.record(B,{B:func.__name__,_G:resource_type,'execution_time':execution_time,'success':success,C:error,'in_loop':loop_detected,'loop_depth':len(call_history),'content_triggered':content_triggered,E:datetime.now().isoformat(),'retry_count':retries if retries>0 else _D})
					if content_triggered:collector.record('ad_opportunity',{B:func.__name__,_G:resource_type,'call_frequency':len(call_history)/time_window,'consecutive_loops':consecutive_loop_detections,E:datetime.now().isoformat()})
				except ImportError:pass
			break
	return wrapper
def rate_limit_status(resource_type=_C):return guardian.get_limit_status(resource_type)