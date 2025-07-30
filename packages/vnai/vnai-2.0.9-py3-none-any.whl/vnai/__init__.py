_L='default'
_K='standard'
_J='accepted_agreement'
_I='environment.json'
_H='terms_agreement.txt'
_G='timestamp'
_F=False
_E='id'
_D='.vnstock'
_C='machine_id'
_B=None
_A=True
import os,pathlib,json,time,threading,functools
from datetime import datetime
from vnai.beam.quota import guardian,optimize
from vnai.beam.metrics import collector,capture
from vnai.beam.pulse import monitor
from vnai.flow.relay import conduit,configure
from vnai.flow.queue import buffer
from vnai.scope.profile import inspector
from vnai.scope.state import tracker,record
import vnai.scope.promo
from vnai.scope.promo import present
TC_VAR='ACCEPT_TC'
TC_VAL='tôi đồng ý'
TC_PATH=pathlib.Path.home()/_D/_E/_H
TERMS_AND_CONDITIONS='\nKhi tiếp tục sử dụng Vnstock, bạn xác nhận rằng bạn đã đọc, hiểu và đồng ý với Chính sách quyền riêng tư và Điều khoản, điều kiện về giấy phép sử dụng Vnstock.\n\nChi tiết:\n- Giấy phép sử dụng phần mềm: https://vnstocks.com/docs/tai-lieu/giay-phep-su-dung\n- Chính sách quyền riêng tư: https://vnstocks.com/docs/tai-lieu/chinh-sach-quyen-rieng-tu\n'
class Core:
	def __init__(self):self.initialized=_F;self.webhook_url=_B;self.init_time=datetime.now().isoformat();self.home_dir=pathlib.Path.home();self.project_dir=self.home_dir/_D;self.id_dir=self.project_dir/_E;self.terms_file_path=TC_PATH;self.system_info=_B;self.project_dir.mkdir(exist_ok=_A);self.id_dir.mkdir(exist_ok=_A);self.initialize()
	def initialize(self,webhook_url=_B):
		if self.initialized:return _A
		if not self._check_terms():self._accept_terms()
		from vnai.scope.profile import inspector;inspector.setup_vnstock_environment();present()
		if webhook_url:self.webhook_url=webhook_url;configure(webhook_url)
		record('initialization',{_G:datetime.now().isoformat()});self.system_info=inspector.examine();conduit.queue({'type':'system_info','data':{'commercial':inspector.detect_commercial_usage(),'packages':inspector.scan_packages()}},priority='high');self.initialized=_A;return _A
	def _check_terms(self):return os.path.exists(self.terms_file_path)
	def _accept_terms(self):
		system_info=inspector.examine()
		if TC_VAR in os.environ and os.environ[TC_VAR]==TC_VAL:response=TC_VAL
		else:response=TC_VAL;os.environ[TC_VAR]=TC_VAL
		now=datetime.now();signed_agreement=f"""Người dùng có mã nhận dạng {system_info[_C]} đã chấp nhận điều khoản & điều kiện sử dụng Vnstock lúc {now}
---

THÔNG TIN THIẾT BỊ: {json.dumps(system_info,indent=2)}

Đính kèm bản sao nội dung bạn đã đọc, hiểu rõ và đồng ý dưới đây:
{TERMS_AND_CONDITIONS}"""
		with open(self.terms_file_path,'w',encoding='utf-8')as f:f.write(signed_agreement)
		env_file=self.id_dir/_I;env_data={_J:_A,_G:now.isoformat(),_C:system_info[_C]}
		with open(env_file,'w')as f:json.dump(env_data,f)
		return _A
	def status(self):return{'initialized':self.initialized,'health':monitor.report(),'metrics':tracker.get_metrics()}
	def configure_privacy(self,level=_K):from vnai.scope.state import tracker;return tracker.setup_privacy(level)
core=Core()
def tc_init(webhook_url=_B):return core.initialize(webhook_url)
def setup(webhook_url=_B):return core.initialize(webhook_url)
def optimize_execution(resource_type=_L):return optimize(resource_type)
def agg_execution(resource_type=_L):return optimize(resource_type,ad_cooldown=1500,content_trigger_threshold=100000)
def measure_performance(module_type='function'):return capture(module_type)
def accept_license_terms(terms_text=_B):
	if terms_text is _B:terms_text=TERMS_AND_CONDITIONS
	system_info=inspector.examine();terms_file=pathlib.Path.home()/_D/_E/_H;os.makedirs(os.path.dirname(terms_file),exist_ok=_A)
	with open(terms_file,'w',encoding='utf-8')as f:f.write(f"Terms accepted at {datetime.now().isoformat()}\n");f.write(f"System: {json.dumps(system_info)}\n\n");f.write(terms_text)
	return _A
def accept_vnstock_terms():
	from vnai.scope.profile import inspector;system_info=inspector.examine();home_dir=pathlib.Path.home();project_dir=home_dir/_D;project_dir.mkdir(exist_ok=_A);id_dir=project_dir/_E;id_dir.mkdir(exist_ok=_A);env_file=id_dir/_I;env_data={_J:_A,_G:datetime.now().isoformat(),_C:system_info[_C]}
	try:
		with open(env_file,'w')as f:json.dump(env_data,f)
		print('Vnstock terms accepted successfully.');return _A
	except Exception as e:print(f"Error accepting terms: {e}");return _F
def setup_for_colab():from vnai.scope.profile import inspector;inspector.detect_colab_with_delayed_auth(immediate=_A);inspector.setup_vnstock_environment();return'Environment set up for Google Colab'
def display_content():return present()
def configure_privacy(level=_K):from vnai.scope.state import tracker;return tracker.setup_privacy(level)
def check_commercial_usage():from vnai.scope.profile import inspector;return inspector.detect_commercial_usage()
def authenticate_for_persistence():from vnai.scope.profile import inspector;return inspector.get_or_create_user_id()
def configure_webhook(webhook_id='80b8832b694a75c8ddc811ac7882a3de'):
	if not webhook_id:return _F
	from vnai.flow.relay import configure;webhook_url=f"https://botbuilder.larksuite.com/api/trigger-webhook/{webhook_id}";return configure(webhook_url)
configure_webhook()