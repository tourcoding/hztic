import time

class BeisenRateLimiter:
    def __init__(self, requests_per_second=100, requests_per_minute=3000):
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self.request_counter = 0
        self.start_time = time.time()

    def _reset_rate_limit(self):
        """重置速率限制计数器"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= 60:            # 每60秒重置一次计数器
            self.request_counter = 0
            self.start_time = current_time

    def wait_for_rate_limit(self):
        """根据速率限制等待适当的时间"""
        self._reset_rate_limit()
        self.request_counter += 1

        if self.request_counter > self.requests_per_second:
            sleep_time = max(0, 1 - (time.time() - self.start_time))
            time.sleep(sleep_time)
            self._reset_rate_limit()
            self.request_counter = 1  # 重置计数器，因为已经等待了一秒

        if self.request_counter % self.requests_per_second == 0 and self.request_counter > 0:
            # 如果接近requests_per_minute次/分钟，则强制等待直到下一分钟开始
            time_until_next_minute = 60 - (time.time() - self.start_time) % 60 + 1
            time.sleep(time_until_next_minute)
            self._reset_rate_limit()