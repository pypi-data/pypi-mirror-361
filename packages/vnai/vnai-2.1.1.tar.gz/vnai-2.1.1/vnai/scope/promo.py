_H='init'
_G='simple'
_F='markdown'
_E='terminal'
_D='html'
_C=True
_B=False
_A=None
import logging,requests
from datetime import datetime
import random,threading,time,urllib.parse
_vnii_check_attempted=_B
class AdCategory:FREE=0;MANDATORY=1;ANNOUNCEMENT=2;REFERRAL=3;FEATURE=4;GUIDE=5;SURVEY=6;PROMOTION=7;SECURITY=8;MAINTENANCE=9;WARNING=10
try:from vnii import lc_init
except ImportError:lc_init=_A
logger=logging.getLogger(__name__)
if not logger.hasHandlers():handler=logging.StreamHandler();handler.setFormatter(logging.Formatter('%(message)s'));logger.addHandler(handler);logger.setLevel(logging.INFO)
class ContentManager:
	_instance=_A;_lock=threading.Lock()
	def __new__(cls):
		with cls._lock:
			if cls._instance is _A:cls._instance=super(ContentManager,cls).__new__(cls);cls._instance._initialize()
			return cls._instance
	def _initialize(self):
		A='vnii';global _vnii_check_attempted
		if _vnii_check_attempted:return
		_vnii_check_attempted=_C;import sys,importlib
		try:
			import importlib.metadata
			try:
				old_version=importlib.metadata.version(A);VNII_LATEST_VERSION='0.0.9';VNII_URL=f"https://github.com/vnstock-hq/licensing/releases/download/vnii-{VNII_LATEST_VERSION}/vnii-{VNII_LATEST_VERSION}.tar.gz";logger.debug(f"Đã phát hiện vnii version {old_version}. Đang cập nhật lên bản mới nhất...");import subprocess;subprocess.check_call([sys.executable,'-m','pip','install',f"vnii@{VNII_URL}"]);importlib.invalidate_caches()
				if A in sys.modules:importlib.reload(sys.modules[A])
				else:import vnii
				new_version=importlib.metadata.version(A);logger.debug(f"Đã cập nhật vnii lên version {new_version}")
			except importlib.metadata.PackageNotFoundError:logger.debug('Không phát hiện vnii trên hệ thống. Luôn coi là free user, không kiểm tra license.');self.is_paid_user=_B;return
		except Exception as e:
			logger.warning(f"Lỗi khi kiểm tra/cài đặt vnii: {e}");user_msg=f"Không thể tự động cài đặt/cập nhật vnii. Vui lòng liên hệ admin hoặc hỗ trợ kỹ thuật của Vnstock để được trợ giúp. Chi tiết lỗi: {e}";logger.error(user_msg)
			try:print(user_msg)
			except Exception:pass
			self.is_paid_user=_B;return
		self.is_paid_user=_B;logger.debug('[promo] Bắt đầu kiểm tra trạng thái paid user với vnii...')
		if lc_init is not _A:
			try:
				license_info=lc_init(repo_name='vnstock');logger.debug(f"[promo] license_info trả về: {license_info}");status=license_info.get('status','').lower()
				if'recognized and verified'in status:self.is_paid_user=_C;logger.debug('[promo] Đã xác nhận paid user từ vnii. Sẽ không hiện quảng cáo.')
				else:logger.debug(f"[promo] Không xác nhận được paid user từ vnii. Status: {status}")
			except Exception as e:logger.warning(f"[promo] Không thể kiểm tra trạng thái sponsor: {e}. Sẽ coi là free user và hiện quảng cáo.")
		else:logger.debug('[promo] Không tìm thấy module vnii. Luôn coi là free user và hiện quảng cáo.')
		self.last_display=0;self.display_interval=86400;self.content_base_url='https://hq.vnstocks.com/static';self.target_url='https://vnstocks.com/lp-khoa-hoc-python-chung-khoan';self.image_url='https://vnstocks.com/img/trang-chu-vnstock-python-api-phan-tich-giao-dich-chung-khoan.jpg';logger.debug(f"[promo] is_paid_user = {self.is_paid_user}");self._start_periodic_display()
	def _start_periodic_display(self):
		logger.debug('[promo] Khởi tạo thread hiển thị quảng cáo định kỳ...')
		def periodic_display():
			logger.debug('[promo] Thread quảng cáo bắt đầu chạy.')
			while _C:
				if self.is_paid_user:logger.debug('[promo] Đang là paid user trong thread. Không hiện quảng cáo, dừng thread.');break
				sleep_time=random.randint(7200,21600);logger.debug(f"[promo] Thread quảng cáo sẽ ngủ {sleep_time//3600} giờ...");time.sleep(sleep_time);current_time=time.time();logger.debug(f"[promo] Kiểm tra điều kiện hiện quảng cáo: time since last_display = {current_time-self.last_display}s")
				if current_time-self.last_display>=self.display_interval:logger.debug("[promo] Đã đủ thời gian, sẽ gọi present_content(context='periodic')");self.present_content(context='periodic')
				else:logger.debug('[promo] Chưa đủ thời gian, chưa hiện quảng cáo.')
		thread=threading.Thread(target=periodic_display,daemon=_C);thread.start()
	def fetch_remote_content(self,context:str=_H,html:bool=_C)->str:
		if self.is_paid_user:logger.debug('Paid user detected. Skip fetching remote content (ads).');return''
		try:
			params={'context':context,_D:'true'if html else'false'};url=f"{self.content_base_url}?{urllib.parse.urlencode(params)}";response=requests.get(url,timeout=3)
			if response.status_code==200:return response.text
			logger.debug(f"Non-200 response fetching content: {response.status_code}");return
		except Exception as e:logger.debug(f"Failed to fetch remote content: {e}");return
	def present_content(self,context:str=_H,ad_category:int=AdCategory.FREE)->_A:
		C='jupyter';B='unknown';A='is_paid_user';environment=_A;logger.debug(f"[promo] Gọi present_content(context={context}, ad_category={ad_category}). is_paid_user = {getattr(self,A,_A)}")
		if getattr(self,A,_B)and ad_category==AdCategory.FREE:logger.debug('[promo] Đang là paid user và ad_category là FREE. Không hiện quảng cáo.');return
		if logger.level<=logging.DEBUG:logger.debug(f"[promo] Sẽ hiển thị quảng cáo với context={context}, ad_category={ad_category}")
		self.last_display=time.time()
		if environment is _A:
			try:from vnai.scope.profile import inspector;environment=inspector.examine().get('environment',B);logger.debug(f"[promo] Đã detect environment: {environment}")
			except Exception as e:logger.debug(f"[promo] Không detect được environment: {e}");environment=B
		remote_content=self.fetch_remote_content(context=context,html=environment==C);logger.debug(f"[promo] remote_content = {bool(remote_content)} (None -> False, có nội dung -> True)");fallback=self._generate_fallback_content(context);logger.debug(f"[promo] fallback keys: {list(fallback.keys())}")
		if environment==C:
			logger.debug('[promo] Đang ở môi trường Jupyter, sẽ thử display HTML/Markdown.')
			try:
				from IPython.display import display,HTML,Markdown
				if remote_content:logger.debug('[promo] Hiển thị quảng cáo bằng HTML từ remote_content.');display(HTML(remote_content))
				else:
					logger.debug('[promo] Không có remote_content, thử display fallback Markdown/HTML.')
					try:display(Markdown(fallback[_F]))
					except Exception as e:logger.debug(f"[promo] Lỗi khi display Markdown: {e}, fallback HTML.");display(HTML(fallback[_D]))
			except Exception as e:logger.debug(f"[promo] Jupyter display failed: {e}")
		elif environment==_E:
			logger.debug('[promo] Đang ở môi trường terminal, sẽ log quảng cáo ra logger.')
			if remote_content:logger.debug('[promo] Hiển thị quảng cáo bằng remote_content cho terminal.');logger.debug(remote_content)
			else:logger.debug('[promo] Không có remote_content, hiển thị fallback terminal.');logger.debug(fallback[_E])
		else:logger.debug(f"[promo] Môi trường khác ({environment}), hiển thị fallback simple.");logger.debug(fallback[_G])
	def _generate_fallback_content(self,context):
		fallback={_D:'',_F:'',_E:'',_G:''}
		if context=='loop':fallback[_D]=f'''
            <div style="border: 1px solid #e74c3c; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3 style="color: #e74c3c;">⚠️ Bạn đang sử dụng vòng lặp với quá nhiều requests</h3>
                <p>Để tránh bị giới hạn tốc độ và tối ưu hiệu suất:</p>
                <ul>
                    <li>Thêm thời gian chờ giữa các lần gọi API</li>
                    <li>Sử dụng xử lý theo batch thay vì lặp liên tục</li>
                    <li>Tham gia gói tài trợ <a href="https://vnstocks.com/insiders-program" style="color: #3498db;">Vnstock Insider</a> để tăng 5X giới hạn API</li>
                </ul>
            </div>
            ''';fallback[_F]='\n## ⚠️ Bạn đang sử dụng vòng lặp với quá nhiều requests\n\nĐể tránh bị giới hạn tốc độ và tối ưu hiệu suất:\n* Thêm thời gian chờ giữa các lần gọi API\n* Sử dụng xử lý theo batch thay vì lặp liên tục\n* Tham gia gói tài trợ [Vnstock Insider](https://vnstocks.com/insiders-program) để tăng 5X giới hạn API\n            ';fallback[_E]='\n╔═════════════════════════════════════════════════════════════════╗\n║                                                                 ║\n║   🚫 ĐANG BỊ CHẶN BỞI GIỚI HẠN API? GIẢI PHÁP Ở ĐÂY!            ║\n║                                                                 ║\n║   ✓ Tăng ngay 500% tốc độ gọi API - Không còn lỗi RateLimit     ║\n║   ✓ Tiết kiệm 85% thời gian chờ đợi giữa các request            ║\n║                                                                 ║\n║   ➤ NÂNG CẤP NGAY VỚI GÓI TÀI TRỢ VNSTOCK:                      ║\n║     https://vnstocks.com/insiders-program                       ║\n║                                                                 ║\n╚═════════════════════════════════════════════════════════════════╝\n                ';fallback[_G]='🚫 Đang bị giới hạn API? Tăng tốc độ gọi API lên 500% với gói Vnstock Insider: https://vnstocks.com/insiders-program'
		else:fallback[_D]=f'''
            <div style="border: 1px solid #3498db; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3 style="color: #3498db;">👋 Chào mừng bạn đến với Vnstock!</h3>
                <p>Cảm ơn bạn đã sử dụng thư viện phân tích chứng khoán #1 tại Việt Nam cho Python</p>
                <ul>
                    <li>Tài liệu: <a href="https://vnstocks.com/docs/category/s%E1%BB%95-tay-h%C6%B0%E1%BB%9Bng-d%E1%BA%ABn" style="color: #3498db;">vnstocks.com/docs</a></li>
                    <li>Cộng đồng: <a href="https://www.facebook.com/groups/vnstock.official" style="color: #3498db;">vnstocks.com/community</a></li>
                </ul>
                <p>Khám phá các tính năng mới nhất và tham gia cộng đồng để nhận hỗ trợ.</p>
            </div>
            ''';fallback[_F]='\n## 👋 Chào mừng bạn đến với Vnstock!\n\nCảm ơn bạn đã sử dụng package phân tích chứng khoán #1 tại Việt Nam\n\n* Tài liệu: [Sổ tay hướng dẫn](https://vnstocks.com/docs)\n* Cộng đồng: [Nhóm Facebook](https://facebook.com/groups/vnstock.official)\n\nKhám phá các tính năng mới nhất và tham gia cộng đồng để nhận hỗ trợ.\n                ';fallback[_E]='\n╔════════════════════════════════════════════════════════════╗\n║                                                            ║\n║  👋 Chào mừng bạn đến với Vnstock!                         ║\n║                                                            ║\n║  Cảm ơn bạn đã sử dụng package phân tích                   ║\n║  chứng khoán #1 tại Việt Nam                               ║\n║                                                            ║\n║  ✓ Tài liệu: https://vnstocks.com/docs                     ║\n║  ✓ Cộng đồng: https://facebook.com/groups/vnstock.official ║\n║                                                            ║\n║  Khám phá các tính năng mới nhất và tham gia               ║\n║  cộng đồng để nhận hỗ trợ.                                 ║\n║                                                            ║\n╚════════════════════════════════════════════════════════════╝\n                ';fallback[_G]='👋 Chào mừng bạn đến với Vnstock! Tài liệu: https://vnstocks.com/onboard | Cộng đồng: https://facebook.com/groups/vnstock.official'
		return fallback
manager=ContentManager()
def present(context:str=_H,ad_category:int=AdCategory.FREE)->_A:manager.present_content(context=context,ad_category=ad_category)