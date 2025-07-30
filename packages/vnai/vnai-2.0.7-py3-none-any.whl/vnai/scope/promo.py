"""
Promo module for vnai: fetches and presents promotional content periodically or on demand,
using logging instead of printing to avoid polluting stdout for AI tools.
"""
import logging
import requests
from datetime import datetime
import random
import threading
import time
import urllib.parse

_vnii_check_attempted = False

# Enum AdCategory (tương thích với vnii)
class AdCategory:
    FREE = 0
    MANDATORY = 1
    ANNOUNCEMENT = 2
    REFERRAL = 3
    FEATURE = 4
    GUIDE = 5
    SURVEY = 6
    PROMOTION = 7
    SECURITY = 8
    MAINTENANCE = 9
    WARNING = 10

# Thêm import kiểm tra license từ vnii
try:
    from vnii import lc_init
except ImportError:
    lc_init = None  # Nếu không có vnii, luôn coi là free user

# Module-level logger setup
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    # Add a simple stream handler that only outputs the message text
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class ContentManager:
    """
    Singleton manager to fetch remote or fallback promotional content and
    present it in different environments (Jupyter, terminal, other).

    Displays content automatically at randomized intervals via a background thread.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Ensure only one instance of ContentManager is created (thread-safe).
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ContentManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """
        Internal initializer: sets up display timing, URLs, and starts the periodic display thread.
        """
        global _vnii_check_attempted
        if _vnii_check_attempted:
            # Đã kiểm tra/cài đặt vnii trước đó, không làm lại nữa
            return
        _vnii_check_attempted = True
        # Nếu máy đã từng cài vnii, luôn cài lại bản mới nhất; nếu chưa từng cài thì coi là free user
        import sys
        import importlib
        try:
            import importlib.metadata
            try:
                old_version = importlib.metadata.version("vnii")
                # Nếu đã từng cài, luôn force cài bản mới nhất
                VNII_LATEST_VERSION = "0.0.9"
                VNII_URL = f"https://github.com/vnstock-hq/licensing/releases/download/vnii-{VNII_LATEST_VERSION}/vnii-{VNII_LATEST_VERSION}.tar.gz"
                logger.debug(f"Đã phát hiện vnii version {old_version}. Đang cập nhật lên bản mới nhất...")
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", f"vnii@{VNII_URL}"])
                importlib.invalidate_caches()
                if "vnii" in sys.modules:
                    importlib.reload(sys.modules["vnii"])
                else:
                    import vnii
                new_version = importlib.metadata.version("vnii")
                logger.debug(f"Đã cập nhật vnii lên version {new_version}")
            except importlib.metadata.PackageNotFoundError:
                # Nếu chưa từng cài, không cài, luôn coi là free user
                logger.debug("Không phát hiện vnii trên hệ thống. Luôn coi là free user, không kiểm tra license.")
                self.is_paid_user = False
                return
        except Exception as e:
            logger.warning(f"Lỗi khi kiểm tra/cài đặt vnii: {e}")
            user_msg = (
                "Không thể tự động cài đặt/cập nhật vnii. "
                "Vui lòng liên hệ admin hoặc hỗ trợ kỹ thuật của Vnstock để được trợ giúp. "
                f"Chi tiết lỗi: {e}"
            )
            logger.error(user_msg)
            try:
                print(user_msg)
            except Exception:
                pass
            self.is_paid_user = False
            return

        # Kiểm tra trạng thái paid user (sponsor) và cache lại
        self.is_paid_user = False
        logger.debug("[promo] Bắt đầu kiểm tra trạng thái paid user với vnii...")
        if lc_init is not None:
            try:
                license_info = lc_init(repo_name='vnstock')
                logger.debug(f"[promo] license_info trả về: {license_info}")
                status = license_info.get('status', '').lower()
                if 'recognized and verified' in status:
                    self.is_paid_user = True
                    logger.debug("[promo] Đã xác nhận paid user từ vnii. Sẽ không hiện quảng cáo.")
                else:
                    logger.debug(f"[promo] Không xác nhận được paid user từ vnii. Status: {status}")
            except Exception as e:
                logger.warning(f"[promo] Không thể kiểm tra trạng thái sponsor: {e}. Sẽ coi là free user và hiện quảng cáo.")
        else:
            logger.debug("[promo] Không tìm thấy module vnii. Luôn coi là free user và hiện quảng cáo.")

        # Timestamp of last content display (epoch seconds)
        self.last_display = 0
        # Minimum interval between displays (24 hours)
        self.display_interval = 24 * 3600

        # Base endpoints for fetching remote content and linking
        self.content_base_url = "https://hq.vnstocks.com/static"
        self.target_url = "https://vnstocks.com/lp-khoa-hoc-python-chung-khoan"
        self.image_url = (
            "https://vnstocks.com/img/trang-chu-vnstock-python-api-phan-tich-giao-dich-chung-khoan.jpg"
        )

        # Launch the background thread to periodically present content
        logger.debug(f"[promo] is_paid_user = {self.is_paid_user}")
        self._start_periodic_display()

    def _start_periodic_display(self):
        """
        Launch a daemon thread that sleeps a random duration between 2–6 hours,
        then checks if the display interval has elapsed and calls present_content.
        """
        logger.debug("[promo] Khởi tạo thread hiển thị quảng cáo định kỳ...")
        def periodic_display():
            logger.debug("[promo] Thread quảng cáo bắt đầu chạy.")
            while True:
                # Nếu là paid user thì không bao giờ hiện ads
                if self.is_paid_user:
                    logger.debug("[promo] Đang là paid user trong thread. Không hiện quảng cáo, dừng thread.")
                    break
                # Randomize sleep to avoid synchronized requests across instances
                sleep_time = random.randint(2 * 3600, 6 * 3600)
                logger.debug(f"[promo] Thread quảng cáo sẽ ngủ {sleep_time//3600} giờ...")
                time.sleep(sleep_time)

                # Present content if enough time has passed since last_display
                current_time = time.time()
                logger.debug(f"[promo] Kiểm tra điều kiện hiện quảng cáo: time since last_display = {current_time - self.last_display}s")
                if current_time - self.last_display >= self.display_interval:
                    logger.debug("[promo] Đã đủ thời gian, sẽ gọi present_content(context='periodic')")
                    self.present_content(context="periodic")
                else:
                    logger.debug("[promo] Chưa đủ thời gian, chưa hiện quảng cáo.")

        thread = threading.Thread(target=periodic_display, daemon=True)
        thread.start()

    def fetch_remote_content(self, context: str = "init", html: bool = True) -> str:
        if self.is_paid_user:
            logger.debug("Paid user detected. Skip fetching remote content (ads).")
            return ""

        """
        Fetch promotional content from remote service with context and format flag.

        Args:
            context: usage context (e.g., "init", "periodic", "loop").
            html: if True, request HTML; otherwise plain text.

        Returns:
            The content string on HTTP 200, or None on failure.
        """
        try:
            # Build query params and URL
            params = {"context": context, "html": "true" if html else "false"}
            url = f"{self.content_base_url}?{urllib.parse.urlencode(params)}"

            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                return response.text
            # Log non-200 responses at debug level
            logger.debug(f"Non-200 response fetching content: {response.status_code}")
            return None
        except Exception as e:
            # Log exceptions without interrupting user code
            logger.debug(f"Failed to fetch remote content: {e}")
            return None

    def present_content(self, context: str = "init", ad_category: int = AdCategory.FREE) -> None:
        environment = None
        logger.debug(f"[promo] Gọi present_content(context={context}, ad_category={ad_category}). is_paid_user = {getattr(self, 'is_paid_user', None)}")
        """
        Display promotional content in the appropriate environment.
        ad_category: Loại quảng cáo (FREE, ANNOUNCEMENT, ...)
        """
        # Nếu là paid user và ad_category là FREE thì skip, còn lại vẫn hiện
        if getattr(self, 'is_paid_user', False) and ad_category == AdCategory.FREE:
            logger.debug("[promo] Đang là paid user và ad_category là FREE. Không hiện quảng cáo.")
            return

        # Chỉ hiện log này nếu debug mode
        if logger.level <= logging.DEBUG:
            logger.debug(f"[promo] Sẽ hiển thị quảng cáo với context={context}, ad_category={ad_category}")
        # Update last display timestamp
        self.last_display = time.time()

        # Auto-detect environment if not provided
        if environment is None:
            try:
                from vnai.scope.profile import inspector
                environment = inspector.examine().get("environment", "unknown")
                logger.debug(f"[promo] Đã detect environment: {environment}")
            except Exception as e:
                logger.debug(f"[promo] Không detect được environment: {e}")
                environment = "unknown"

        # Retrieve remote or HTML/text content based on environment
        remote_content = self.fetch_remote_content(
            context=context, html=(environment == "jupyter")
        )
        logger.debug(f"[promo] remote_content = {bool(remote_content)} (None -> False, có nội dung -> True)")
        # Generate fallback messages if remote fetch fails
        fallback = self._generate_fallback_content(context)
        logger.debug(f"[promo] fallback keys: {list(fallback.keys())}")

        if environment == "jupyter":
            logger.debug("[promo] Đang ở môi trường Jupyter, sẽ thử display HTML/Markdown.")
            try:
                from IPython.display import display, HTML, Markdown

                if remote_content:
                    logger.debug("[promo] Hiển thị quảng cáo bằng HTML từ remote_content.")
                    display(HTML(remote_content))
                else:
                    logger.debug("[promo] Không có remote_content, thử display fallback Markdown/HTML.")
                    try:
                        display(Markdown(fallback["markdown"]))
                    except Exception as e:
                        logger.debug(f"[promo] Lỗi khi display Markdown: {e}, fallback HTML.")
                        display(HTML(fallback["html"]))
            except Exception as e:
                logger.debug(f"[promo] Jupyter display failed: {e}")

        elif environment == "terminal":
            logger.debug("[promo] Đang ở môi trường terminal, sẽ log quảng cáo ra logger.")
            # Log terminal-friendly or raw content via logger
            if remote_content:
                logger.debug("[promo] Hiển thị quảng cáo bằng remote_content cho terminal.")
                logger.debug(remote_content)
            else:
                logger.debug("[promo] Không có remote_content, hiển thị fallback terminal.")
                logger.debug(fallback["terminal"])

        else:
            logger.debug(f"[promo] Môi trường khác ({environment}), hiển thị fallback simple.")
            # Generic simple message for other environments
            logger.debug(fallback["simple"])

    def _generate_fallback_content(self, context):
        fallback = {"html": "", "markdown": "", "terminal": "", "simple": ""}

        if context == "loop":
            fallback["html"] = (
                f"""
            <div style="border: 1px solid #e74c3c; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3 style="color: #e74c3c;">⚠️ Bạn đang sử dụng vòng lặp với quá nhiều requests</h3>
                <p>Để tránh bị giới hạn tốc độ và tối ưu hiệu suất:</p>
                <ul>
                    <li>Thêm thời gian chờ giữa các lần gọi API</li>
                    <li>Sử dụng xử lý theo batch thay vì lặp liên tục</li>
                    <li>Tham gia gói tài trợ <a href="https://vnstocks.com/insiders-program" style="color: #3498db;">Vnstock Insider</a> để tăng 5X giới hạn API</li>
                </ul>
            </div>
            """
            )
            fallback["markdown"] = (
                """
## ⚠️ Bạn đang sử dụng vòng lặp với quá nhiều requests

Để tránh bị giới hạn tốc độ và tối ưu hiệu suất:
* Thêm thời gian chờ giữa các lần gọi API
* Sử dụng xử lý theo batch thay vì lặp liên tục
* Tham gia gói tài trợ [Vnstock Insider](https://vnstocks.com/insiders-program) để tăng 5X giới hạn API
            """
            )
            fallback["terminal"] = (
                """
╔═════════════════════════════════════════════════════════════════╗
║                                                                 ║
║   🚫 ĐANG BỊ CHẶN BỞI GIỚI HẠN API? GIẢI PHÁP Ở ĐÂY!            ║
║                                                                 ║
║   ✓ Tăng ngay 500% tốc độ gọi API - Không còn lỗi RateLimit     ║
║   ✓ Tiết kiệm 85% thời gian chờ đợi giữa các request            ║
║                                                                 ║
║   ➤ NÂNG CẤP NGAY VỚI GÓI TÀI TRỢ VNSTOCK:                      ║
║     https://vnstocks.com/insiders-program                       ║
║                                                                 ║
╚═════════════════════════════════════════════════════════════════╝
                """
            )
            fallback["simple"] = (
                "🚫 Đang bị giới hạn API? Tăng tốc độ gọi API lên 500% với gói "
                "Vnstock Insider: https://vnstocks.com/insiders-program"
            )
        else:
            fallback["html"] = (
                f"""
            <div style="border: 1px solid #3498db; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3 style="color: #3498db;">👋 Chào mừng bạn đến với Vnstock!</h3>
                <p>Cảm ơn bạn đã sử dụng thư viện phân tích chứng khoán #1 tại Việt Nam cho Python</p>
                <ul>
                    <li>Tài liệu: <a href="https://vnstocks.com/docs/category/s%E1%BB%95-tay-h%C6%B0%E1%BB%9Bng-d%E1%BA%ABn" style="color: #3498db;">vnstocks.com/docs</a></li>
                    <li>Cộng đồng: <a href="https://www.facebook.com/groups/vnstock.official" style="color: #3498db;">vnstocks.com/community</a></li>
                </ul>
                <p>Khám phá các tính năng mới nhất và tham gia cộng đồng để nhận hỗ trợ.</p>
            </div>
            """
            )
            fallback["markdown"] = (
                """
## 👋 Chào mừng bạn đến với Vnstock!

Cảm ơn bạn đã sử dụng package phân tích chứng khoán #1 tại Việt Nam

* Tài liệu: [Sổ tay hướng dẫn](https://vnstocks.com/docs)
* Cộng đồng: [Nhóm Facebook](https://facebook.com/groups/vnstock.official)

Khám phá các tính năng mới nhất và tham gia cộng đồng để nhận hỗ trợ.
                """
            )
            fallback["terminal"] = (
                """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  👋 Chào mừng bạn đến với Vnstock!                         ║
║                                                            ║
║  Cảm ơn bạn đã sử dụng package phân tích                   ║
║  chứng khoán #1 tại Việt Nam                               ║
║                                                            ║
║  ✓ Tài liệu: https://vnstocks.com/docs                     ║
║  ✓ Cộng đồng: https://facebook.com/groups/vnstock.official ║
║                                                            ║
║  Khám phá các tính năng mới nhất và tham gia               ║
║  cộng đồng để nhận hỗ trợ.                                 ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
                """
            )
            fallback["simple"] = (
                "👋 Chào mừng bạn đến với Vnstock! "
                "Tài liệu: https://vnstocks.com/onboard | "
                "Cộng đồng: https://facebook.com/groups/vnstock.official"
            )
        return fallback

# Singleton instance for module-level use
manager = ContentManager()

def present(context: str = "init", ad_category: int = AdCategory.FREE) -> None:
    """
    Shortcut to ContentManager.present_content for external callers.

    Args:
        context: propagate context string to ContentManager.
        ad_category: loại quảng cáo (FREE, ANNOUNCEMENT, ...)
    """
    manager.present_content(context=context, ad_category=ad_category)
